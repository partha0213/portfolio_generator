'use client';

import Link from 'next/link';
import { useAuth } from './AuthProvider';
import { useState, useRef, useEffect } from 'react';
import { usePathname } from 'next/navigation';
import { useEditor } from '@/contexts/EditorContext';

interface NavbarProps {
    // Props for editor page (kept for backward compatibility but now uses context)
    activeTab?: 'preview' | 'code';
    onTabChange?: (tab: 'preview' | 'code') => void;
    onExport?: () => void;
    onDeploy?: () => void;
}

export default function Navbar({ activeTab: propActiveTab, onTabChange: propOnTabChange, onExport: propOnExport, onDeploy: propOnDeploy }: NavbarProps) {
    const { user, logout } = useAuth();
    const pathname = usePathname();
    const { activeTab: contextActiveTab, setActiveTab, onExport: contextOnExport, onDeploy: contextOnDeploy } = useEditor();
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);
    const dropdownRef = useRef<HTMLDivElement>(null);
    const isDashboard = pathname === '/dashboard';
    const isEditor = pathname === '/editor';

    // Use context values if available, otherwise fall back to props
    const activeTab = contextActiveTab || propActiveTab;
    const onTabChange = propOnTabChange || setActiveTab;
    const onExport = propOnExport || contextOnExport;
    const onDeploy = propOnDeploy || contextOnDeploy;

    // Get user initials from name or email
    const getUserInitial = () => {
        if (user?.full_name) {
            return user.full_name.charAt(0).toUpperCase();
        }
        if (user?.email) {
            return user.email.charAt(0).toUpperCase();
        }
        return 'U';
    };

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setIsDropdownOpen(false);
            }
        };

        if (isDropdownOpen) {
            document.addEventListener('mousedown', handleClickOutside);
        }

        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [isDropdownOpen]);

    return (
        <nav className="sticky top-0 z-50 bg-gradient-to-r from-[#0d1117] via-[#161b22] to-[#0d1117] border-b border-gray-800/50 shadow-lg">
            <div className="w-full px-4 sm:px-6 lg:px-8">
                {/* Main Flex Container */}
                <div className="flex justify-between items-center h-16 gap-4">
                    
                    {/* LEFT CORNER - Logo */}
                    <Link href="/" className="flex items-center gap-3 group flex-shrink-0">
                        <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/30 group-hover:shadow-blue-500/50 transition-all">
                            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                            </svg>
                        </div>
                        <span className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent hidden sm:block">
                            Portfolio.AI
                        </span>
                    </Link>

                    {/* CENTER - Editor Controls (Only on Editor Page) */}
                    {isEditor && onTabChange && (
                        <div className="flex items-center gap-4 flex-1 justify-center">
                            {/* Preview/Code Tabs with animated background */}
                            <div className="relative flex items-center gap-1 bg-gray-800/30 p-1 rounded-lg">
                                {/* Animated background - Fixed widths to cover full buttons */}
                                <div
                                    className={`absolute top-1 bottom-1 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-md transition-all duration-300 ease-out shadow-lg shadow-blue-500/30 ${
                                        activeTab === 'preview' 
                                            ? 'left-1 w-[calc(50%-2px)]'  // Takes half the container minus gap
                                            : 'left-[calc(50%+1px)] w-[calc(50%-2px)]'  // Starts at halfway point
                                    }`}
                                />
                                
                                {/* Preview Button */}
                                <button
                                    onClick={() => onTabChange('preview')}
                                    className={`relative flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors duration-300 z-10 ${
                                        activeTab === 'preview'
                                            ? 'text-white'
                                            : 'text-gray-400 hover:text-gray-200'
                                    }`}
                                >
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                                    </svg>
                                    <span className="hidden md:inline">Preview</span>
                                </button>
                                
                                {/* Code Button */}
                                <button
                                    onClick={() => onTabChange('code')}
                                    className={`relative flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors duration-300 z-10 ${
                                        activeTab === 'code'
                                            ? 'text-white'
                                            : 'text-gray-400 hover:text-gray-200'
                                    }`}
                                >
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                                    </svg>
                                    <span className="hidden md:inline">Code</span>
                                </button>
                            </div>
                        </div>
                    )}

                    {/* RIGHT CORNER - Auth Section + Export/Deploy */}
                    <div className="flex items-center gap-3 flex-shrink-0">
                        {/* Export and Deploy Buttons (Only on Editor Page) */}
                        {isEditor && onExport && (
                            <div className="flex items-center gap-2">
                                <button
                                    onClick={() => onExport?.()}
                                    className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-purple-500 text-white rounded-lg text-sm font-medium hover:from-purple-700 hover:to-purple-600 transition-all shadow-lg shadow-purple-500/20 hover:shadow-purple-500/40"
                                >
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                                    </svg>
                                    <span className="hidden lg:inline">Export</span>
                                </button>
                                <button
                                    onClick={() => onDeploy?.()}
                                    className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-500 text-white rounded-lg text-sm font-medium hover:from-blue-700 hover:to-blue-600 transition-all shadow-lg shadow-blue-500/20 hover:shadow-blue-500/40"
                                >
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                                    </svg>
                                    <span className="hidden lg:inline">Deploy</span>
                                </button>
                            </div>
                        )}
                        
                        {/* User Authentication */}
                        {user ? (
                            <div className="relative" ref={dropdownRef}>
                                {/* Profile Avatar Button */}
                                <button
                                    onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                                    className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-800/50 transition-all group"
                                >
                                    {/* Avatar Circle */}
                                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white font-bold text-lg shadow-lg shadow-purple-500/30 group-hover:shadow-purple-500/50 transition-all">
                                        {getUserInitial()}
                                    </div>
                                    
                                    {/* Chevron Icon */}
                                    <svg 
                                        className={`w-4 h-4 text-gray-400 transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`}
                                        fill="none" 
                                        stroke="currentColor" 
                                        viewBox="0 0 24 24"
                                    >
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                    </svg>
                                </button>

                                {/* Dropdown Menu */}
                                {isDropdownOpen && (
                                    <div className="absolute right-0 mt-2 w-64 bg-[#161b22] border border-gray-800/50 rounded-xl shadow-2xl shadow-black/50 py-2 z-50">
                                        {/* User Info Section */}
                                        <div className="px-4 py-3 border-b border-gray-800/50">
                                            <div className="flex items-center gap-3">
                                                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white font-bold text-xl shadow-lg">
                                                    {getUserInitial()}
                                                </div>
                                                <div className="flex-1 min-w-0">
                                                    <p className="text-sm font-semibold text-white truncate">
                                                        {user.full_name || 'User'}
                                                    </p>
                                                    <p className="text-xs text-gray-400 truncate">
                                                        {user.email}
                                                    </p>
                                                </div>
                                            </div>
                                        </div>

                                        {/* Menu Items */}
                                        <div className="py-2">
                                            {!isDashboard && (
                                                <Link
                                                    href="/dashboard"
                                                    onClick={() => setIsDropdownOpen(false)}
                                                    className="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-300 hover:bg-gray-800/50 hover:text-white transition-all"
                                                >
                                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                                                    </svg>
                                                    Dashboard
                                                </Link>
                                            )}

                                            <button
                                                onClick={() => {
                                                    setIsDropdownOpen(false);
                                                    logout();
                                                }}
                                                className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-gray-300 hover:bg-red-500/10 hover:text-red-400 transition-all"
                                            >
                                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                                                </svg>
                                                Sign out
                                            </button>
                                        </div>
                                    </div>
                                )}
                            </div>
                        ) : (
                            <div className="flex items-center gap-3">
                                <Link 
                                    href="/auth/login" 
                                    className="px-4 py-2 text-sm font-semibold bg-gradient-to-r from-gray-700 to-gray-600 text-white hover:from-gray-600 hover:to-gray-500 rounded-lg transition-all shadow-md"
                                >
                                    Sign in
                                </Link>
                                <Link
                                    href="/auth/signup"
                                    className="px-5 py-2 bg-gradient-to-r from-blue-600 to-blue-500 text-white rounded-lg text-sm font-semibold hover:from-blue-700 hover:to-blue-600 transition-all shadow-lg shadow-blue-500/30 hover:shadow-blue-500/50"
                                >
                                    Sign up
                                </Link>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </nav>
    );
}
