"""Predictive scoring tool using Vertex AI to predict risk levels 3-7 days ahead"""

import logging
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from agent.config import Config
from agent.data_ingestion import RiskDataPoint, get_data_ingestion_service
from agent.tools.risk_tool import RiskAssessment, RiskLevel, get_risk_tool

logger = logging.getLogger(__name__)


@dataclass
class PredictiveScore:
    """Predictive risk score for a future time period"""
    days_ahead: int  # 3, 5, or 7 days
    predicted_risk_score: float  # 0.0 to 1.0
    predicted_risk_level: RiskLevel
    confidence: float  # 0.0 to 1.0
    trend: str  # "increasing", "decreasing", "stable"
    factors: List[str]  # Key factors influencing prediction
    prediction_timestamp: datetime = field(default_factory=datetime.now)
    target_date: datetime = field(default_factory=datetime.now)


@dataclass
class PredictiveAssessment:
    """Complete predictive assessment for a route"""
    route_id: Optional[str]
    origin: str
    destination: str
    current_risk_score: float
    predictions: List[PredictiveScore]  # For 3, 5, 7 days
    overall_trend: str
    recommendation: str
    assessment_timestamp: datetime = field(default_factory=datetime.now)


class PredictiveScoringTool:
    """Tool for predicting future risk levels using Vertex AI"""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize predictive scoring tool"""
        self.config = config or Config()
        self.data_service = get_data_ingestion_service()
        self.risk_tool = get_risk_tool()
        self._vertex_ai_available = False
        self._initialize_vertex_ai()
    
    def _initialize_vertex_ai(self):
        """Initialize Vertex AI client"""
        try:
            import vertexai
            from vertexai.generative_models import GenerativeModel
            
            vertexai.init(
                project=self.config.GOOGLE_CLOUD_PROJECT,
                location=self.config.GOOGLE_CLOUD_LOCATION
            )
            
            self.model = GenerativeModel("gemini-2.0-flash-exp")
            self._vertex_ai_available = True
            logger.info("Vertex AI initialized successfully")
        except ImportError:
            logger.warning("Vertex AI not available. Using statistical prediction fallback.")
            self._vertex_ai_available = False
        except Exception as e:
            logger.warning(f"Failed to initialize Vertex AI: {e}. Using fallback.")
            self._vertex_ai_available = False
    
    def predict_route_risk(
        self,
        origin: str,
        destination: str,
        route_regions: Optional[List[str]] = None,
        route_id: Optional[str] = None,
        days_ahead: Optional[List[int]] = None
    ) -> PredictiveAssessment:
        """Predict risk levels for a route 3-7 days ahead"""
        # Get current risk assessment
        current_assessment = self.risk_tool.assess_route_risk(
            origin=origin,
            destination=destination,
            route_regions=route_regions,
            route_id=route_id
        )
        
        # Get historical risk data
        historical_data = self._get_historical_risk_data(
            origin=origin,
            destination=destination,
            route_regions=route_regions
        )
        
        # Default to 3, 5, 7 days if not specified
        if days_ahead is None:
            days_ahead = [3, 5, 7]
        
        # Generate predictions for each time horizon
        predictions = []
        for days in days_ahead:
            prediction = self._predict_risk_for_horizon(
                current_assessment=current_assessment,
                historical_data=historical_data,
                days_ahead=days,
                origin=origin,
                destination=destination
            )
            predictions.append(prediction)
        
        # Determine overall trend
        overall_trend = self._determine_overall_trend(predictions)
        
        # Generate recommendation
        recommendation = self._generate_predictive_recommendation(
            current_assessment, predictions, overall_trend
        )
        
        return PredictiveAssessment(
            route_id=route_id,
            origin=origin,
            destination=destination,
            current_risk_score=current_assessment.overall_risk_score,
            predictions=predictions,
            overall_trend=overall_trend,
            recommendation=recommendation
        )
    
    def _get_historical_risk_data(
        self,
        origin: str,
        destination: str,
        route_regions: Optional[List[str]]
    ) -> List[RiskDataPoint]:
        """Get historical risk data for analysis"""
        # Fetch current data (in production, this would fetch historical data)
        # For MVP, we'll use current data and simulate historical patterns
        current_data = self.data_service.fetch_risk_data_for_route(
            origin=origin,
            destination=destination,
            route_regions=route_regions
        )
        
        # In production, this would fetch data from a time series database
        # For MVP, we'll use current data as baseline
        return current_data
    
    def _predict_risk_for_horizon(
        self,
        current_assessment: RiskAssessment,
        historical_data: List[RiskDataPoint],
        days_ahead: int,
        origin: str,
        destination: str
    ) -> PredictiveScore:
        """Predict risk for a specific time horizon"""
        if self._vertex_ai_available:
            return self._predict_with_vertex_ai(
                current_assessment, historical_data, days_ahead, origin, destination
            )
        else:
            return self._predict_statistical(
                current_assessment, historical_data, days_ahead
            )
    
    def _predict_with_vertex_ai(
        self,
        current_assessment: RiskAssessment,
        historical_data: List[RiskDataPoint],
        days_ahead: int,
        origin: str,
        destination: str
    ) -> PredictiveScore:
        """Use Vertex AI (Gemini) to predict future risk"""
        try:
            # Prepare context for Gemini
            context = self._prepare_prediction_context(
                current_assessment, historical_data, days_ahead, origin, destination
            )
            
            # Create prediction prompt
            prompt = self._create_prediction_prompt(context, days_ahead)
            
            # Generate prediction using Gemini
            response = self.model.generate_content(prompt)
            
            # Parse Gemini response
            prediction = self._parse_gemini_response(
                response.text, current_assessment, days_ahead
            )
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error in Vertex AI prediction: {e}")
            # Fallback to statistical prediction
            return self._predict_statistical(
                current_assessment, historical_data, days_ahead
            )
    
    def _prepare_prediction_context(
        self,
        current_assessment: RiskAssessment,
        historical_data: List[RiskDataPoint],
        days_ahead: int,
        origin: str,
        destination: str
    ) -> Dict[str, Any]:
        """Prepare context for AI prediction"""
        # Summarize current risk factors
        current_factors = [
            f"{f['category']}: {f['title']} (severity: {f['severity']:.2f})"
            for f in current_assessment.contributing_factors[:5]
        ]
        
        # Summarize historical patterns
        recent_high_severity = [
            d for d in historical_data
            if d.severity > 0.6 and (datetime.now() - d.timestamp).days < 7
        ]
        
        return {
            "current_risk_score": current_assessment.overall_risk_score,
            "current_risk_level": current_assessment.risk_level.value,
            "current_factors": current_factors,
            "recent_high_severity_events": len(recent_high_severity),
            "breakdown": {
                "trade_news": current_assessment.breakdown.trade_news,
                "political": current_assessment.breakdown.political,
                "port_congestion": current_assessment.breakdown.port_congestion
            },
            "route": f"{origin} → {destination}",
            "days_ahead": days_ahead
        }
    
    def _create_prediction_prompt(self, context: Dict[str, Any], days_ahead: int) -> str:
        """Create prompt for Gemini prediction"""
        prompt = f"""You are a supply chain risk prediction expert. Analyze the following risk data and predict the risk level {days_ahead} days into the future.

