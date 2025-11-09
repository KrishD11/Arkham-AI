import React, { useState } from 'react';
import type { Page } from './App';
import { LogoIcon } from './components/Icons';
import type { UserConfiguration } from './types';

interface AuthPageProps {
    navigate: (page: Page) => void;
    setUserConfig: (config: UserConfiguration | null) => void;
}

const AuthPage: React.FC<AuthPageProps> = ({ navigate, setUserConfig }) => {
    const [isLogin, setIsLogin] = useState(false);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (isLogin) {
            // In a real app, you'd fetch user config here before navigating
            navigate('dashboard');
        } else {
            // On sign up, clear any existing config and go to onboarding
            setUserConfig(null);
            navigate('onboarding');
        }
    };

    return (
        <div className="min-h-screen page-bg flex flex-col justify-center items-center p-4">
            <div className="w-full max-w-md">
                <div className="bg-white/60 dark:bg-gray-800/60 backdrop-blur-lg rounded-xl shadow-lg border border-gray-300 dark:border-gray-700 p-8">
                    <div className="flex flex-col items-center mb-6">
                        <LogoIcon className="w-10 h-10 text-cyan-500 dark:text-cyan-400 mb-2" />
                        <h2 className="text-2xl font-bold text-center text-gray-800 dark:text-gray-100">
                            {isLogin ? 'Welcome Back' : 'Create Your Account'}
                        </h2>
                    </div>
                    <form onSubmit={handleSubmit}>
                        {!isLogin && (
                            <div className="mb-4">
                                <label className="block text-gray-700 dark:text-gray-300 text-sm font-bold mb-2" htmlFor="name">
                                    Full Name
                                </label>
                                <input className="shadow-sm appearance-none border rounded w-full py-2 px-3 bg-gray-50 dark:bg-gray-700 text-gray-700 dark:text-gray-200 leading-tight focus:outline-none focus:ring-2 focus:ring-cyan-500" id="name" type="text" placeholder="Jane Doe" required />
                            </div>
                        )}
                        <div className="mb-4">
                            <label className="block text-gray-700 dark:text-gray-300 text-sm font-bold mb-2" htmlFor="email">
                                Email Address
                            </label>
                            <input className="shadow-sm appearance-none border rounded w-full py-2 px-3 bg-gray-50 dark:bg-gray-700 text-gray-700 dark:text-gray-200 leading-tight focus:outline-none focus:ring-2 focus:ring-cyan-500" id="email" type="email" placeholder="jane.doe@example.com" required />
                        </div>
                        <div className="mb-6">
                            <label className="block text-gray-700 dark:text-gray-300 text-sm font-bold mb-2" htmlFor="password">
                                Password
                            </label>
                            <input className="shadow-sm appearance-none border rounded w-full py-2 px-3 bg-gray-50 dark:bg-gray-700 text-gray-700 dark:text-gray-200 mb-3 leading-tight focus:outline-none focus:ring-2 focus:ring-cyan-500" id="password" type="password" placeholder="******************" required />
                        </div>
                        <div className="flex items-center justify-between">
                            <button className="bg-cyan-500 hover:bg-cyan-600 text-white font-bold py-2 px-4 rounded-lg focus:outline-none focus:shadow-outline w-full" type="submit">
                                {isLogin ? 'Sign In' : 'Create Account'}
                            </button>
                        </div>
                    </form>
                    <p className="text-center text-gray-600 dark:text-gray-400 text-sm mt-6">
                        {isLogin ? "Don't have an account?" : 'Already have an account?'}
                        <button onClick={() => setIsLogin(!isLogin)} className="font-bold text-cyan-600 dark:text-cyan-400 hover:underline ml-2">
                            {isLogin ? 'Sign Up' : 'Sign In'}
                        </button>
                    </p>
                </div>
            </div>
            <footer className="absolute bottom-0 text-center text-gray-500 dark:text-gray-500 text-sm p-4">
                &copy; {new Date().getFullYear()} Arkham AI. All rights reserved.
            </footer>
        </div>
    );
};

export default AuthPage;
