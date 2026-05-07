import api from './api';

// Deadline management service
export const deadlinesService = {
  // Get all deadlines with optional filters
  getAllDeadlines: async (skip = 0, limit = 10, filters = {}) => {
    const params = new URLSearchParams({ skip, limit });
    
    if (filters.case_id) params.append('case_id', filters.case_id);
    if (filters.status) params.append('status', filters.status);
    if (filters.due_date) params.append('due_date', filters.due_date);
    if (filters.due_date_from) params.append('due_date_from', filters.due_date_from);
    if (filters.due_date_to) params.append('due_date_to', filters.due_date_to);

    const response = await api.get(`/deadlines?${params.toString()}`);
    return response.data;
  },

  // Get pending deadlines
  getPendingDeadlines: async (skip = 0, limit = 10) => {
    const response = await api.get(`/deadlines/pending?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  // Get overdue deadlines
  getOverdueDeadlines: async (skip = 0, limit = 10) => {
    const response = await api.get(`/deadlines/overdue?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  // Get single deadline
  getDeadlineById: async (id) => {
    const response = await api.get(`/deadlines/${id}`);
    return response.data;
  },

  // Create new deadline
  createDeadline: async (deadlineData) => {
    const response = await api.post('/deadlines', deadlineData);
    return response.data;
  },

  // Update deadline
  updateDeadline: async (id, deadlineData) => {
    const response = await api.put(`/deadlines/${id}`, deadlineData);
    return response.data;
  },

  // Mark deadline as complete
  completeDeadline: async (id) => {
    const response = await api.put(`/deadlines/${id}/complete`, {});
    return response.data;
  },

  // Mark deadline as missed
  missDeadline: async (id) => {
    const response = await api.put(`/deadlines/${id}/miss`, {});
    return response.data;
  },

  // Delete deadline
  deleteDeadline: async (id) => {
    const response = await api.delete(`/deadlines/${id}`);
    return response.data;
  },
};
