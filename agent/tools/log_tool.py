"""Logging tool for structured logging of agent actions and decisions"""

import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum

from agent.config import Config

logger = logging.getLogger(__name__)


class LogLevel(Enum):
    """Log level"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LogCategory(Enum):
    """Log category"""
    MONITORING = "monitoring"
    RISK_ASSESSMENT = "risk_assessment"
    PREDICTION = "prediction"
    OPTIMIZATION = "optimization"
    EXECUTION = "execution"
    DATA_INGESTION = "data_ingestion"
    AGENT_QUERY = "agent_query"
    SYSTEM = "system"


@dataclass
class LogEntry:
    """Structured log entry"""
    timestamp: datetime
    level: LogLevel
    category: LogCategory
    message: str
    shipment_id: Optional[str] = None
    route_id: Optional[str] = None
    action_id: Optional[str] = None
    user_id: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class LoggingTool:
    """Tool for structured logging of agent actions"""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize logging tool"""
        self.config = config or Config()
        self.logs: List[LogEntry] = []  # In-memory storage for MVP
        self.max_logs = 10000  # Maximum logs to keep in memory
        
        # Set up Python logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Set up Python logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('arkham_ai.log')
            ]
        )
    
    def log(
        self,
        level: LogLevel,
        category: LogCategory,
        message: str,
        shipment_id: Optional[str] = None,
        route_id: Optional[str] = None,
        action_id: Optional[str] = None,
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log an entry"""
        entry = LogEntry(
            timestamp=datetime.now(),
            level=level,
            category=category,
            message=message,
            shipment_id=shipment_id,
            route_id=route_id,
            action_id=action_id,
            user_id=user_id,
            details=details or {},
            metadata=metadata or {}
        )
        
        # Add to in-memory storage
        self.logs.append(entry)
        
        # Trim if exceeds max
        if len(self.logs) > self.max_logs:
            self.logs = self.logs[-self.max_logs:]
        
        # Also log to Python logger
        log_method = getattr(logger, level.value, logger.info)
        log_message = f"[{category.value}] {message}"
        if shipment_id:
            log_message += f" | Shipment: {shipment_id}"
        if route_id:
            log_message += f" | Route: {route_id}"
        if action_id:
            log_message += f" | Action: {action_id}"
        
        log_method(log_message, extra={"details": details, "metadata": metadata})
    
    def log_monitoring_event(
        self,
        shipment_id: str,
        risk_score: float,
        risk_level: str,
        action_taken: str,
        reason: str,
        route_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log a monitoring event"""
        level = LogLevel.INFO
        if risk_score >= 0.75:
            level = LogLevel.CRITICAL
        elif risk_score >= 0.50:
            level = LogLevel.WARNING
        
        self.log(
            level=level,
            category=LogCategory.MONITORING,
            message=f"Monitoring event: Risk {risk_score:.2f} ({risk_level}), Action: {action_taken}",
            shipment_id=shipment_id,
            route_id=route_id,
            details={
                "risk_score": risk_score,
                "risk_level": risk_level,
                "action_taken": action_taken,
                "reason": reason,
                **(details or {})
            }
        )
    
    def log_risk_assessment(
        self,
        route_id: str,
        risk_score: float,
        risk_level: str,
        origin: str,
        destination: str,
        breakdown: Dict[str, float],
        recommendation: str,
        shipment_id: Optional[str] = None
    ):
        """Log a risk assessment"""
        level = LogLevel.INFO
        if risk_score >= 0.75:
            level = LogLevel.CRITICAL
        elif risk_score >= 0.50:
            level = LogLevel.WARNING
        
        self.log(
            level=level,
            category=LogCategory.RISK_ASSESSMENT,
            message=f"Risk assessment: Route {route_id} - Risk {risk_score:.2f} ({risk_level})",
            route_id=route_id,
            shipment_id=shipment_id,
            details={
                "risk_score": risk_score,
                "risk_level": risk_level,
                "origin": origin,
                "destination": destination,
                "breakdown": breakdown,
                "recommendation": recommendation
            }
        )
    
    def log_prediction(
        self,
        route_id: str,
        days_ahead: int,
        predicted_score: float,
        trend: str,
        confidence: float,
        shipment_id: Optional[str] = None
    ):
        """Log a prediction"""
        self.log(
            level=LogLevel.INFO,
            category=LogCategory.PREDICTION,
            message=f"Prediction: Route {route_id} - {days_ahead} days ahead: {predicted_score:.2f} ({trend})",
            route_id=route_id,
            shipment_id=shipment_id,
            details={
                "days_ahead": days_ahead,
                "predicted_score": predicted_score,
                "trend": trend,
                "confidence": confidence
            }
        )
    
    def log_optimization(
        self,
        original_route_id: str,
        optimized_routes: List[Dict[str, Any]],
        recommendation: str,
        shipment_id: Optional[str] = None
    ):
        """Log route optimization"""
        self.log(
            level=LogLevel.INFO,
            category=LogCategory.OPTIMIZATION,
            message=f"Route optimization: {len(optimized_routes)} alternatives found for route {original_route_id}",
            route_id=original_route_id,
            shipment_id=shipment_id,
            details={
                "original_route_id": original_route_id,
                "alternatives_count": len(optimized_routes),
                "optimized_routes": optimized_routes,
                "recommendation": recommendation
            }
        )
    
    def log_execution(
        self,
        action_id: str,
        action_type: str,
        shipment_id: str,
        status: str,
        details: Optional[Dict[str, Any]] = None,
        route_id: Optional[str] = None
    ):
        """Log an execution action"""
        level = LogLevel.INFO
        if status == "failed":
            level = LogLevel.ERROR
        elif status == "completed":
            level = LogLevel.INFO
        elif status == "executing":
            level = LogLevel.WARNING
        
        self.log(
            level=level,
            category=LogCategory.EXECUTION,
            message=f"Execution: {action_type} for shipment {shipment_id} - Status: {status}",
            action_id=action_id,
            shipment_id=shipment_id,
            route_id=route_id,
            details={
                "action_type": action_type,
                "status": status,
                **(details or {})
            }
        )
    
    def log_data_ingestion(
        self,
        source: str,
        data_points_count: int,
        region: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log data ingestion"""
        self.log(
            level=LogLevel.INFO,
            category=LogCategory.DATA_INGESTION,
            message=f"Data ingestion: {data_points_count} points from {source}",
            details={
                "source": source,
                "data_points_count": data_points_count,
                "region": region,
                **(details or {})
            }
        )
    
    def log_agent_query(
        self,
        user_id: str,
        query: str,
        response: str,
        success: bool,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log an agent query"""
        level = LogLevel.INFO if success else LogLevel.ERROR
        self.log(
            level=level,
            category=LogCategory.AGENT_QUERY,
            message=f"Agent query from user {user_id}: {query[:50]}...",
            user_id=user_id,
            details={
                "query": query,
                "response": response[:200] if response else "",
                "success": success,
                **(details or {})
            }
        )
    
    def get_logs(
        self,
        category: Optional[LogCategory] = None,
        level: Optional[LogLevel] = None,
        shipment_id: Optional[str] = None,
        route_id: Optional[str] = None,
        limit: int = 100
    ) -> List[LogEntry]:
        """Get logs with filters"""
        filtered_logs = self.logs.copy()
        
        if category:
            filtered_logs = [log for log in filtered_logs if log.category == category]
        
        if level:
            filtered_logs = [log for log in filtered_logs if log.level == level]
        
        if shipment_id:
            filtered_logs = [log for log in filtered_logs if log.shipment_id == shipment_id]
        
        if route_id:
            filtered_logs = [log for log in filtered_logs if log.route_id == route_id]
        
        # Sort by timestamp (newest first)
        filtered_logs.sort(key=lambda x: x.timestamp, reverse=True)
        
        return filtered_logs[:limit]
    
    def get_logs_json(
        self,
        category: Optional[LogCategory] = None,
        level: Optional[LogLevel] = None,
        shipment_id: Optional[str] = None,
        route_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get logs as JSON-serializable dictionaries"""
        logs = self.get_logs(category, level, shipment_id, route_id, limit)
        
        result = []
        for log in logs:
            log_dict = asdict(log)
            log_dict["timestamp"] = log.timestamp.isoformat()
            log_dict["level"] = log.level.value
            log_dict["category"] = log.category.value
            result.append(log_dict)
        
        return result
    
    def export_logs(self, filepath: str, filters: Optional[Dict[str, Any]] = None):
        """Export logs to a file"""
        logs = self.get_logs_json(
            category=filters.get("category") if filters else None,
            level=filters.get("level") if filters else None,
            shipment_id=filters.get("shipment_id") if filters else None,
            route_id=filters.get("route_id") if filters else None,
            limit=filters.get("limit", 1000) if filters else 1000
        )
        
        with open(filepath, 'w') as f:
            json.dump(logs, f, indent=2, default=str)
        
        logger.info(f"Exported {len(logs)} logs to {filepath}")


# Global tool instance
_tool_instance: Optional[LoggingTool] = None


def get_logging_tool() -> LoggingTool:
    """Get or create the global logging tool instance"""
    global _tool_instance
    if _tool_instance is None:
        _tool_instance = LoggingTool()
    return _tool_instance

