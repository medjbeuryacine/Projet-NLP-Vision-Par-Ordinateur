import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import io
import logging
from typing import Dict, Any
import sys
import types

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Classe Config pour compatibilité
class Config:
    def __init__(self):
        self.EMBEDDING_DIM = 256
        self.HIDDEN_DIM = 256
        self.ATTENTION_DIM = 256
        self.NUM_LAYERS = 2
        self.DROPOUT = 0.35
        self.LEARNING_RATE = 1e-4
        self.BATCH_SIZE = 32
        self.NUM_EPOCHS = 15
        self.MAX_SEQ_LENGTH = 25
        self.DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.GRAD_CLIP = 5.0
        self.WEIGHT_DECAY = 5e-5

# Classes du modèle (copiées de votre code)
class AdditiveAttention(nn.Module):
    def __init__(self, encoder_dim, decoder_dim, attention_dim):
        super(AdditiveAttention, self).__init__()
        self.encoder_att = nn.Linear(encoder_dim, attention_dim)
        self.decoder_att = nn.Linear(decoder_dim, attention_dim)
        self.full_att = nn.Linear(attention_dim, 1)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.1)
        
    def forward(self, encoder_out, decoder_hidden):
        att1 = self.encoder_att(encoder_out)
        att2 = self.decoder_att(decoder_hidden)
        att = self.full_att(self.relu(att1 + att2.unsqueeze(1))).squeeze(2)
        att = att - att.max(dim=1, keepdim=True)[0]
        alpha = F.softmax(att, dim=1)
        alpha = self.dropout(alpha)
        attention_weighted_encoding = (encoder_out * alpha.unsqueeze(2)).sum(dim=1)
        return attention_weighted_encoding, alpha

class StableVisionEncoder(nn.Module):
    def __init__(self, encoded_image_size=14):
        super(StableVisionEncoder, self).__init__()
        resnet = models.resnet50(weights='DEFAULT')
        modules = list(resnet.children())[:-2]
        self.resnet = nn.Sequential(*modules)
        
        for i, child in enumerate(self.resnet.children()):
            if i < 6:
                for param in child.parameters():
                    param.requires_grad = False
        
        self.adaptive_pool = nn.AdaptiveAvgPool2d((encoded_image_size, encoded_image_size))
        self.bn = nn.BatchNorm2d(2048)
        
    def forward(self, images):
        out = self.resnet(images)
        out = self.adaptive_pool(out)
        out = self.bn(out)
        batch_size = out.size(0)
        out = out.view(batch_size, 2048, -1)
        out = out.permute(0, 2, 1)
        return out

