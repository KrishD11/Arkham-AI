"""Route optimization tool that balances risk, cost, and time"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from agent.tools.risk_tool import RiskAssessment, get_risk_tool
from agent.tools.score_tool import PredictiveAssessment, get_predictive_scoring_tool

logger = logging.getLogger(__name__)


class OptimizationPriority(Enum):
    """Optimization priority"""
    RISK = "risk"  # Minimize risk
    COST = "cost"  # Minimize cost
    TIME = "time"  # Minimize time
    BALANCED = "balanced"  # Balance all factors


@dataclass
class RouteMetrics:
    """Metrics for a route"""
    risk_score: float  # 0.0 to 1.0
    cost_usd: float  # Cost in USD
    time_days: float  # Transit time in days
    distance_km: float  # Distance in kilometers
    port_calls: int  # Number of port calls


@dataclass
class OptimizedRoute:
    """An optimized route option"""
    route_id: str
    origin: str
    destination: str
    waypoints: List[str]  # Intermediate ports/waypoints
    metrics: RouteMetrics
    risk_assessment: RiskAssessment
    predictive_assessment: Optional[PredictiveAssessment] = None
    optimization_score: float = 0.0  # Overall optimization score
    rank: int = 0
    recommendation_reason: str = ""


@dataclass
class OptimizationResult:
    """Result of route optimization"""
    original_route: OptimizedRoute
    optimized_routes: List[OptimizedRoute]  # Ranked alternatives
    optimization_criteria: Dict[str, float]  # Weights used
    optimization_timestamp: datetime = field(default_factory=datetime.now)
    recommendation: str = ""


class RouteOptimizationTool:
    """Tool for optimizing routes by balancing risk, cost, and time"""
    
    def __init__(self):
        """Initialize route optimization tool"""
        self.risk_tool = get_risk_tool()
        self.predictive_tool = get_predictive_scoring_tool()
        
        # Default optimization weights
        self.default_weights = {
            "risk": 0.50,
            "cost": 0.30,
            "time": 0.20
        }
        
        # Route database (mock for MVP - in production would be real database)
        self._route_database = self._initialize_route_database()
    
    def optimize_route(
        self,
        origin: str,
        destination: str,
        priority: OptimizationPriority = OptimizationPriority.BALANCED,
        custom_weights: Optional[Dict[str, float]] = None,
        include_predictions: bool = True,
        max_alternatives: int = 5
    ) -> OptimizationResult:
        """Optimize route with alternatives"""
        # Get optimization weights
        weights = self._get_optimization_weights(priority, custom_weights)
        
        # Assess original route
        original_route = self._assess_route(origin, destination, "ORIGINAL")
        
        # Generate alternative routes
        alternatives = self._generate_alternative_routes(origin, destination)
        
        # Assess all alternatives
        assessed_routes = []
        for alt_route in alternatives:
            assessed = self._assess_route(
                alt_route["origin"],
                alt_route["destination"],
                alt_route["route_id"],
                waypoints=alt_route.get("waypoints", []),
                route_regions=alt_route.get("route_regions", []),
                metrics=alt_route.get("metrics", {})
            )
            assessed_routes.append(assessed)
        
        # Calculate optimization scores
        for route in [original_route] + assessed_routes:
            route.optimization_score = self._calculate_optimization_score(
                route, weights
            )
        
        # Rank routes by optimization score (lower is better)
        all_routes = [original_route] + assessed_routes
        all_routes.sort(key=lambda r: r.optimization_score)
        
        # Add rankings
        for idx, route in enumerate(all_routes, 1):
            route.rank = idx
        
        # Get top alternatives (excluding original)
        optimized_routes = [
            r for r in all_routes if r.route_id != "ORIGINAL"
        ][:max_alternatives]
        
        # Generate recommendations
        recommendation = self._generate_optimization_recommendation(
            original_route, optimized_routes, weights
        )
        
        return OptimizationResult(
            original_route=original_route,
            optimized_routes=optimized_routes,
            optimization_criteria=weights,
            recommendation=recommendation
        )
    
    def _assess_route(
        self,
        origin: str,
        destination: str,
        route_id: str,
        waypoints: Optional[List[str]] = None,
        route_regions: Optional[List[str]] = None,
        metrics: Optional[Dict[str, Any]] = None
    ) -> OptimizedRoute:
        """Assess a route with risk and metrics"""
        # Build comprehensive route regions list
        all_regions = list(route_regions) if route_regions else []
        
        # Extract regions from waypoints
        if waypoints:
            for waypoint in waypoints:
                # Extract region from waypoint name
                waypoint_lower = waypoint.lower()
                if 'vietnam' in waypoint_lower or 'ho chi minh' in waypoint_lower:
                    all_regions.append('vietnam')
                elif 'japan' in waypoint_lower or 'tokyo' in waypoint_lower:
                    all_regions.append('japan')
                elif 'singapore' in waypoint_lower:
                    all_regions.append('singapore')
                elif 'shanghai' in waypoint_lower or 'china' in waypoint_lower:
                    all_regions.append('china')
                elif 'taiwan' in waypoint_lower or 'taipei' in waypoint_lower:
                    all_regions.append('taiwan')
        
        # Remove duplicates
        all_regions = list(set(all_regions))
        
        # Get risk assessment with specific regions
        risk_assessment = self.risk_tool.assess_route_risk(
            origin=origin,
            destination=destination,
            route_regions=all_regions if all_regions else None,
            route_id=route_id
        )
        
        # Get predictive assessment (optional)
        predictive_assessment = None
        try:
            predictive_assessment = self.predictive_tool.predict_route_risk(
                origin=origin,
                destination=destination,
                route_regions=all_regions if all_regions else None,
                route_id=route_id,
                days_ahead=[3, 5, 7]
            )
        except Exception as e:
            logger.warning(f"Could not get predictive assessment: {e}")
        
        # Get or calculate metrics
        if metrics:
            route_metrics = RouteMetrics(
                risk_score=risk_assessment.overall_risk_score,
                cost_usd=metrics.get("cost_usd", 0.0),
                time_days=metrics.get("time_days", 0.0),
                distance_km=metrics.get("distance_km", 0.0),
                port_calls=metrics.get("port_calls", 0)
            )
        else:
            route_metrics = self._estimate_route_metrics(
                origin, destination, waypoints or []
            )
            # Update risk score from assessment
            route_metrics.risk_score = risk_assessment.overall_risk_score
        
        return OptimizedRoute(
            route_id=route_id,
            origin=origin,
            destination=destination,
            waypoints=waypoints or [],
            metrics=route_metrics,
            risk_assessment=risk_assessment,
            predictive_assessment=predictive_assessment
        )
    
    def _estimate_route_metrics(
        self,
        origin: str,
        destination: str,
        waypoints: List[str]
    ) -> RouteMetrics:
        """Estimate route metrics (mock for MVP)"""
        # Base distance estimates (mock data)
        base_distances = {
            ("Taiwan", "Los Angeles"): 11000,
            ("Vietnam", "Los Angeles"): 12000,
            ("Japan", "Los Angeles"): 9000,
            ("Singapore", "Los Angeles"): 14000,
        }
        
        # Estimate distance
        key = (origin, destination)
        base_distance = base_distances.get(key, 10000)
        
        # Add distance for waypoints
        waypoint_distance = len(waypoints) * 500
        total_distance = base_distance + waypoint_distance
        
        # Estimate time (assuming ~20 knots average speed)
        time_days = (total_distance / 1852) / 20 / 24  # Convert km to nautical miles
        
        # Estimate cost (mock: $1000 per 1000km base + $500 per port call)
        base_cost = (total_distance / 1000) * 1000
        port_cost = (len(waypoints) + 2) * 500  # Origin + destination + waypoints
        total_cost = base_cost + port_cost
        
        return RouteMetrics(
            risk_score=0.0,  # Will be set by risk assessment
            cost_usd=total_cost,
            time_days=time_days,
            distance_km=total_distance,
            port_calls=len(waypoints) + 2
        )
    
    def _generate_alternative_routes(
        self,
        origin: str,
        destination: str
    ) -> List[Dict[str, Any]]:
        """Generate alternative routes based on common shipping patterns"""
        # Extract port names for matching
        origin_lower = origin.lower()
        dest_lower = destination.lower()
        
        # Common alternative routes based on origin/destination patterns
        alternatives_map = {
            ("taiwan", "los angeles"): [
                {
                    "route_id": "TW-VN-LA",
                    "origin": origin,  # Keep original origin
                    "destination": destination,  # Keep original destination
                    "waypoints": ["Port of Ho Chi Minh City, Vietnam"],
                    "route_regions": ["taiwan", "vietnam", "south china sea", "pacific"],
                    "metrics": {
                        "cost_usd": 15000,
                        "time_days": 15,
                        "distance_km": 12000,
                        "port_calls": 3
                    }
                },
                {
                    "route_id": "TW-JP-LA",
                    "origin": origin,
                    "destination": destination,
                    "waypoints": ["Port of Tokyo, Japan"],
                    "route_regions": ["taiwan", "japan", "pacific"],
                    "metrics": {
                        "cost_usd": 25000,
                        "time_days": 16,
                        "distance_km": 11000,
                        "port_calls": 3
                    }
                },
                {
                    "route_id": "TW-SG-LA",
                    "origin": origin,
                    "destination": destination,
                    "waypoints": ["Port of Singapore, Singapore"],
                    "route_regions": ["taiwan", "singapore", "south china sea", "pacific"],
                    "metrics": {
                        "cost_usd": 18000,
                        "time_days": 17,
                        "distance_km": 14000,
                        "port_calls": 3
                    }
                },
                {
                    "route_id": "TW-SH-LA",
                    "origin": origin,
                    "destination": destination,
                    "waypoints": ["Port of Shanghai, China"],
                    "route_regions": ["taiwan", "china", "pacific"],
                    "metrics": {
                        "cost_usd": 12000,
                        "time_days": 16,
                        "distance_km": 11500,
                        "port_calls": 3
                    }
                },
            ]
        }
        
        # Try to find matching routes
        for (orig_key, dest_key), routes in alternatives_map.items():
            if orig_key in origin_lower and dest_key in dest_lower:
                return routes
        
        # Generic alternatives if no specific match
        return [
            {
                "route_id": f"ALT-{i:03d}",
                "origin": origin,
                "destination": destination,
                "waypoints": [],
                "route_regions": [],
                "metrics": {
                    "cost_usd": 10000 + (i * 2000),
                    "time_days": 14 + i,
                    "distance_km": 10000 + (i * 500),
                    "port_calls": 2
                }
            }
            for i in range(1, 4)
        ]
    
    def _get_optimization_weights(
        self,
        priority: OptimizationPriority,
        custom_weights: Optional[Dict[str, float]]
    ) -> Dict[str, float]:
        """Get optimization weights based on priority"""
        if custom_weights:
            # Normalize custom weights
            total = sum(custom_weights.values())
            return {k: v / total for k, v in custom_weights.items()}
        
        if priority == OptimizationPriority.RISK:
            return {"risk": 0.70, "cost": 0.15, "time": 0.15}
        elif priority == OptimizationPriority.COST:
            return {"risk": 0.20, "cost": 0.60, "time": 0.20}
        elif priority == OptimizationPriority.TIME:
            return {"risk": 0.20, "cost": 0.20, "time": 0.60}
        else:  # BALANCED
            return self.default_weights.copy()
    
    def _calculate_optimization_score(
        self,
        route: OptimizedRoute,
        weights: Dict[str, float]
    ) -> float:
        """Calculate overall optimization score (lower is better)"""
        # Normalize metrics to 0-1 scale
        # Risk is already 0-1
        normalized_risk = route.metrics.risk_score
        
        # Normalize cost (assuming max $50000, min $5000)
        max_cost = 50000
        min_cost = 5000
        normalized_cost = min(1.0, max(0.0, 
            (route.metrics.cost_usd - min_cost) / (max_cost - min_cost)
        ))
        
        # Normalize time (assuming max 30 days, min 10 days)
        max_time = 30
        min_time = 10
        normalized_time = min(1.0, max(0.0,
            (route.metrics.time_days - min_time) / (max_time - min_time)
        ))
        
        # Calculate weighted score
        score = (
            normalized_risk * weights.get("risk", 0.5) +
            normalized_cost * weights.get("cost", 0.3) +
            normalized_time * weights.get("time", 0.2)
        )
        
        return round(score, 4)
    
    def _generate_optimization_recommendation(
        self,
        original_route: OptimizedRoute,
        optimized_routes: List[OptimizedRoute],
        weights: Dict[str, float]
    ) -> str:
        """Generate optimization recommendation using AI agent"""
        if not optimized_routes:
            return "No alternative routes found. Current route is the only option."
        
        best_alternative = optimized_routes[0]
        
        # Calculate improvements
        risk_improvement = original_route.metrics.risk_score - best_alternative.metrics.risk_score
        cost_delta = best_alternative.metrics.cost_usd - original_route.metrics.cost_usd
        time_delta = best_alternative.metrics.time_days - original_route.metrics.time_days
        
        # Use AI agent for intelligent recommendation
        try:
            from agent.adk_agent import get_agent
            
            agent = get_agent()
            
            # Build context for AI agent
            route_comparison = f"""
