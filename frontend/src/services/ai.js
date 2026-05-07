import api from './api';

// AI Assistant service
export const aiAssistantService = {
  // Ask a structured question
  askAssistant: async (question) => {
    const response = await api.post('/assistant/ask', { question });
    return response.data;
  },

  // Query AI for insights
  queryInsights: async (question, conversationHistory = []) => {
    const response = await api.post('/ai/query', {
      question,
      conversation_history: conversationHistory,
    });
    return response.data;
  },

  // Check AI service health
  checkHealth: async () => {
    const response = await api.get('/assistant/health');
    return response.data;
  },

  // Check AI query service health
  checkQueryHealth: async () => {
    const response = await api.get('/ai/health');
    return response.data;
  },
};
