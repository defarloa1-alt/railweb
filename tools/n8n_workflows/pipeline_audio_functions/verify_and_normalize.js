// Input: webhook body. Output: {run_id, workflow_name, status, duration_ms, top_logs, highlights}
const crypto = require('crypto');
const input = items[0].json;
const headers = (items[0].jsonHeaders) ? items[0].jsonHeaders : {};
const secret = process.env.WEBHOOK_SECRET;

if (secret && headers['x-webhook-signature']) {
  const sig = headers['x-webhook-signature'];
  const payload = JSON.stringify(input);
  const h = 'sha256=' + crypto.createHmac('sha256', secret).update(payload).digest('hex');
  if (sig !== h) {
    throw new Error('Invalid webhook signature');
  }
}

// Normalize fields, tolerant to different callers
const run_id = input.run_id || input.executionId || (new Date()).toISOString();
const workflow_name = input.workflowName || input.workflow || input.name || 'pipeline-workflow';
const status = input.status || 'completed';
const duration_ms = input.duration_ms || input.duration || 0;
const highlights = input.highlights || input.highlights_excerpt || [];
// top_logs: optional array of {level, message}
const top_logs = input.top_logs || input.logs || [];

return [{ json: { run_id, workflow_name, status, duration_ms, highlights, top_logs, fetched_at: new Date().toISOString() } }];