Original Route: {original_route.origin} -> {original_route.destination}
- Risk Score: {original_route.metrics.risk_score:.2f}
- Cost: ${original_route.metrics.cost_usd:,.0f}
- Time: {original_route.metrics.time_days:.1f} days
- Risk Breakdown: Trade News: {original_route.risk_assessment.breakdown.trade_news:.2f}, Political: {original_route.risk_assessment.breakdown.political:.2f}, Port Congestion: {original_route.risk_assessment.breakdown.port_congestion:.2f}

Best Alternative Route: {best_alternative.origin} -> {best_alternative.destination}
- Risk Score: {best_alternative.metrics.risk_score:.2f}
- Cost: ${best_alternative.metrics.cost_usd:,.0f}
- Time: {best_alternative.metrics.time_days:.1f} days
- Risk Breakdown: Trade News: {best_alternative.risk_assessment.breakdown.trade_news:.2f}, Political: {best_alternative.risk_assessment.breakdown.political:.2f}, Port Congestion: {best_alternative.risk_assessment.breakdown.port_congestion:.2f}
- Waypoints: {', '.join(best_alternative.waypoints) if best_alternative.waypoints else 'None'}

Risk Improvement: {risk_improvement:.2f} ({risk_improvement*100:.1f}% reduction)
Cost Impact: ${cost_delta:+,.0f}
Time Impact: {time_delta:+.1f} days

