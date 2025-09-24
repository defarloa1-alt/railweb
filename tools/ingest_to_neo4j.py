#!/usr/bin/env python3
"""Simple ingestion helper: reads JSON-LD and upserts nodes into Neo4j.

Usage: tools/ingest_to_neo4j.py artifact.jsonld
"""
import sys
import json
from pathlib import Path

from neo4j import GraphDatabase

NEO_URL = 'bolt://localhost:7687'
NEO_USER = 'neo4j'
NEO_PASSWORD = 'test'


def upsert_node(tx, node):
    q = '''
    MERGE (n:Artifact {id: $id})
    SET n.title = $title, n.description = $description, n.tags = $tags, n.provenance = $prov, n.type = $type
    RETURN n
    '''
    tx.run(q, id=node.get('@id'), title=node.get('title'), description=node.get('description'), tags=node.get('tags'), prov=node.get('provenance'), type=node.get('@type'))


def main():
    if len(sys.argv) < 2:
        print('Usage: ingest_to_neo4j.py artifact.jsonld', file=sys.stderr)
        sys.exit(2)
    p = Path(sys.argv[1])
    node = json.loads(p.read_text(encoding='utf8'))
    driver = GraphDatabase.driver(NEO_URL, auth=(NEO_USER, NEO_PASSWORD))
    with driver.session() as s:
        s.write_transaction(upsert_node, node)
    print('Ingested', node.get('@id'))


if __name__ == '__main__':
    main()
