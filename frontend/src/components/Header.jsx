import React from 'react';
import { Brain, LogOut } from 'lucide-react';

function Header({ userName, onDisconnect }) {
  return (
    <div style={{ 
      backgroundColor: 'white', 
      borderRadius: '12px', 
      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)', 
      padding: '20px', 
      marginBottom: '24px',
      border: '1px solid #e5e7eb'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ 
            backgroundColor: '#4f46e5', 
            borderRadius: '12px', 
            padding: '12px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <Brain size={32} color="white" />
          </div>
          <div>
            <h1 style={{ fontSize: '22px', fontWeight: 'bold', color: '#1f2937', margin: 0 }}>
              Modèle de Description d'Image IA
            </h1>
            <p style={{ fontSize: '14px', color: '#6b7280', margin: '4px 0 0 0' }}>
              Connecté en tant que: <span style={{ fontWeight: '500', color: '#4f46e5' }}>{userName}</span>
            </p>
          </div>
        </div>
        <button
          onClick={onDisconnect}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '10px 16px',
            backgroundColor: '#ef4444',
            color: 'white',
            borderRadius: '8px',
            border: 'none',
            cursor: 'pointer',
            fontWeight: '500',
            fontSize: '14px',
            transition: 'all 0.2s',
            boxShadow: '0 2px 4px rgba(239, 68, 68, 0.2)'
          }}
          onMouseOver={(e) => {
            e.target.style.backgroundColor = '#dc2626';
            e.target.style.transform = 'translateY(-1px)';
          }}
          onMouseOut={(e) => {
            e.target.style.backgroundColor = '#ef4444';
            e.target.style.transform = 'translateY(0)';
          }}
        >
          <LogOut size={16} />
          Déconnexion
        </button>
      </div>
    </div>
  );
}

export default Header;