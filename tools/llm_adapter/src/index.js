require('dotenv').config();
const express = require('express');
const bodyParser = require('body-parser');
const OpenAIProvider = require('./providers/openai');
const PerplexityProvider = require('./providers/perplexity');

const app = express();
app.use(bodyParser.json());

const PROVIDER = process.env.DEFAULT_PROVIDER || 'mock';

function getProvider(name) {
  switch ((name||PROVIDER).toLowerCase()) {
    case 'openai':
      return new OpenAIProvider(process.env.OPENAI_API_KEY);
    case 'perplexity':
      return new PerplexityProvider(process.env.PERPLEXITY_API_KEY);
    default:
      return {
        async call(prompt, opts) {
          return {
            text: `MOCK RESPONSE for intent=${opts.intent||'none'}`,
            provenance_suggestions: {
              source_id: 'mock-1',
              source_title: 'Mock run',
              source_url: 'runs/mock/meta.yaml',
              confidence: 0.5
            },
            citations: []
          };
        }
      };
  }
}

app.post('/api/llm/summarizeRun', async (req, res) => {
  const { run_id, artifacts, intent } = req.body || {};
  const providerName = req.query.provider || process.env.DEFAULT_PROVIDER;
  const provider = getProvider(providerName);
  try {
    const prompt = `Summarize run ${run_id} with ${artifacts ? artifacts.length : 0} artifacts. Intent: ${intent}`;
    const out = await provider.call(prompt, { intent, run_id });
    res.json({ ok: true, provider: providerName, ...out });
  } catch (err) {
    console.error(err);
    res.status(500).json({ ok: false, error: String(err) });
  }
});

app.post('/api/llm/explainChange', async (req, res) => {
  const { run_id, diff_text, goal } = req.body || {};
  const providerName = req.query.provider || process.env.DEFAULT_PROVIDER;
  const provider = getProvider(providerName);
  try {
    const prompt = `Explain change for run ${run_id}. Goal: ${goal}\nDiff:\n${diff_text}`;
    const out = await provider.call(prompt, { goal, run_id });
    res.json({ ok: true, provider: providerName, ...out });
  } catch (err) {
    console.error(err);
    res.status(500).json({ ok: false, error: String(err) });
  }
});

const port = process.env.PORT || 3001;
app.listen(port, () => console.log(`LLM adapter listening on ${port} (provider=${PROVIDER})`));