Contributing Risk Factors:
{chr(10).join([f"- {f['title']}: {f['description'][:100]} (Severity: {f['severity']:.2f})" for f in best_alternative.risk_assessment.contributing_factors[:3]])}
"""
            
            prompt = f"""Analyze these shipping routes and provide a recommendation:

{route_comparison}

Based on the risk assessment, cost, and time analysis, should we reroute? Provide a clear, concise recommendation (2-3 sentences) explaining:
1. Whether to reroute or stay on current route
2. Key reasons (risk reduction, cost/time tradeoffs)
3. Any important considerations

Be specific about the risk factors and why the alternative is better or worse."""
            
            ai_response = agent.query(prompt)
            
            if ai_response.get("success") and ai_response.get("response"):
                return ai_response["response"]
            else:
                logger.warning("AI agent query failed, using fallback recommendation")
                # Fallback to rule-based recommendation
                return self._generate_fallback_recommendation(
                    original_route, best_alternative, risk_improvement, cost_delta, time_delta
                )
                
        except Exception as e:
            logger.warning(f"Could not get AI recommendation: {e}")
            # Fallback to rule-based recommendation
            return self._generate_fallback_recommendation(
                original_route, best_alternative, risk_improvement, cost_delta, time_delta
            )
    
    def _generate_fallback_recommendation(
        self,
        original_route: OptimizedRoute,
        best_alternative: OptimizedRoute,
        risk_improvement: float,
        cost_delta: float,
        time_delta: float
    ) -> str:
        """Generate fallback recommendation when AI is unavailable"""
        if risk_improvement > 0.2:  # Significant risk reduction
            return (
                f"STRONGLY RECOMMENDED: Reroute via {best_alternative.origin}. "
                f"Risk reduction: {risk_improvement:.2f} ({original_route.metrics.risk_score:.2f} → {best_alternative.metrics.risk_score:.2f}). "
                f"Cost impact: ${cost_delta:+,.0f}. Time impact: {time_delta:+.1f} days."
            )
        elif risk_improvement > 0.1:  # Moderate risk reduction
            return (
                f"RECOMMENDED: Consider rerouting via {best_alternative.origin}. "
                f"Risk reduction: {risk_improvement:.2f}. "
                f"Cost impact: ${cost_delta:+,.0f}. Time impact: {time_delta:+.1f} days."
            )
        elif best_alternative.optimization_score < original_route.optimization_score:
            return (
                f"OPTIONAL: Alternative route via {best_alternative.origin} offers better overall optimization. "
                f"Risk: {best_alternative.metrics.risk_score:.2f} vs {original_route.metrics.risk_score:.2f}. "
                f"Cost: ${best_alternative.metrics.cost_usd:,.0f} vs ${original_route.metrics.cost_usd:,.0f}. "
                f"Time: {best_alternative.metrics.time_days:.1f} vs {original_route.metrics.time_days:.1f} days."
            )
        else:
            return (
                "CURRENT ROUTE OPTIMAL: Current route appears to be the best option "
                "based on the selected optimization criteria."
            )
    
    def _initialize_route_database(self) -> Dict[str, Any]:
        """Initialize mock route database"""
        # In production, this would connect to a real database
        return {
            "routes": [],
            "ports": [],
            "distances": {}
        }
    
    def compare_routes_detailed(
        self,
        routes: List[Tuple[str, str, Optional[List[str]]]]
    ) -> List[OptimizedRoute]:
        """Compare multiple routes in detail"""
        optimized_routes = []
        
        for idx, (origin, destination, regions) in enumerate(routes, 1):
            route = self._assess_route(
                origin=origin,
                destination=destination,
                route_id=f"COMPARE-{idx:03d}",
                route_regions=regions or []
            )
            optimized_routes.append(route)
        
        # Sort by risk score
        optimized_routes.sort(key=lambda r: r.metrics.risk_score)
        
        return optimized_routes


# Global tool instance
_tool_instance: Optional[RouteOptimizationTool] = None


def get_route_optimization_tool() -> RouteOptimizationTool:
    """Get or create the global route optimization tool instance"""
    global _tool_instance
    if _tool_instance is None:
        _tool_instance = RouteOptimizationTool()
    return _tool_instance

