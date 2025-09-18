const express = require('express');
const path = require('path');
const fs = require('fs');
const yaml = require('yaml');
const bodyParser = require('body-parser');

const app = express();
const PORT = process.env.PORT || 3002;

app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, '..', 'public')));

app.get('/health', (req, res) => res.json({ok: true}));

// Demo endpoint: approve a run by adding push_authorized_by to runs/<id>/meta.yaml
function generateRunId({ project = 'railweb', kind = 'ops' } = {}) {
  const d = new Date();
  const y = d.getUTCFullYear();
  const m = String(d.getUTCMonth() + 1).padStart(2, '0');
  const day = String(d.getUTCDate()).padStart(2, '0');
  const date = `${y}${m}${day}`;
  const suffix = Math.random().toString(16).slice(2, 8); // 6 hex chars
  return `${project}-${date}-${kind}-${suffix}`;
}

app.post('/api/approve', async (req, res) => {
  let { runId, approver, note, title, confidence, rounding_rule, kind } = req.body || {};
  try {
    // generate runId if missing
    if (!runId) {
      runId = generateRunId({ kind: kind || 'ops' });
    }

    const metaPath = path.join(process.cwd(), 'runs', runId, 'meta.yaml');

    // prepare minimal meta
    let data = {};
    if (fs.existsSync(metaPath)) {
      const text = fs.readFileSync(metaPath, 'utf8');
      data = yaml.parse(text) || {};
    }

    // ensure provenance-required fields are present
    data.source = data.source || {};
    data.source.id = String(runId);
    data.source.title = data.source.title || (title || `Run ${runId}`);
    data.source.date = data.source.date || new Date().toISOString().split('T')[0];
    data.source.url = data.source.url || '';
    data.confidence = data.confidence || (confidence || 'medium');
    data.rounding_rule = data.rounding_rule || (rounding_rule || 'none');
    // optional created metadata
    data.created_by = data.created_by || approver || 'unknown';
    data.created_at = data.created_at || new Date().toISOString();

    if (approver) {
      data.push_authorized_by = approver;
      if (note) data.push_authorized_note = note;
    }

    const out = yaml.stringify(data);
    fs.mkdirSync(path.dirname(metaPath), { recursive: true });
    fs.writeFileSync(metaPath, out, 'utf8');
    return res.json({ ok: true, runId, metaPath });
  } catch (err) {
    console.error('approve error', err);
    return res.status(500).json({ error: String(err) });
  }
});

app.listen(PORT, () => {
  console.log(`Approval UI running on http://localhost:${PORT}`);
});
