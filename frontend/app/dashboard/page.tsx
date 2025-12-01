'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/components/AuthProvider';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';

interface Portfolio {
    id: string;
    name: string;
    description: string;
    framework: string;
    theme: string;
    createdAt: string;
    updatedAt: string;
    status: 'draft' | 'published';
    url?: string;
    views?: number;
    thumbnail?: string;
    deploymentUrl?: string;
}

export default function DashboardPage() {
    const { user, loading } = useAuth();
    const router = useRouter();
    const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
    const [loadingPortfolios, setLoadingPortfolios] = useState(true);
    const [stats, setStats] = useState({
        total: 0,
        published: 0,
        totalViews: 0
    });

    // Dialog state
    const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
    const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);

    // Open dialog
    const openDeleteDialog = (projectId: string) => {
        setSelectedProjectId(projectId);
        setDeleteDialogOpen(true);
    };

    // Close dialog
    const closeDeleteDialog = () => {
        setDeleteDialogOpen(false);
        setSelectedProjectId(null);
    };

    // Handle project deletion (to be called after confirmation)
    const handleDelete = async () => {
        if (!selectedProjectId) return;
        try {
            await api.delete(`/api/history/${selectedProjectId}`);
            setPortfolios((prev) => prev.filter((p) => p.id !== selectedProjectId));
            closeDeleteDialog();
        } catch (err) {
            alert('Failed to delete project.');
        }
    };

    useEffect(() => {
        if (!loading && !user) {
            router.push('/auth/login');
        }
    }, [user, loading, router]);

    useEffect(() => {
        const fetchPortfolios = async () => {
            try {
                // Debug: Check if token exists
                const token = localStorage.getItem('accessToken');
                console.log('Token exists:', !!token);

                // ✅ FIX: Add leading slash
                const response = await api.get('/api/history/');

                if (response.status === 200) {
                    const data = response.data;
                    setPortfolios(data.portfolios || []);

                    const published = data.portfolios.filter((p: Portfolio) => p.status === 'published').length;

                    setStats({
                        total: data.portfolios.length,
                        published,
                        totalViews: 0
                    });
                }
            } catch (error) {
                console.error('Error fetching portfolios:', error);
            } finally {
                setLoadingPortfolios(false);
            }
        };

        if (user) {
            fetchPortfolios();
        }
    }, [user]);

    if (loading || !user) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#0d1117] via-[#161b22] to-[#010409]">
                <div className="text-center">
                    <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mb-4"></div>
                    <p className="text-white text-lg">Loading...</p>
                </div>
            </div>
        );
    }




    return (
        <>
            {/* Delete Confirmation Dialog */}
            {deleteDialogOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
                    <div className="bg-[#161b22] rounded-xl shadow-2xl p-8 w-full max-w-sm text-center border border-gray-700">
                        <svg className="mx-auto mb-4 w-12 h-12 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6M1 7h22M10 3h4a1 1 0 011 1v2H9V4a1 1 0 011-1z" />
                        </svg>
                        <h2 className="text-xl font-semibold text-white mb-2">Delete Project?</h2>
                        <p className="text-gray-400 mb-6">Are you sure you want to delete this project? This action cannot be undone.</p>
                        <div className="flex justify-center gap-4">
                            <button
                                className="px-6 py-2 rounded-lg bg-gray-700 text-gray-200 hover:bg-gray-600 transition"
                                onClick={closeDeleteDialog}
                            >
                                Cancel
                            </button>
                            <button
                                className="px-6 py-2 rounded-lg bg-red-600 text-white hover:bg-red-700 transition font-semibold"
                                onClick={handleDelete}
                            >
                                Delete
                            </button>
                        </div>
                    </div>
                </div>
            )}
            <div className="min-h-screen bg-gradient-to-br from-[#0d1117] via-[#161b22] to-[#010409]">
                {/* Header */}
                <div className="border-b border-gray-800/50 bg-[#0d1117]/50 backdrop-blur-sm">
                    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                            <div>
                                <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
                                    Dashboard
                                </h1>
                                <p className="mt-2 text-sm text-gray-400">
                                    Manage and track your portfolio projects
                                </p>
                            </div>
                            <Link
                                href="/resume"
                                className="inline-flex items-center justify-center px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-500 text-white rounded-lg hover:from-blue-700 hover:to-blue-600 transition-all shadow-lg shadow-blue-500/20 hover:shadow-blue-500/40 font-semibold"
                            >
                                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                                </svg>
                                New Project
                            </Link>
                        </div>
                    </div>
                </div>

                {/* Stats Cards */}
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {/* Total Generated */}
                        <div className="bg-[#161b22] border border-gray-800/50 rounded-xl p-6 hover:border-blue-500/30 transition-all">
                            <div className="flex items-start justify-between">
                                <div className="flex-1">
                                    <div className="flex items-center gap-2 mb-4">
                                        <div className="w-10 h-10 bg-blue-500/10 rounded-lg flex items-center justify-center">
                                            <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                                            </svg>
                                        </div>
                                        <p className="text-sm font-medium text-blue-400">Total Projects</p>
                                    </div>
                                    <p className="text-4xl font-bold text-white">{stats.total}</p>
                                    <p className="text-xs text-gray-500 mt-2">Portfolios created</p>
                                </div>
                            </div>
                        </div>

                        {/* Published */}
                        <div className="bg-[#161b22] border border-gray-800/50 rounded-xl p-6 hover:border-green-500/30 transition-all">
                            <div className="flex items-start justify-between">
                                <div className="flex-1">
                                    <div className="flex items-center gap-2 mb-4">
                                        <div className="w-10 h-10 bg-green-500/10 rounded-lg flex items-center justify-center">
                                            <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                            </svg>
                                        </div>
                                        <p className="text-sm font-medium text-green-400">Published</p>
                                    </div>
                                    <p className="text-4xl font-bold text-white">{stats.published}</p>
                                    <p className="text-xs text-gray-500 mt-2">Live portfolios</p>
                                </div>
                            </div>
                        </div>

                        {/* Drafts */}
                        <div className="bg-[#161b22] border border-gray-800/50 rounded-xl p-6 hover:border-purple-500/30 transition-all">
                            <div className="flex items-start justify-between">
                                <div className="flex-1">
                                    <div className="flex items-center gap-2 mb-4">
                                        <div className="w-10 h-10 bg-purple-500/10 rounded-lg flex items-center justify-center">
                                            <svg className="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                            </svg>
                                        </div>
                                        <p className="text-sm font-medium text-purple-400">Drafts</p>
                                    </div>
                                    <p className="text-4xl font-bold text-white">{stats.total - stats.published}</p>
                                    <p className="text-xs text-gray-500 mt-2">Work in progress</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Recent Projects */}
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-12">
                    <div className="flex items-center gap-2 mb-6">
                        <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <h2 className="text-xl font-semibold text-white">Recent Projects</h2>
                    </div>

                    {loadingPortfolios ? (
                        <div className="flex justify-center items-center h-64 bg-[#161b22] border border-gray-800/50 rounded-xl">
                            <div className="text-center">
                                <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mb-4"></div>
                                <p className="text-gray-400">Loading projects...</p>
                            </div>
                        </div>
                    ) : portfolios.length === 0 ? (
                        <div className="bg-[#161b22] border border-gray-800/50 rounded-xl p-12 text-center">
                            <div className="w-20 h-20 bg-blue-500/10 rounded-full mx-auto flex items-center justify-center mb-4">
                                <svg className="w-10 h-10 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                                </svg>
                            </div>
                            <h3 className="text-lg font-semibold text-white mb-2">No projects yet</h3>
                            <p className="text-gray-400 text-sm mb-6">Start by creating your first portfolio</p>
                            <Link
                                href="/resume"
                                className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-500 text-white rounded-lg hover:from-blue-700 hover:to-blue-600 transition-all shadow-lg shadow-blue-500/20 hover:shadow-blue-500/40 font-semibold"
                            >
                                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                                </svg>
                                Create Your First Portfolio
                            </Link>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {portfolios.map((portfolio) => (
                                <div
                                    key={portfolio.id}
                                    className="bg-[#161b22] border border-gray-800/50 rounded-xl overflow-hidden hover:border-blue-500/50 transition-all hover:shadow-lg hover:shadow-blue-500/10 group relative"
                                >
                                    {/* Clickable area for editing */}
                                    <div
                                        onClick={() => {
                                            sessionStorage.setItem('sessionId', portfolio.id);
                                            window.location.href = '/editor';
                                        }}
                                        style={{ cursor: 'pointer' }}
                                    >
                                        {/* Thumbnail */}
                                        <div className="h-40 bg-gradient-to-br from-blue-900/20 to-purple-900/20 relative border-b border-gray-800/50 overflow-hidden">
                                            {portfolio.thumbnail ? (
                                                <img src={portfolio.thumbnail} alt={portfolio.name} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
                                            ) : (
                                                <div className="flex items-center justify-center h-full">
                                                    <svg className="w-16 h-16 text-gray-700 group-hover:text-gray-600 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                                                    </svg>
                                                </div>
                                            )}
                                            {/* Status Badge */}
                                            <div className="absolute top-3 right-3">
                                                <span className={`px-3 py-1 rounded-full text-xs font-semibold backdrop-blur-sm ${portfolio.status === 'published'
                                                    ? 'bg-green-500/20 text-green-400 border border-green-500/50'
                                                    : 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/50'
                                                    }`}>
                                                    {portfolio.status === 'published' ? '● Published' : '○ Draft'}
                                                </span>
                                            </div>
                                        </div>

                                        {/* Content */}
                                        <div className="p-5 flex items-center justify-between">
                                            <div>
                                                <h3 className="text-lg font-semibold text-white truncate group-hover:text-blue-400 transition-colors flex items-center">
                                                    {portfolio.name}
                                                </h3>
                                                <p className="mt-2 text-sm text-gray-400 line-clamp-2 min-h-[40px]">
                                                    {portfolio.description || 'No description'}
                                                </p>
                                            </div>
                                            {/* Inline Delete Icon */}
                                            <button
                                                className="ml-4 p-2 text-gray-400 hover:text-red-500 transition-colors"
                                                title="Delete Project"
                                                onClick={e => {
                                                    e.stopPropagation();
                                                    openDeleteDialog(portfolio.id);
                                                }}
                                            >
                                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6M1 7h22M10 3h4a1 1 0 011 1v2H9V4a1 1 0 011-1z" />
                                                </svg>
                                            </button>
                                        </div>
                                        {/* Meta Info */}
                                        <div className="mt-4 flex items-center gap-2">
                                            <span className="px-2 py-1 bg-blue-500/10 text-blue-400 border border-blue-500/30 rounded text-xs font-medium">
                                                {portfolio.framework}
                                            </span>
                                            <span className="text-xs text-gray-500">
                                                {new Date(portfolio.updatedAt).toLocaleDateString()}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </>
    );
}
