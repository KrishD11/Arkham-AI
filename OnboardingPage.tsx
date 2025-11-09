import React, { useState, useEffect } from 'react';
import type { Page } from './App';
import { LogoIcon } from './components/Icons';
import type { UserConfiguration } from './types';

interface OnboardingPageProps {
    navigate: (page: Page) => void;
    setUserConfig: (config: UserConfiguration | null) => void;
    userConfig: UserConfiguration | null;
}

const OnboardingPage: React.FC<OnboardingPageProps> = ({ navigate, setUserConfig, userConfig }) => {
    const [product, setProduct] = useState('');
    const [origin, setOrigin] = useState('');
    const [destination, setDestination] = useState('');

    useEffect(() => {
        if (userConfig) {
            setProduct(userConfig.product);
            setOrigin(userConfig.origin);
            setDestination(userConfig.destination);
        }
    }, [userConfig]);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (product.trim() === '' || origin.trim() === '' || destination.trim() === '') {
            alert('Please fill out all fields.');
            return;
        }
        setUserConfig({ product, origin, destination });
        navigate('dashboard');
    };

    return (
        <div className="min-h-screen page-bg flex flex-col justify-center items-center p-4">
            <div className="w-full max-w-lg">
                <div className="bg-white/60 dark:bg-gray-800/60 backdrop-blur-lg rounded-xl shadow-lg border border-gray-300 dark:border-gray-700 p-8">
                    <div className="flex flex-col items-center mb-6">
                        <LogoIcon className="w-10 h-10 text-cyan-500 dark:text-cyan-400 mb-2" />
                        <h2 className="text-2xl font-bold text-center text-gray-800 dark:text-gray-100">
                            Configure Your Supply Chain
                        </h2>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1 text-center">
                            Set up your primary shipment to begin monitoring.
                        </p>
                    </div>
                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div>
                            <label className="block text-gray-700 dark:text-gray-300 text-sm font-bold mb-2" htmlFor="product">
                                Product Being Shipped
                            </label>
                            <input 
                                className="shadow-sm appearance-none border rounded w-full py-3 px-4 bg-gray-50 dark:bg-gray-700 text-gray-700 dark:text-gray-200 leading-tight focus:outline-none focus:ring-2 focus:ring-cyan-500" 
                                id="product" 
                                type="text" 
                                placeholder="e.g., High-Performance Semiconductors" 
                                value={product}
                                onChange={(e) => setProduct(e.target.value)}
                                required 
                            />
                        </div>
                        <div>
                             <label className="block text-gray-700 dark:text-gray-300 text-sm font-bold mb-2" htmlFor="origin">
                                Origin Port
                            </label>
                            <input
                                id="origin"
                                type="text"
                                value={origin}
                                onChange={(e) => setOrigin(e.target.value)}
                                placeholder="e.g., Port of Taipei, Taiwan"
                                className="shadow-sm appearance-none border rounded w-full py-3 px-4 bg-gray-50 dark:bg-gray-700 text-gray-700 dark:text-gray-200 leading-tight focus:outline-none focus:ring-2 focus:ring-cyan-500"
                                required
                            />
                        </div>
                        <div>
                             <label className="block text-gray-700 dark:text-gray-300 text-sm font-bold mb-2" htmlFor="destination">
                                Destination Port
                            </label>
                            <input
                                id="destination"
                                type="text"
                                value={destination}
                                onChange={(e) => setDestination(e.target.value)}
                                placeholder="e.g., Port of Los Angeles, USA"
                                className="shadow-sm appearance-none border rounded w-full py-3 px-4 bg-gray-50 dark:bg-gray-700 text-gray-700 dark:text-gray-200 leading-tight focus:outline-none focus:ring-2 focus:ring-cyan-500"
                                required
                            />
                        </div>
                        <div className="pt-2">
                            <button className="bg-cyan-500 hover:bg-cyan-600 text-white font-bold py-3 px-4 rounded-lg focus:outline-none focus:shadow-outline w-full transition" type="submit">
                                {userConfig ? 'Update Configuration' : 'Save & Go to Dashboard'}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default OnboardingPage;