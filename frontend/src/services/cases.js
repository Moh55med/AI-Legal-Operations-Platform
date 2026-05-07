import api from './api';

// Case management service
export const casesService = {
  // Get all cases with optional filters
  getAllCases: async (skip = 0, limit = 10, filters = {}) => {
    const params = new URLSearchParams({ skip, limit });
    
    if (filters.status) params.append('status', filters.status);
    if (filters.title) params.append('title', filters.title);
    if (filters.client_name) params.append('client_name', filters.client_name);
    if (filters.case_reference_number) params.append('case_reference_number', filters.case_reference_number);
    if (filters.assigned_user_id) params.append('assigned_user_id', filters.assigned_user_id);
    if (filters.date_from) params.append('date_from', filters.date_from);
    if (filters.date_to) params.append('date_to', filters.date_to);

    const response = await api.get(`/cases?${params.toString()}`);
    return response.data;
  },

  // Get single case
  getCaseById: async (id) => {
    const response = await api.get(`/cases/${id}`);
    return response.data;
  },

  // Create new case
  createCase: async (caseData) => {
    const response = await api.post('/cases', caseData);
    return response.data;
  },

  // Update case
  updateCase: async (id, caseData) => {
    const response = await api.put(`/cases/${id}`, caseData);
    return response.data;
  },

  // Close case
  closeCase: async (id) => {
    const response = await api.put(`/cases/${id}/close`, {});
    return response.data;
  },

  // Delete case
  deleteCase: async (id) => {
    const response = await api.delete(`/cases/${id}`);
    return response.data;
  },
};
