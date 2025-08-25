// API service for communicating with the FastAPI backend

const API_BASE_URL = 'http://localhost:8000/api';

class ApiService {
  async extractParameters(data) {
    const response = await fetch(`${API_BASE_URL}/extract-parameters`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to extract parameters');
    }
    
    return response.json();
  }

  async parseParameters(extractedParameters) {
    const response = await fetch(`${API_BASE_URL}/parse-parameters`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ extractedParameters }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to parse parameters');
    }
    
    return response.json();
  }

  async generateGCode(data) {
    const response = await fetch(`${API_BASE_URL}/generate-gcode`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to generate G-code');
    }
    
    return response.json();
  }

  async uploadPDF(files) {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });
    
    const response = await fetch(`${API_BASE_URL}/upload-pdf`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to upload PDF files');
    }
    
    return response.json();
  }

  async getAvailableModels() {
    const response = await fetch(`${API_BASE_URL}/models`);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch models');
    }
    
    return response.json();
  }

  async healthCheck() {
    const response = await fetch(`${API_BASE_URL}/health`);
    
    if (!response.ok) {
      throw new Error('Backend is not responding');
    }
    
    return response.json();
  }
}

export default new ApiService();
