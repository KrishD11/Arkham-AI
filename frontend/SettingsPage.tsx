import React, { useState } from 'react';
import type { Page, Theme } from './App';
import Header from './components/Header';
import { UserIcon } from './components/Icons';

interface SettingsPageProps {
    navigate: (page: Page) => void;
}

const SettingsPage: React.FC<SettingsPageProps> = ({ navigate }) => {
    const [isBillingModalOpen, setIsBillingModalOpen] = useState(false);

    return (
        <>
            <div className="flex flex-col h-screen bg-gray-100 dark:bg-gray-900 text-gray-800 dark:text-gray-200 font-sans">
                <Header navigate={navigate} currentPage="settings" />
                <main className="flex-grow p-8 md:p-12 overflow-y-auto">
                    <div className="max-w-2xl mx-auto">
                        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">Settings</h1>
                        
                        <div className="bg-white dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-lg p-6 mb-8">
                            <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-gray-100">Profile</h2>
                            <div className="flex items-center space-x-4">
                                <div className="w-16 h-16 bg-gray-200 dark:bg-gray-700 rounded-full flex items-center justify-center">
                                    <UserIcon className="w-8 h-8 text-gray-500 dark:text-gray-400" />
                                </div>
                                <div>
                                    <p className="font-semibold text-lg">Jane Doe</p>
                                    <p className="text-gray-500 dark:text-gray-400">jane.doe@example.com</p>
                                    <span className="mt-1 inline-block bg-cyan-100 dark:bg-cyan-900/50 text-cyan-700 dark:text-cyan-300 text-xs font-semibold px-2.5 py-0.5 rounded-full">Free Plan</span>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
                            <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-gray-100">Preferences</h2>
                            <ul className="divide-y divide-gray-200 dark:divide-gray-700">
                                <li className="py-4 flex justify-between items-center">
                                    <span className="font-medium">Supply Chain Configuration</span>
                                    <button onClick={() => navigate('onboarding')} className="text-sm text-cyan-600 dark:text-cyan-400 hover:underline">Modify Configuration</button>
                                </li>
                                <li className="py-4 flex justify-between items-center">
                                    <span className="font-medium">Manage Billing</span>
                                    <button onClick={() => setIsBillingModalOpen(true)} className="text-sm text-cyan-600 dark:text-cyan-400 hover:underline">Update</button>
                                </li>
                            </ul>
                        </div>
                    </div>
                </main>
            </div>

            {isBillingModalOpen && (
                <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 animate-fade-in">
                    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-8 max-w-sm w-full m-4">
                        <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">Manage Billing</h2>
                        <p className="text-gray-600 dark:text-gray-400 mb-6">Choose a method to link for your subscription.</p>
                        <div className="space-y-3">
                            <button onClick={() => navigate('404')} className="w-full text-left p-3 bg-gray-100 dark:bg-gray-700/50 hover:bg-gray-200 dark:hover:bg-gray-600/50 rounded-lg transition">Link Credit Card</button>
                            <button onClick={() => navigate('404')} className="w-full text-left p-3 bg-gray-100 dark:bg-gray-700/50 hover:bg-gray-200 dark:hover:bg-gray-600/50 rounded-lg transition">Link Bank Account</button>
                        </div>
                        <button onClick={() => setIsBillingModalOpen(false)} className="mt-6 w-full text-center p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition">Cancel</button>
                    </div>
                </div>
            )}
        </>
    );
};

export default SettingsPage;