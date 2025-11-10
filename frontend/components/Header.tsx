import React, { useState, useEffect, useRef } from 'react';
import type { Page } from '../App';
import { LogoIcon, UserIcon } from './Icons';

interface HeaderProps {
    navigate: (page: Page) => void;
    currentPage: 'dashboard' | 'settings' | 'history';
}

const Header: React.FC<HeaderProps> = ({ navigate }) => {
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);
    const dropdownRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setIsDropdownOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const headerClasses = "p-4 flex justify-between items-center border-b border-gray-200 dark:border-gray-700 bg-gray-100/80 dark:bg-gray-900/80 backdrop-blur-sm sticky top-0 z-20";

    return (
        <header className={headerClasses}>
            <div className="flex items-center space-x-2 cursor-pointer" onClick={() => navigate('dashboard')}>
                <LogoIcon className="w-6 h-6 text-cyan-500 dark:text-cyan-400" />
                <span className="text-xl font-bold text-gray-900 dark:text-white">Arkham AI</span>
            </div>
            <div className="relative" ref={dropdownRef}>
                <button onClick={() => setIsDropdownOpen(!isDropdownOpen)} className="w-10 h-10 rounded-full bg-white/50 dark:bg-gray-700/50 flex items-center justify-center border border-gray-300 dark:border-gray-600">
                    <UserIcon className="w-5 h-5 text-gray-800 dark:text-white" />
                </button>
                {isDropdownOpen && (
                    <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1 z-20 animate-fade-in-down">
                        <a onClick={() => { navigate('onboarding'); setIsDropdownOpen(false); }} className="block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer">Configuration</a>
                        <a onClick={() => { navigate('settings'); setIsDropdownOpen(false); }} className="block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer">Settings</a>
                        <div className="border-t border-gray-200 dark:border-gray-600 my-1"></div>
                        <a onClick={() => { navigate('landing'); setIsDropdownOpen(false); }} className="block px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer">Log Out</a>
                    </div>
                )}
            </div>
        </header>
    );
};

export default Header;