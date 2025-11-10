"""Autonomous execution tool for automatically executing route changes"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from agent.tools.risk_tool import RiskLevel, get_risk_tool
from agent.tools.route_tool import get_route_optimization_tool, OptimizationPriority

logger = logging.getLogger(__name__)


class ExecutionStatus(Enum):
    """Execution status"""
    PENDING = "pending"
    APPROVED = "approved"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected"


class ExecutionMode(Enum):
    """Execution mode"""
    AUTOMATIC = "automatic"  # Execute automatically when threshold met
    MANUAL = "manual"  # Require manual approval
    SEMI_AUTOMATIC = "semi_automatic"  # Auto-approve low-risk changes, manual for high-risk


@dataclass
class ExecutionAction:
    """An execution action"""
    action_id: str
    action_type: str  # "reroute", "delay", "cancel", "notify"
    shipment_id: str
    original_route_id: str
    new_route_id: Optional[str] = None
    reason: str = ""
    risk_score_before: float = 0.0
    risk_score_after: float = 0.0
    estimated_impact: Dict[str, Any] = field(default_factory=dict)
    status: ExecutionStatus = ExecutionStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    executed_at: Optional[datetime] = None
    executed_by: str = "arkham_ai"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    """Result of execution"""
    action: ExecutionAction
    success: bool
    message: str
    execution_timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)


class AutonomousExecutionTool:
    """Tool for autonomously executing route changes and actions"""
    
    def __init__(self):
        """Initialize autonomous execution tool"""
        self.risk_tool = get_risk_tool()
        self.route_optimization_tool = get_route_optimization_tool()
        
        # Try to import logging tool, but don't fail if not available yet
        try:
            from agent.tools.log_tool import get_logging_tool
            self.log_tool = get_logging_tool()
        except:
            self.log_tool = None
        
        # Execution thresholds
        self.auto_execute_threshold = 0.75  # Auto-execute if risk >= 0.75
        self.auto_approve_threshold = 0.50  # Auto-approve if risk reduction >= 0.50
        self.min_risk_reduction = 0.20  # Minimum risk reduction to recommend reroute
        
        # Execution mode
        self.execution_mode = ExecutionMode.SEMI_AUTOMATIC
    
    def monitor_and_execute(
        self,
        shipment_id: str,
        origin: str,
        destination: str,
        route_regions: Optional[List[str]] = None,
        execution_mode: Optional[ExecutionMode] = None
    ) -> Optional[ExecutionAction]:
        """Monitor route and execute actions if thresholds are met"""
        mode = execution_mode or self.execution_mode
        
        # Assess current risk
        risk_assessment = self.risk_tool.assess_route_risk(
            origin=origin,
            destination=destination,
            route_regions=route_regions,
            route_id=f"SHIP-{shipment_id}"
        )
        
        current_risk = risk_assessment.overall_risk_score
        
        # Check if action is needed
        if current_risk >= self.auto_execute_threshold:
            # High risk detected - optimize and execute
            return self._execute_reroute(
                shipment_id=shipment_id,
                origin=origin,
                destination=destination,
                route_regions=route_regions,
                current_risk=current_risk,
                execution_mode=mode
            )
        elif current_risk >= 0.50:  # Medium-high risk
            # Check if optimization would help
            optimization_result = self.route_optimization_tool.optimize_route(
                origin=origin,
                destination=destination,
                priority=OptimizationPriority.RISK,
                include_predictions=True,
                max_alternatives=3
            )
            
            if optimization_result.optimized_routes:
                best_alternative = optimization_result.optimized_routes[0]
                risk_reduction = current_risk - best_alternative.metrics.risk_score
                
                if risk_reduction >= self.min_risk_reduction:
                    return self._create_reroute_action(
                        shipment_id=shipment_id,
                        original_route_id=f"SHIP-{shipment_id}",
                        new_route_id=best_alternative.route_id,
                        current_risk=current_risk,
                        new_risk=best_alternative.metrics.risk_score,
                        reason=optimization_result.recommendation,
                        execution_mode=mode
                    )
        
        # Log monitoring event
        if self.log_tool:
            self.log_tool.log_monitoring_event(
                shipment_id=shipment_id,
                risk_score=current_risk,
                risk_level=risk_assessment.risk_level.value,
                action_taken="none",
                reason="Risk below threshold"
            )
        
        return None
    
    def execute_reroute(
        self,
        shipment_id: str,
        new_route_id: str,
        origin: str,
        destination: str,
        route_regions: Optional[List[str]] = None,
        reason: Optional[str] = None
    ) -> ExecutionResult:
        """Execute a reroute action"""
        # Assess new route
        new_risk_assessment = self.risk_tool.assess_route_risk(
            origin=origin,
            destination=destination,
            route_regions=route_regions,
            route_id=new_route_id
        )
        
        # Get original route risk
        original_risk_assessment = self.risk_tool.assess_route_risk(
            origin=origin,
            destination=destination,
            route_regions=route_regions,
            route_id=f"SHIP-{shipment_id}"
        )
        
        # Create action
        action = ExecutionAction(
            action_id=f"EXEC-{shipment_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            action_type="reroute",
            shipment_id=shipment_id,
            original_route_id=f"SHIP-{shipment_id}",
            new_route_id=new_route_id,
            reason=reason or "Risk mitigation reroute",
            risk_score_before=original_risk_assessment.overall_risk_score,
            risk_score_after=new_risk_assessment.overall_risk_score,
            estimated_impact={
                "risk_reduction": original_risk_assessment.overall_risk_score - new_risk_assessment.overall_risk_score,
                "cost_delta": 0,  # Would be calculated from route metrics
                "time_delta": 0   # Would be calculated from route metrics
            }
        )
        
        # Execute action
        return self._execute_action(action)
    
    def _execute_reroute(
        self,
        shipment_id: str,
        origin: str,
        destination: str,
        route_regions: Optional[List[str]],
        current_risk: float,
        execution_mode: ExecutionMode
    ) -> Optional[ExecutionAction]:
        """Execute automatic reroute"""
        # Optimize route
        optimization_result = self.route_optimization_tool.optimize_route(
            origin=origin,
            destination=destination,
            priority=OptimizationPriority.RISK,
            include_predictions=True,
            max_alternatives=3
        )
        
        if not optimization_result.optimized_routes:
            return None
        
        best_alternative = optimization_result.optimized_routes[0]
        new_risk = best_alternative.metrics.risk_score
        risk_reduction = current_risk - new_risk
        
        # Check if reroute is beneficial
        if risk_reduction < self.min_risk_reduction:
            return None
        
        # Create action
        action = self._create_reroute_action(
            shipment_id=shipment_id,
            original_route_id=f"SHIP-{shipment_id}",
            new_route_id=best_alternative.route_id,
            current_risk=current_risk,
            new_risk=new_risk,
            reason=f"CRITICAL RISK DETECTED: Risk {current_risk:.2f} exceeds threshold. "
                   f"Rerouting to reduce risk to {new_risk:.2f} (reduction: {risk_reduction:.2f})",
            execution_mode=execution_mode
        )
        
        # Execute based on mode
        if execution_mode == ExecutionMode.AUTOMATIC:
            result = self._execute_action(action)
            if result.success:
                return action
        elif execution_mode == ExecutionMode.SEMI_AUTOMATIC:
            if risk_reduction >= self.auto_approve_threshold:
                result = self._execute_action(action)
                if result.success:
                    return action
            else:
                action.status = ExecutionStatus.PENDING
                # Would send notification for manual approval
                return action
        
        return action
    
    def _create_reroute_action(
        self,
        shipment_id: str,
        original_route_id: str,
        new_route_id: str,
        current_risk: float,
        new_risk: float,
        reason: str,
        execution_mode: ExecutionMode
    ) -> ExecutionAction:
        """Create a reroute action"""
        action = ExecutionAction(
            action_id=f"EXEC-{shipment_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            action_type="reroute",
            shipment_id=shipment_id,
            original_route_id=original_route_id,
            new_route_id=new_route_id,
            reason=reason,
            risk_score_before=current_risk,
            risk_score_after=new_risk,
            estimated_impact={
                "risk_reduction": current_risk - new_risk,
                "risk_reduction_percent": ((current_risk - new_risk) / current_risk * 100) if current_risk > 0 else 0
            }
        )
        
        # Set status based on execution mode
        if execution_mode == ExecutionMode.AUTOMATIC:
            action.status = ExecutionStatus.APPROVED
        elif execution_mode == ExecutionMode.SEMI_AUTOMATIC:
            risk_reduction = current_risk - new_risk
            if risk_reduction >= self.auto_approve_threshold:
                action.status = ExecutionStatus.APPROVED
            else:
                action.status = ExecutionStatus.PENDING
        else:
            action.status = ExecutionStatus.PENDING
        
        return action
    
    def _execute_action(self, action: ExecutionAction) -> ExecutionResult:
        """Execute an action"""
        try:
            # In production, this would integrate with logistics systems
            # For MVP, we simulate execution
            
            if action.status != ExecutionStatus.APPROVED:
                return ExecutionResult(
                    action=action,
                    success=False,
                    message=f"Action not approved. Status: {action.status.value}",
                    details={"status": action.status.value}
                )
            
            # Simulate execution
            action.status = ExecutionStatus.EXECUTING
            action.executed_at = datetime.now()
            
            # Log execution
            if self.log_tool:
                self.log_tool.log_execution(
                    action_id=action.action_id,
                    action_type=action.action_type,
                    shipment_id=action.shipment_id,
                    status="executing",
                    details={
                        "original_route": action.original_route_id,
                        "new_route": action.new_route_id,
                        "risk_before": action.risk_score_before,
                        "risk_after": action.risk_score_after
                    }
                )
            
            # Simulate successful execution
            action.status = ExecutionStatus.COMPLETED
            
            # Log completion
            if self.log_tool:
                self.log_tool.log_execution(
                    action_id=action.action_id,
                    action_type=action.action_type,
                    shipment_id=action.shipment_id,
                    status="completed",
                    details={"executed_at": action.executed_at.isoformat()}
                )
            
            return ExecutionResult(
                action=action,
                success=True,
                message=f"Successfully executed {action.action_type} for shipment {action.shipment_id}",
                details={
                    "action_id": action.action_id,
                    "risk_reduction": action.risk_score_before - action.risk_score_after,
                    "executed_at": action.executed_at.isoformat()
                }
            )
            
        except Exception as e:
            action.status = ExecutionStatus.FAILED
            logger.error(f"Failed to execute action {action.action_id}: {e}")
            
            if self.log_tool:
                self.log_tool.log_execution(
                    action_id=action.action_id,
                    action_type=action.action_type,
                    shipment_id=action.shipment_id,
                    status="failed",
                    details={"error": str(e)}
                )
            
            return ExecutionResult(
                action=action,
                success=False,
                message=f"Execution failed: {str(e)}",
                details={"error": str(e)}
            )
    
    def get_action_status(self, action_id: str) -> Optional[ExecutionAction]:
        """Get status of an execution action"""
        # In production, this would query a database
        # For MVP, return None (would be implemented with storage)
        return None
    
    def list_actions(
        self,
        shipment_id: Optional[str] = None,
        status: Optional[ExecutionStatus] = None
    ) -> List[ExecutionAction]:
        """List execution actions"""
        # In production, this would query a database
        # For MVP, return empty list
        return []


# Global tool instance
_tool_instance: Optional[AutonomousExecutionTool] = None


def get_execution_tool() -> AutonomousExecutionTool:
    """Get or create the global autonomous execution tool instance"""
    global _tool_instance
    if _tool_instance is None:
        _tool_instance = AutonomousExecutionTool()
    return _tool_instance

