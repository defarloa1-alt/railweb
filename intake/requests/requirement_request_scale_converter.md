---
uid: b4a616ab-8e52-4d35-88b6-27b906e3e9b6
type: block
block_type: requirement_request
system: railweb
author: AD
block_name: Requirements for Scale Converter
in_port: User
out_port: Requirements Manager
priority: high
impact: foundational
source: obsidian
source_path: "user vault / Requirements for Scale Converter"
date: 2025-09-17
---

# Requirements: Navigator tree (Scale Converter)

## Use case: Navigator tree of typical model-railroading objects

## Summary

As a user I want a tree explorer (navigator) of typical objects used in model railroading so I can find objects and see real-world and scale dimensions filtered by scale and unit system.

## Primary flow (happy path)

1. The user opens the navigator UI.
2. The navigator displays the top-level tree.
   - The top-level tree nodes are derived from curated requirements that enumerate typical object categories found in model railroad scenery (examples: vehicles → cars → tires, structures → windows/doors/roofing, vegetation → trees/bushes, infrastructure → roads → rural roads → two-lane with shoulders).
   - Requirement: extrapolate high-level categories based on topologies common in model railroading. The depth of the tree for any subject should not exceed 8 levels.
3. The user selects a node.
4. The system drills down into that node and displays its child (edge) nodes.
5. The user navigates until the desired object node is reached.
6. For a selected object, the system displays filters and results:
   - Scale filter (defaults to the user's saved preference if available).
   - Measurement type filter: imperial, metric, or all (e.g., mm, inches, ft).
   - Based on the filters, the system displays a table with:
     - Object name
     - Real-world dimensions (width, length, height, ...)
     - Dimensions converted to the selected scale

## Non-goals / constraints

- The depth of the tree must not exceed 8.
- The system must present sources for dimension values (citation + version/date) alongside any published spec values.
- UI must default to local-only safe behaviors for any live-control features (per `intake/assumptions.yaml` safety constraints).

## Acceptance criteria

- Navigator displays a curated top-level tree derived from requirements and domain examples.
- Selecting an object displays a table with real-world dimensions and scale conversions.
- Filters for scale and measurement type are present and functional.
- Each numeric/spec value is accompanied by a source citation and version/date.

## Implementation notes / suggestions

- Build a content taxonomy first (CSV or YAML) listing categories and example objects to seed the navigator tree.
- Provide a converter utility that follows the project's rounding rules and includes test vectors.
- Store object dimension data with provenance (source, url, version/date) in a structured data file under `data/objects/`.

## Provenance

- Original draft: Obsidian note (author: AD), converted to intake request on 2025-09-17.
