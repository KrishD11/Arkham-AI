import React from 'react';
import type { Shipment, Route, RiskProfile, EventLog } from '../types';
import { AlertIcon } from './Icons';
import { DISRUPTION_EVENT, PRIMARY_ROUTE, INITIAL_SHIPMENT } from '../constants';
import type { Page } from '../App';

interface DashboardProps {
    shipment: Shipment;
    activeRoute: Route;
    allRoutes: Route[];
    riskProfile: RiskProfile;
    isDisruptionTriggered: boolean;
    isLoading: boolean;
    triggerDisruption: () => void;
    aiAnalysis: string;
    notification: string | null;
    navigate: (page: Page) => void;
}

const RiskBar: React.FC<{ value: number }> = ({ value }) => {
    const percentage = value * 100;
    let barColor = 'bg-green-500';
    if (value > 0.3) barColor = 'bg-yellow-500';
    if (value > 0.6) barColor = 'bg-red-500';

    return (
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
            <div className={`${barColor} h-2.5 rounded-full`} style={{ width: `${percentage}%` }}></div>
        </div>
    );
};

const Dashboard: React.FC<DashboardProps> = ({
    shipment,
    activeRoute,
    allRoutes,
    riskProfile,
    isDisruptionTriggered,
    isLoading,
    triggerDisruption,
    aiAnalysis,
    notification,
    navigate,
}) => {
    const primaryRisk = riskProfile[PRIMARY_ROUTE.id]?.overall || 0;
    const activeRisk = riskProfile[activeRoute.id]?.overall || 0;
    const riskReduction = primaryRisk - activeRisk;

    return (
        <div className="bg-gray-100/80 dark:bg-gray-900/80 backdrop-blur-sm p-4 md:p-6 flex flex-col space-y-4 custom-scrollbar h-full">
            {notification && (
                <div className="p-3 bg-blue-900/50 border border-blue-400 rounded-lg text-blue-200 text-sm animate-fade-in-down">
                    <p className="font-semibold">SYSTEM NOTIFICATION:</p>
                    <p>{notification}</p>
                </div>
            )}
            
            <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
                <h2 className="text-lg font-semibold text-cyan-500 dark:text-cyan-400 mb-2">Shipment Details</h2>
                <div className="grid grid-cols-2 gap-2 text-sm">
                    <p><span className="font-bold text-gray-500 dark:text-gray-400">ID:</span> {shipment.id}</p>
                    <p><span className="font-bold text-gray-500 dark:text-gray-400">Contents:</span> {shipment.contents}</p>
                    <p><span className="font-bold text-gray-500 dark:text-gray-400">Origin:</span> {shipment.origin.name}</p>
                    <p><span className="font-bold text-gray-500 dark:text-gray-400">Destination:</span> {shipment.destination.name}</p>
                    <p className="col-span-2"><span className="font-bold text-gray-500 dark:text-gray-400">ETA:</span> {shipment.eta} days
                     {activeRoute.id !== PRIMARY_ROUTE.id && (
                        <span className="text-yellow-600 dark:text-yellow-400 ml-2 text-xs font-mono">
                            (was {INITIAL_SHIPMENT.eta}, +{activeRoute.timeDeltaDays}d)
                        </span>
                    )}
                    </p>
                </div>
            </div>

            <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
                <div className="flex justify-between items-center">
                    <h2 className="text-lg font-semibold text-cyan-500 dark:text-cyan-400">Shipment History Log</h2>
                    <button onClick={() => navigate('history')} className="text-sm bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200 font-semibold py-1 px-3 rounded-lg transition">
                        View Full History
                    </button>
                </div>
            </div>


            <div className="flex-grow bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700 flex flex-col">
                <h2 className="text-lg font-semibold text-cyan-500 dark:text-cyan-400 mb-3">Route Analysis</h2>
                <div className="space-y-4">
                    {allRoutes.map(route => (
                        <div key={route.id} className={`p-3 rounded-lg border-2 ${activeRoute.id === route.id ? 'bg-cyan-50 dark:bg-cyan-900/50 border-cyan-400' : 'bg-gray-200/50 dark:bg-gray-700/50 border-gray-300 dark:border-gray-600'}`}>
                            <h3 className="font-bold">{route.name} {activeRoute.id === route.id && <span className="text-xs text-cyan-500 dark:text-cyan-400 ml-2">(ACTIVE)</span>}</h3>
                            <div className="flex items-center justify-between mt-2">
                                <span className="text-sm font-medium">Risk: {((riskProfile[route.id]?.overall || 0) * 100).toFixed(0)}%</span>
                                <RiskBar value={riskProfile[route.id]?.overall || 0} />
                            </div>
                        </div>
                    ))}
                </div>

                {!isDisruptionTriggered && (
                    <button onClick={triggerDisruption} disabled={isLoading} className="mt-6 w-full bg-red-600 hover:bg-red-700 text-white font-bold py-3 px-4 rounded-lg transition duration-300 ease-in-out flex items-center justify-center space-x-2 disabled:bg-gray-500">
                        {isLoading ? (
                          <>
                            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                            <span>Analyzing...</span>
                          </>
                        ) : (
                          <>
                            <AlertIcon />
                            <span>Simulate Disruption Event</span>
                          </>
                        )}
                    </button>
                )}

                {isDisruptionTriggered && (
                    <div className="mt-6 p-4 bg-gray-200/50 dark:bg-gray-700/50 rounded-lg border border-gray-300 dark:border-gray-600 animate-fade-in-up">
                        <h3 className="font-bold text-yellow-500 dark:text-yellow-400 mb-2">Disruption Analysis</h3>
                        <div className="border-l-2 border-yellow-500 dark:border-yellow-400 pl-3">
                            <p className="font-semibold">{DISRUPTION_EVENT.name}</p>
                            <p className="text-sm text-gray-600 dark:text-gray-300">{DISRUPTION_EVENT.description}</p>
                            <div className="mt-4">
                                <h4 className="font-semibold text-gray-700 dark:text-gray-200">AI Recommendation:</h4>
                                {isLoading ? <p className="text-sm text-gray-500 dark:text-gray-400 italic mt-1">Generating analysis...</p> : <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">{aiAnalysis}</p>}
                            </div>
                            {!isLoading && activeRoute.id !== PRIMARY_ROUTE.id && (
                                <div className="mt-4 grid grid-cols-2 gap-2 text-center">
                                    <div className="bg-green-100 dark:bg-green-900/50 p-2 rounded">
                                        <p className="text-xl font-bold text-green-600 dark:text-green-400">{(riskReduction * 100).toFixed(0)}%</p>
                                        <p className="text-xs text-gray-500 dark:text-gray-400">Risk Reduction</p>
                                    </div>
                                    <div className="bg-yellow-100 dark:bg-yellow-900/50 p-2 rounded">
                                        <p className="text-xl font-bold text-yellow-600 dark:text-yellow-400">+{activeRoute.timeDeltaDays} Day</p>
                                        <p className="text-xs text-gray-500 dark:text-gray-400">ETA Impact</p>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Dashboard;