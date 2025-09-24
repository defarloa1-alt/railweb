import requests
from typing import Dict, Any, List, Optional

class NotionSDLCClient:
    # ...existing code...
    
    def get_task_by_id(self, task_id: str) -> Dict[str, Any]:
        """Fetch task data by ID for PM orchestrator"""
        
        url = f"https://api.notion.com/v1/pages/{task_id}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            page_data = response.json()
            # Convert Notion properties to flat dict
            return self._flatten_notion_properties(page_data)
        else:
            return {}
    
    def get_framework_node(self, framework_id: str) -> Dict[str, Any]:
        """Fetch Framework Library node data"""
        
        url = f"https://api.notion.com/v1/pages/{framework_id}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            page_data = response.json()
            return self._flatten_notion_properties(page_data)
        else:
            return {}
    
    def append_task_notes(self, task_id: str, notes: List[str], correlation_id: str, needs_review: bool = False) -> Dict[str, Any]:
        """Append notes to task (idempotent by correlation_id)"""
        
        # First, check if this correlation_id was already processed
        existing_notes = self._get_task_notes(task_id)
        if correlation_id in existing_notes:
            return {"status": "already_processed", "correlation_id": correlation_id}
        
        # Append new notes with correlation marker
        notes_text = f"\n\n**PM Orchestrator ({correlation_id})**:\n" + "\n".join(f"- {note}" for note in notes)
        
        # Update task properties
        url = f"https://api.notion.com/v1/pages/{task_id}"
        properties = {}
        
        # Add needs-review tag if required
        if needs_review:
            properties["Tags"] = {"multi_select": [{"name": "needs-review"}]}
        
        # Append to Notes property (this is tricky in Notion API - may need to read + write)
        current_notes = existing_notes
        updated_notes = current_notes + notes_text
        
        properties["Notes"] = {"rich_text": [{"text": {"content": updated_notes}}]}
        
        payload = {"properties": properties}
        response = requests.patch(url, headers=self.headers, json=payload)
        
        return response.json()
    
    def create_escalation_note(self, escalation_note: Dict[str, Any]) -> Dict[str, Any]:
        """Create escalation note in Decision Log or separate database"""
        
        # Create page in a Decision Log database or append to Project page
        # Implementation depends on your Notion structure preference
        
        url = f"https://api.notion.com/v1/pages"
        payload = {
            "parent": {"database_id": self.projects_db_id},  # Or dedicated escalations DB
            "properties": {
                "Title": {"title": [{"text": {"content": escalation_note["title"]}}]},
                "Content": {"rich_text": [{"text": {"content": escalation_note["content"]}}]},
                "Type": {"select": {"name": "Escalation"}},
                "Correlation ID": {"rich_text": [{"text": {"content": escalation_note["correlation_id"]}}]}
            }
        }
        
        response = requests.post(url, headers=self.headers, json=payload)
        return response.json()
    
    def create_plan_adjustment_note(self, plan_adjustment: Dict[str, Any], project_id: str) -> Dict[str, Any]:
        """Create planAdjustment note in Project's Decision Log"""
        
        # Format as structured decision log entry per your template
        content = f"""
**Decision**: {plan_adjustment['decision']}

**Why**: {plan_adjustment['why']}

**Evidence Links**: 
{chr(10).join(f'- {link}' for link in plan_adjustment['evidence_links'])}

**Next Actions**:
{chr(10).join(f'- {action}' for action in plan_adjustment['next_actions'])}

**Owner**: {plan_adjustment['owner']}
**Created**: {plan_adjustment['created_at']}
**Correlation ID**: {plan_adjustment['correlation_id']}
"""
        
        # Create as child page or block in Project
        url = f"https://api.notion.com/v1/pages"
        payload = {
            "parent": {"page_id": project_id},
            "properties": {
                "title": {"title": [{"text": {"content": f"Plan Adjustment - {plan_adjustment['correlation_id'][:8]}"}}]}
            },
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": content}}]
                    }
                }
            ]
        }
        
        response = requests.post(url, headers=self.headers, json=payload)
        return response.json()
    
    def _flatten_notion_properties(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Notion page properties to flat dict for easier processing"""
        
        properties = page_data.get("properties", {})
        flattened = {"id": page_data["id"], "url": page_data["url"]}
        
        for prop_name, prop_data in properties.items():
            prop_type = prop_data.get("type")
            
            if prop_type == "title":
                flattened[prop_name] = prop_data.get("title", [{}])[0].get("text", {}).get("content", "")
            elif prop_type == "rich_text":
                flattened[prop_name] = prop_data.get("rich_text", [{}])[0].get("text", {}).get("content", "")
            elif prop_type == "select":
                flattened[prop_name] = prop_data.get("select", {}).get("name", "")
            elif prop_type == "multi_select":
                flattened[prop_name] = [item.get("name", "") for item in prop_data.get("multi_select", [])]
            elif prop_type == "relation":
                flattened[prop_name] = [item.get("id", "") for item in prop_data.get("relation", [])]
            elif prop_type == "url":
                flattened[prop_name] = prop_data.get("url", "")
            # Add other property types as needed
        
        return flattened
    
    def _get_task_notes(self, task_id: str) -> str:
        """Get current notes from task"""
        task_data = self.get_task_by_id(task_id)
        return task_data.get("Notes", "")