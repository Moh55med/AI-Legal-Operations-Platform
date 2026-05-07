import api from './api';

// Document management service
export const documentsService = {
  // Get all documents with optional filters
  getAllDocuments: async (skip = 0, limit = 10, filters = {}) => {
    const params = new URLSearchParams({ skip, limit });
    
    if (filters.case_id) params.append('case_id', filters.case_id);
    if (filters.filename) params.append('filename', filters.filename);
    if (filters.uploaded_by) params.append('uploaded_by', filters.uploaded_by);
    if (filters.uploaded_at) params.append('uploaded_at', filters.uploaded_at);
    if (filters.uploaded_at_from) params.append('uploaded_at_from', filters.uploaded_at_from);
    if (filters.uploaded_at_to) params.append('uploaded_at_to', filters.uploaded_at_to);

    const response = await api.get(`/documents?${params.toString()}`);
    return response.data;
  },

  // Get single document
  getDocumentById: async (id) => {
    const response = await api.get(`/documents/${id}`);
    return response.data;
  },

  // Upload document
  uploadDocument: async (caseId, formData) => {
    return api.post('/documents/upload', formData, {
      params: { case_id: caseId },
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  // Download document
  downloadDocument: async (id) => {
    const response = await api.get(`/documents/${id}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Delete document
  deleteDocument: async (id) => {
    const response = await api.delete(`/documents/${id}`);
    return response.data;
  },

  // Search documents
  searchDocuments: async (query, skip = 0, limit = 10) => {
    const response = await api.get(`/documents/search?query=${query}&skip=${skip}&limit=${limit}`);
    return response.data;
  },
};
