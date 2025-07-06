import React from 'react';
import { Brain, Loader2 } from 'lucide-react';

function ResultsSection({ isLoading, description }) {
  return (
    <div style={{ 
      flex: '1', 
      backgroundColor: 'white', 
      borderRadius: '12px', 
      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)', 
      padding: '24px',
      display: 'flex',
      flexDirection: 'column',
      border: '1px solid #e5e7eb'
    }}>
      <div style={{ marginBottom: '20px' }}>
        <h2 style={{ fontSize: '20px', fontWeight: '600', color: '#1f2937', margin: '0 0 8px 0' }}>
          Résultats de l'Analyse
        </h2>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '14px', color: '#6b7280' }}>
            <div style={{ 
              width: '8px', 
              height: '8px', 
              borderRadius: '50%', 
              backgroundColor: isLoading ? '#f59e0b' : description ? '#10b981' : '#6b7280' 
            }}></div>
            <span>
              {isLoading ? 'Traitement en cours...' : description ? 'Description générée' : 'En attente d\'analyse'}
            </span>
          </div>
          {isLoading && <Loader2 size={16} color="#f59e0b" style={{ animation: 'spin 1s linear infinite' }} />}
        </div>
      </div>
      
      <div style={{ 
        backgroundColor: '#f8fafc', 
        borderRadius: '12px', 
        padding: '24px', 
        flex: '1',
        overflow: 'auto',
        border: '1px solid #e2e8f0'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
          <Brain size={20} color="#4f46e5" />
          <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#1f2937', margin: 0 }}>
            Modèle LSTM - Description Automatique
          </h3>
        </div>
        
        {isLoading ? (
          <LoadingState />
        ) : description ? (
          <DescriptionResult description={description} />
        ) : (
          <EmptyState />
        )}
      </div>
      
      {/* Style pour les animations */}
      <style jsx>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

function LoadingState() {
  return (
    <div style={{ 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center', 
      height: '250px',
      flexDirection: 'column',
      gap: '16px'
    }}>
      <div style={{ position: 'relative' }}>
        <Loader2 size={40} color="#4f46e5" style={{ animation: 'spin 1s linear infinite' }} />
      </div>
      <div style={{ textAlign: 'center' }}>
        <p style={{ color: '#4f46e5', margin: '0 0 4px 0', fontWeight: '500' }}>
          Génération en cours...
        </p>
        <p style={{ color: '#6b7280', margin: 0, fontSize: '14px' }}>
          Le modèle analyse votre image
        </p>
      </div>
    </div>
  );
}

function DescriptionResult({ description }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div style={{ 
        backgroundColor: 'white', 
        padding: '20px', 
        borderRadius: '10px', 
        borderLeft: '4px solid #4f46e5',
        boxShadow: '0 2px 4px rgba(0, 0, 0, 0.05)'
      }}>
        <div style={{ display: 'flex', alignItems: 'start', gap: '12px' }}>
          <div style={{ 
            backgroundColor: '#ede9fe', 
            borderRadius: '6px', 
            padding: '6px',
            marginTop: '2px'
          }}>
            <Brain size={16} color="#7c3aed" />
          </div>
          <p style={{ 
            color: '#1f2937', 
            lineHeight: '1.6', 
            margin: 0,
            fontSize: '15px'
          }}>
            {description}
          </p>
        </div>
      </div>
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        fontSize: '12px', 
        color: '#9ca3af',
        paddingTop: '8px',
        borderTop: '1px solid #e5e7eb'
      }}>
        <span>Modèle: LSTM Neural Network</span>
        <span>{new Date().toLocaleString('fr-FR')}</span>
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div style={{ 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center', 
      height: '250px',
      flexDirection: 'column',
      gap: '16px'
    }}>
      <div style={{ 
        backgroundColor: '#f1f5f9', 
        borderRadius: '50%', 
        padding: '24px' 
      }}>
        <Brain size={48} color="#cbd5e1" />
      </div>
      <div style={{ textAlign: 'center' }}>
        <p style={{ color: '#475569', margin: '0 0 4px 0', fontWeight: '500' }}>
          Prêt pour l'analyse
        </p>
        <p style={{ color: '#94a3b8', margin: 0, fontSize: '14px' }}>
          Uploadez une image pour obtenir une description automatique
        </p>
      </div>
    </div>
  );
}

export default ResultsSection;