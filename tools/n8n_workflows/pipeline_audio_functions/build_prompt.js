const d = items[0].json;
const maxSegments = 3;
const len = d.highlights && d.highlights.length ? d.highlights.length : 0;
const chosen = (d.highlights && d.highlights.slice) ? d.highlights.slice(0, maxSegments) : [];
const shortList = chosen.map((h,i)=>`(${i+1}) ${h.title || h.source || 'untitled'} - ${h.excerpt || h.text || ''}`.replace(/\n/g,' '));
const prompt = `You are a friendly podcast host. Given the pipeline execution summary and up to ${maxSegments} highlights, write a conversational 2-4 minute host script with: an intro (10s), ${Math.min(maxSegments,3)} short segments that summarize each highlight (30-50s each) with a 1-sentence takeaway, and a 10s outro. Keep language concise and avoid hallucination. Include in parentheses the source (Title — Author) after each quoted excerpt.\n\nPipeline summary:\n- workflow: ${d.workflow_name}\n- status: ${d.status}\n- duration_ms: ${d.duration_ms}\n\nHighlights:\n${shortList.join('\n')}\n\nRespond with JSON: {"script": "<the host script>", "show_notes": "<short markdown show notes>" }`;
return [{ json: { prompt, run_id: d.run_id, workflow_name: d.workflow_name } }];
