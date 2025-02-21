import config from '../config/config';

export const templatesService = {
  async getTemplates() {
    const response = await fetch(`${config.apiBaseUrl}${config.endpoints.templates}`);
    if (!response.ok) {
      throw new Error('Failed to fetch templates');
    }
    return response.json();
  },

  async getTemplateChunks(templateId) {
    const response = await fetch(`${config.apiBaseUrl}${config.endpoints.templates}/${templateId}/chunks`);
    if (!response.ok) {
      throw new Error('Failed to fetch template chunks');
    }
    return response.json();
  }
}; 