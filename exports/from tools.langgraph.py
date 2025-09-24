from tools.langgraph.pm_orchestrator import PMOrchestrator
from typing import Dict, Any
import json
import os

class SDLCEventProcessor:
    """Process events and route to PM Orchestrator"""
    
    def __init__(self, notion_token: str):
        self.pm_orchestrator = PMOrchestrator(notion_token)
    
    def handle_task_created(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle new task creation event"""
        
        return self.pm_orchestrator.process_event("task_created", {
            "task": task_data,
            "event_id": f"task_created_{task_data.get('id', 'unknown')}"
        })
    
    def handle_pr_merged(self, pr_event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle PR merged webhook"""
        
        return self.pm_orchestrator.process_event("pr_merged", {
            "pr_data": pr_event,
            "event_id": f"pr_merged_{pr_event.get('pull_request', {}).get('id', 'unknown')}"
        })
    
    def handle_task_updated(self, task_data: Dict[str, Any], changes: Dict[str, Any]) -> Dict[str, Any]:
        """Handle task update event"""
        
        return self.pm_orchestrator.process_event("task_updated", {
            "task": task_data,
            "changes": changes,
            "event_id": f"task_updated_{task_data.get('id', 'unknown')}"
        })

# CLI interface for testing
if __name__ == "__main__":
    import sys
    
    notion_token = os.getenv('NOTION_TOKEN')
    if not notion_token:
        print("Set NOTION_TOKEN environment variable")
        sys.exit(1)
    
    processor = SDLCEventProcessor(notion_token)
    
    # Test with sample task created event
    sample_task = {
        "id": "test_task_123",
        "Task Name": "Implement scale conversion calculator",
        "Status": "Todo",
        "Framework link": "your_framework_node_id_here",
        "Source link": "https://github.com/user/repo/issues/123",
        "Notes": ""
    }
    
    result = processor.handle_task_created(sample_task)
    print(json.dumps(result, indent=2))