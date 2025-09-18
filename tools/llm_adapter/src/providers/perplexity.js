const axios = require('axios');

class PerplexityProvider {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.base = process.env.PERPLEXITY_API_BASE || 'https://api.perplexity.ai';
  }

  async call(prompt, opts={}) {
    if (!this.apiKey) {
      throw new Error('PERPLEXITY_API_KEY not set');
    }
    // NOTE: Perplexity's public API surface may differ; this is a placeholder/prototype.
    // If you provide exact API docs/keys we can wire this up properly.
    const resp = await axios.post(`${this.base}/v1/answer`, { query: prompt }, { headers: { Authorization: `Bearer ${this.apiKey}` } });
    const text = resp.data && resp.data.answer ? resp.data.answer : `Perplexity response placeholder`;
    const citations = resp.data && resp.data.sources ? resp.data.sources : [];
    return { text, provenance_suggestions: { source_id: opts.run_id || 'perplexity-run', source_title: 'Perplexity summary', source_url: '', confidence: 0.85 }, citations };
  }
}

module.exports = PerplexityProvider;
