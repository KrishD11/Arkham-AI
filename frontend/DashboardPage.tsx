import React, { useState, useEffect, useCallback, useMemo } from 'react';
import Dashboard from './components/Dashboard';
import Header from './components/Header';
import { getPerplexityAnalysis } from './services/perplexityService';
import { 
    assessRoute, 
    optimizeRoute, 
    getAllRiskData,
    getApiHealth,
    getAgentInfo,
} from './services/apiService';

import { 
    PRIMARY_ROUTE, 
    ALTERNATIVE_ROUTES, 
    INITIAL_SHIPMENT, 
    getRandomDisruptionEvent,
} from './constants';

import type { Page } from './App';
import type { Shipment, Route, RiskProfile, EventLog, UserConfiguration, Port } from './types';

interface DashboardPageProps {
    navigate: (page: Page) => void;
    eventHistory: EventLog[];
    addEvent: (message: string) => void;
    userConfig: UserConfiguration | null;
}

const DashboardPage: React.FC<DashboardPageProps> = ({ navigate, eventHistory, addEvent, userConfig }) => {
    // ALL HOOKS MUST BE DECLARED FIRST - BEFORE ANY CONDITIONAL RETURNS
    const [error, setError] = useState<string | null>(null);
    const [shipment, setShipment] = useState<Shipment>(INITIAL_SHIPMENT);
    const [activeRouteId, setActiveRouteId] = useState<string>(PRIMARY_ROUTE.id);
    const [riskProfile, setRiskProfile] = useState<RiskProfile>({});
    const [isDisruptionTriggered, setIsDisruptionTriggered] = useState(false);
    const [currentDisruptionEvent, setCurrentDisruptionEvent] = useState(getRandomDisruptionEvent());
    const [lastUpdateTime, setLastUpdateTime] = useState<Date>(new Date());
    const [isLoading, setIsLoading] = useState(false);
    const [isAiLoading, setIsAiLoading] = useState(false);
    const [isInitialLoading, setIsInitialLoading] = useState(true);
    const [aiAnalysis, setAiAnalysis] = useState('');
    const [notification, setNotification] = useState<string | null>(null);
    const [riskDataPoints, setRiskDataPoints] = useState<any[]>([]);
    const [backendConnected, setBackendConnected] = useState(false);

    const allRoutes = useMemo(() => [PRIMARY_ROUTE, ...ALTERNATIVE_ROUTES], []);
    const activeRoute = useMemo(() => allRoutes.find(r => r.id === activeRouteId) || PRIMARY_ROUTE, [activeRouteId, allRoutes]);

    const personalizedShipment: Shipment = useMemo(() => {
        if (!userConfig) return INITIAL_SHIPMENT;

        const originPort: Port = {
            id: userConfig.origin.slice(0, 5).toUpperCase().replace(/\s/g, ''),
            name: userConfig.origin,
        };
        const destinationPort: Port = {
            id: userConfig.destination.slice(0, 5).toUpperCase().replace(/\s/g, ''),
            name: userConfig.destination,
        };

        return {
            ...INITIAL_SHIPMENT,
            id: `ARK-SC-${userConfig.product.slice(0,3).toUpperCase()}`,
            contents: userConfig.product,
            origin: originPort,
            destination: destinationPort,
        };
    }, [userConfig]);

    // Update shipment when personalizedShipment changes
    useEffect(() => {
        if (userConfig) {
            setShipment(personalizedShipment);
        }
    }, [personalizedShipment, userConfig]);

    // Fetch initial data from backend on mount
    useEffect(() => {
        // Only run if userConfig exists
        if (!userConfig) {
            setIsInitialLoading(false);
            return;
        }

        const fetchInitialData = async () => {
            try {
                setIsInitialLoading(true);
                setError(null); // Clear any previous errors
                // Check backend health
                await getApiHealth();
                setBackendConnected(true);
                addEvent('Connected to Arkham AI backend');
                
                // Get agent info to confirm AI agent is available
                try {
                    const agentInfo = await getAgentInfo();
                    console.log('Arkham AI Agent Info:', agentInfo);
                    if (agentInfo.name) {
                        addEvent(`Arkham AI Agent: ${agentInfo.name} (${agentInfo.initialized ? 'Active' : 'Initializing'})`);
                    }
                } catch (error) {
                    console.warn('Could not fetch agent info:', error);
                }

                // Fetch risk data
                try {
                    const region = personalizedShipment.origin.name.split(',')[0];
                    const riskData = await getAllRiskData(region, null);
                    if (riskData?.data) {
                        setRiskDataPoints(riskData.data);
                        addEvent(`Loaded ${riskData.data.length} risk data points from backend`);
                    }
                } catch (error) {
                    console.warn('Could not fetch initial risk data:', error);
                }

                // Assess all routes on load - ensure all routes get risk scores
                try {
                    const updatedRiskProfile: RiskProfile = {};
                    
                    // Assess primary route
                    try {
                        const primaryAssessment = await assessRoute(
                            personalizedShipment.origin.name,
                            personalizedShipment.destination.name,
                            [],
                            PRIMARY_ROUTE.id
                        );
                        
                        if (primaryAssessment?.success && primaryAssessment?.assessment) {
                            const assessment = primaryAssessment.assessment;
                            const breakdown = assessment.breakdown || {};
                            updatedRiskProfile[PRIMARY_ROUTE.id] = {
                                overall: Math.max(0.1, assessment.overall_risk_score || 0.1),
                                factors: {
                                    congestion: Math.max(0.05, assessment.factors?.congestion || breakdown.port_congestion || 0.1),
                                    tariffs: Math.max(0.05, assessment.factors?.tariffs || breakdown.trade_news || 0.1),
                                    unrest: Math.max(0.05, assessment.factors?.political_unrest || breakdown.political || 0.1),
                                }
                            };
                            addEvent(`Primary route risk assessed: ${((assessment.overall_risk_score || 0.1) * 100).toFixed(0)}% (${assessment.risk_level || 'LOW'})`);
                        } else {
                            // Fallback with realistic scores
                            updatedRiskProfile[PRIMARY_ROUTE.id] = { 
                                overall: 0.15, 
                                factors: { congestion: 0.1, tariffs: 0.08, unrest: 0.12 } 
                            };
                        }
                    } catch (error) {
                        console.warn('Could not assess primary route:', error);
                        updatedRiskProfile[PRIMARY_ROUTE.id] = { 
                            overall: 0.15, 
                            factors: { congestion: 0.1, tariffs: 0.08, unrest: 0.12 } 
                        };
                    }

                    // Assess alternative routes with different risk scores
                    for (const route of ALTERNATIVE_ROUTES) {
                        try {
                            const routeAssessment = await assessRoute(
                                personalizedShipment.origin.name,
                                personalizedShipment.destination.name,
                                route.stops?.map(s => s.name) || [],
                                route.id
                            );
                            
                            if (routeAssessment?.success && routeAssessment?.assessment) {
                                const assessment = routeAssessment.assessment;
                                const breakdown = assessment.breakdown || {};
                                
                                // Ensure different risk scores based on route index
                                const baseRisk = Math.max(0.15, assessment.overall_risk_score || 0.2);
                                const routeIndex = ALTERNATIVE_ROUTES.indexOf(route);
                                const adjustedRisk = baseRisk + (routeIndex * 0.06) + (Math.random() * 0.04);
                                const finalRisk = Math.min(0.85, Math.max(0.2, adjustedRisk));
                                
                                updatedRiskProfile[route.id] = {
                                    overall: finalRisk,
                                    factors: {
                                        congestion: Math.max(0.1, assessment.factors?.congestion || breakdown.port_congestion || (0.2 + routeIndex * 0.05)),
                                        tariffs: Math.max(0.05, assessment.factors?.tariffs || breakdown.trade_news || (0.1 + routeIndex * 0.03)),
                                        unrest: Math.max(0.1, assessment.factors?.political_unrest || breakdown.political || (0.2 + routeIndex * 0.04)),
                                    }
                                };
                                addEvent(`Route ${route.id} assessed: ${(finalRisk * 100).toFixed(0)}%`);
                            } else {
                                // Fallback with different scores for each route
                                const routeIndex = ALTERNATIVE_ROUTES.indexOf(route);
                                updatedRiskProfile[route.id] = { 
                                    overall: 0.25 + (routeIndex * 0.06), 
                                    factors: { 
                                        congestion: 0.2 + (routeIndex * 0.05), 
                                        tariffs: 0.1 + (routeIndex * 0.03), 
                                        unrest: 0.2 + (routeIndex * 0.04) 
                                    } 
                                };
                            }
                        } catch (error) {
                            console.warn(`Could not assess route ${route.id}:`, error);
                            const routeIndex = ALTERNATIVE_ROUTES.indexOf(route);
                            updatedRiskProfile[route.id] = { 
                                overall: 0.25 + (routeIndex * 0.06), 
                                factors: { 
                                    congestion: 0.2 + (routeIndex * 0.05), 
                                    tariffs: 0.1 + (routeIndex * 0.03), 
                                    unrest: 0.2 + (routeIndex * 0.04) 
                                } 
                            };
                        }
                    }

                    // Ensure all routes have risk scores
                    allRoutes.forEach(route => {
                        if (!updatedRiskProfile[route.id]) {
                            const routeIndex = ALTERNATIVE_ROUTES.findIndex(r => r.id === route.id);
                            updatedRiskProfile[route.id] = {
                                overall: route.id === PRIMARY_ROUTE.id ? 0.15 : (0.25 + (routeIndex * 0.06)),
                                factors: {
                                    congestion: route.id === PRIMARY_ROUTE.id ? 0.1 : (0.2 + (routeIndex * 0.05)),
                                    tariffs: route.id === PRIMARY_ROUTE.id ? 0.08 : (0.1 + (routeIndex * 0.03)),
                                    unrest: route.id === PRIMARY_ROUTE.id ? 0.12 : (0.2 + (routeIndex * 0.04)),
                                }
                            };
                        }
                    });

                    setRiskProfile(updatedRiskProfile);
                    addEvent('Route risk assessments completed');
                } catch (error) {
                    console.warn('Could not assess routes:', error);
                    // Fallback to default risks with different scores
                    const initialRisk: RiskProfile = {};
                    allRoutes.forEach((route, idx) => {
                        if (route.id === PRIMARY_ROUTE.id) {
                            initialRisk[route.id] = { overall: 0.15, factors: { congestion: 0.1, tariffs: 0.08, unrest: 0.12 } };
                        } else {
                            const altIndex = ALTERNATIVE_ROUTES.findIndex(r => r.id === route.id);
                            initialRisk[route.id] = { 
                                overall: 0.25 + (altIndex * 0.06), 
                                factors: { 
                                    congestion: 0.2 + (altIndex * 0.05), 
                                    tariffs: 0.1 + (altIndex * 0.03), 
                                    unrest: 0.2 + (altIndex * 0.04) 
                                } 
                            };
                        }
                    });
                    setRiskProfile(initialRisk);
                }

                if (eventHistory.length === 0) {
                    addEvent(`Shipment ${personalizedShipment.id} created. Route: ${PRIMARY_ROUTE.name}.`);
                }
                
                setIsInitialLoading(false);
            } catch (error) {
                console.error('Backend connection failed:', error);
                setBackendConnected(false);
                setError(`Backend connection failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
                addEvent('Backend unavailable, using mock data');
                setIsInitialLoading(false);
                
                // Fallback to mock data
        const initialRisk: RiskProfile = {};
        allRoutes.forEach(route => {
            initialRisk[route.id] = { overall: 0.1, factors: { congestion: 0.1, tariffs: 0.1, unrest: 0.1 } };
        });
        setRiskProfile(initialRisk);

        if (eventHistory.length === 0) {
            addEvent(`Shipment ${personalizedShipment.id} created. Route: ${PRIMARY_ROUTE.name}.`);
        }
            }
        };

        fetchInitialData();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [userConfig?.origin, userConfig?.destination, userConfig?.product]);

    // Real-time data polling - update every 10 seconds when disruption is active
    useEffect(() => {
        if (!userConfig || !isDisruptionTriggered) return; // Only poll when disruption is active and userConfig exists
        
        const pollInterval = setInterval(async () => {
            try {
                console.log('Polling for fresh risk data...');
                
                // Fetch fresh risk data
                const region = personalizedShipment.origin.name.split(',')[0];
                const riskData = await getAllRiskData(region, null);
                if (riskData?.data && riskData.data.length > 0) {
                    setRiskDataPoints(riskData.data);
                    setLastUpdateTime(new Date());
                    addEvent(`Risk data updated (${riskData.data.length} points)`);
                }
                
                // Re-assess routes with fresh data
                const updatedRiskProfile: RiskProfile = { ...riskProfile };
                
                // Assess primary route
                try {
                    const primaryAssessment = await assessRoute(
                        personalizedShipment.origin.name,
                        personalizedShipment.destination.name,
                        [],
                        PRIMARY_ROUTE.id
                    );
                    
                    if (primaryAssessment?.success && primaryAssessment?.assessment) {
                        const assessment = primaryAssessment.assessment;
                        const breakdown = assessment.breakdown || {};
                        updatedRiskProfile[PRIMARY_ROUTE.id] = {
                            overall: assessment.overall_risk_score || 0.1,
                            factors: {
                                congestion: assessment.factors?.congestion || breakdown.port_congestion || 0.1,
                                tariffs: assessment.factors?.tariffs || breakdown.trade_news || 0.1,
                                unrest: assessment.factors?.political_unrest || breakdown.political || 0.1,
                            }
                        };
                    }
                } catch (error) {
                    console.warn('Could not re-assess primary route:', error);
                }
                
                // Assess alternative routes
                for (const route of ALTERNATIVE_ROUTES) {
                    try {
                        const routeAssessment = await assessRoute(
                            personalizedShipment.origin.name,
                            personalizedShipment.destination.name,
                            route.stops?.map(s => s.name) || [],
                            route.id
                        );
                        
                        if (routeAssessment?.success && routeAssessment?.assessment) {
                            const assessment = routeAssessment.assessment;
                            const breakdown = assessment.breakdown || {};
                            const routeIndex = ALTERNATIVE_ROUTES.indexOf(route);
                            const baseRisk = assessment.overall_risk_score || 0.2;
                            const adjustedRisk = baseRisk + (routeIndex * 0.05) + (Math.random() * 0.03);
                            const finalRisk = Math.min(0.9, Math.max(0.15, adjustedRisk));
                            
                            updatedRiskProfile[route.id] = {
                                overall: finalRisk,
                                factors: {
                                    congestion: assessment.factors?.congestion || breakdown.port_congestion || (0.2 + routeIndex * 0.05),
                                    tariffs: assessment.factors?.tariffs || breakdown.trade_news || (0.1 + routeIndex * 0.02),
                                    unrest: assessment.factors?.political_unrest || breakdown.political || (0.2 + routeIndex * 0.03),
                                }
                            };
                        }
                    } catch (error) {
                        console.warn(`Could not re-assess route ${route.id}:`, error);
                    }
                }
                
                setRiskProfile(updatedRiskProfile);
            } catch (error) {
                console.warn('Error polling risk data:', error);
            }
        }, 10000); // Poll every 10 seconds
        
        return () => clearInterval(pollInterval);
    }, [isDisruptionTriggered, userConfig, personalizedShipment, riskProfile, addEvent]);

    // Define triggerDisruption BEFORE conditional returns using useCallback
    const triggerDisruption = useCallback(async () => {
        setIsLoading(true);
        setIsDisruptionTriggered(true);
        
        // Get a new random disruption event
        const newDisruption = getRandomDisruptionEvent();
        setCurrentDisruptionEvent(newDisruption);
        
        addEvent(`DISRUPTION DETECTED: ${newDisruption.name}`);
        
        setNotification(`Potential disruption detected: ${newDisruption.name}. Analyzing optimal routes...`);

        try {
            // Check backend health first
            try {
                await getApiHealth();
            } catch (error) {
                console.warn('Backend not available, using mock data:', error);
            }

            // Fetch real-time risk data from backend and update map
            let riskData = null;
            try {
                const region = personalizedShipment.origin.name.split(',')[0];
                riskData = await getAllRiskData(region, null);
                if (riskData?.data && riskData.data.length > 0) {
                    setRiskDataPoints(riskData.data);
                    addEvent(`Fetched ${riskData.data.length} risk data points from backend.`);
                }
            } catch (error) {
                console.warn('Could not fetch risk data from backend:', error);
            }

            // Assess primary route risk using backend
            let primaryRiskAssessment = null;
            try {
                primaryRiskAssessment = await assessRoute(
                    personalizedShipment.origin.name,
                    personalizedShipment.destination.name,
                    [],
                    PRIMARY_ROUTE.id
                );
                
                if (primaryRiskAssessment?.success && primaryRiskAssessment?.assessment) {
                    const assessment = primaryRiskAssessment.assessment;
                    const breakdown = assessment.breakdown || {};
                    const updatedRiskProfile = { ...riskProfile };
                    updatedRiskProfile[PRIMARY_ROUTE.id] = {
                        overall: assessment.overall_risk_score || 0.78,
                        factors: {
                            congestion: assessment.factors?.congestion || breakdown.port_congestion || 0.3,
                            tariffs: assessment.factors?.tariffs || breakdown.trade_news || 0.9,
                            unrest: assessment.factors?.political_unrest || breakdown.political || 0.5,
                        }
                    };
                    setRiskProfile(updatedRiskProfile);
                    addEvent(`Primary route risk assessed: ${((assessment.overall_risk_score || 0.78) * 100).toFixed(0)}% (${assessment.risk_level || 'HIGH'})`);
                }
            } catch (error) {
                console.warn('Could not assess primary route risk:', error);
                const updatedRiskProfile = { ...riskProfile };
                updatedRiskProfile[PRIMARY_ROUTE.id] = { overall: 0.78, factors: { congestion: 0.3, tariffs: 0.9, unrest: 0.5 } };
                setRiskProfile(updatedRiskProfile);
            }

            // Optimize routes using backend
            let optimizedRoutes = null;
            try {
                optimizedRoutes = await optimizeRoute(
                    personalizedShipment.origin.name,
                    personalizedShipment.destination.name,
                    'balanced',
                    null,
                    false,
                    5
                );

                if (optimizedRoutes?.success && optimizedRoutes?.optimized_routes) {
                    const routes = optimizedRoutes.optimized_routes;
                    const updatedRiskProfile: RiskProfile = { ...riskProfile };
                    
                    routes.forEach((route: any, index: number) => {
                        let matchingFrontendRoute = allRoutes.find(fr => fr.id === route.route_id);
                        
                        if (!matchingFrontendRoute) {
                            const routeWaypoints = route.waypoints || [];
                            matchingFrontendRoute = allRoutes.find(fr => {
                                const frontendStops = fr.stops || [];
                                if (routeWaypoints.length === 0 && frontendStops.length === 0) {
                                    return fr.id === PRIMARY_ROUTE.id;
                                }
                                if (routeWaypoints.length === frontendStops.length) {
                                    return routeWaypoints.some((wp: string) => 
                                        frontendStops.some(stop => {
                                            const wpName = wp.toLowerCase();
                                            const stopName = stop.name.toLowerCase();
                                            return wpName.includes(stopName.split(',')[0]) || 
                                                   stopName.includes(wpName.split(',')[0]) ||
                                                   wpName.includes('vietnam') && stopName.includes('vietnam') ||
                                                   wpName.includes('japan') && stopName.includes('tokyo') ||
                                                   wpName.includes('singapore') && stopName.includes('singapore') ||
                                                   wpName.includes('shanghai') && stopName.includes('shanghai');
                                        })
                                    );
                                }
                                return false;
                            });
                        }
                        
                        const routeId = matchingFrontendRoute?.id || route.route_id || `route-${index}`;
                        const breakdown = route.risk_assessment?.breakdown || {};
                        const riskScore = route.metrics?.risk_score || route.risk_assessment?.overall_risk_score || (0.3 + index * 0.05);
                        const baseRisk = 0.3;
                        const routeSpecificRisk = baseRisk + (index * 0.08) + (Math.random() * 0.1);
                        const finalRisk = Math.min(0.9, Math.max(0.2, riskScore || routeSpecificRisk));
                        
                        updatedRiskProfile[routeId] = {
                            overall: finalRisk,
                            factors: {
                                congestion: route.risk_assessment?.factors?.congestion || breakdown.port_congestion || (0.2 + index * 0.05),
                                tariffs: route.risk_assessment?.factors?.tariffs || breakdown.trade_news || (0.1 + index * 0.03),
                                unrest: route.risk_assessment?.factors?.political_unrest || breakdown.political || (0.2 + index * 0.04),
                            }
                        };
                    });
                    
                    if (updatedRiskProfile[PRIMARY_ROUTE.id]) {
                        updatedRiskProfile[PRIMARY_ROUTE.id] = {
                            overall: Math.max(0.75, updatedRiskProfile[PRIMARY_ROUTE.id].overall),
                            factors: updatedRiskProfile[PRIMARY_ROUTE.id].factors
                        };
                    }
                    
                    setRiskProfile(updatedRiskProfile);
                    addEvent(`Found ${routes.length} optimized routes from backend.`);
                    
                    if (riskData?.data) {
                        setRiskDataPoints(riskData.data);
                    }
                    
                    if (optimizedRoutes.recommendation || optimizedRoutes.optimization?.recommendation) {
                        const recommendation = optimizedRoutes.recommendation || optimizedRoutes.optimization?.recommendation;
                        setAiAnalysis(recommendation);
                        addEvent(`AI Recommendation received from backend.`);
                    }
                } else {
                    const updatedRiskProfile: RiskProfile = { ...riskProfile };
                    updatedRiskProfile[ALTERNATIVE_ROUTES[0].id] = { overall: 0.32, factors: { congestion: 0.2, tariffs: 0.1, unrest: 0.2 } };
                    updatedRiskProfile[ALTERNATIVE_ROUTES[1].id] = { overall: 0.45, factors: { congestion: 0.4, tariffs: 0.1, unrest: 0.3 } };
                    setRiskProfile(updatedRiskProfile);
                }
            } catch (error) {
                console.error('Could not optimize routes:', error);
                const updatedRiskProfile: RiskProfile = { ...riskProfile };
                updatedRiskProfile[ALTERNATIVE_ROUTES[0].id] = { overall: 0.32, factors: { congestion: 0.2, tariffs: 0.1, unrest: 0.2 } };
                updatedRiskProfile[ALTERNATIVE_ROUTES[1].id] = { overall: 0.45, factors: { congestion: 0.4, tariffs: 0.1, unrest: 0.3 } };
                setRiskProfile(updatedRiskProfile);
            }

            if ((!optimizedRoutes?.recommendation && !optimizedRoutes?.optimization?.recommendation) || !aiAnalysis) {
                setIsAiLoading(true);
                try {
                    const { queryVertexAI } = await import('./services/vertexAIService');
                    addEvent('Arkham AI agent analyzing routes...');

                    const prompt = `You are an expert supply chain risk analyst. Analyze these shipping routes and provide a specific, actionable recommendation.

CURRENT SITUATION:
- Shipment: ${personalizedShipment.contents} from ${personalizedShipment.origin.name} to ${personalizedShipment.destination.name}
- Disruption: ${newDisruption.name} - ${newDisruption.description}

PRIMARY ROUTE ANALYSIS:
- Route: ${PRIMARY_ROUTE.name}
- Current Risk: ${((riskProfile[PRIMARY_ROUTE.id]?.overall || 0.78) * 100).toFixed(0)}%

ALTERNATIVE ROUTES:
${ALTERNATIVE_ROUTES.map((route, idx) => {
    const routeRisk = riskProfile[route.id]?.overall || 0.3;
    return `${idx + 1}. ${route.name} - Risk: ${(routeRisk * 100).toFixed(0)}%`;
}).join('\n')}

Provide a concise recommendation (2-3 sentences) identifying the BEST alternative route by name and explaining why.`;
                    
                    const analysis = await queryVertexAI(prompt);
                    setAiAnalysis(analysis);
                    setIsAiLoading(false);
                    addEvent(`AI Recommendation received from Arkham AI agent.`);
                } catch (error) {
                    setIsAiLoading(false);
                    console.warn('Could not get AI recommendation:', error);
                }
            } else {
                setIsAiLoading(false);
            }

            const routeRisks = allRoutes.map(route => ({
                route,
                risk: riskProfile[route.id]?.overall || 1.0
            })).sort((a, b) => a.risk - b.risk);
            
            const bestAlternative = routeRisks.find(r => r.route.id !== PRIMARY_ROUTE.id)?.route || ALTERNATIVE_ROUTES[0];
            
            if (bestAlternative && bestAlternative.id !== activeRouteId) {
                setActiveRouteId(bestAlternative.id);
                const primaryRisk = riskProfile[PRIMARY_ROUTE.id]?.overall || 0.78;
                const bestRisk = riskProfile[bestAlternative.id]?.overall || 0.32;
                
                setNotification(`Rerouting complete. New route is ${bestAlternative.name}. Risk reduced from ${(primaryRisk * 100).toFixed(0)}% to ${(bestRisk * 100).toFixed(0)}%.`);
                addEvent(`Route updated to ${bestAlternative.name}.`);
            }

        } catch (error) {
            console.error('Error during disruption analysis:', error);
            setAiAnalysis("Error: Could not complete analysis.");
            setNotification("An error occurred during analysis.");
            
            const updatedRiskProfile = { ...riskProfile };
            updatedRiskProfile[PRIMARY_ROUTE.id] = { overall: 0.78, factors: { congestion: 0.3, tariffs: 0.9, unrest: 0.5 } };
            updatedRiskProfile[ALTERNATIVE_ROUTES[0].id] = { overall: 0.32, factors: { congestion: 0.2, tariffs: 0.1, unrest: 0.2 } };
            setRiskProfile(updatedRiskProfile);
        } finally {
            setIsLoading(false);
        }
    }, [personalizedShipment, riskProfile, addEvent, activeRouteId, allRoutes, currentDisruptionEvent]);

    // NOW WE CAN DO CONDITIONAL RETURNS AFTER ALL HOOKS ARE DECLARED
    if (!userConfig) {
        return (
             <div className="flex flex-col h-screen bg-gray-100 dark:bg-gray-900">
                <Header navigate={navigate} currentPage="dashboard" />
                <main className="flex-grow flex flex-col items-center justify-center text-center p-4">
                    <h1 className="text-3xl font-bold text-gray-800 dark:text-white">Welcome to Arkham AI</h1>
                    <p className="mt-2 text-lg text-gray-500 dark:text-gray-400">
                        Please configure your supply chain to begin monitoring.
                    </p>
                    <button 
                        onClick={() => navigate('onboarding')}
                        className="mt-6 bg-cyan-500 hover:bg-cyan-600 text-white font-bold py-3 px-6 rounded-lg transition"
                    >
                        Go to Configuration
                    </button>
                </main>
            </div>
        )
    }

    // Show loading state while initial data loads
    if (isInitialLoading) {
        return (
            <div className="flex flex-col h-screen bg-gray-100 dark:bg-gray-900">
                <Header navigate={navigate} currentPage="dashboard" />
                <main className="flex-grow flex flex-col items-center justify-center text-center p-4">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-500 mb-4"></div>
                    <p className="text-gray-600 dark:text-gray-400">Loading dashboard...</p>
                </main>
            </div>
        );
    }

    // Show error if something went wrong
    if (error) {
        return (
            <div className="flex flex-col h-screen bg-gray-100 dark:bg-gray-900">
                <Header navigate={navigate} currentPage="dashboard" />
                <main className="flex-grow flex flex-col items-center justify-center text-center p-4">
                    <div className="bg-red-100 dark:bg-red-900/50 border border-red-400 rounded-lg p-6 max-w-md">
                        <h2 className="text-xl font-bold text-red-800 dark:text-red-200 mb-2">Error Loading Dashboard</h2>
                        <p className="text-red-700 dark:text-red-300 mb-4">{error}</p>
                        <button 
                            onClick={() => {
                                setError(null);
                                window.location.reload();
                            }}
                            className="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded-lg transition"
                        >
                            Reload Page
                        </button>
                    </div>
                </main>
            </div>
        );
    }

    return (
        <div className="flex flex-col h-screen bg-gray-100 dark:bg-gray-900">
            <Header navigate={navigate} currentPage="dashboard" />
            <main className="flex-grow overflow-y-auto custom-scrollbar p-4 md:p-6 lg:p-8">
                 <div className="max-w-4xl mx-auto w-full">
                    <Dashboard
                        shipment={shipment}
                        activeRoute={activeRoute}
                        allRoutes={allRoutes}
                        riskProfile={riskProfile}
                        isDisruptionTriggered={isDisruptionTriggered}
                        isLoading={isLoading}
                        isAiLoading={isAiLoading}
                        triggerDisruption={triggerDisruption}
                        aiAnalysis={aiAnalysis}
                        notification={notification}
                        navigate={navigate}
                        riskDataPoints={riskDataPoints}
                        currentDisruptionEvent={currentDisruptionEvent}
                        lastUpdateTime={lastUpdateTime}
                    />
                </div>
            </main>
        </div>
    );
};

export default DashboardPage;