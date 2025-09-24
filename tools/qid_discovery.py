#!/usr/bin/env python3
"""QID Discovery and Synthetic Identifier System.

This module handles entities that don't have Wikidata QIDs by:
1. Attempting intelligent QID discovery through search
2. Creating synthetic identifiers for truly novel entities
3. Providing fallback enrichment strategies
4. Managing the knowledge graph with mixed QID/synthetic entities
"""
import hashlib
import json
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from urllib.parse import quote

# Add chronograph-vault scripts to path for Wikidata search
VAULT_SCRIPTS = Path(__file__).resolve().parent / 'external' / 'chronograph-vault' / '_scripts'
sys.path.insert(0, str(VAULT_SCRIPTS))

try:
    import requests
except ImportError:
    requests = None


def generate_synthetic_qid(entity_name: str, entity_type: str = "unknown", namespace: str = "railweb") -> str:
    """Generate a synthetic QID for entities not in Wikidata.
    
    Args:
        entity_name: Human-readable name of the entity
        entity_type: Type hint (person, organization, concept, etc.)
        namespace: Project namespace for collision avoidance
        
    Returns:
        Synthetic QID in format RW_{hash} where RW = railweb namespace
    """
    # Normalize the input for consistent hashing
    normalized = f"{namespace}:{entity_type}:{entity_name.lower().strip()}"
    hash_value = hashlib.md5(normalized.encode('utf-8')).hexdigest()[:8]
    return f"RW_{hash_value.upper()}"


