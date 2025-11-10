import React, { useState, useCallback, useEffect, Component, ErrorInfo, ReactNode } from 'react';
import LandingPage from './LandingPage';
import AuthPage from './AuthPage';
import DashboardPage from './DashboardPage';
import HistoryPage from './HistoryPage';
import SettingsPage from './SettingsPage';
import OnboardingPage from './OnboardingPage';
import type { EventLog, UserConfiguration } from './types';

// Error Boundary Component
class ErrorBoundary extends Component<{ children: ReactNode }, { hasError: boolean; error: Error | null }> {
    constructor(props: { children: ReactNode }) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error: Error) {
        return { hasError: true, error };
    }

    componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error('Error caught by boundary:', error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex flex-col items-center justify-center p-4">
                    <div className="bg-red-100 dark:bg-red-900/50 border border-red-400 rounded-lg p-6 max-w-md">
                        <h2 className="text-xl font-bold text-red-800 dark:text-red-200 mb-2">Something went wrong</h2>
                        <p className="text-red-700 dark:text-red-300 mb-4">
                            {this.state.error?.message || 'An unexpected error occurred'}
                        </p>
                        <button 
                            onClick={() => {
                                this.setState({ hasError: false, error: null });
                                window.location.reload();
                            }}
                            className="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded-lg transition"
                        >
                            Reload Page
                        </button>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

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

    return (
        <ErrorBoundary>
            <div className="app-container min-h-screen bg-gray-100 dark:bg-gray-900">
                {renderPage()}
            </div>
        </ErrorBoundary>
    );
};

export default App;
