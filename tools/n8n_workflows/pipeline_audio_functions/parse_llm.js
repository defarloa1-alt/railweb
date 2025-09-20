const body = items[0].json;
const text = body.choices && body.choices[0] && body.choices[0].message && body.choices[0].message.content ? body.choices[0].message.content : '';
// Try to parse JSON out of the content
let parsed = { script: '', show_notes: '' };
try { parsed = JSON.parse(text); } catch (e) {
  // attempt to find JSON substring
  const m = text.match(/\{[\s\S]*\}/);
  if (m) try { parsed = JSON.parse(m[0]); } catch(e2) { parsed.script = text; }
}
return [{ json: { script: parsed.script || text, show_notes: parsed.show_notes || '' } }];
