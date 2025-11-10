"""Flask application entry point for Arkham AI agent"""

import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from agent.config import Config
from agent.adk_agent import get_agent
from agent.data_ingestion import get_data_ingestion_service
from agent.database import get_database_service
from agent.tools.risk_tool import get_risk_tool
from agent.tools.score_tool import get_predictive_scoring_tool
from agent.tools.route_tool import get_route_optimization_tool, OptimizationPriority
from agent.tools.exec_tool import get_execution_tool, ExecutionMode
from agent.tools.log_tool import get_logging_tool, LogCategory, LogLevel
from agent.policy import get_acled_auth_policy

app = Flask(__name__)
CORS(app)

# Load configuration
app.config.from_object(Config)

# Initialize ADK agent
agent = get_agent()

# Initialize data ingestion service
data_service = get_data_ingestion_service()

# Initialize risk assessment tool
risk_tool = get_risk_tool()

# Initialize predictive scoring tool
predictive_tool = get_predictive_scoring_tool()

# Initialize route optimization tool
route_optimization_tool = get_route_optimization_tool()

# Initialize autonomous execution tool
execution_tool = get_execution_tool()

# Initialize logging tool
logging_tool = get_logging_tool()

# Initialize database service
db_service = get_database_service()


# Frontend static files serving
FRONTEND_DIST_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'dist')

@app.route("/", methods=["GET"])
def index():
    """Serve frontend index.html"""
    if os.path.exists(FRONTEND_DIST_PATH):
        return send_from_directory(FRONTEND_DIST_PATH, 'index.html')
    return jsonify({
        "status": "healthy",
        "service": Config.AGENT_NAME,
        "version": "0.1.0",
        "note": "Frontend not found, serving API only"
    })

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": Config.AGENT_NAME,
        "version": "0.1.0"
    })

@app.route("/<path:path>")
def serve_frontend(path):
    """Serve frontend static files"""
    if os.path.exists(FRONTEND_DIST_PATH):
        # Check if it's an API route
        if path.startswith('api/'):
            # Let Flask handle API routes
            return app.handle_request()
        
        # Serve static files
        if os.path.exists(os.path.join(FRONTEND_DIST_PATH, path)):
            return send_from_directory(FRONTEND_DIST_PATH, path)
        
        # For SPA routing, serve index.html
        return send_from_directory(FRONTEND_DIST_PATH, 'index.html')
    
    # Fallback if frontend not found
    return jsonify({"error": "Frontend not found"}), 404


@app.route("/api/health", methods=["GET"])
def api_health():
    """API health check"""
    return jsonify({
        "status": "ok",
        "message": f"{Config.AGENT_NAME} agent is running"
    })


