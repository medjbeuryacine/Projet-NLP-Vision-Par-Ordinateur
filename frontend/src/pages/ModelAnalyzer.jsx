import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { authService } from '../services/authService';
import Header from '../components/Header';
import UploadSection from '../components/UploadSection';
import ResultsSection from '../components/ResultsSection';
import LogoutModal from '../components/LogoutModal';

function ModelAnalyzer() {
  const { user, logout } = useAuth();
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [description, setDescription] = useState('');
  const [showLogoutModal, setShowLogoutModal] = useState(false);
  const [userProfile, setUserProfile] = useState(null);

  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      console.log('Image sélectionnée:', file.name);
      setSelectedImage(file);
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagePreview(e.target.result);
        console.log('Aperçu de l\'image généré');
      };
      reader.readAsDataURL(file);
      setDescription(''); // Reset description when new image is uploaded
    }
  };

  const handleAnalyze = async () => {
    if (!selectedImage) {
      console.log('Aucune image sélectionnée');
      return;
    }
    
    console.log('Début de l\'analyse de l\'image');
    setIsLoading(true);
    
    try {
      const result = await authService.generateCaption(selectedImage);
      setDescription(result.caption_final);
      console.log('Analyse terminée, description générée:', result);
    } catch (error) {
      console.error('Erreur lors de l\'analyse:', error);
      setDescription('Erreur lors de la génération de la description. Veuillez réessayer.');
    } finally {
      setIsLoading(false);
    }
  };

  const clearImage = () => {
    console.log('Nettoyage de l\'image');
    setSelectedImage(null);
    setImagePreview(null);
    setDescription('');
    // Reset du champ file input
    const fileInput = document.getElementById('image-upload');
    if (fileInput) {
      fileInput.value = '';
    }
  };

  const handleDisconnect = () => {
    console.log('Demande de déconnexion');
    setShowLogoutModal(true);
  };

  const confirmLogout = () => {
    console.log('Début du processus de déconnexion');
    // Nettoyage complet des données de l'application
    setSelectedImage(null);
    setImagePreview(null);
    setDescription('');
    setIsLoading(false);
    setShowLogoutModal(false);
    // Déconnexion
    logout();
  };

  const cancelLogout = () => {
    console.log('Déconnexion annulée');
    setShowLogoutModal(false);
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f8fafc', padding: '24px' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        {/* Header */}
        <Header 
            userName={user?.username || 'Utilisateur Demo'} 
            onDisconnect={handleDisconnect} 
          />

        {/* Main Content */}
        <div style={{ display: 'flex', gap: '24px', minHeight: '600px' }}>
          {/* Upload Section */}
          <UploadSection 
            selectedImage={selectedImage}
            imagePreview={imagePreview}
            isLoading={isLoading}
            onImageUpload={handleImageUpload}
            onAnalyze={handleAnalyze}
            onClearImage={clearImage}
          />

          {/* Results Section */}
          <ResultsSection 
            isLoading={isLoading}
            description={description}
          />
        </div>

        {/* Footer */}
        <div style={{ 
          marginTop: '32px', 
          textAlign: 'center', 
          padding: '20px',
          backgroundColor: 'white',
          borderRadius: '12px',
          border: '1px solid #e5e7eb'
        }}>
          <p style={{ 
            margin: '0 0 8px 0', 
            fontSize: '14px', 
            color: '#1f2937',
            fontWeight: '500'
          }}>
            Application de Description d'Image IA
          </p>
          <p style={{ 
            margin: 0, 
            fontSize: '12px', 
            color: '#6b7280'
          }}>
            Propulsé par un modèle LSTM pour la génération de descriptions naturelles
          </p>
        </div>
      </div>

      {/* Modal de déconnexion */}
      {showLogoutModal && (
        <LogoutModal 
          onConfirm={confirmLogout}
          onCancel={cancelLogout}
        />
      )}
    </div>
  );
}

export default ModelAnalyzer;