Current Risk Assessment:
- Overall Risk Score: {context['current_risk_score']:.2f}
- Risk Level: {context['current_risk_level']}
- Route: {context['route']}

Current Risk Factors:
{chr(10).join(f"- {f}" for f in context['current_factors'])}

Risk Breakdown:
- Trade News Risk: {context['breakdown']['trade_news']:.2f}
- Political Risk: {context['breakdown']['political']:.2f}
- Port Congestion Risk: {context['breakdown']['port_congestion']:.2f}

Recent High-Severity Events (last 7 days): {context['recent_high_severity_events']}

Based on this data, predict the risk level {days_ahead} days from now. Consider:
1. Current trends and patterns
2. Historical risk patterns for similar routes
3. Geopolitical and trade dynamics
4. Port congestion patterns

Provide your prediction in the following JSON format:
{{
    "predicted_risk_score": <float between 0.0 and 1.0>,
    "confidence": <float between 0.0 and 1.0>,
    "trend": "<increasing|decreasing|stable>",
    "key_factors": ["factor1", "factor2", "factor3"]
}}

Be specific and data-driven in your prediction."""
        
        return prompt
    
    def _parse_gemini_response(
        self,
        response_text: str,
        current_assessment: RiskAssessment,
        days_ahead: int
    ) -> PredictiveScore:
        """Parse Gemini response into PredictiveScore"""
        import json
        import re
        
        try:
            # Extract JSON from response
            json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
            if json_match:
                prediction_data = json.loads(json_match.group())
            else:
                # Fallback: try to parse the whole response
                prediction_data = json.loads(response_text)
            
            predicted_score = float(prediction_data.get("predicted_risk_score", 0.5))
            confidence = float(prediction_data.get("confidence", 0.7))
            trend = prediction_data.get("trend", "stable")
            factors = prediction_data.get("key_factors", [])
            
            # Determine risk level
            if predicted_score >= 0.75:
                risk_level = RiskLevel.CRITICAL
            elif predicted_score >= 0.50:
                risk_level = RiskLevel.HIGH
            elif predicted_score >= 0.25:
                risk_level = RiskLevel.MEDIUM
            else:
                risk_level = RiskLevel.LOW
            
            target_date = datetime.now() + timedelta(days=days_ahead)
            
            return PredictiveScore(
                days_ahead=days_ahead,
                predicted_risk_score=round(predicted_score, 3),
                predicted_risk_level=risk_level,
                confidence=round(confidence, 2),
                trend=trend,
                factors=factors,
                target_date=target_date
            )
            
        except Exception as e:
            logger.error(f"Error parsing Gemini response: {e}")
            # Fallback to statistical prediction
            return self._predict_statistical(
                current_assessment, [], days_ahead
            )
    
    def _predict_statistical(
        self,
        current_assessment: RiskAssessment,
        historical_data: List[RiskDataPoint],
        days_ahead: int
    ) -> PredictiveScore:
        """Statistical prediction fallback (when Vertex AI unavailable)"""
        current_score = current_assessment.overall_risk_score
        
        # Simple trend analysis based on recent data
        if historical_data:
            recent_scores = [d.severity for d in historical_data[:10]]
            avg_recent = sum(recent_scores) / len(recent_scores) if recent_scores else current_score
            
            # Calculate trend
            if avg_recent > current_score * 1.1:
                trend = "increasing"
                predicted_score = min(1.0, current_score * 1.15)
            elif avg_recent < current_score * 0.9:
                trend = "decreasing"
                predicted_score = max(0.0, current_score * 0.85)
            else:
                trend = "stable"
                predicted_score = current_score
        else:
            trend = "stable"
            predicted_score = current_score
        
        # Apply time decay (uncertainty increases with time)
        time_factor = 1.0 - (days_ahead * 0.02)  # 2% uncertainty per day
        predicted_score = current_score * time_factor + (predicted_score * (1 - time_factor))
        
        # Determine risk level
        if predicted_score >= 0.75:
            risk_level = RiskLevel.CRITICAL
        elif predicted_score >= 0.50:
            risk_level = RiskLevel.HIGH
        elif predicted_score >= 0.25:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW
        
        # Extract key factors
        factors = [
            f["title"] for f in current_assessment.contributing_factors[:3]
        ]
        
        # Lower confidence for statistical predictions
        confidence = max(0.5, 0.8 - (days_ahead * 0.05))
        
        target_date = datetime.now() + timedelta(days=days_ahead)
        
        return PredictiveScore(
            days_ahead=days_ahead,
            predicted_risk_score=round(predicted_score, 3),
            predicted_risk_level=risk_level,
            confidence=round(confidence, 2),
            trend=trend,
            factors=factors,
            target_date=target_date
        )
    
    def _determine_overall_trend(self, predictions: List[PredictiveScore]) -> str:
        """Determine overall trend from multiple predictions"""
        if not predictions:
            return "stable"
        
        trends = [p.trend for p in predictions]
        increasing_count = trends.count("increasing")
        decreasing_count = trends.count("decreasing")
        
        if increasing_count > decreasing_count:
            return "increasing"
        elif decreasing_count > increasing_count:
            return "decreasing"
        else:
            return "stable"
    
    def _generate_predictive_recommendation(
        self,
        current_assessment: RiskAssessment,
        predictions: List[PredictiveScore],
        overall_trend: str
    ) -> str:
        """Generate recommendation based on predictions"""
        # Get worst-case prediction
        worst_prediction = max(predictions, key=lambda p: p.predicted_risk_score)
        
        if worst_prediction.predicted_risk_level == RiskLevel.CRITICAL:
            return (
                f"CRITICAL RISK PREDICTED: Risk is predicted to reach critical levels "
                f"({worst_prediction.predicted_risk_score:.2f}) in {worst_prediction.days_ahead} days. "
                f"Immediate action required. Consider rerouting or delaying shipment."
            )
        elif worst_prediction.predicted_risk_level == RiskLevel.HIGH:
            if overall_trend == "increasing":
                return (
                    f"HIGH RISK TREND: Risk is increasing and predicted to reach "
                    f"{worst_prediction.predicted_risk_score:.2f} in {worst_prediction.days_ahead} days. "
                    f"Prepare alternative routes and monitor closely."
                )
            else:
                return (
                    f"MODERATE RISK: Risk predicted to remain manageable. "
                    f"Monitor conditions and have contingency plans ready."
                )
        elif overall_trend == "decreasing":
            return (
                f"POSITIVE TREND: Risk is decreasing. Current risk should improve over time. "
                f"Continue monitoring but conditions appear favorable."
            )
        else:
            return (
                f"STABLE CONDITIONS: Risk levels predicted to remain relatively stable. "
                f"Continue standard monitoring procedures."
            )


# Global tool instance
_tool_instance: Optional[PredictiveScoringTool] = None


def get_predictive_scoring_tool() -> PredictiveScoringTool:
    """Get or create the global predictive scoring tool instance"""
    global _tool_instance
    if _tool_instance is None:
        _tool_instance = PredictiveScoringTool()
    return _tool_instance

