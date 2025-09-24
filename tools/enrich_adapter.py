#!/usr/bin/env python3
"""Adapter for chronograph-vault enrichment tooling.

This module provides a simplified interface to the chronograph-vault
Wikidata enrichment functions for use in the railweb intake pipeline.
"""
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional

# Add chronograph-vault scripts to path
VAULT_SCRIPTS = Path(__file__).resolve().parent / 'external' / 'chronograph-vault' / '_scripts'
VAULT_ROOT = Path(__file__).resolve().parent / 'external' / 'chronograph-vault'
sys.path.insert(0, str(VAULT_SCRIPTS))
sys.path.insert(0, str(VAULT_ROOT))

try:
    from emit_from_wikidata_qid import fetch_label_birth_death, fetch_spouses_with_qualifiers, fetch_children_for_pair
    from repair_family_links import fetch_entity
    from generate_enriched_profile import fetch_claims, resolve_labels, generate_markdown, send_event_prompt_to_perplexity
except ImportError as e:
    print(f"Warning: Could not import chronograph-vault functions: {e}", file=sys.stderr)
    # Provide stub functions for testing
    def fetch_label_birth_death(qid: str):
        return {"label": f"STUB-{qid}", "birth": None, "death": None}
    def fetch_spouses_with_qualifiers(qid: str):
        return []
    def fetch_children_for_pair(pqid: str, sqid: str):
        return []
    def fetch_entity(qid: str):
        return {"id": qid, "labels": {"en": {"value": f"STUB-{qid}"}}}
    def fetch_claims(qid: str):
        return {}
    def resolve_labels(qids: List[str]):
        return {qid: {"label": f"STUB-{qid}", "wikidata": f"https://www.wikidata.org/wiki/{qid}"} for qid in qids}
    def generate_markdown(entity_id: str, claims: Dict, labels: Dict):
        return f"# STUB Profile for {entity_id}", f"STUB-{entity_id}"
    def send_event_prompt_to_perplexity(qid: str):
        return f"STUB: Historical events for {qid} (Perplexity API unavailable)"


def enrich_with_wikidata(qid: str) -> Dict:
    """Fetch enrichment data for a single Wikidata QID.
    
    Returns a dict with normalized properties suitable for JSON-LD.
    """
    try:
        # Fetch basic person data
        person_data = fetch_label_birth_death(qid)
        entity_data = fetch_entity(qid)
        
        # Normalize to our schema
        enrichment = {
            "qid": qid,
            "label": person_data.get("label", ""),
            "birth_date": person_data.get("birth", ""),
            "death_date": person_data.get("death", ""),
            "wikidata_url": f"https://www.wikidata.org/wiki/{qid}",
            "properties": {}
        }
        
        # Add raw entity properties for advanced use
        if "claims" in entity_data:
            enrichment["properties"] = entity_data["claims"]
            
        return enrichment
        
    except Exception as e:
        print(f"Error enriching QID {qid}: {e}", file=sys.stderr)
        return {
            "qid": qid,
            "error": str(e),
            "wikidata_url": f"https://www.wikidata.org/wiki/{qid}"
        }


def enrich_with_perplexity_profile(qid: str) -> Dict:
    """Generate a comprehensive enriched profile using both Wikidata and Perplexity.
    
    This function replicates the generate_enriched_profile.py workflow but returns
    structured data instead of writing markdown files.
    """
    try:
        print(f"🔍 Fetching claims for {qid}...")
        claims = fetch_claims(qid)
        if not claims:
            print(f"⚠️ No claims found for {qid}")
            return {"qid": qid, "error": "No claims found"}

        print("🔍 Resolving labels...")
        # Get all property IDs and linked QIDs
        property_ids = list(claims.keys())
        linked_qids = [qid]
        
        for statements in claims.values():
            for stmt in statements:
                snak = stmt.get("mainsnak", {})
                val = snak.get("datavalue", {}).get("value")
                if isinstance(val, dict) and "id" in val:
                    linked_qids.append(val["id"])
        
        all_ids = list(set(property_ids + linked_qids))
        labels = resolve_labels(all_ids)

        print("🧠 Generating Markdown...")
        markdown, label = generate_markdown(qid, claims, labels)
        
        print("📡 Sending historical event prompt to Perplexity...")
        event_markdown = send_event_prompt_to_perplexity(qid)
        
        # Combine both parts
        full_markdown = markdown + "\n\n---\n\n## 📜 Historical Events Extracted from Perplexity\n\n" + event_markdown
        
        return {
            "qid": qid,
            "label": label,
            "claims": claims,
            "labels": labels,
            "wikidata_markdown": markdown,
            "perplexity_events": event_markdown,
            "full_profile_markdown": full_markdown,
            "wikidata_url": f"https://www.wikidata.org/wiki/{qid}"
        }
        
    except Exception as e:
        print(f"Error generating enriched profile for {qid}: {e}", file=sys.stderr)
        return {
            "qid": qid,
            "error": str(e),
            "wikidata_url": f"https://www.wikidata.org/wiki/{qid}"
        }


