"""Risk assessment tool for analyzing and scoring route risks"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from agent.data_ingestion import RiskDataPoint, get_data_ingestion_service

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class RiskBreakdown:
    """Breakdown of risk by category"""
    trade_news: float = 0.0
    political: float = 0.0
    port_congestion: float = 0.0
    total: float = 0.0


@dataclass
class RiskAssessment:
    """Complete risk assessment for a route"""
    route_id: Optional[str]
    origin: str
    destination: str
    overall_risk_score: float  # 0.0 to 1.0
    risk_level: RiskLevel
    breakdown: RiskBreakdown
    contributing_factors: List[Dict[str, Any]]
    assessment_timestamp: datetime = field(default_factory=datetime.now)
    recommendation: str = ""
    confidence: float = 0.0  # 0.0 to 1.0


class RiskAssessmentTool:
    """Tool for assessing and scoring route risks"""
    
    def __init__(self):
        """Initialize risk assessment tool"""
        self.data_service = get_data_ingestion_service()
        
        # Risk category weights (can be adjusted based on business priorities)
        self.category_weights = {
            "trade_news": 0.35,
            "political": 0.40,
            "port_congestion": 0.25
        }
        
        # Time decay factor (recent events weighted more heavily)
        self.time_decay_hours = 168  # 7 days
    
    def assess_route_risk(
        self,
        origin: str,
        destination: str,
        route_regions: Optional[List[str]] = None,
        route_id: Optional[str] = None
    ) -> RiskAssessment:
        """Assess overall risk for a shipping route"""
        # Fetch risk data for the route
        risk_data = self.data_service.fetch_risk_data_for_route(
            origin=origin,
            destination=destination,
            route_regions=route_regions
        )
        
        # Calculate risk breakdown by category
        breakdown = self._calculate_risk_breakdown(risk_data)
        
        # Calculate overall risk score
        overall_score = self._calculate_overall_risk(breakdown, risk_data)
        
        # Determine risk level
        risk_level = self._determine_risk_level(overall_score)
        
        # Get contributing factors
        contributing_factors = self._get_contributing_factors(risk_data)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(risk_level, overall_score, breakdown)
        
        # Calculate confidence based on data quality and recency
        confidence = self._calculate_confidence(risk_data)
        
        return RiskAssessment(
            route_id=route_id,
            origin=origin,
            destination=destination,
            overall_risk_score=overall_score,
            risk_level=risk_level,
            breakdown=breakdown,
            contributing_factors=contributing_factors,
            recommendation=recommendation,
            confidence=confidence
        )
    
    def assess_risk_from_data(
        self,
        risk_data: List[RiskDataPoint],
        origin: str,
        destination: str,
        route_id: Optional[str] = None
    ) -> RiskAssessment:
        """Assess risk from provided risk data points"""
        # Calculate risk breakdown
        breakdown = self._calculate_risk_breakdown(risk_data)
        
        # Calculate overall risk score
        overall_score = self._calculate_overall_risk(breakdown, risk_data)
        
        # Determine risk level
        risk_level = self._determine_risk_level(overall_score)
        
        # Get contributing factors
        contributing_factors = self._get_contributing_factors(risk_data)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(risk_level, overall_score, breakdown)
        
        # Calculate confidence
        confidence = self._calculate_confidence(risk_data)
        
        return RiskAssessment(
            route_id=route_id,
            origin=origin,
            destination=destination,
            overall_risk_score=overall_score,
            risk_level=risk_level,
            breakdown=breakdown,
            contributing_factors=contributing_factors,
            recommendation=recommendation,
            confidence=confidence
        )
    
    def _calculate_risk_breakdown(self, risk_data: List[RiskDataPoint]) -> RiskBreakdown:
        """Calculate risk breakdown by category"""
        breakdown = RiskBreakdown()
        
        # Group data by category
        trade_news_data = [d for d in risk_data if d.category == "trade_news"]
        political_data = [d for d in risk_data if d.category == "political"]
        port_data = [d for d in risk_data if d.category == "port_congestion"]
        
        # Calculate weighted average for each category
        breakdown.trade_news = self._calculate_category_risk(trade_news_data)
        breakdown.political = self._calculate_category_risk(political_data)
        breakdown.port_congestion = self._calculate_category_risk(port_data)
        
        # Calculate total weighted risk
        breakdown.total = (
            breakdown.trade_news * self.category_weights["trade_news"] +
            breakdown.political * self.category_weights["political"] +
            breakdown.port_congestion * self.category_weights["port_congestion"]
        )
        
        return breakdown
    
    def _calculate_category_risk(self, data_points: List[RiskDataPoint]) -> float:
        """Calculate risk score for a category with time decay"""
        if not data_points:
            return 0.0
        
        now = datetime.now()
        weighted_scores = []
        total_weight = 0.0
        
        for point in data_points:
            # Calculate time decay factor
            hours_ago = (now - point.timestamp).total_seconds() / 3600
            time_weight = max(0, 1 - (hours_ago / self.time_decay_hours))
            
            # Weighted score
            weighted_score = point.severity * time_weight
            weighted_scores.append(weighted_score)
            total_weight += time_weight
        
        if total_weight == 0:
            return 0.0
        
        # Return weighted average, capped at 1.0
        return min(1.0, sum(weighted_scores) / max(1, len(weighted_scores)))
    
    def _calculate_overall_risk(
        self,
        breakdown: RiskBreakdown,
        risk_data: List[RiskDataPoint]
    ) -> float:
        """Calculate overall risk score"""
        base_score = breakdown.total
        
        # Apply multipliers for critical factors
        critical_multiplier = 1.0
        
        # Check for critical events (severity > 0.8)
        critical_events = [d for d in risk_data if d.severity > 0.8]
        if critical_events:
            # Increase risk if multiple critical events
            critical_multiplier = min(1.2, 1.0 + (len(critical_events) * 0.05))
        
        # Check for recent high-severity events (within 24 hours)
        recent_critical = [
            d for d in risk_data
            if d.severity > 0.7 and (datetime.now() - d.timestamp).total_seconds() < 86400
        ]
        if recent_critical:
            critical_multiplier = min(1.3, critical_multiplier + 0.1)
        
        final_score = min(1.0, base_score * critical_multiplier)
        
        return round(final_score, 3)
    
    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level from score"""
        if risk_score >= 0.75:
            return RiskLevel.CRITICAL
        elif risk_score >= 0.50:
            return RiskLevel.HIGH
        elif risk_score >= 0.25:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _get_contributing_factors(self, risk_data: List[RiskDataPoint]) -> List[Dict[str, Any]]:
        """Get top contributing risk factors"""
        # Sort by severity and recency
        sorted_data = sorted(
            risk_data,
            key=lambda x: (x.severity, x.timestamp),
            reverse=True
        )
        
        # Get top 5 factors
        top_factors = sorted_data[:5]
        
        factors = []
        for point in top_factors:
            hours_ago = (datetime.now() - point.timestamp).total_seconds() / 3600
            
            factors.append({
                "category": point.category,
                "title": point.title,
                "description": point.description,
                "severity": point.severity,
                "location": point.location,
                "hours_ago": round(hours_ago, 1),
                "impact": self._get_impact_level(point.severity)
            })
        
        return factors
    
    def _get_impact_level(self, severity: float) -> str:
        """Get impact level description"""
        if severity >= 0.75:
            return "critical"
        elif severity >= 0.50:
            return "high"
        elif severity >= 0.25:
            return "medium"
        else:
            return "low"
    
    def _generate_recommendation(
        self,
        risk_level: RiskLevel,
        risk_score: float,
        breakdown: RiskBreakdown
    ) -> str:
        """Generate risk-based recommendation"""
        if risk_level == RiskLevel.CRITICAL:
            return (
                "CRITICAL RISK: Immediate rerouting recommended. "
                "Multiple high-severity risks detected. "
                "Consider alternative routes or delay shipment."
            )
        elif risk_level == RiskLevel.HIGH:
            primary_risk = self._get_primary_risk_category(breakdown)
            return (
                f"HIGH RISK: Consider rerouting. "
                f"Primary concern: {primary_risk}. "
                "Monitor closely and prepare alternative routes."
            )
        elif risk_level == RiskLevel.MEDIUM:
            return (
                "MEDIUM RISK: Monitor route conditions. "
                "Some risks present but manageable. "
                "Have contingency plans ready."
            )
        else:
            return (
                "LOW RISK: Route appears safe. "
                "Continue monitoring for any changes in conditions."
            )
    
    def _get_primary_risk_category(self, breakdown: RiskBreakdown) -> str:
        """Get primary risk category"""
        categories = {
            "Trade News": breakdown.trade_news,
            "Political": breakdown.political,
            "Port Congestion": breakdown.port_congestion
        }
        return max(categories.items(), key=lambda x: x[1])[0]
    
    def _calculate_confidence(self, risk_data: List[RiskDataPoint]) -> float:
        """Calculate confidence in assessment based on data quality"""
        if not risk_data:
            return 0.3  # Low confidence with no data
        
        # Base confidence on number of data points
        data_points_score = min(1.0, len(risk_data) / 10)
        
        # Check data recency (more recent = higher confidence)
        now = datetime.now()
        recent_data = [
            d for d in risk_data
            if (now - d.timestamp).total_seconds() < 86400  # Within 24 hours
        ]
        recency_score = min(1.0, len(recent_data) / 5)
        
        # Average the scores
        confidence = (data_points_score * 0.6 + recency_score * 0.4)
        
        return round(confidence, 2)
    
    def compare_routes(
        self,
        routes: List[Tuple[str, str, Optional[List[str]]]]
    ) -> List[RiskAssessment]:
        """Compare risk across multiple routes"""
        assessments = []
        
        for origin, destination, regions in routes:
            assessment = self.assess_route_risk(
                origin=origin,
                destination=destination,
                route_regions=regions
            )
            assessments.append(assessment)
        
        # Sort by risk score (lowest first)
        assessments.sort(key=lambda x: x.overall_risk_score)
        
        return assessments


# Global tool instance
_tool_instance: Optional[RiskAssessmentTool] = None


def get_risk_tool() -> RiskAssessmentTool:
    """Get or create the global risk assessment tool instance"""
    global _tool_instance
    if _tool_instance is None:
        _tool_instance = RiskAssessmentTool()
    return _tool_instance

