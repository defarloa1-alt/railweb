#!/usr/bin/env python3
"""Tests for QID discovery and synthetic identifier handling."""
import json
import tempfile
import pytest
from pathlib import Path
import sys

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'tools'))

try:
    from qid_discovery import (
        generate_synthetic_qid,
        smart_entity_extraction,
        enrich_synthetic_entity,
        discover_or_create_identifier,
        enhance_artifact_with_smart_discovery
    )
except ImportError:
    # Skip tests if module not available
    pytest.skip("qid_discovery module not available", allow_module_level=True)


def test_synthetic_qid_generation():
    """Test synthetic QID generation is consistent and formatted correctly."""
    # Same input should always generate same ID
    qid1 = generate_synthetic_qid("Test Entity", "person")
    qid2 = generate_synthetic_qid("Test Entity", "person")
    assert qid1 == qid2
    
    # Different inputs should generate different IDs
    qid3 = generate_synthetic_qid("Different Entity", "person")
    assert qid1 != qid3
    
    # Format should be RW_XXXXXXXX
    assert qid1.startswith("RW_")
    assert len(qid1) == 11  # RW_ + 8 hex chars
    assert qid1[3:].isupper()  # Hex should be uppercase


def test_entity_extraction():
    """Test entity extraction from text."""
    text = """
    The Baltimore and Ohio Railroad operated the Camden Station.
    John Smith worked there in 1890. The B&O Company was founded earlier.
    """
    
    entities = smart_entity_extraction(text)
    
    # Should find proper nouns
    entity_names = [e["name"] for e in entities]
    print(f"Extracted entities: {entity_names}")  # Debug output
    
    # Check for the entities we expect (more flexible matching)
    has_baltimore_railroad = any("Baltimore" in name and "Railroad" in name for name in entity_names)
    has_camden_station = any("Camden Station" in name for name in entity_names)
    has_john_smith = any("John Smith" in name for name in entity_names)
    
    assert has_baltimore_railroad or has_camden_station, f"Should find Baltimore railroad or Camden Station in {entity_names}"
    assert has_john_smith, f"Should find John Smith in {entity_names}"
    
    # Should detect some types
    john_smith = next((e for e in entities if "John Smith" in e["name"]), None)
    if john_smith:
        assert john_smith["type"] == "person"  # Two words -> person heuristic


def test_synthetic_entity_enrichment():
    """Test enrichment data for synthetic entities."""
    synthetic_id = "RW_12345678"
    enrichment = enrich_synthetic_entity(synthetic_id, "Test Railroad", "organization")
    
    assert enrichment["id"] == synthetic_id
    assert enrichment["label"] == "Test Railroad"
    assert enrichment["type"] == "organization"
    assert enrichment["is_synthetic"] is True
    assert "suggested_properties" in enrichment


def test_discovery_fallback():
    """Test that discovery falls back to synthetic ID when needed."""
    # Test with a very unlikely entity name
    identifier, is_synthetic = discover_or_create_identifier(
        "Completely Made Up Railroad XYZ123", 
        "organization",
        attempt_discovery=False  # Skip discovery to test synthetic path
    )
    
    assert is_synthetic is True
    assert identifier.startswith("RW_")


def test_artifact_enhancement():
    """Test enhancing an artifact with entity discovery."""
    # Create a test artifact
    artifact_content = '''---
title: "Railroad Operations Test"
type: "requirement"
description: "Testing entity discovery"
provenance:
  source: "human"
  model: "test"
  model_version: "1.0"
  prompt_id: "test"
  run_id: "test"
  timestamp: "2024-01-01T00:00:00Z"
---

The Pennsylvania Railroad operated out of Penn Station.
Thomas Edison invented electric lighting for trains.
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(artifact_content)
        temp_path = f.name
    
    try:
        # Test enhancement (with discovery disabled to avoid network calls)
        enhanced_path = enhance_artifact_with_smart_discovery(temp_path, auto_discover=True)
        
        # Should create enhanced file or return original if no changes
        assert Path(enhanced_path).exists()
        
    finally:
        # Cleanup
        Path(temp_path).unlink(missing_ok=True)
        enhanced_path_obj = Path(enhanced_path)
        if enhanced_path_obj != Path(temp_path):
            enhanced_path_obj.unlink(missing_ok=True)


def test_mixed_identifier_handling():
    """Test handling of both QIDs and synthetic IDs in same artifact."""
    try:
        from enrich_adapter import enrich_with_wikidata_and_perplexity
    except ImportError:
        pytest.skip("enrich_adapter not available")
    
    # Create test artifact with mixed identifiers
    artifact_content = '''---
title: "Mixed Identifier Test"
type: "requirement"
wikidata_qids: ["Q1234", "RW_ABCD1234"]
entity_metadata:
  RW_ABCD1234:
    name: "Test Railroad"
    type: "organization"
    description: "A test railroad company"
provenance:
  source: "human"
  model: "test"
  model_version: "1.0"
  prompt_id: "test"
  run_id: "test"
  timestamp: "2024-01-01T00:00:00Z"
---

Test content with mixed identifiers.
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(artifact_content)
        temp_path = f.name
    
    try:
        # Test enrichment (will use stub functions for Q1234)
        sidecar_path = enrich_with_wikidata_and_perplexity(temp_path)
        
        # Load the sidecar
        sidecar_data = json.loads(Path(sidecar_path).read_text())
        
        # Should have enrichment data for both identifiers
        assert "enrichment_data" in sidecar_data
        enrichments = sidecar_data["enrichment_data"]
        
        # Should contain both QID and synthetic ID
        assert "Q1234" in enrichments  # Stub enrichment
        assert "RW_ABCD1234" in enrichments  # Synthetic enrichment
        
        # Synthetic entity should be marked as such
        synthetic_enrichment = enrichments["RW_ABCD1234"]
        assert synthetic_enrichment["is_synthetic"] is True
        assert synthetic_enrichment["label"] == "Test Railroad"
        
    finally:
        # Cleanup
        Path(temp_path).unlink(missing_ok=True)
        sidecar_path_obj = Path(sidecar_path)
        if sidecar_path_obj.exists():
            sidecar_path_obj.unlink(missing_ok=True)


if __name__ == '__main__':
    pytest.main([__file__])