def enrich_with_wikidata_and_perplexity(artifact_path: str, use_perplexity_profile: bool = False) -> str:
    """Main entrypoint: enrich an intake artifact with Wikidata + optional Perplexity data.
    
    Handles both real Wikidata QIDs and synthetic railweb identifiers (RW_xxxxxxxx).
    
    Args:
        artifact_path: Path to Markdown file with YAML front-matter
        use_perplexity_profile: If True, use enhanced Perplexity profile generation
        
    Returns:
        Path to enriched JSON-LD sidecar file
    """
    # Import here to avoid circular imports
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from artifact_to_jsonld import load_front_matter, to_jsonld
    from qid_discovery import process_mixed_identifiers
    
    artifact = Path(artifact_path)
    if not artifact.exists():
        raise FileNotFoundError(f"Artifact not found: {artifact_path}")
    
    # Load front-matter
    fm, body = load_front_matter(artifact)
    
    # Check for identifiers to enrich (QIDs or synthetic IDs)
    identifiers = fm.get("wikidata_qids", [])
    entity_metadata = fm.get("entity_metadata", {})
    
    if not identifiers:
        print(f"No identifiers found in {artifact_path}, skipping enrichment")
        # Still create JSON-LD without enrichment
        node = to_jsonld(fm, body)
    else:
        # Enrich with mixed identifiers (QIDs + synthetic)
        enrichments = {}
        for identifier in identifiers:
            if identifier.startswith('Q') and identifier[1:].isdigit():
                # Real Wikidata QID
                if use_perplexity_profile:
                    enrichments[identifier] = enrich_with_perplexity_profile(identifier)
                else:
                    enrichments[identifier] = enrich_with_wikidata(identifier)
            elif identifier.startswith('RW_'):
                # Synthetic railweb identifier
                from qid_discovery import enrich_synthetic_entity
                entity_info = entity_metadata.get(identifier, {})
                entity_name = entity_info.get('name', f'Entity-{identifier}')
                entity_type = entity_info.get('type', 'unknown')
                enrichments[identifier] = enrich_synthetic_entity(identifier, entity_name, entity_type)
            else:
                print(f"Warning: Unknown identifier format: {identifier}")
                # Try to discover or create
                from qid_discovery import discover_or_create_identifier, enrich_synthetic_entity
                discovered_id, is_synthetic = discover_or_create_identifier(identifier)
                if is_synthetic:
                    enrichments[identifier] = enrich_synthetic_entity(discovered_id, identifier)
                else:
                    enrichments[identifier] = enrich_with_wikidata(discovered_id)
        
        # Create enriched JSON-LD
        node = to_jsonld(fm, body)
        node["enrichment_data"] = enrichments
        
        # Add sameAs links for real QIDs only
        real_qids = [id for id in identifiers if id.startswith('Q') and id[1:].isdigit()]
        if len(real_qids) == 1:
            node["sameAs"] = f"https://www.wikidata.org/wiki/{real_qids[0]}"
        elif len(real_qids) > 1:
            node["sameAs"] = [f"https://www.wikidata.org/wiki/{qid}" for qid in real_qids]
        
        # Add synthetic entity metadata
        synthetic_ids = [id for id in identifiers if id.startswith('RW_')]
        if synthetic_ids:
            node["synthetic_entities"] = {id: entity_metadata.get(id, {}) for id in synthetic_ids}
    
    # Write enriched JSON-LD sidecar
    sidecar_path = artifact.with_suffix('.jsonld')
    
    # Ensure all values are JSON serializable
    def clean_for_json(obj):
        if hasattr(obj, 'isoformat'):  # datetime objects
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: clean_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [clean_for_json(v) for v in obj]
        else:
            return obj
    
    clean_node = clean_for_json(node)
    sidecar_path.write_text(json.dumps(clean_node, indent=2, default=str), encoding='utf8')
    
    print(f"Enriched artifact written to {sidecar_path}")
    return str(sidecar_path)


def main():
    if len(sys.argv) < 2:
        print("Usage: enrich_adapter.py path/to/artifact.md [--perplexity]")
        sys.exit(2)
    
    artifact_path = sys.argv[1]
    use_perplexity = "--perplexity" in sys.argv
    
    sidecar_path = enrich_with_wikidata_and_perplexity(artifact_path, use_perplexity_profile=use_perplexity)
    print(f"Enriched sidecar: {sidecar_path}")


if __name__ == '__main__':
    main()