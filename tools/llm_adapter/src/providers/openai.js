const axios = require('axios');

class OpenAIProvider {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.base = 'https://api.openai.com/v1';
  }

  async call(prompt, opts={}) {
    if (!this.apiKey) {
      throw new Error('OPENAI_API_KEY not set');
    }
    // Minimal completion call - keep simple for prototype
    const payload = {
      model: process.env.OPENAI_MODEL || 'gpt-4o-mini',
      messages: [{ role: 'system', content: 'You are a helpful assistant.' }, { role: 'user', content: prompt }],
      max_tokens: 800
    };
    const resp = await axios.post(`${this.base}/chat/completions`, payload, {
      headers: { Authorization: `Bearer ${this.apiKey}` }
    });
    const text = resp.data.choices && resp.data.choices[0].message.content;
    return { text, provenance_suggestions: { source_id: opts.run_id || 'openai-run', source_title: 'OpenAI summary', source_url: '', confidence: 0.8 }, citations: [] };
  }
}

module.exports = OpenAIProvider;
