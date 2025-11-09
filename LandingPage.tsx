import React from 'react';
import type { Page } from './App';
import { LogoIcon } from './components/Icons';

interface LandingPageProps {
    navigate: (page: Page) => void;
}

const LandingPage: React.FC<LandingPageProps> = ({ navigate }) => {
    return (
        <div className="page-bg text-gray-800 dark:text-gray-200 font-sans min-h-screen flex flex-col">
            <header className="p-4 flex justify-between items-center border-b border-gray-300/20 dark:border-gray-700/20">
                <div className="flex items-center space-x-2">
                    <LogoIcon className="w-6 h-6 text-cyan-500 dark:text-cyan-400" />
                    <span className="text-xl font-bold text-gray-900 dark:text-white">Arkham AI</span>
                </div>
                <button 
                    onClick={() => navigate('auth')} 
                    className="bg-white/50 dark:bg-gray-700/50 hover:bg-gray-200/50 dark:hover:bg-gray-600/50 text-gray-800 dark:text-white font-semibold py-2 px-4 border border-gray-300 dark:border-gray-600 rounded-lg transition"
                >
                    Sign In
                </button>
            </header>

            <main className="flex-grow flex flex-col justify-center items-center text-center p-4">
                <div className="max-w-3xl">
                    <h1 className="text-4xl md:text-6xl font-bold tracking-tight text-gray-900 dark:text-white animate-fade-in-down">
                        Autonomous Supply Chain Intelligence
                    </h1>
                    <p className="mt-4 text-lg md:text-xl text-gray-600 dark:text-gray-400 animate-fade-in-up" style={{ animationDelay: '0.5s' }}>
                        Predict disruptions, reroute shipments, and secure your logistics with a new class of AI agent.
                    </p>
                    <button onClick={() => navigate('auth')} className="mt-8 bg-cyan-500 hover:bg-cyan-600 text-white font-bold py-3 px-8 rounded-lg transition text-lg animate-fade-in-up" style={{ animationDelay: '1s' }}>
                        Get Started for Free
                    </button>
                </div>

                <div className="mt-24 grid md:grid-cols-3 gap-8 max-w-5xl w-full">
                     <div className="bg-white/40 dark:bg-gray-800/40 p-6 rounded-xl border border-gray-300 dark:border-gray-700 backdrop-blur-sm">
                        <h3 className="font-bold text-xl text-cyan-600 dark:text-cyan-400">Real-time Risk Monitoring</h3>
                        <p className="mt-2 text-gray-600 dark:text-gray-400">Aggregates geopolitical, weather, and trade data to generate live risk profiles for any shipping route.</p>
                    </div>
                     <div className="bg-white/40 dark:bg-gray-800/40 p-6 rounded-xl border border-gray-300 dark:border-gray-700 backdrop-blur-sm">
                        <h3 className="font-bold text-xl text-cyan-600 dark:text-cyan-400">AI-Powered Rerouting</h3>
                        <p className="mt-2 text-gray-600 dark:text-gray-400">Our agent analyzes threats and autonomously executes the safest, most efficient alternative routes.</p>
                    </div>
                     <div className="bg-white/40 dark:bg-gray-800/40 p-6 rounded-xl border border-gray-300 dark:border-gray-700 backdrop-blur-sm">
                        <h3 className="font-bold text-xl text-cyan-600 dark:text-cyan-400">Interactive Visualization</h3>
                        <p className="mt-2 text-gray-600 dark:text-gray-400">Monitor your assets on a global map with dynamic risk overlays and suggested pathing in real-time.</p>
                    </div>
                </div>
            </main>

            <footer className="p-4 text-center text-gray-500 dark:text-gray-500 text-sm">
                <div className="flex justify-center space-x-4">
                    <a href="#" className="hover:text-gray-800 dark:hover:text-gray-300">Terms of Service</a>
                    <span className="text-gray-400 dark:text-gray-600">|</span>
                    <a href="#" className="hover:text-gray-800 dark:hover:text-gray-300">Privacy Policy</a>
                    <span className="text-gray-400 dark:text-gray-600">|</span>
                    <a href="#" className="hover:text-gray-800 dark:hover:text-gray-300">Cookies</a>
                </div>
            </footer>
        </div>
    );
};

export default LandingPage;