def search_wikidata_for_entity(entity_name: str, entity_type: str = None) -> Optional[str]:
    """Search Wikidata for potential QID matches.
    
    Args:
        entity_name: Name to search for
        entity_type: Optional type hint for better matching
        
    Returns:
        QID if found, None otherwise
    """
    if not requests:
        print("Warning: requests library not available, skipping Wikidata search", file=sys.stderr)
        return None
        
    try:
        # Use Wikidata search API
        search_url = "https://www.wikidata.org/w/api.php"
        params = {
            "action": "wbsearchentities",
            "format": "json",
            "language": "en",
            "type": "item",
            "search": entity_name,
            "limit": 5
        }
        
        response = requests.get(search_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if "search" in data and data["search"]:
            # Return the first match - could be made smarter with type matching
            first_result = data["search"][0]
            return first_result["id"]
            
    except Exception as e:
        print(f"Warning: Wikidata search failed for '{entity_name}': {e}", file=sys.stderr)
        
    return None


def discover_or_create_identifier(entity_name: str, entity_type: str = "unknown", 
                                 attempt_discovery: bool = True) -> Tuple[str, bool]:
    """Discover QID or create synthetic identifier for an entity.
    
    Args:
        entity_name: Name of the entity
        entity_type: Type hint for better discovery
        attempt_discovery: Whether to try Wikidata search first
        
    Returns:
        Tuple of (identifier, is_synthetic) where is_synthetic=True for synthetic IDs
    """
    if attempt_discovery:
        # First try to find it in Wikidata
        qid = search_wikidata_for_entity(entity_name, entity_type)
        if qid:
            print(f"✓ Discovered QID {qid} for '{entity_name}'")
            return qid, False
    
    # Create synthetic identifier
    synthetic_id = generate_synthetic_qid(entity_name, entity_type)
    print(f"⚡ Created synthetic ID {synthetic_id} for '{entity_name}' (type: {entity_type})")
    return synthetic_id, True


def enrich_synthetic_entity(synthetic_id: str, entity_name: str, entity_type: str = "unknown") -> Dict:
    """Provide fallback enrichment for synthetic entities.
    
    Args:
        synthetic_id: The synthetic identifier (e.g., RW_12345678)
        entity_name: Human-readable name
        entity_type: Entity type
        
    Returns:
        Enrichment data structure similar to Wikidata enrichment
    """
    return {
        "id": synthetic_id,
        "label": entity_name,
        "type": entity_type,
        "is_synthetic": True,
        "namespace": "railweb",
        "created_timestamp": time.time(),
        "description": f"Synthetic entity for {entity_name} (type: {entity_type})",
        "enrichment_status": "synthetic_fallback",
        "suggested_properties": {
            # Could be enhanced with AI-generated property suggestions
            "label": entity_name,
            "instance_of": entity_type,
            "described_by_source": "railweb_intake_system"
        }
    }


def smart_entity_extraction(text: str) -> List[Dict[str, str]]:
    """Extract potential entities from text for QID discovery.
    
    Args:
        text: Input text to analyze
        
    Returns:
        List of dicts with 'name' and 'type' keys
    """
    entities = []
    
    # Multiple extraction strategies
    
    # Strategy 1: Multi-word proper noun phrases (organizations, places)
    # Look for sequences like "Baltimore and Ohio Railroad"
    compound_pattern = r'\b[A-Z][a-z]+(?:\s+(?:and|&|of|the)\s+[A-Z][a-z]+)+(?:\s+[A-Z][a-z]+)*\b'
    compounds = re.findall(compound_pattern, text)
    
    for match in compounds:
        match = match.strip()
        entity_type = "organization"
        if any(word in match.lower() for word in ['railroad', 'railway', 'company', 'corp']):
            entity_type = "organization"
        elif any(word in match.lower() for word in ['station', 'depot', 'yard', 'bridge']):
            entity_type = "facility"
        
        entities.append({"name": match, "type": entity_type})
    
    # Strategy 2: Simple proper nouns (2-3 words max)
    simple_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}\b'
    simples = re.findall(simple_pattern, text)
    
    for match in simples:
        match = match.strip()
        
        # Skip if already captured by compound pattern
        if any(match in compound for compound in compounds):
            continue
            
        # Skip common words
        if match.lower() in ['The', 'This', 'That', 'When', 'Where', 'Why', 'How', 'What']:
            continue
        if len(match) < 3:
            continue
            
        # Type detection for simple patterns
        entity_type = "unknown"
        match_lower = match.lower()
        words = match.split()
        
        if any(word in match_lower for word in ['station', 'depot', 'yard', 'bridge']):
            entity_type = "facility"
        elif len(words) == 2 and all(len(word) > 2 for word in words):
            entity_type = "person"  # Two substantial words likely a person
        elif any(word in match_lower for word in ['company', 'corp', 'inc']):
            entity_type = "organization"
        
        entities.append({"name": match, "type": entity_type})
    
    # Remove duplicates and filter
    seen = set()
    unique_entities = []
    
    for entity in entities:
        # Normalize for deduplication
        key = entity["name"].lower().strip()
        if key not in seen and len(entity["name"]) > 2:
            seen.add(key)
            unique_entities.append(entity)
    
    return unique_entities


def process_mixed_identifiers(identifiers: List[str], entity_data: Dict[str, Dict] = None) -> Dict:
    """Process a mix of QIDs and synthetic identifiers for enrichment.
    
    Args:
        identifiers: List of QIDs and/or synthetic IDs
        entity_data: Optional mapping of identifier -> entity info
        
    Returns:
        Enrichment results for all identifiers
    """
    from enrich_adapter import enrich_with_wikidata
    
    results = {}
    
    for identifier in identifiers:
        if identifier.startswith('Q') and identifier[1:].isdigit():
            # Real Wikidata QID
            results[identifier] = enrich_with_wikidata(identifier)
        elif identifier.startswith('RW_'):
            # Synthetic railweb identifier
            entity_info = entity_data.get(identifier, {}) if entity_data else {}
            entity_name = entity_info.get('name', f'Entity-{identifier}')
            entity_type = entity_info.get('type', 'unknown')
            results[identifier] = enrich_synthetic_entity(identifier, entity_name, entity_type)
        else:
            # Unknown format - attempt discovery
            discovered_id, is_synthetic = discover_or_create_identifier(identifier)
            if is_synthetic:
                results[identifier] = enrich_synthetic_entity(discovered_id, identifier)
            else:
                results[identifier] = enrich_with_wikidata(discovered_id)
    
    return results


