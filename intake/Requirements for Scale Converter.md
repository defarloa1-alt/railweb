---
uid: b4a616ab-8e52-4d35-88b6-27b906e3e9b6
type: block
block type: requirement_request
system: railweb
author: AD
block name: Requirements for Scale Converter
in_port: User
out_port: Requirements Manager
priority: high
impact: foundational
---
use case: as a user i want to have a tree explorer of typical objects used in model railroading.
	happy path:
		the user goes to navigator
		the navigator displays the top level tree
			the top level tree should be derived by requirements 
				examples: tire -> car -> vehicles, structures -> windows and doors , roofing, 
				**requirement is to extrapolate high level categories based on topologies common in model railroads, trees, bushes, roads --> rural roads --> two lane with shoulders. the requirements are to enumerate typical objects found in the scenary of model railroads. the depth of the tree for any subject should not exceed 8 deep**
		the user selects a node
		the system drill down into that node, displaying the edge nodes
		the user navigates until they reach the desired object
		the system responds with 
			a filter for the user to select scale (default to a user config)	
			a filter for measurement type 
				imperial, metric, all
					mm, inches, ft etc
			based on the filter the system displays in a table
				object name
				real-world dimensions width length height etc
				same dimensions in the selected scale
			user may copy the results
			end of use case
				
				