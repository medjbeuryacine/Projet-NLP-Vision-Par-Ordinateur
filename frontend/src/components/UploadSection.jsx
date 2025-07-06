import React from 'react';
import { Upload, Camera, Brain, Loader2, X } from 'lucide-react';

function UploadSection({ selectedImage, imagePreview, isLoading, onImageUpload, onAnalyze, onClearImage }) {
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
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2 style={{ fontSize: '20px', fontWeight: '600', color: '#1f2937', margin: 0 }}>
          Upload d'Image
        </h2>
        <div style={{ 
          backgroundColor: '#f0f9ff', 
          borderRadius: '8px', 
          padding: '8px',
          display: 'flex',
          alignItems: 'center'
        }}>
          <Upload size={20} color="#0ea5e9" />
        </div>
      </div>
      
      <div style={{ flex: '1', display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <div style={{ flex: '1', position: 'relative', minHeight: imagePreview ? 'auto' : '300px' }}>
          <input
            type="file"
            accept="image/*"
            onChange={onImageUpload}
            style={{ display: 'none' }}
            id="image-upload"
          />
          <label
            htmlFor="image-upload"
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              width: '100%',
              height: '100%',
              border: imagePreview ? '2px solid #4f46e5' : '2px dashed #d1d5db',
              borderRadius: '12px',
              cursor: 'pointer',
              backgroundColor: imagePreview ? '#fafafa' : '#fafafa',
              transition: 'all 0.2s',
              position: 'relative'
            }}
            onMouseOver={(e) => {
              if (!imagePreview) {
                e.target.style.backgroundColor = '#f3f4f6';
                e.target.style.borderColor = '#9ca3af';
              }
            }}
            onMouseOut={(e) => {
              if (!imagePreview) {
                e.target.style.backgroundColor = '#fafafa';
                e.target.style.borderColor = '#d1d5db';
              }
            }}
          >
            {imagePreview ? (
              <div style={{ 
                position: 'relative', 
                width: '100%', 
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                padding: '8px'
              }}>
                <img
                  src={imagePreview}
                  alt="Preview"
                  style={{
                    maxWidth: '100%',
                    height: 'auto',
                    borderRadius: '10px',
                    display: 'block'
                  }}
                />
                <button
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    onClearImage();
                  }}
                  style={{
                    position: 'absolute',
                    top: '12px',
                    right: '12px',
                    backgroundColor: '#ef4444',
                    color: 'white',
                    borderRadius: '50%',
                    border: 'none',
                    padding: '8px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.2)',
                    transition: 'all 0.2s'
                  }}
                  onMouseOver={(e) => {
                    e.target.style.backgroundColor = '#dc2626';
                    e.target.style.transform = 'scale(1.1)';
                  }}
                  onMouseOut={(e) => {
                    e.target.style.backgroundColor = '#ef4444';
                    e.target.style.transform = 'scale(1)';
                  }}
                >
                  <X size={16} />
                </button>
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '40px' }}>
                <div style={{ 
                  backgroundColor: '#f0f9ff', 
                  borderRadius: '50%', 
                  padding: '20px', 
                  display: 'inline-flex',
                  marginBottom: '16px'
                }}>
                  <Camera size={48} color="#0ea5e9" />
                </div>
                <p style={{ color: '#1f2937', fontWeight: '600', margin: '0 0 8px 0', fontSize: '18px' }}>
                  Sélectionnez une image
                </p>
                <p style={{ fontSize: '14px', color: '#6b7280', margin: 0 }}>
                  Cliquez ici ou glissez-déposez votre image<br/>
                  <span style={{ fontSize: '12px', color: '#9ca3af' }}>
                    Formats supportés: JPG, PNG, GIF
                  </span>
                </p>
              </div>
            )}
          </label>
        </div>
        
        <button
          onClick={onAnalyze}
          disabled={!selectedImage || isLoading}
          style={{
            width: '100%',
            padding: '14px 16px',
            backgroundColor: !selectedImage || isLoading ? '#9ca3af' : '#4f46e5',
            color: 'white',
            borderRadius: '10px',
            border: 'none',
            cursor: !selectedImage || isLoading ? 'not-allowed' : 'pointer',
            fontWeight: '600',
            fontSize: '16px',
            transition: 'all 0.2s',
            boxShadow: !selectedImage || isLoading ? 'none' : '0 4px 12px rgba(79, 70, 229, 0.3)'
          }}
          onMouseOver={(e) => {
            if (selectedImage && !isLoading) {
              e.target.style.backgroundColor = '#4338ca';
              e.target.style.transform = 'translateY(-2px)';
            }
          }}
          onMouseOut={(e) => {
            if (selectedImage && !isLoading) {
              e.target.style.backgroundColor = '#4f46e5';
              e.target.style.transform = 'translateY(0)';
            }
          }}
        >
          {isLoading ? (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '12px' }}>
              <Loader2 size={20} style={{ animation: 'spin 1s linear infinite' }} />
              <span>Analyse en cours...</span>
            </div>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
              <Brain size={18} />
              <span>Analyser avec IA</span>
            </div>
          )}
        </button>
      </div>
      
      {/* Style pour l'animation */}
      <style jsx>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

export default UploadSection;