def enhance_artifact_with_smart_discovery(artifact_path: str, auto_discover: bool = True) -> str:
    """Enhance an artifact by discovering QIDs and creating synthetic IDs as needed.
    
    Args:
        artifact_path: Path to the artifact file
        auto_discover: Whether to automatically discover entities from text
        
    Returns:
        Path to enhanced artifact with discovered/synthetic identifiers
    """
    from artifact_to_jsonld import load_front_matter
    
    artifact = Path(artifact_path)
    if not artifact.exists():
        raise FileNotFoundError(f"Artifact not found: {artifact_path}")
    
    # Load current front-matter and body
    fm, body = load_front_matter(artifact)
    
    # Get existing QIDs
    existing_qids = fm.get("wikidata_qids", [])
    
    # Extract potential entities if auto-discovery is enabled
    discovered_entities = []
    if auto_discover:
        # Extract from title, description, and body
        search_text = f"{fm.get('title', '')} {fm.get('description', '')} {body}"
        discovered_entities = smart_entity_extraction(search_text)
    
    # Discover or create identifiers for new entities
    all_identifiers = existing_qids.copy()
    entity_metadata = {}
    
    for entity in discovered_entities:
        identifier, is_synthetic = discover_or_create_identifier(
            entity["name"], entity["type"], attempt_discovery=True
        )
        
        if identifier not in all_identifiers:
            all_identifiers.append(identifier)
            entity_metadata[identifier] = entity
    
    # Update front-matter with enhanced identifiers
    if all_identifiers != existing_qids:
        fm["wikidata_qids"] = all_identifiers
        
        # Add metadata for synthetic entities
        if entity_metadata:
            fm["entity_metadata"] = entity_metadata
        
        # Write enhanced artifact
        enhanced_path = artifact.with_stem(f"{artifact.stem}_enhanced")
        
        # Reconstruct file with updated front-matter
        yaml_content = "---\n"
        import yaml
        yaml_content += yaml.dump(fm, default_flow_style=False, allow_unicode=True)
        yaml_content += "---\n\n"
        yaml_content += body
        
        enhanced_path.write_text(yaml_content, encoding='utf-8')
        print(f"Enhanced artifact written to {enhanced_path}")
        return str(enhanced_path)
    
    print(f"No new entities discovered for {artifact_path}")
    return artifact_path


def main():
    """Command-line interface for QID discovery and synthetic ID creation."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python qid_discovery.py discover 'Entity Name' [type]")
        print("  python qid_discovery.py synthetic 'Entity Name' [type]")
        print("  python qid_discovery.py enhance path/to/artifact.md")
        print("  python qid_discovery.py extract 'Some text with entities'")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "discover":
        entity_name = sys.argv[2]
        entity_type = sys.argv[3] if len(sys.argv) > 3 else "unknown"
        identifier, is_synthetic = discover_or_create_identifier(entity_name, entity_type)
        print(f"Result: {identifier} (synthetic: {is_synthetic})")
        
    elif command == "synthetic":
        entity_name = sys.argv[2]
        entity_type = sys.argv[3] if len(sys.argv) > 3 else "unknown"
        synthetic_id = generate_synthetic_qid(entity_name, entity_type)
        print(f"Synthetic ID: {synthetic_id}")
        
    elif command == "enhance":
        artifact_path = sys.argv[2]
        enhanced_path = enhance_artifact_with_smart_discovery(artifact_path)
        print(f"Enhanced: {enhanced_path}")
        
    elif command == "extract":
        text = sys.argv[2]
        entities = smart_entity_extraction(text)
        print("Extracted entities:")
        for entity in entities:
            print(f"  {entity['name']} (type: {entity['type']})")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()