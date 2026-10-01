const BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function request(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };

  const token = localStorage.getItem('nb_token');
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    const res = await fetch(url, { ...options, headers });
    if (!res.ok) {
      const errBody = await res.json().catch(() => ({}));
      throw new Error(errBody.detail || `HTTP Error ${res.status}`);
    }
    return await res.json();
  } catch (err) {
    console.warn(`[NoticeBridge API] Request to ${endpoint} failed:`, err.message);
    throw err;
  }
}

export const api = {
  getHealth: () => request('/health'),
  
  // Employment
  getCurrentEmployment: () => request('/employment/current'),
  saveCurrentEmployment: (data) => request('/employment/current', {
    method: 'POST',
    body: JSON.stringify(data)
  }),

  // Offer
  getOffer: () => request('/employment/offer'),
  saveOffer: (data) => request('/employment/offer', {
    method: 'POST',
    body: JSON.stringify(data)
  }),

  // Deterministic Engines
  calculateNotice: (data) => request('/notice/calculate', {
    method: 'POST',
    body: JSON.stringify(data)
  }),

  calculateBuyout: (data) => request('/buyout/calculate', {
    method: 'POST',
    body: JSON.stringify(data)
  }),

  calculateRepayment: (data) => request('/repayment/calculate', {
    method: 'POST',
    body: JSON.stringify(data)
  }),

  simulateScenarios: (data) => request('/scenario/simulate', {
    method: 'POST',
    body: JSON.stringify(data)
  }),

  // Dashboard
  getDashboardSummary: () => request('/dashboard/summary'),

  // Auth
  login: (data) => request('/auth/login', {
    method: 'POST',
    body: JSON.stringify(data)
  }),

  register: (data) => request('/auth/register', {
    method: 'POST',
    body: JSON.stringify(data)
  }),

  logout: () => request('/auth/logout', {
    method: 'POST'
  }),

  getMe: () => request('/auth/me'),

  seedDemo: () => request('/auth/seed-demo', {
    method: 'POST'
  }),

  // Document Intelligence & Targeted RAG
  uploadDocument: async (file, employeeId = null, documentType = 'employment_agreement') => {
    const formData = new FormData();
    formData.append('file', file);
    if (employeeId) {
      formData.append('employee_id', employeeId);
    }
    formData.append('document_type', documentType);

    const headers = {};
    const token = localStorage.getItem('nb_token');
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const url = `${BASE_URL}/documents/upload`;
    const res = await fetch(url, {
      method: 'POST',
      headers,
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Upload failed with status ${res.status}`);
    }
    return await res.json();
  },

  extractContract: (documentId) => request(`/documents/${documentId}/extract-contract`, {
    method: 'POST'
  }),

  extractOffer: (documentId) => request(`/documents/${documentId}/extract-offer`, {
    method: 'POST'
  }),

  confirmContract: (data) => request('/documents/confirm-contract', {
    method: 'POST',
    body: JSON.stringify(data)
  }),

  // Affordability Simulation
  simulateAffordability: (data) => request('/affordability/simulate', {
    method: 'POST',
    body: JSON.stringify(data)
  })
};
