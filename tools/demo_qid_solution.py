#!/usr/bin/env python3
"""Demo script showing how the QID discovery system handles entities without QIDs."""
import json
import tempfile
from pathlib import Path
import sys

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'tools'))

from qid_discovery import (
    discover_or_create_identifier,
    smart_entity_extraction,
    enhance_artifact_with_smart_discovery
)
from enrich_adapter import enrich_with_wikidata_and_perplexity

def demo_mixed_identifiers():
    """Demo: handling both real and fictional entities."""
    print("🔍 QID Discovery Demo: Handling Mixed Real/Fictional Entities")
    print("=" * 60)
    
    # Test entities: mix of real and fictional
    test_entities = [
        ("Baltimore and Ohio Railroad", "organization"),  # Real - should find QID
        ("Fictional Valley Railway", "organization"),     # Fictional - gets synthetic ID
        ("John Smith", "person"),                        # Common name - might find QID or create synthetic
        ("Imaginary Junction Station", "facility"),      # Fictional - gets synthetic ID
    ]
    
    results = []
    for entity_name, entity_type in test_entities:
        print(f"\n🧩 Processing: {entity_name} ({entity_type})")
        
        # Try discovery first, then synthetic
        identifier, is_synthetic = discover_or_create_identifier(
            entity_name, entity_type, attempt_discovery=False  # Skip network calls for demo
        )
        
        results.append({
            "name": entity_name,
            "type": entity_type,
            "identifier": identifier,
            "is_synthetic": is_synthetic
        })
        
        if is_synthetic:
            print(f"   ⚡ Created synthetic ID: {identifier}")
        else:
            print(f"   ✓ Found QID: {identifier}")
    
    return results


def demo_artifact_enhancement():
    """Demo: enhancing an artifact with automatic entity discovery."""
    print("\n\n📄 Artifact Enhancement Demo")
    print("=" * 40)
    
    # Create a sample artifact with mixed entities
    artifact_content = '''---
title: "Railroad Operations in Fictional Valley"
type: "requirement"
description: "Testing mixed real and fictional entities"
provenance:
  source: "human"
  model: "demo"
  model_version: "1.0"
  prompt_id: "demo"
  run_id: "demo123"
  timestamp: "2024-09-20T12:00:00Z"
---

The Baltimore and Ohio Railroad operated freight services between
Penn Station and the fictional Imaginary Junction Station.
John Smith was the stationmaster, working closely with 
the Fictional Valley Railway Company.

Historical note: The B&O was a real railroad, but Imaginary Junction
and Fictional Valley Railway are made-up for this demo.
'''
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(artifact_content)
        temp_path = f.name
    
    try:
        print(f"📝 Original artifact: {temp_path}")
        
        # Extract entities from the text
        entities = smart_entity_extraction(artifact_content)
        print(f"\n🔍 Extracted {len(entities)} entities:")
        for entity in entities:
            print(f"   • {entity['name']} ({entity['type']})")
        
        # Enhance the artifact
        enhanced_path = enhance_artifact_with_smart_discovery(temp_path, auto_discover=True)
        
        if enhanced_path != temp_path:
            print(f"✨ Enhanced artifact: {enhanced_path}")
            
            # Show the enhanced front-matter
            enhanced_content = Path(enhanced_path).read_text()
            front_matter_end = enhanced_content.find('---', 4) + 3
            front_matter = enhanced_content[:front_matter_end]
            print(f"\n📋 Enhanced front-matter:\n{front_matter}")
        else:
            print("📋 No enhancements needed")
            
    finally:
        # Cleanup
        Path(temp_path).unlink(missing_ok=True)
        if enhanced_path != temp_path:
            Path(enhanced_path).unlink(missing_ok=True)


def demo_enrichment_with_mixed_ids():
    """Demo: enrichment process with both QIDs and synthetic IDs."""
    print("\n\n🧠 Mixed Identifier Enrichment Demo")
    print("=" * 45)
    
    # Create artifact with pre-assigned mixed identifiers
    artifact_content = '''---
title: "Mixed Identifier Test"
type: "requirement"
wikidata_qids: ["Q1234", "RW_DEMO1234"]
entity_metadata:
  RW_DEMO1234:
    name: "Fictional Valley Railway"
    type: "organization"
    description: "A fictional railway company for testing"
provenance:
  source: "human"
  model: "demo"
  model_version: "1.0"
  prompt_id: "demo"
  run_id: "demo123"
  timestamp: "2024-09-20T12:00:00Z"
---

This artifact references both a real entity (Q1234) and a fictional one (RW_DEMO1234).
'''
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(artifact_content)
        temp_path = f.name
    
    try:
        print(f"📝 Processing artifact with mixed identifiers...")
        
        # Enrich the artifact
        sidecar_path = enrich_with_wikidata_and_perplexity(temp_path)
        
        # Load and display the enriched data
        sidecar_data = json.loads(Path(sidecar_path).read_text())
        
        print(f"💎 Enriched sidecar: {sidecar_path}")
        print("\n📊 Enrichment Summary:")
        
        if "enrichment_data" in sidecar_data:
            for identifier, enrichment in sidecar_data["enrichment_data"].items():
                is_synthetic = enrichment.get("is_synthetic", False)
                label = enrichment.get("label", "Unknown")
                
                if is_synthetic:
                    print(f"   ⚡ {identifier}: {label} (synthetic entity)")
                else:
                    print(f"   ✓ {identifier}: {label} (real entity - stub)")
        
        print(f"\n📋 Full sidecar structure:")
        print(json.dumps(sidecar_data, indent=2)[:500] + "...")
        
    finally:
        # Cleanup
        Path(temp_path).unlink(missing_ok=True)
        Path(sidecar_path).unlink(missing_ok=True)


if __name__ == '__main__':
    print("🎯 Non-QID Entity Handling Solution Demo")
    print("This demonstrates how Chrystallum handles entities that don't have Wikidata QIDs")
    print()
    
    # Run all demos
    demo_mixed_identifiers()
    demo_artifact_enhancement()
    demo_enrichment_with_mixed_ids()
    
    print("\n\n✅ Demo Complete!")
    print("\nKey Benefits:")
    print("  • Real entities get discovered QIDs when possible")
    print("  • Fictional entities get consistent synthetic IDs")
    print("  • Mixed real/fictional content works seamlessly")
    print("  • Knowledge graph can handle both types")
    print("  • No data loss - everything gets an identifier")