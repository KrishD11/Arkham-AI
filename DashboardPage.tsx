import React, { useState, useEffect, useCallback, useMemo } from 'react';
import Dashboard from './components/Dashboard';
import Header from './components/Header';
import { getPerplexityAnalysis } from './services/perplexityService';

import { 
    PRIMARY_ROUTE, 
    ALTERNATIVE_ROUTES, 
    INITIAL_SHIPMENT, 
    DISRUPTION_EVENT,
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

    const [shipment, setShipment] = useState<Shipment>(personalizedShipment);
    const [activeRouteId, setActiveRouteId] = useState<string>(PRIMARY_ROUTE.id);
    const [riskProfile, setRiskProfile] = useState<RiskProfile>({});
    const [isDisruptionTriggered, setIsDisruptionTriggered] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [aiAnalysis, setAiAnalysis] = useState('');
    const [notification, setNotification] = useState<string | null>(null);

    const allRoutes = useMemo(() => [PRIMARY_ROUTE, ...ALTERNATIVE_ROUTES], []);
    const activeRoute = useMemo(() => allRoutes.find(r => r.id === activeRouteId) || PRIMARY_ROUTE, [activeRouteId, allRoutes]);

    const initializeState = useCallback(() => {
        const initialRisk: RiskProfile = {};
        allRoutes.forEach(route => {
            initialRisk[route.id] = { overall: 0.1, factors: { congestion: 0.1, tariffs: 0.1, unrest: 0.1 } };
        });
        setRiskProfile(initialRisk);

        if (eventHistory.length === 0) {
            addEvent(`Shipment ${personalizedShipment.id} created. Route: ${PRIMARY_ROUTE.name}.`);
        }
    }, [allRoutes, addEvent, eventHistory.length, personalizedShipment]);
    
    useEffect(() => {
        initializeState();
    }, [initializeState]);

    const triggerDisruption = async () => {
        setIsLoading(true);
        setIsDisruptionTriggered(true);
        addEvent(`DISRUPTION DETECTED: ${DISRUPTION_EVENT.name}`);
        
        setNotification(`Potential disruption detected: ${DISRUPTION_EVENT.name}. Analyzing optimal routes...`);

        const updatedRiskProfile = { ...riskProfile };
        updatedRiskProfile[PRIMARY_ROUTE.id] = { overall: 0.78, factors: { congestion: 0.3, tariffs: 0.9, unrest: 0.5 } };
        updatedRiskProfile[ALTERNATIVE_ROUTES[0].id] = { overall: 0.32, factors: { congestion: 0.2, tariffs: 0.1, unrest: 0.2 } };
        updatedRiskProfile[ALTERNATIVE_ROUTES[1].id] = { overall: 0.45, factors: { congestion: 0.4, tariffs: 0.1, unrest: 0.3 } };
        setRiskProfile(updatedRiskProfile);

        const prompt = `
            Analyze the following supply chain disruption and recommend the best alternative route.
            Shipment: ${personalizedShipment.contents} from ${personalizedShipment.origin.name} to ${personalizedShipment.destination.name}.
            Primary Route: ${PRIMARY_ROUTE.name} (Current Risk: 78%)
            Disruption: ${DISRUPTION_EVENT.name} - ${DISRUPTION_EVENT.description}
            
            Alternative Routes:
            1. ${ALTERNATIVE_ROUTES[0].name} (Risk: 32%)
            2. ${ALTERNATIVE_ROUTES[1].name} (Risk: 45%)

            Provide a concise recommendation.
        `;
        
        try {
            const analysis = await getPerplexityAnalysis(prompt);
            setAiAnalysis(analysis);
            addEvent(`AI Analysis Complete. Recommendation received.`);

            const bestAlternative = ALTERNATIVE_ROUTES[0];
            setActiveRouteId(bestAlternative.id);
            setShipment(prev => ({
                ...prev,
                currentRouteId: bestAlternative.id,
                eta: INITIAL_SHIPMENT.eta + bestAlternative.timeDeltaDays
            }));
            
            setNotification(`Rerouting complete. New route is ${bestAlternative.name}. Risk reduced from 78% to 32%.`);
            addEvent(`Route updated to ${bestAlternative.name}. ETA changed by +${bestAlternative.timeDeltaDays} day(s).`);

        } catch (error) {
            setAiAnalysis("Error: Could not get AI analysis.");
            setNotification("An error occurred during AI analysis.");
        } finally {
            setIsLoading(false);
        }
    };
    
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
                        triggerDisruption={triggerDisruption}
                        aiAnalysis={aiAnalysis}
                        notification={notification}
                        navigate={navigate}
                    />
                </div>
            </main>
        </div>
    );
};

export default DashboardPage;