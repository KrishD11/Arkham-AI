import React from 'react';
import type { Page } from './App';
import type { EventLog, UserConfiguration } from './types';
import Header from './components/Header';
import { INITIAL_SHIPMENT } from './constants';

interface HistoryPageProps {
    navigate: (page: Page) => void;
    eventHistory: EventLog[];
    userConfig: UserConfiguration | null;
}

const HistoryPage: React.FC<HistoryPageProps> = ({ navigate, eventHistory, userConfig }) => {
    
    const getIconForMessage = (message: string) => {
        const lowerMessage = message.toLowerCase();
        if (lowerMessage.includes('created')) return '📝';
        if (lowerMessage.includes('disruption')) return '⚠️';
        if (lowerMessage.includes('analysis')) return '🤖';
        if (lowerMessage.includes('route updated')) return '➡️';
        return '🔹';
    }

    const shipmentId = userConfig ? `ARK-SC-${userConfig.product.slice(0,3).toUpperCase()}` : INITIAL_SHIPMENT.id;

    return (
        <div className="flex flex-col h-screen bg-gray-100 dark:bg-gray-900 text-gray-800 dark:text-gray-200 font-sans">
            <Header navigate={navigate} currentPage="history" />
            <main className="flex-grow p-8 md:p-12 overflow-y-auto custom-scrollbar">
                <div className="max-w-4xl mx-auto">
                    <div className="flex items-center justify-between mb-2">
                        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Shipment History Log</h1>
                        <button 
                            onClick={() => navigate('dashboard')}
                            className="text-sm bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200 font-semibold py-2 px-4 rounded-lg transition"
                        >
                            &larr; Back to Dashboard
                        </button>
                    </div>
                    <p className="text-gray-500 dark:text-gray-400 mb-8">
                        A complete event timeline for Shipment ID: <span className="font-mono text-cyan-600 dark:text-cyan-400">{shipmentId}</span>
                    </p>

                    <div className="space-y-8 relative">
                         <div className="absolute left-5 top-2 bottom-2 w-0.5 bg-gray-300 dark:bg-gray-700 -z-0"></div>

                        {eventHistory.length > 0 ? eventHistory.slice().reverse().map((log, index) => (
                             <div key={index} className="flex items-start space-x-4 relative">
                                <div className="flex-shrink-0 w-10 h-10 bg-cyan-100 dark:bg-cyan-900/50 rounded-full flex items-center justify-center text-xl border-4 border-gray-100 dark:border-gray-900">
                                    {getIconForMessage(log.message)}
                                </div>
                                
                                <div className="bg-white dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-lg p-4 flex-grow">
                                     <p className="font-semibold text-gray-800 dark:text-gray-100">{log.message}</p>
                                    <p className="text-sm text-gray-500 dark:text-gray-400 font-mono mt-1">
                                        {log.timestamp.toLocaleString()}
                                    </p>
                                </div>
                            </div>
                        )) : (
                            <div className="text-center py-12">
                                <p className="text-gray-500 dark:text-gray-400">No events recorded yet.</p>
                            </div>
                        )}
                    </div>
                </div>
            </main>
        </div>
    );
};

export default HistoryPage;