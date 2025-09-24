from pathlib import Path
import json
import subprocess
import tempfile


def test_enrich_adapter_no_qids(tmp_path):
    """Test adapter with artifact that has no wikidata_qids."""
    artifact = tmp_path / 'test.md'
    artifact.write_text('''---
title: Test Artifact
type: requirement
provenance:
  source: human
  model: test
  model_version: 1.0
  prompt_id: test
  run_id: test-123
  timestamp: 2025-09-20T12:00:00Z
---

This is a test artifact without QIDs.''')
    
    res = subprocess.run(['python', 'tools/enrich_adapter.py', str(artifact)], 
                        capture_output=True, text=True)
    assert res.returncode == 0, f"Adapter failed: {res.stderr}"
    
    # Check sidecar was created
    sidecar = artifact.with_suffix('.jsonld')
    assert sidecar.exists()
    
    # Check JSON-LD structure
    data = json.loads(sidecar.read_text())
    assert data['title'] == 'Test Artifact'
    assert 'wikidata_enrichment' not in data


def test_enrich_adapter_with_qids(tmp_path):
    """Test adapter with artifact that has wikidata_qids (uses stub functions)."""
    artifact = tmp_path / 'test_qid.md'
    artifact.write_text('''---
title: Douglas Adams
type: note
wikidata_qids: ["Q42"]
provenance:
  source: human
  model: test
  model_version: 1.0
  prompt_id: test
  run_id: test-456
  timestamp: 2025-09-20T12:00:00Z
---

Author of The Hitchhiker's Guide to the Galaxy.''')
    
    res = subprocess.run(['python', 'tools/enrich_adapter.py', str(artifact)], 
                        capture_output=True, text=True)
    assert res.returncode == 0, f"Adapter failed: {res.stderr}"
    
    # Check sidecar was created
    sidecar = artifact.with_suffix('.jsonld')
    assert sidecar.exists()
    
    # Check JSON-LD structure
    data = json.loads(sidecar.read_text())
    assert data['title'] == 'Douglas Adams'
    assert 'wikidata_enrichment' in data
    assert 'Q42' in data['wikidata_enrichment']
    assert data['sameAs'] == 'https://www.wikidata.org/wiki/Q42'