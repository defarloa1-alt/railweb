from langgraph.graph import StateGraph
from typing import TypedDict, List, Dict, Any, Optional
from tools.notion.client import NotionSDLCClient
from tools.sdlc.safety_validator import RailwebSafetyValidator
import json
import logging
from datetime import datetime
import hashlib

# Set up logging per your observability requirements
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OrchestratorState(TypedDict):
    """LangGraph state for PM orchestrator workflow"""
    event_type: str  # "task_created", "task_updated", "pr_merged"
    event_data: Dict[str, Any]
    task_data: Dict[str, Any]
    framework_data: Dict[str, Any]
    rule_evaluations: List[Dict[str, Any]]
    plan_adjustment: Optional[Dict[str, Any]]
    escalation_notice: Optional[Dict[str, Any]]
    correlation_id: str
    needs_review: bool

class PMOrchestrator:
    """Project Manager orchestrator using LangGraph for SDLC workflow automation"""
    
    def __init__(self, notion_token: str):
        self.notion_client = NotionSDLCClient(notion_token)
        self.safety_validator = RailwebSafetyValidator()
        self.workflow = StateGraph(OrchestratorState)
        self._build_workflow()
        
        # Rule packs for v1 (as specified)
        self.rule_packs = {
            "MVP_Feature_Prioritization": self._evaluate_mvp_feature_rules,
            "L1_Requirements_Modeling": self._evaluate_l1_requirements_rules,
            "Metrics_Analysis_Reporting": self._evaluate_metrics_rules
        }
    
    def _build_workflow(self):
        """Build LangGraph workflow for PM orchestration"""
        
        # PM drives the orchestration sequence
        self.workflow.add_node("initialize", self._initialize_state)
        self.workflow.add_node("fetch_context", self._fetch_framework_context)
        self.workflow.add_node("evaluate_rules", self._evaluate_dod_gates)
        self.workflow.add_node("safety_check", self._apply_safety_validation)
        self.workflow.add_node("generate_outputs", self._generate_plan_adjustment)
        self.workflow.add_node("update_notion", self._update_notion_task)
        self.workflow.add_node("escalate", self._handle_escalation)
        
        # PM controls the flow based on evaluation results
        self.workflow.set_entry_point("initialize")
        self.workflow.add_edge("initialize", "fetch_context")
        self.workflow.add_edge("fetch_context", "evaluate_rules")
        self.workflow.add_edge("evaluate_rules", "safety_check")
        
        # Conditional routing based on safety and rule results
        self.workflow.add_conditional_edges(
            "safety_check",
            self._routing_logic,
            {
                "escalate": "escalate",
                "generate": "generate_outputs"
            }
        )
        self.workflow.add_edge("generate_outputs", "update_notion")
        self.workflow.add_edge("escalate", "update_notion")
    
    def process_event(self, event_type: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main entry point: process Notion/PR events through PM orchestration"""
        
        # Generate correlation ID for observability
        correlation_id = self._generate_correlation_id(event_type, event_data)
        
        logger.info(f"PM Orchestrator processing event", extra={
            "correlation_id": correlation_id,
            "event_type": event_type
        })
        
        # Initialize state
        initial_state = OrchestratorState(
            event_type=event_type,
            event_data=event_data,
            task_data={},
            framework_data={},
            rule_evaluations=[],
            plan_adjustment=None,
            escalation_notice=None,
            correlation_id=correlation_id,
            needs_review=False
        )
        
        # Run LangGraph workflow
        try:
            final_state = self.workflow.invoke(initial_state)
            
            # Log observability metrics
            self._emit_metrics(final_state)
            
            return {
                "status": "success",
                "correlation_id": correlation_id,
                "plan_adjustment": final_state.get("plan_adjustment"),
                "escalation_notice": final_state.get("escalation_notice"),
                "needs_review": final_state.get("needs_review", False)
            }
            
        except Exception as e:
            logger.error(f"PM Orchestrator failed", extra={
                "correlation_id": correlation_id,
                "error": str(e)
            })
            return {"status": "error", "correlation_id": correlation_id, "error": str(e)}
    
    def _initialize_state(self, state: OrchestratorState) -> OrchestratorState:
        """Initialize orchestrator state from event data"""
        
        # Extract task information based on event type
        if state["event_type"] == "task_created":
            state["task_data"] = state["event_data"].get("task", {})
        elif state["event_type"] == "pr_merged":
            # Find associated task from PR data
            task_id = self._extract_task_id_from_pr(state["event_data"])
            if task_id:
                state["task_data"] = self.notion_client.get_task_by_id(task_id)
        
        logger.info(f"Initialized state for task", extra={
            "correlation_id": state["correlation_id"],
            "task_name": state["task_data"].get("Task Name", "unknown")
        })
        
        return state
    
    def _fetch_framework_context(self, state: OrchestratorState) -> OrchestratorState:
        """Fetch canonical Framework link and acceptance criteria"""
        
        framework_link = state["task_data"].get("Framework link")
        if not framework_link:
            logger.warning(f"No Framework link found", extra={
                "correlation_id": state["correlation_id"]
            })
            state["framework_data"] = {}
            return state
        
        # Fetch Framework node data from Notion
        framework_data = self.notion_client.get_framework_node(framework_link)
        state["framework_data"] = framework_data
        
        logger.info(f"Fetched framework context", extra={
            "correlation_id": state["correlation_id"],
            "framework_name": framework_data.get("Title", "unknown")
        })
        
        return state
    
    def _evaluate_dod_gates(self, state: OrchestratorState) -> OrchestratorState:
        """Evaluate Definition of Done gates using rule packs"""
        
        evaluations = []
        
        # Determine which rule pack to apply based on Framework node
        framework_title = state["framework_data"].get("Title", "").lower()
        
        # Apply relevant rule packs (v1 scope: 3 rule packs)
        for rule_pack_name, rule_evaluator in self.rule_packs.items():
            if self._should_apply_rule_pack(rule_pack_name, framework_title):
                evaluation = rule_evaluator(state["task_data"], state["framework_data"])
                evaluation["rule_pack"] = rule_pack_name
                evaluation["correlation_id"] = state["correlation_id"]
                evaluations.append(evaluation)
                
                # Log each rule evaluation per observability requirements
                logger.info(f"Rule evaluation complete", extra={
                    "correlation_id": state["correlation_id"],
                    "rule_pack": rule_pack_name,
                    "passed": evaluation["passed"],
                    "score": evaluation.get("score", 0)
                })
        
        state["rule_evaluations"] = evaluations
        return state
    
    def _evaluate_mvp_feature_rules(self, task_data: Dict[str, Any], framework_data: Dict[str, Any]) -> Dict[str, Any]:
        """MVP Feature Prioritization rule pack"""
        
        checks = []
        score = 0
        max_score = 2
        
        # Check 1: Has Baseline Functionality task linked
        baseline_linked = self._has_related_task_type(task_data, "Baseline Functionality")
        checks.append({
            "rule": "baseline_functionality_linked",
            "passed": baseline_linked,
            "evidence": f"Related tasks: {task_data.get('Framework refs', [])}"
        })
        if baseline_linked:
            score += 1
        
        # Check 2: Must-Have Analysis checked
        must_have_analysis = self._has_analysis_artifact(task_data, "Must-Have")
        checks.append({
            "rule": "must_have_analysis_present",
            "passed": must_have_analysis,
            "evidence": f"Source links: {task_data.get('Source link', '')}"
        })
        if must_have_analysis:
            score += 1
        
        return {
            "rule_pack": "MVP_Feature_Prioritization",
            "passed": score == max_score,
            "score": score,
            "max_score": max_score,
            "checks": checks,
            "next_actions": self._generate_mvp_next_actions(checks)
        }
    
    def _evaluate_l1_requirements_rules(self, task_data: Dict[str, Any], framework_data: Dict[str, Any]) -> Dict[str, Any]:
        """L1 Requirements Modeling rule pack"""
        
        checks = []
        score = 0
        max_score = 2
        
        # Check 1: SysML artifact path present in docs/architecture
        sysml_artifact = self._has_sysml_artifact(task_data)
        checks.append({
            "rule": "sysml_artifact_present",
            "passed": sysml_artifact,
            "evidence": f"Looking for docs/architecture/*.sysml in Source link"
        })
        if sysml_artifact:
            score += 1
        
        # Check 2: Artifact linked in Source link
        artifact_linked = self._has_architecture_link(task_data)
        checks.append({
            "rule": "architecture_artifact_linked",
            "passed": artifact_linked,
            "evidence": f"Source link: {task_data.get('Source link', '')}"
        })
        if artifact_linked:
            score += 1
        
        return {
            "rule_pack": "L1_Requirements_Modeling",
            "passed": score == max_score,
            "score": score,
            "max_score": max_score,
            "checks": checks,
            "next_actions": self._generate_l1_next_actions(checks)
        }
    
    def _evaluate_metrics_rules(self, task_data: Dict[str, Any], framework_data: Dict[str, Any]) -> Dict[str, Any]:
        """Metrics Analysis and Reporting rule pack"""
        
        checks = []
        score = 0
        max_score = 2
        
        # Check 1: Performance threshold stub present
        perf_threshold = self._has_performance_threshold(task_data)
        checks.append({
            "rule": "performance_threshold_defined",
            "passed": perf_threshold,
            "evidence": f"Checking Notes and Source link for perf targets"
        })
        if perf_threshold:
            score += 1
        
        # Check 2: Dashboard URL present
        dashboard_url = self._has_dashboard_url(task_data)
        checks.append({
            "rule": "dashboard_url_present", 
            "passed": dashboard_url,
            "evidence": f"Observability URL or dashboard link in Source"
        })
        if dashboard_url:
            score += 1
        
        return {
            "rule_pack": "Metrics_Analysis_Reporting",
            "passed": score == max_score,
            "score": score,
            "max_score": max_score,
            "checks": checks,
            "next_actions": self._generate_metrics_next_actions(checks)
        }
    
    def _apply_safety_validation(self, state: OrchestratorState) -> OrchestratorState:
        """Apply railweb safety validation per intake constraints"""
        
        # Use existing safety validator
        safety_assessment = self.safety_validator.validate_task_safety(
            state["task_data"], 
            {"recommendation": state["event_data"]}  # Convert event to expected format
        )
        
        # Check escalation condition: safety_tag=true AND missing perf target or test coverage
        safety_escalation_needed = (
            safety_assessment.get("safety_flags") and
            any(flag in ["HARDWARE_CONTROL_DETECTED", "DCC_PROGRAMMING_DETECTED"] 
                for flag in safety_assessment["safety_flags"]) and
            self._missing_safety_requirements(state["rule_evaluations"])
        )
        
        if safety_escalation_needed:
            state["escalation_notice"] = {
                "type": "safety_critical",
                "reason": "Safety-critical task failing DoD requirements",
                "safety_flags": safety_assessment["safety_flags"],
                "suggested_action": "Pause",
                "correlation_id": state["correlation_id"]
            }
            state["needs_review"] = True
        
        return state
    
    def _routing_logic(self, state: OrchestratorState) -> str:
        """PM routing logic: escalate vs generate based on evaluation results"""
        
        if state.get("escalation_notice"):
            return "escalate"
        else:
            return "generate"
    
    def _generate_plan_adjustment(self, state: OrchestratorState) -> OrchestratorState:
        """Generate planAdjustment based on rule evaluations"""
        
        # Aggregate results from all rule evaluations
        total_passed = sum(1 for eval in state["rule_evaluations"] if eval["passed"])
        total_rules = len(state["rule_evaluations"])
        
        # Collect next actions from all evaluations
        all_next_actions = []
        for evaluation in state["rule_evaluations"]:
            all_next_actions.extend(evaluation.get("next_actions", []))
        
        # Generate plan adjustment following your template
        plan_adjustment = {
            "decision": f"DoD Gate Evaluation: {total_passed}/{total_rules} rule packs passed",
            "why": f"Automated evaluation of Framework acceptance criteria",
            "evidence_links": [
                state["task_data"].get("Source link", ""),
                f"Framework: {state['framework_data'].get('Title', 'unknown')}"
            ],
            "next_actions": all_next_actions[:3],  # Top 3 actions
            "owner": "PM Orchestrator",
            "correlation_id": state["correlation_id"],
            "created_at": datetime.now().isoformat()
        }
        
        state["plan_adjustment"] = plan_adjustment
        return state
    
    def _update_notion_task(self, state: OrchestratorState) -> OrchestratorState:
        """Update Notion task with orchestrator results"""
        
        task_id = state["task_data"].get("id")
        if not task_id:
            return state
        
        # Prepare task updates (append Notes, set needs-review if required)
        notes_to_append = []
        
        # Add rule evaluation summary
        for evaluation in state["rule_evaluations"]:
            rule_summary = f"**{evaluation['rule_pack']}**: {'✅ PASS' if evaluation['passed'] else '❌ FAIL'} ({evaluation['score']}/{evaluation['max_score']})"
            notes_to_append.append(rule_summary)
            
            # Add failed checks for visibility
            if not evaluation["passed"]:
                for check in evaluation["checks"]:
                    if not check["passed"]:
                        notes_to_append.append(f"  - {check['rule']}: {check['evidence']}")
        
        # Update task in Notion (idempotent by correlation_id)
        update_result = self.notion_client.append_task_notes(
            task_id, 
            notes_to_append,
            correlation_id=state["correlation_id"],
            needs_review=state["needs_review"]
        )
        
        logger.info(f"Updated Notion task", extra={
            "correlation_id": state["correlation_id"],
            "task_id": task_id,
            "notes_added": len(notes_to_append)
        })
        
        return state
    
    def _handle_escalation(self, state: OrchestratorState) -> OrchestratorState:
        """Handle escalation by creating escalationNote"""
        
        escalation = state["escalation_notice"]
        if not escalation:
            return state
        
        # Create escalation note in Notion (could be a separate page or task update)
        escalation_note = {
            "title": f"ESCALATION: {escalation['type']}",
            "content": f"""
**Reason**: {escalation['reason']}
**Suggested Action**: {escalation['suggested_action']}
**Safety Flags**: {', '.join(escalation.get('safety_flags', []))}
**Task**: {state['task_data'].get('Task Name', 'unknown')}
**Correlation ID**: {escalation['correlation_id']}
**Created**: {datetime.now().isoformat()}
""",
            "correlation_id": escalation["correlation_id"]
        }
        
        # Post to Notion Decision Log or create Linear issue
        escalation_result = self.notion_client.create_escalation_note(escalation_note)
        
        logger.warning(f"Escalation created", extra={
            "correlation_id": state["correlation_id"],
            "escalation_type": escalation["type"],
            "escalation_id": escalation_result.get("id")
        })
        
        return state
    
    def _emit_metrics(self, final_state: OrchestratorState):
        """Emit observability metrics per requirements"""
        
        correlation_id = final_state["correlation_id"]
        
        # Count rule outcomes
        rules_passed = sum(1 for eval in final_state["rule_evaluations"] if eval["passed"])
        rules_failed = len(final_state["rule_evaluations"]) - rules_passed
        escalations_opened = 1 if final_state.get("escalation_notice") else 0
        
        # Emit metrics (replace with your actual metrics system)
        logger.info("PM Orchestrator metrics", extra={
            "correlation_id": correlation_id,
            "metric_rules_passed": rules_passed,
            "metric_rules_failed": rules_failed,
            "metric_escalations_opened": escalations_opened
        })
    
    # Helper methods for rule evaluation
    def _should_apply_rule_pack(self, rule_pack_name: str, framework_title: str) -> bool:
        """Determine if rule pack applies to this Framework node"""
        
        rule_pack_keywords = {
            "MVP_Feature_Prioritization": ["mvp", "feature", "baseline", "priority"],
            "L1_Requirements_Modeling": ["requirements", "modeling", "architecture", "sysml"],
            "Metrics_Analysis_Reporting": ["metrics", "performance", "reporting", "observability"]
        }
        
        keywords = rule_pack_keywords.get(rule_pack_name, [])
        return any(keyword in framework_title for keyword in keywords)
    
    def _has_related_task_type(self, task_data: Dict[str, Any], task_type: str) -> bool:
        """Check if task has related tasks of specified type"""
        framework_refs = task_data.get("Framework refs", [])
        return any(task_type.lower() in str(ref).lower() for ref in framework_refs)
    
    def _has_analysis_artifact(self, task_data: Dict[str, Any], analysis_type: str) -> bool:
        """Check if task has specified analysis artifact"""
        source_link = task_data.get("Source link", "").lower()
        return analysis_type.lower() in source_link
    
    def _has_sysml_artifact(self, task_data: Dict[str, Any]) -> bool:
        """Check for SysML artifact in docs/architecture"""
        source_link = task_data.get("Source link", "")
        return "docs/architecture" in source_link and ".sysml" in source_link
    
    def _has_architecture_link(self, task_data: Dict[str, Any]) -> bool:
        """Check if architecture artifact is linked"""
        source_link = task_data.get("Source link", "")
        return "docs/" in source_link or "architecture" in source_link
    
    def _has_performance_threshold(self, task_data: Dict[str, Any]) -> bool:
        """Check for performance threshold definition"""
        notes = task_data.get("Notes", "").lower()
        source = task_data.get("Source link", "").lower()
        perf_keywords = ["performance", "threshold", "target", "sla", "benchmark"]
        return any(keyword in notes + source for keyword in perf_keywords)
    
    def _has_dashboard_url(self, task_data: Dict[str, Any]) -> bool:
        """Check for dashboard URL"""
        source = task_data.get("Source link", "").lower()
        dashboard_keywords = ["dashboard", "grafana", "observability", "metrics"]
        return any(keyword in source for keyword in dashboard_keywords)
    
    def _missing_safety_requirements(self, rule_evaluations: List[Dict[str, Any]]) -> bool:
        """Check if safety requirements are missing from evaluations"""
        for evaluation in rule_evaluations:
            if evaluation["rule_pack"] == "Metrics_Analysis_Reporting" and not evaluation["passed"]:
                return True
        return False
    
    def _generate_mvp_next_actions(self, checks: List[Dict[str, Any]]) -> List[str]:
        """Generate next actions for MVP feature rules"""
        actions = []
        for check in checks:
            if not check["passed"]:
                if check["rule"] == "baseline_functionality_linked":
                    actions.append("Link baseline functionality task in Framework refs")
                elif check["rule"] == "must_have_analysis_present":
                    actions.append("Add Must-Have analysis document to Source link")
        return actions
    
    def _generate_l1_next_actions(self, checks: List[Dict[str, Any]]) -> List[str]:
        """Generate next actions for L1 requirements rules"""
        actions = []
        for check in checks:
            if not check["passed"]:
                if check["rule"] == "sysml_artifact_present":
                    actions.append("Create SysML artifact in docs/architecture/")
                elif check["rule"] == "architecture_artifact_linked":
                    actions.append("Link architecture artifact in Source link")
        return actions
    
    def _generate_metrics_next_actions(self, checks: List[Dict[str, Any]]) -> List[str]:
        """Generate next actions for metrics rules"""
        actions = []
        for check in checks:
            if not check["passed"]:
                if check["rule"] == "performance_threshold_defined":
                    actions.append("Define performance thresholds in task Notes")
                elif check["rule"] == "dashboard_url_present":
                    actions.append("Add observability dashboard URL to Source link")
        return actions
    
    def _generate_correlation_id(self, event_type: str, event_data: Dict[str, Any]) -> str:
        """Generate correlation ID for observability tracking"""
        content = f"{event_type}_{event_data.get('task_url', '')}_{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _extract_task_id_from_pr(self, pr_event: Dict[str, Any]) -> Optional[str]:
        """Extract task ID from PR event data"""
        # Implementation depends on your PR webhook format
        return pr_event.get("task_id")  # Placeholder