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
app.post('/api/approve', async (req, res) => {
  const { runId, approver, note } = req.body || {};
  if (!runId || !approver) {
    return res.status(400).json({ error: 'runId and approver are required' });
  }
  const metaPath = path.join(process.cwd(), 'runs', runId, 'meta.yaml');
  try {
    let data = {};
    if (fs.existsSync(metaPath)) {
      const text = fs.readFileSync(metaPath, 'utf8');
      data = yaml.parse(text) || {};
    }
    data.push_authorized_by = approver;
    if (note) data.push_authorized_note = note;
    const out = yaml.stringify(data);
    fs.mkdirSync(path.dirname(metaPath), { recursive: true });
    fs.writeFileSync(metaPath, out, 'utf8');
    return res.json({ ok: true, metaPath });
  } catch (err) {
    console.error('approve error', err);
    return res.status(500).json({ error: String(err) });
  }
});

app.listen(PORT, () => {
  console.log(`Approval UI running on http://localhost:${PORT}`);
});
