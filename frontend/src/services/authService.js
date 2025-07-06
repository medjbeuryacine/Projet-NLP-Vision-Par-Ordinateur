const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const authService = {
  async login(email, password) {
    const response = await fetch(`${API_URL}/users/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Erreur de connexion');
    }

    return response.json();
  },

  async checkAuth() {
    // Optionnel : vérifier si le token est toujours valide
    return true;
  },
  async checkAuth() {
    // Optionnel : vérifier si le token est toujours valide
    return true;
  },

  async generateCaption(imageFile, beamWidth = 3, maxLength = 20) {
    const token = localStorage.getItem('authToken');
    
    if (!token) {
      throw new Error('Aucun token trouvé');
    }
    
    const formData = new FormData();
    formData.append('file', imageFile);
    formData.append('beam_width', beamWidth);
    formData.append('max_length', maxLength);

    const response = await fetch(`${API_URL}/generate_caption`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      console.error('Erreur API:', error); // 🔍 DEBUG
      throw new Error(error.detail || 'Erreur lors de la génération');
    }

    return response.json();
  }
};