@app.route("/api/agent/query", methods=["POST"])
def agent_query():
    """Query the Arkham AI agent"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        message = data.get("message")
        if not message:
            return jsonify({
                "success": False,
                "error": "Missing 'message' field in request"
            }), 400
        
        user_id = data.get("user_id", "anonymous")
        
        # Query the agent
        result = agent.query(message, user_id=user_id)
        
        return jsonify(result), 200 if result.get("success") else 500
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/agent/info", methods=["GET"])
def agent_info():
    """Get agent information"""
    return jsonify(agent.get_agent_info())


@app.route("/api/data/trade-news", methods=["GET"])
def get_trade_news():
    """Get trade news data"""
    try:
        region = request.args.get("region")
        limit = int(request.args.get("limit", 50))
        
        data_points = data_service.fetch_trade_news(region=region, limit=limit)
        
        return jsonify({
            "success": True,
            "count": len(data_points),
            "data": [
                {
                    "source": dp.source,
                    "category": dp.category,
                    "title": dp.title,
                    "description": dp.description,
                    "severity": dp.severity,
                    "location": dp.location,
                    "timestamp": dp.timestamp.isoformat(),
                    "metadata": dp.metadata
                }
                for dp in data_points
            ]
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/data/political", methods=["GET"])
def get_political_data():
    """Get political instability data"""
    try:
        region = request.args.get("region")
        
        data_points = data_service.fetch_political_instability(region=region)
        
        return jsonify({
            "success": True,
            "count": len(data_points),
            "data": [
                {
                    "source": dp.source,
                    "category": dp.category,
                    "title": dp.title,
                    "description": dp.description,
                    "severity": dp.severity,
                    "location": dp.location,
                    "timestamp": dp.timestamp.isoformat(),
                    "metadata": dp.metadata
                }
                for dp in data_points
            ]
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/data/ports", methods=["GET"])
def get_port_data():
    """Get port congestion data"""
    try:
        port_code = request.args.get("port_code")
        
        data_points = data_service.fetch_port_congestion(port_code=port_code)
        
        return jsonify({
            "success": True,
            "count": len(data_points),
            "data": [
                {
                    "source": dp.source,
                    "category": dp.category,
                    "title": dp.title,
                    "description": dp.description,
                    "severity": dp.severity,
                    "location": dp.location,
                    "timestamp": dp.timestamp.isoformat(),
                    "metadata": dp.metadata
                }
                for dp in data_points
            ]
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/data/all", methods=["GET"])
def get_all_data():
    """Get all risk data from all sources"""
    try:
        region = request.args.get("region")
        port_code = request.args.get("port_code")
        
        data_points = data_service.fetch_all_risk_data(region=region, port_code=port_code)
        
        return jsonify({
            "success": True,
            "count": len(data_points),
            "data": [
                {
                    "source": dp.source,
                    "category": dp.category,
                    "title": dp.title,
                    "description": dp.description,
                    "severity": dp.severity,
                    "location": dp.location,
                    "timestamp": dp.timestamp.isoformat(),
                    "metadata": dp.metadata
                }
                for dp in data_points
            ]
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/data/route", methods=["POST"])
def get_route_data():
    """Get risk data for a specific shipping route"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        origin = data.get("origin")
        destination = data.get("destination")
        route_regions = data.get("route_regions", [])
        
        if not origin or not destination:
            return jsonify({
                "success": False,
                "error": "Missing 'origin' or 'destination' field"
            }), 400
        
        data_points = data_service.fetch_risk_data_for_route(
            origin=origin,
            destination=destination,
            route_regions=route_regions
        )
        
        return jsonify({
            "success": True,
            "count": len(data_points),
            "route": {
                "origin": origin,
                "destination": destination,
                "regions": route_regions
            },
            "data": [
                {
                    "source": dp.source,
                    "category": dp.category,
                    "title": dp.title,
                    "description": dp.description,
                    "severity": dp.severity,
                    "location": dp.location,
                    "timestamp": dp.timestamp.isoformat(),
                    "metadata": dp.metadata
                }
                for dp in data_points
            ]
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/routes/assess", methods=["POST"])
def assess_route_risk():
    """Assess risk for a shipping route"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        origin = data.get("origin")
        destination = data.get("destination")
        route_regions = data.get("route_regions", [])
        route_id = data.get("route_id")
        
        if not origin or not destination:
            return jsonify({
                "success": False,
                "error": "Missing 'origin' or 'destination' field"
            }), 400
        
        # Assess route risk
        assessment = risk_tool.assess_route_risk(
            origin=origin,
            destination=destination,
            route_regions=route_regions,
            route_id=route_id
        )
        
        return jsonify({
            "success": True,
            "assessment": {
                "route_id": assessment.route_id,
                "origin": assessment.origin,
                "destination": assessment.destination,
                "overall_risk_score": assessment.overall_risk_score,
                "risk_level": assessment.risk_level.value,
                "breakdown": {
                    "trade_news": assessment.breakdown.trade_news,
                    "political": assessment.breakdown.political,
                    "port_congestion": assessment.breakdown.port_congestion,
                    "total": assessment.breakdown.total
                },
                # Add factors for frontend compatibility
                "factors": {
                    "congestion": assessment.breakdown.port_congestion,
                    "tariffs": assessment.breakdown.trade_news,
                    "political_unrest": assessment.breakdown.political
                },
                "contributing_factors": assessment.contributing_factors,
                "recommendation": assessment.recommendation,
                "confidence": assessment.confidence,
                "assessment_timestamp": assessment.assessment_timestamp.isoformat()
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/routes/<route_id>/risk", methods=["GET"])
def get_route_risk(route_id: str):
    """Get risk assessment for a specific route by ID"""
    try:
        # For MVP, we'll need origin/destination from query params
        # In production, this would fetch route details from database
        origin = request.args.get("origin")
        destination = request.args.get("destination")
        route_regions = request.args.getlist("regions")
        
        if not origin or not destination:
            return jsonify({
                "success": False,
                "error": "Missing 'origin' or 'destination' query parameter"
            }), 400
        
        # Assess route risk
        assessment = risk_tool.assess_route_risk(
            origin=origin,
            destination=destination,
            route_regions=route_regions if route_regions else None,
            route_id=route_id
        )
        
        return jsonify({
            "success": True,
            "route_id": route_id,
            "assessment": {
                "overall_risk_score": assessment.overall_risk_score,
                "risk_level": assessment.risk_level.value,
                "breakdown": {
                    "trade_news": assessment.breakdown.trade_news,
                    "political": assessment.breakdown.political,
                    "port_congestion": assessment.breakdown.port_congestion,
                    "total": assessment.breakdown.total
                },
                "contributing_factors": assessment.contributing_factors,
                "recommendation": assessment.recommendation,
                "confidence": assessment.confidence,
                "assessment_timestamp": assessment.assessment_timestamp.isoformat()
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/routes/compare", methods=["POST"])
def compare_routes():
    """Compare risk across multiple routes"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        routes = data.get("routes", [])
        
        if not routes or len(routes) < 2:
            return jsonify({
                "success": False,
                "error": "At least 2 routes required for comparison"
            }), 400
        
        # Parse routes
        route_tuples = []
        for route in routes:
            origin = route.get("origin")
            destination = route.get("destination")
            regions = route.get("route_regions", [])
            
            if not origin or not destination:
                return jsonify({
                    "success": False,
                    "error": "Each route must have 'origin' and 'destination'"
                }), 400
            
            route_tuples.append((origin, destination, regions))
        
        # Compare routes
        assessments = risk_tool.compare_routes(route_tuples)
        
        return jsonify({
            "success": True,
            "comparison": [
                {
                    "origin": a.origin,
                    "destination": a.destination,
                    "overall_risk_score": a.overall_risk_score,
                    "risk_level": a.risk_level.value,
                    "breakdown": {
                        "trade_news": a.breakdown.trade_news,
                        "political": a.breakdown.political,
                        "port_congestion": a.breakdown.port_congestion,
                        "total": a.breakdown.total
                    },
                    "recommendation": a.recommendation,
                    "confidence": a.confidence
                }
                for a in assessments
            ]
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/routes/predict", methods=["POST"])
def predict_route_risk():
    """Predict risk levels 3-7 days ahead for a route"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        origin = data.get("origin")
        destination = data.get("destination")
        route_regions = data.get("route_regions", [])
        route_id = data.get("route_id")
        days_ahead = data.get("days_ahead", [3, 5, 7])  # Default to 3, 5, 7 days
        
        if not origin or not destination:
            return jsonify({
                "success": False,
                "error": "Missing 'origin' or 'destination' field"
            }), 400
        
        # Generate predictions
        prediction = predictive_tool.predict_route_risk(
            origin=origin,
            destination=destination,
            route_regions=route_regions,
            route_id=route_id,
            days_ahead=days_ahead
        )
        
        return jsonify({
            "success": True,
            "prediction": {
                "route_id": prediction.route_id,
                "origin": prediction.origin,
                "destination": prediction.destination,
                "current_risk_score": prediction.current_risk_score,
                "overall_trend": prediction.overall_trend,
                "recommendation": prediction.recommendation,
                "predictions": [
                    {
                        "days_ahead": p.days_ahead,
                        "predicted_risk_score": p.predicted_risk_score,
                        "predicted_risk_level": p.predicted_risk_level.value,
                        "confidence": p.confidence,
                        "trend": p.trend,
                        "key_factors": p.factors,
                        "target_date": p.target_date.isoformat()
                    }
                    for p in prediction.predictions
                ],
                "assessment_timestamp": prediction.assessment_timestamp.isoformat()
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/routes/<route_id>/predict", methods=["GET"])
def get_route_prediction(route_id: str):
    """Get predictive risk assessment for a specific route"""
    try:
        origin = request.args.get("origin")
        destination = request.args.get("destination")
        route_regions = request.args.getlist("regions")
        days_ahead_param = request.args.get("days_ahead", "3,5,7")
        
        if not origin or not destination:
            return jsonify({
                "success": False,
                "error": "Missing 'origin' or 'destination' query parameter"
            }), 400
        
        # Parse days_ahead
        try:
            days_ahead = [int(d) for d in days_ahead_param.split(",")]
        except ValueError:
            days_ahead = [3, 5, 7]
        
        # Generate predictions
        prediction = predictive_tool.predict_route_risk(
            origin=origin,
            destination=destination,
            route_regions=route_regions if route_regions else None,
            route_id=route_id,
            days_ahead=days_ahead
        )
        
        return jsonify({
            "success": True,
            "route_id": route_id,
            "prediction": {
                "current_risk_score": prediction.current_risk_score,
                "overall_trend": prediction.overall_trend,
                "recommendation": prediction.recommendation,
                "predictions": [
                    {
                        "days_ahead": p.days_ahead,
                        "predicted_risk_score": p.predicted_risk_score,
                        "predicted_risk_level": p.predicted_risk_level.value,
                        "confidence": p.confidence,
                        "trend": p.trend,
                        "key_factors": p.factors,
                        "target_date": p.target_date.isoformat()
                    }
                    for p in prediction.predictions
                ],
                "assessment_timestamp": prediction.assessment_timestamp.isoformat()
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/routes/optimize", methods=["POST"])
def optimize_route():
    """Optimize route by balancing risk, cost, and time"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        origin = data.get("origin")
        destination = data.get("destination")
        
        if not origin or not destination:
            return jsonify({
                "success": False,
                "error": "Missing 'origin' or 'destination' field"
            }), 400
        
        # Get optimization parameters
        priority_str = data.get("priority", "balanced")
        try:
            priority = OptimizationPriority(priority_str.lower())
        except ValueError:
            priority = OptimizationPriority.BALANCED
        
        custom_weights = data.get("weights")
        include_predictions = data.get("include_predictions", True)
        max_alternatives = data.get("max_alternatives", 5)
        
        # Optimize route
        result = route_optimization_tool.optimize_route(
            origin=origin,
            destination=destination,
            priority=priority,
            custom_weights=custom_weights,
            include_predictions=include_predictions,
            max_alternatives=max_alternatives
        )
        
        # Convert dataclass objects to dictionaries for JSON serialization
        optimized_routes_json = []
        for route in result.optimized_routes:
            route_dict = {
                "route_id": route.route_id,
                "origin": route.origin,
                "destination": route.destination,
                "waypoints": route.waypoints,
                "metrics": {
                    "risk_score": route.metrics.risk_score,
                    "cost_usd": route.metrics.cost_usd,
                    "time_days": route.metrics.time_days,
                    "distance_km": route.metrics.distance_km,
                    "port_calls": route.metrics.port_calls,
                },
                "risk_assessment": {
                    "route_id": route.risk_assessment.route_id,
                    "origin": route.risk_assessment.origin,
                    "destination": route.risk_assessment.destination,
                    "overall_risk_score": route.risk_assessment.overall_risk_score,
                    "risk_level": route.risk_assessment.risk_level.value,
                    "breakdown": {
                        "trade_news": route.risk_assessment.breakdown.trade_news,
                        "political": route.risk_assessment.breakdown.political,
                        "port_congestion": route.risk_assessment.breakdown.port_congestion,
                        "total": route.risk_assessment.breakdown.total
                    },
                    "factors": {
                        "congestion": route.risk_assessment.breakdown.port_congestion,
                        "tariffs": route.risk_assessment.breakdown.trade_news,
                        "political_unrest": route.risk_assessment.breakdown.political
                    },
                    "contributing_factors": route.risk_assessment.contributing_factors,
                    "recommendation": route.risk_assessment.recommendation,
                    "confidence": route.risk_assessment.confidence,
                    "assessment_timestamp": route.risk_assessment.assessment_timestamp.isoformat()
                } if route.risk_assessment else None,
                "predictive_assessment": None,  # Disabled for now to avoid errors
            }
            optimized_routes_json.append(route_dict)
        
        return jsonify({
            "success": True,
            "message": "Route optimization complete",
            "optimized_routes": optimized_routes_json,
            "recommendation": result.recommendation,
            "optimization": {
                "recommendation": result.recommendation,
                "optimization_criteria": result.optimization_criteria,
                "optimization_timestamp": result.optimization_timestamp.isoformat()
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/routes", methods=["GET"])
def get_routes():
    """Get all available routes (mock for MVP)"""
    try:
        # In production, this would fetch from database
        return jsonify({
            "success": True,
            "routes": [
                {
                    "route_id": "ROUTE-001",
                    "origin": "Taiwan",
                    "destination": "Los Angeles",
                    "status": "active"
                },
                {
                    "route_id": "ROUTE-002",
                    "origin": "Vietnam",
                    "destination": "Los Angeles",
                    "status": "active"
                }
            ]
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/execution/monitor", methods=["POST"])
def monitor_and_execute():
    """Monitor shipment and execute actions if thresholds are met"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        shipment_id = data.get("shipment_id")
        origin = data.get("origin")
        destination = data.get("destination")
        route_regions = data.get("route_regions", [])
        execution_mode_str = data.get("execution_mode", "semi_automatic")
        
        if not shipment_id or not origin or not destination:
            return jsonify({
                "success": False,
                "error": "Missing required fields: shipment_id, origin, destination"
            }), 400
        
        try:
            execution_mode = ExecutionMode(execution_mode_str.lower())
        except ValueError:
            execution_mode = ExecutionMode.SEMI_AUTOMATIC
        
        # Monitor and execute
        action = execution_tool.monitor_and_execute(
            shipment_id=shipment_id,
            origin=origin,
            destination=destination,
            route_regions=route_regions,
            execution_mode=execution_mode
        )
        
        if action:
            return jsonify({
                "success": True,
                "action_triggered": True,
                "action": {
                    "action_id": action.action_id,
                    "action_type": action.action_type,
                    "shipment_id": action.shipment_id,
                    "original_route_id": action.original_route_id,
                    "new_route_id": action.new_route_id,
                    "reason": action.reason,
                    "risk_score_before": action.risk_score_before,
                    "risk_score_after": action.risk_score_after,
                    "status": action.status.value,
                    "created_at": action.created_at.isoformat(),
                    "estimated_impact": action.estimated_impact
                }
            })
        else:
            return jsonify({
                "success": True,
                "action_triggered": False,
                "message": "No action required. Risk levels are acceptable."
            })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/execution/execute", methods=["POST"])
def execute_reroute():
    """Execute a reroute action"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        shipment_id = data.get("shipment_id")
        new_route_id = data.get("new_route_id")
        origin = data.get("origin")
        destination = data.get("destination")
        route_regions = data.get("route_regions", [])
        reason = data.get("reason")
        
        if not all([shipment_id, new_route_id, origin, destination]):
            return jsonify({
                "success": False,
                "error": "Missing required fields: shipment_id, new_route_id, origin, destination"
            }), 400
        
        # Execute reroute
        result = execution_tool.execute_reroute(
            shipment_id=shipment_id,
            new_route_id=new_route_id,
            origin=origin,
            destination=destination,
            route_regions=route_regions,
            reason=reason
        )
        
        return jsonify({
            "success": result.success,
            "message": result.message,
            "action": {
                "action_id": result.action.action_id,
                "action_type": result.action.action_type,
                "shipment_id": result.action.shipment_id,
                "status": result.action.status.value,
                "risk_score_before": result.action.risk_score_before,
                "risk_score_after": result.action.risk_score_after,
                "executed_at": result.action.executed_at.isoformat() if result.action.executed_at else None
            },
            "details": result.details,
            "execution_timestamp": result.execution_timestamp.isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/logs", methods=["GET"])
def get_logs():
    """Get logs with optional filters"""
    try:
        category_str = request.args.get("category")
        level_str = request.args.get("level")
        shipment_id = request.args.get("shipment_id")
        route_id = request.args.get("route_id")
        limit = int(request.args.get("limit", 100))
        
        category = None
        if category_str:
            try:
                category = LogCategory(category_str.lower())
            except ValueError:
                pass
        
        level = None
        if level_str:
            try:
                level = LogLevel(level_str.lower())
            except ValueError:
                pass
        
        logs = logging_tool.get_logs_json(
            category=category,
            level=level,
            shipment_id=shipment_id,
            route_id=route_id,
            limit=limit
        )
        
        return jsonify({
            "success": True,
            "count": len(logs),
            "logs": logs
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/logs/export", methods=["GET"])
def export_logs():
    """Export logs to file"""
    try:
        import os
        from datetime import datetime
        
        category_str = request.args.get("category")
        level_str = request.args.get("level")
        shipment_id = request.args.get("shipment_id")
        route_id = request.args.get("route_id")
        
        filters = {}
        if category_str:
            try:
                filters["category"] = LogCategory(category_str.lower())
            except ValueError:
                pass
        if level_str:
            try:
                filters["level"] = LogLevel(level_str.lower())
            except ValueError:
                pass
        if shipment_id:
            filters["shipment_id"] = shipment_id
        if route_id:
            filters["route_id"] = route_id
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"logs_export_{timestamp}.json"
        filepath = os.path.join("logs", filename)
        
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        # Export logs
        logging_tool.export_logs(filepath, filters)
        
        return jsonify({
            "success": True,
            "message": f"Logs exported to {filepath}",
            "filepath": filepath
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/auth/acled/token", methods=["GET"])
def get_acled_token_status():
    """Get ACLED token status"""
    try:
        acled_policy = get_acled_auth_policy()
        
        if acled_policy.token:
            return jsonify({
                "success": True,
                "token_status": {
                    "has_token": True,
                    "is_expired": acled_policy.token.is_expired(),
                    "is_expiring_soon": acled_policy.token.is_expiring_soon(),
                    "expires_at": acled_policy.token.expires_at.isoformat(),
                    "created_at": acled_policy.token.created_at.isoformat()
                }
            })
        else:
            return jsonify({
                "success": True,
                "token_status": {
                    "has_token": False,
                    "message": "No token available. Configure ACLED credentials to authenticate."
                }
            })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/auth/acled/refresh", methods=["POST"])
def refresh_acled_token():
    """Refresh ACLED access token"""
    try:
        acled_policy = get_acled_auth_policy()
        
        # Force refresh
        token = acled_policy.get_access_token(force_refresh=True)
        
        if token:
            return jsonify({
                "success": True,
                "message": "Token refreshed successfully",
                "token_status": {
                    "expires_at": acled_policy.token.expires_at.isoformat() if acled_policy.token else None
                }
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to refresh token. Check ACLED credentials."
            }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/auth/acled/test", methods=["GET"])
def test_acled_connection():
    """Test ACLED API connection"""
    try:
        acled_policy = get_acled_auth_policy()
        
        # Try to fetch a small amount of data
        data = acled_policy.fetch_acled_data(
            endpoint="acled/read",
            limit=1,
            format="json"
        )
        
        if data.get("status") == 200:
            return jsonify({
                "success": True,
                "message": "ACLED API connection successful",
                "data_count": len(data.get("data", []))
            })
        else:
            return jsonify({
                "success": False,
                "error": f"ACLED API returned status {data.get('status')}"
            }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/db/health", methods=["GET"])
def db_health():
    """Check MongoDB database connection status"""
    try:
        if db_service and db_service.is_connected():
            return jsonify({
                "success": True,
                "status": "connected",
                "database": Config.MONGODB_DATABASE,
                "message": "MongoDB Atlas connection is active"
            })
        else:
            return jsonify({
                "success": False,
                "status": "disconnected",
                "message": "MongoDB Atlas not configured or connection failed"
            }), 503
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/db/risk-data", methods=["GET"])
def get_db_risk_data():
    """Query risk data from MongoDB"""
    try:
        if not db_service or not db_service.is_connected():
            return jsonify({
                "success": False,
                "error": "MongoDB not connected"
            }), 503
        
        # Get query parameters
        category = request.args.get("category")
        location = request.args.get("location")
        source = request.args.get("source")
        limit = int(request.args.get("limit", 100))
        days_back = request.args.get("days_back")
        days_back = int(days_back) if days_back else None
        
        # Query database
        results = db_service.get_risk_data(
            category=category,
            location=location,
            source=source,
            limit=limit,
            days_back=days_back
        )
        
        return jsonify({
            "success": True,
            "count": len(results),
            "data": results
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/db/stats", methods=["GET"])
def get_db_stats():
    """Get database statistics"""
    try:
        if not db_service or not db_service.is_connected():
            return jsonify({
                "success": False,
                "error": "MongoDB not connected"
            }), 503
        
        stats = {}
        
        # Get collection counts
        collections = [
            Config.MONGODB_COLLECTION_RISK_DATA,
            Config.MONGODB_COLLECTION_ROUTES,
            Config.MONGODB_COLLECTION_ASSESSMENTS,
            Config.MONGODB_COLLECTION_EXECUTIONS,
            Config.MONGODB_COLLECTION_LOGS
        ]
        
        for collection_name in collections:
            collection = db_service.get_collection(collection_name)
            if collection is not None:
                stats[collection_name] = collection.count_documents({})
        
        return jsonify({
            "success": True,
            "database": Config.MONGODB_DATABASE,
            "stats": stats
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    debug = os.environ.get("DEBUG", "False").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)

