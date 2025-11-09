import React, { useState, useCallback, useEffect } from 'react';
import LandingPage from './LandingPage';
import AuthPage from './AuthPage';
import DashboardPage from './DashboardPage';
import HistoryPage from './HistoryPage';
import SettingsPage from './SettingsPage';
import OnboardingPage from './OnboardingPage';
import type { EventLog, UserConfiguration } from './types';

export type Page = 'landing' | 'auth' | 'onboarding' | 'dashboard' | 'history' | 'settings' | '404';
export type Theme = 'light' | 'dark';

const NotFoundPage: React.FC<{ navigate: (page: Page) => void }> = ({ navigate }) => (
    <div className="min-h-screen flex flex-col items-center justify-center page-bg text-center p-4">
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white">404 - Not Found</h1>
        <p className="mt-4 text-lg text-gray-600 dark:text-gray-400">The page you're looking for doesn't exist.</p>
        <button onClick={() => navigate('dashboard')} className="mt-8 bg-cyan-500 hover:bg-cyan-600 text-white font-bold py-3 px-8 rounded-lg transition text-lg">
            Go to Dashboard
        </button>
    </div>
);


const App: React.FC = () => {
    const [page, setPage] = useState<Page>('landing');
    const [theme, setTheme] = useState<Theme>('dark');
    const [eventHistory, setEventHistory] = useState<EventLog[]>([]);
    const [userConfig, setUserConfig] = useState<UserConfiguration | null>(null);

    useEffect(() => {
        const root = window.document.documentElement;
        root.classList.remove(theme === 'dark' ? 'light' : 'dark');
        root.classList.add(theme);
    }, [theme]);

    const navigate = (newPage: Page) => {
        window.scrollTo(0, 0);
        setPage(newPage);
    };

    const addEvent = useCallback((message: string) => {
        setEventHistory(prev => [...prev, { message, timestamp: new Date() }]);
    }, []);

    const renderPage = () => {
        switch (page) {
            case 'landing':
                return <LandingPage navigate={navigate} />;
            case 'auth':
                return <AuthPage navigate={navigate} setUserConfig={setUserConfig} />;
            case 'onboarding':
                 return <OnboardingPage navigate={navigate} setUserConfig={setUserConfig} userConfig={userConfig} />;
            case 'dashboard':
                return <DashboardPage navigate={navigate} eventHistory={eventHistory} addEvent={addEvent} userConfig={userConfig} />;
            case 'history':
                return <HistoryPage navigate={navigate} eventHistory={eventHistory} userConfig={userConfig} />;
            case 'settings':
                return <SettingsPage navigate={navigate} theme={theme} setTheme={setTheme} />;
            case '404':
                return <NotFoundPage navigate={navigate} />;
            default:
                return <LandingPage navigate={navigate} />;
        }
    };

    return <div className="app-container">{renderPage()}</div>;
};

export default App;