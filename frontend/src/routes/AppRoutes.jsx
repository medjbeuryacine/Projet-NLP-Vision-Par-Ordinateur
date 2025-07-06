import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Login from '../pages/Login';
import ModelAnalyzer from '../pages/ModelAnalyzer';

function AppRoutes() {
  const { isAuthenticated, loading } = useAuth();

  console.log('AppRoutes - isAuthenticated:', isAuthenticated, 'loading:', loading); // Debug

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <div className="text-lg font-medium text-gray-900">Chargement...</div>
        </div>
      </div>
    );
  }

  return (
    <Routes>
      <Route 
        path="/login" 
        element={isAuthenticated ? <Navigate to="/analyzer" replace /> : <Login />} 
      />
      <Route 
        path="/analyzer" 
        element={isAuthenticated ? <ModelAnalyzer /> : <Navigate to="/login" replace />} 
      />
      <Route 
        path="/" 
        element={<Navigate to={isAuthenticated ? "/analyzer" : "/login"} replace />} 
      />
    </Routes>
  );
}

export default AppRoutes;