class StableLSTMCaptioningModel(nn.Module):
    def __init__(self, vocab_size, embedding_dim=512, hidden_dim=512, attention_dim=256, 
                 num_layers=2, dropout=0.3, encoded_image_size=14):
        super(StableLSTMCaptioningModel, self).__init__()
        
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.encoded_image_size = encoded_image_size
        
        self.encoder = StableVisionEncoder(encoded_image_size)
        
        self.feature_adapter = nn.Sequential(
            nn.Linear(2048, embedding_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.LayerNorm(embedding_dim)
        )
        
        self.attention = AdditiveAttention(embedding_dim, hidden_dim, attention_dim)
        
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.embedding.weight.data.uniform_(-0.1, 0.1)
        
        self.lstm = nn.LSTM(
            embedding_dim + embedding_dim,
            hidden_dim,
            num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=False
        )
        
        for name, param in self.lstm.named_parameters():
            if 'weight_ih' in name:
                nn.init.xavier_uniform_(param.data)
            elif 'weight_hh' in name:
                nn.init.orthogonal_(param.data)
            elif 'bias' in name:
                param.data.fill_(0)
                n = param.size(0)
                param.data[(n//4):(n//2)].fill_(1)
        
        self.fc1 = nn.Linear(hidden_dim, hidden_dim // 2)
        self.ln1 = nn.LayerNorm(hidden_dim // 2)
        self.dropout1 = nn.Dropout(dropout)
        self.fc2 = nn.Linear(hidden_dim // 2, vocab_size)
        
        self.fc1.weight.data.uniform_(-0.1, 0.1)
        self.fc1.bias.data.fill_(0)
        self.fc2.weight.data.uniform_(-0.1, 0.1)
        self.fc2.bias.data.fill_(0)
        
        self.dropout = nn.Dropout(dropout)
        
    def init_hidden_state(self, batch_size, device):
        h = torch.zeros(self.num_layers, batch_size, self.hidden_dim).to(device)
        c = torch.zeros(self.num_layers, batch_size, self.hidden_dim).to(device)
        return h, c
    
    def forward(self, images, captions):
        batch_size = images.size(0)
        seq_len = captions.size(1)
        
        encoder_out = self.encoder(images)
        encoder_out = self.feature_adapter(encoder_out)
        
        h, c = self.init_hidden_state(batch_size, images.device)
        embeddings = self.embedding(captions)
        outputs = torch.zeros(batch_size, seq_len, self.vocab_size).to(images.device)
        
        for t in range(seq_len):
            attention_weighted_encoding, alpha = self.attention(encoder_out, h[-1])
            lstm_input = torch.cat([embeddings[:, t, :], attention_weighted_encoding], dim=1)
            lstm_input = lstm_input.unsqueeze(1)
            
            lstm_out, (h, c) = self.lstm(lstm_input, (h, c))
            
            output = self.fc1(lstm_out.squeeze(1))
            output = self.ln1(output)
            output = F.relu(output)
            output = self.dropout1(output)
            output = self.fc2(output)
            output = torch.clamp(output, -10, 10)
            
            outputs[:, t, :] = output
        
        return outputs

# Fonction de génération avec beam search
def beam_search_generate(model, image, word_to_idx, idx_to_word, beam_width=3, max_length=20, device='cpu'):
    model.eval()
    
    with torch.no_grad():
        encoder_out = model.encoder(image.unsqueeze(0))
        encoder_out = model.feature_adapter(encoder_out)
        
        start_token = word_to_idx.get('<start>', 1)
        end_token = word_to_idx.get('<end>', 2)
        
        beams = [(torch.tensor([[start_token]]).to(device), 0.0, 
                 model.init_hidden_state(1, device))]
        
        for step in range(max_length - 1):
            new_beams = []
            
            for seq, score, (h, c) in beams:
                if seq[0, -1].item() == end_token:
                    new_beams.append((seq, score, (h, c)))
                    continue
                
                last_word = seq[0, -1].unsqueeze(0).unsqueeze(0)
                word_emb = model.embedding(last_word)
                
                attention_weighted_encoding, _ = model.attention(encoder_out, h[-1])
                
                lstm_input = torch.cat([word_emb.squeeze(1), attention_weighted_encoding], dim=1)
                lstm_input = lstm_input.unsqueeze(1)
                
                lstm_out, (h_new, c_new) = model.lstm(lstm_input, (h, c))
                
                output = model.fc1(lstm_out.squeeze(1))
                output = model.ln1(output)
                output = F.relu(output)
                output = model.fc2(output)
                
                log_probs = F.log_softmax(output, dim=1)
                top_k_scores, top_k_words = torch.topk(log_probs, beam_width)
                
                for i in range(beam_width):
                    word_idx = top_k_words[0, i].item()
                    word_score = top_k_scores[0, i].item()
                    
                    new_seq = torch.cat([seq, torch.tensor([[word_idx]]).to(device)], dim=1)
                    new_score = score + word_score
                    new_beams.append((new_seq, new_score, (h_new, c_new)))
            
            beams = sorted(new_beams, key=lambda x: x[1], reverse=True)[:beam_width]
        
        best_seq = beams[0][0][0].cpu().numpy()
        
        words = []
        for idx in best_seq[1:]:
            if idx == end_token:
                break
            if idx in idx_to_word and idx_to_word[idx] not in ['<pad>', '<unk>', '<start>']:
                words.append(idx_to_word[idx])
        
        return ' '.join(words) if words else "a photo"

# Classe pour gérer le modèle
class CaptionGenerator:
    def __init__(self, model_path: str):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.word_to_idx = None
        self.idx_to_word = None
        self.transform = None
        self.load_model(model_path)
    
    def load_model(self, model_path: str):
        try:
            logger.info(f"Chargement du modèle depuis {model_path}")
            
            # Solution complète pour le problème Config
            import warnings
            warnings.filterwarnings("ignore")
            
            # Créer le module __main__ avec Config
            if '__main__' not in sys.modules:
                main_module = types.ModuleType('__main__')
                main_module.Config = Config
                sys.modules['__main__'] = main_module
            else:
                # Ajouter Config au module __main__ existant
                sys.modules['__main__'].Config = Config
            
            # Créer aussi __mp_main__ pour compatibilité
            if '__mp_main__' not in sys.modules:
                mp_module = types.ModuleType('__mp_main__')
                mp_module.Config = Config
                sys.modules['__mp_main__'] = mp_module
            else:
                sys.modules['__mp_main__'].Config = Config

            # Charger avec weights_only=False (obligatoire pour ce type de modèle)
            checkpoint = torch.load(model_path, map_location=self.device, weights_only=False)
            
            # Charger d'abord les dictionnaires de mots pour avoir la vraie taille du vocabulaire
            if 'word_to_idx' in checkpoint and 'idx_to_word' in checkpoint:
                self.word_to_idx = checkpoint['word_to_idx']
                self.idx_to_word = checkpoint['idx_to_word']
                vocab_size = len(self.word_to_idx)
                logger.info(f"Vocabulaire chargé: {vocab_size} mots")
            else:
                raise ValueError("Dictionnaires word_to_idx et idx_to_word non trouvés dans le checkpoint")
            
            # Récupérer les paramètres du modèle depuis le checkpoint
            if 'model_state_dict' in checkpoint:
                model_state = checkpoint['model_state_dict']
                
                # Vérifier la cohérence entre le vocabulaire et les poids du modèle
                embedding_weight_vocab_size = model_state['embedding.weight'].shape[0]
                logger.info(f"Taille vocabulaire dans embedding.weight: {embedding_weight_vocab_size}")
                logger.info(f"Taille vocabulaire dans word_to_idx: {vocab_size}")
                
                # Utiliser la taille du vocabulaire des poids (plus fiable)
                vocab_size = embedding_weight_vocab_size
                
                # Extraire les autres dimensions
                embedding_dim = model_state['embedding.weight'].shape[1]
                hidden_dim = model_state['fc1.weight'].shape[1]
                attention_dim = model_state['attention.encoder_att.weight'].shape[0]
                num_layers = len([k for k in model_state.keys() if 'lstm.weight_ih_l' in k])
                
                # Si config disponible, utiliser le dropout de là, sinon par défaut
                if 'config' in checkpoint and hasattr(checkpoint['config'], 'DROPOUT'):
                    dropout = checkpoint['config'].DROPOUT
                else:
                    dropout = 0.3
                
                logger.info(f"Paramètres du modèle détectés:")
                logger.info(f"  - vocab_size: {vocab_size}")
                logger.info(f"  - embedding_dim: {embedding_dim}")
                logger.info(f"  - hidden_dim: {hidden_dim}")
                logger.info(f"  - attention_dim: {attention_dim}")
                logger.info(f"  - num_layers: {num_layers}")
                logger.info(f"  - dropout: {dropout}")
                
            else:
                # Fallback vers l'ancienne structure
                vocab_size = checkpoint['vocab_size']
                embedding_dim = checkpoint['embedding_dim']
                hidden_dim = checkpoint['hidden_dim']
                attention_dim = checkpoint['attention_dim']
                num_layers = checkpoint['num_layers']
                dropout = checkpoint['dropout']
                logger.info("Utilisation des paramètres depuis l'ancienne structure du checkpoint")
            
            # Créer le modèle avec les bonnes dimensions
            self.model = StableLSTMCaptioningModel(
                vocab_size=vocab_size,
                embedding_dim=embedding_dim,
                hidden_dim=hidden_dim,
                attention_dim=attention_dim,
                num_layers=num_layers,
                dropout=dropout
            )
            
            # Charger les poids
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.model.to(self.device)
            self.model.eval()
            
            # Transformation pour les images
            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                   std=[0.229, 0.224, 0.225])
            ])
            
            logger.info("Modèle chargé avec succès")
            logger.info(f"Device: {self.device}")
            logger.info(f"Vocabulaire final: {len(self.word_to_idx)} mots")
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle: {e}")
            raise
    
    def generate_caption(self, image: Image.Image, beam_width: int = 3, max_length: int = 20) -> str:
        try:
            # Préprocesser l'image
            image_tensor = self.transform(image).to(self.device)
            
            # Générer la caption
            caption = beam_search_generate(
                self.model, image_tensor, self.word_to_idx, self.idx_to_word,
                beam_width=beam_width, max_length=max_length, device=self.device
            )
            
            return caption
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération: {e}")
            return "error generating caption"
        
    def is_loaded(self):
        return self.model is not None
        
# Fonctions globales pour l'API
_caption_generator = None

def get_caption_generator():
    return _caption_generator

def initialize_caption_generator(model_path: str):
    global _caption_generator
    _caption_generator = CaptionGenerator(model_path)
    return _caption_generator