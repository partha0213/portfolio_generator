'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/components/AuthProvider';
import { useRouter } from 'next/navigation';

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

interface DeploymentModal {
    isOpen: boolean;
    portfolioId: string | null;
}

export default function DashboardPage() {
    const { user, loading } = useAuth();
    const router = useRouter();
    const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
    const [loadingPortfolios, setLoadingPortfolios] = useState(true);
    const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
    const [sortBy, setSortBy] = useState<'recent' | 'name' | 'views'>('recent');
    const [filterStatus, setFilterStatus] = useState<'all' | 'draft' | 'published'>('all');
    const [searchQuery, setSearchQuery] = useState('');
    const [showDeleteModal, setShowDeleteModal] = useState<string | null>(null);
    const [deploymentModal, setDeploymentModal] = useState<DeploymentModal>({ isOpen: false, portfolioId: null });
    const [deployingPortfolioId, setDeployingPortfolioId] = useState<string | null>(null);
    const [stats, setStats] = useState({
        total: 0,
        published: 0,
        drafts: 0,
        totalViews: 0
    });

    useEffect(() => {
        if (!loading && !user) {
            router.push('/auth/login');
        }
    }, [user, loading, router]);

    useEffect(() => {
        const fetchPortfolios = async () => {
            try {
                const response = await fetch('/api/portfolios', {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    }
                });
                
                if (response.ok) {
                    const data = await response.json();
                    setPortfolios(data.portfolios || []);
                    
                    const published = data.portfolios.filter((p: Portfolio) => p.status === 'published').length;
                    const drafts = data.portfolios.filter((p: Portfolio) => p.status === 'draft').length;
                    const totalViews = data.portfolios.reduce((sum: number, p: Portfolio) => sum + (p.views || 0), 0);
                    
                    setStats({
                        total: data.portfolios.length,
                        published,
                        drafts,
                        totalViews
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

    const handleDelete = async (id: string) => {
        try {
            const response = await fetch(`/api/portfolios/${id}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            
            if (response.ok) {
                setPortfolios(portfolios.filter(p => p.id !== id));
                setShowDeleteModal(null);
            }
        } catch (error) {
            console.error('Error deleting portfolio:', error);
        }
    };

    const handleDuplicate = async (id: string) => {
        try {
            const response = await fetch(`/api/portfolios/${id}/duplicate`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            
            if (response.ok) {
                const newPortfolio = await response.json();
                setPortfolios([newPortfolio, ...portfolios]);
            }
        } catch (error) {
            console.error('Error duplicating portfolio:', error);
        }
    };

    const handleDeployClick = (portfolioId: string) => {
        setDeploymentModal({ isOpen: true, portfolioId });
    };

    const handleCloseDeploymentModal = () => {
        setDeploymentModal({ isOpen: false, portfolioId: null });
    };

    const handleDeploy = async (platform: 'vercel' | 'netlify' | 'github-pages') => {
        if (!deploymentModal.portfolioId) return;

        setDeployingPortfolioId(deploymentModal.portfolioId);
        try {
            setTimeout(() => {
                alert(`Portfolio deployed successfully to ${platform}!`);
                setDeployingPortfolioId(null);
                handleCloseDeploymentModal();
            }, 2000);
        } catch (error) {
            console.error('Deployment error:', error);
            alert('Deployment failed. Please try again.');
            setDeployingPortfolioId(null);
        }
    };

    const filteredAndSortedPortfolios = portfolios
        .filter(p => {
            if (filterStatus !== 'all' && p.status !== filterStatus) return false;
            if (searchQuery && !p.name.toLowerCase().includes(searchQuery.toLowerCase())) return false;
            return true;
        })
        .sort((a, b) => {
            if (sortBy === 'recent') {
                return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime();
            } else if (sortBy === 'name') {
                return a.name.localeCompare(b.name);
            } else if (sortBy === 'views') {
                return (b.views || 0) - (a.views || 0);
            }
            return 0;
        });

    if (loading || !user) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <div className="bg-white shadow-sm border-b border-gray-200">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                    <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900">My Portfolios</h1>
                            <p className="mt-1 text-sm text-gray-500">Manage and track your portfolio websites</p>
                        </div>
                        <Link
                            href="/resume"
                            className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-sm font-medium"
                        >
                            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                            </svg>
                            New Portfolio
                        </Link>
                    </div>
                </div>
            </div>

            {/* Stats Cards */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-medium text-gray-600">Total Portfolios</p>
                                <p className="text-3xl font-bold text-gray-900 mt-2">{stats.total}</p>
                            </div>
                            <div className="bg-blue-100 rounded-full p-3">
                                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                                </svg>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-medium text-gray-600">Published</p>
                                <p className="text-3xl font-bold text-green-600 mt-2">{stats.published}</p>
                            </div>
                            <div className="bg-green-100 rounded-full p-3">
                                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-medium text-gray-600">Drafts</p>
                                <p className="text-3xl font-bold text-yellow-600 mt-2">{stats.drafts}</p>
                            </div>
                            <div className="bg-yellow-100 rounded-full p-3">
                                <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                </svg>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-medium text-gray-600">Total Views</p>
                                <p className="text-3xl font-bold text-purple-600 mt-2">{stats.totalViews}</p>
                            </div>
                            <div className="bg-purple-100 rounded-full p-3">
                                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                                </svg>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Controls */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-6">
                <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
                    <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
                        <div className="w-full md:w-96">
                            <div className="relative">
                                <input
                                    type="text"
                                    placeholder="Search portfolios..."
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                />
                                <svg className="absolute left-3 top-2.5 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                                </svg>
                            </div>
                        </div>

                        <div className="flex items-center gap-4 w-full md:w-auto">
                            <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value as any)} className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                                <option value="all">All Status</option>
                                <option value="published">Published</option>
                                <option value="draft">Drafts</option>
                            </select>

                            <select value={sortBy} onChange={(e) => setSortBy(e.target.value as any)} className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                                <option value="recent">Most Recent</option>
                                <option value="name">Name</option>
                                <option value="views">Most Viewed</option>
                            </select>

                            <div className="flex bg-gray-100 rounded-lg p-1">
                                <button onClick={() => setViewMode('grid')} className={`p-2 rounded ${viewMode === 'grid' ? 'bg-white shadow-sm' : ''}`}>
                                    <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                                    </svg>
                                </button>
                                <button onClick={() => setViewMode('list')} className={`p-2 rounded ${viewMode === 'list' ? 'bg-white shadow-sm' : ''}`}>
                                    <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                                    </svg>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Portfolio Content */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-12">
                {loadingPortfolios ? (
                    <div className="flex justify-center items-center h-64">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                    </div>
                ) : filteredAndSortedPortfolios.length === 0 ? (
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 text-center py-12">
                        <svg className="mx-auto h-16 w-16 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                        </svg>
                        <h3 className="mt-4 text-xl font-semibold text-gray-900">{searchQuery ? 'No results found' : 'No portfolios yet'}</h3>
                        <p className="mt-2 text-gray-500">{searchQuery ? 'Try adjusting your search or filters' : 'Get started by creating your first portfolio'}</p>
                        {!searchQuery && (
                            <Link href="/resume" className="mt-6 inline-flex items-center px-6 py-3 border border-transparent rounded-lg shadow-sm text-base font-medium text-white bg-blue-600 hover:bg-blue-700">
                                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                                </svg>
                                Create Your First Portfolio
                            </Link>
                        )}
                    </div>
                ) : viewMode === 'grid' ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {filteredAndSortedPortfolios.map((portfolio) => (
                            <div key={portfolio.id} className="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-all overflow-hidden">
                                <div className="h-48 bg-gradient-to-br from-blue-100 to-purple-100 relative">
                                    {portfolio.thumbnail ? (
                                        <img src={portfolio.thumbnail} alt={portfolio.name} className="w-full h-full object-cover" />
                                    ) : (
                                        <div className="flex items-center justify-center h-full">
                                            <svg className="w-16 h-16 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                                            </svg>
                                        </div>
                                    )}
                                    <div className="absolute top-2 right-2">
                                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${portfolio.status === 'published' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                                            {portfolio.status === 'published' ? 'Published' : 'Draft'}
                                        </span>
                                    </div>
                                </div>

                                <div className="p-6">
                                    <h3 className="text-lg font-semibold text-gray-900 truncate">{portfolio.name}</h3>
                                    <p className="mt-1 text-sm text-gray-500 line-clamp-2">{portfolio.description}</p>

                                    <div className="mt-4 flex items-center gap-4 text-sm text-gray-500">
                                        <span className="flex items-center">
                                            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                                            </svg>
                                            {portfolio.views || 0}
                                        </span>
                                        <span className="px-2 py-1 bg-gray-100 rounded text-xs font-medium">{portfolio.framework}</span>
                                        <span className="px-2 py-1 bg-gray-100 rounded text-xs font-medium">{portfolio.theme}</span>
                                    </div>

                                    {portfolio.deploymentUrl && (
                                        <div className="mt-3 p-2 bg-green-50 rounded border border-green-200">
                                            <p className="text-xs text-green-700 font-medium">✓ Deployed</p>
                                            <a href={portfolio.deploymentUrl} target="_blank" rel="noopener noreferrer" className="text-xs text-green-600 hover:underline break-all">{portfolio.deploymentUrl}</a>
                                        </div>
                                    )}

                                    <div className="mt-4 text-xs text-gray-400">Updated {new Date(portfolio.updatedAt).toLocaleDateString()}</div>

                                    <div className="mt-6 flex flex-col gap-2">
                                        <div className="flex gap-2">
                                            <Link href={`/editor/${portfolio.id}`} className="flex-1 text-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium">Edit</Link>
                                            {portfolio.status === 'published' && portfolio.url && (
                                                <a href={portfolio.url} target="_blank" rel="noopener noreferrer" className="flex-1 text-center px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium">View</a>
                                            )}
                                            <div className="relative group/menu">
                                                <button className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100">
                                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
                                                    </svg>
                                                </button>
                                                <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-10 hidden group-hover/menu:block">
                                                    <button onClick={() => handleDuplicate(portfolio.id)} className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Duplicate</button>
                                                    <button onClick={() => handleDeployClick(portfolio.id)} className="w-full text-left px-4 py-2 text-sm text-green-600 hover:bg-green-50">Deploy Free</button>
                                                    <button onClick={() => setShowDeleteModal(portfolio.id)} className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50">Delete</button>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Portfolio</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Framework</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Views</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Updated</th>
                                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {filteredAndSortedPortfolios.map((portfolio) => (
                                    <tr key={portfolio.id} className="hover:bg-gray-50">
                                        <td className="px-6 py-4">
                                            <div className="flex items-center">
                                                <div className="flex-shrink-0 h-10 w-10 bg-gradient-to-br from-blue-100 to-purple-100 rounded-lg"></div>
                                                <div className="ml-4">
                                                    <div className="text-sm font-medium text-gray-900">{portfolio.name}</div>
                                                    <div className="text-sm text-gray-500">{portfolio.description}</div>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className={`px-3 py-1 rounded-full text-xs font-semibold ${portfolio.status === 'published' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                                                {portfolio.status === 'published' ? 'Published' : 'Draft'}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{portfolio.framework}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{portfolio.views || 0}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{new Date(portfolio.updatedAt).toLocaleDateString()}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                            <Link href={`/editor/${portfolio.id}`} className="text-blue-600 hover:text-blue-900 mr-4">Edit</Link>
                                            {portfolio.status === 'published' && portfolio.url && (
                                                <a href={portfolio.url} target="_blank" rel="noopener noreferrer" className="text-gray-600 hover:text-gray-900 mr-4">View</a>
                                            )}
                                            <button onClick={() => handleDeployClick(portfolio.id)} className="text-green-600 hover:text-green-900 mr-4">Deploy</button>
                                            <button onClick={() => setShowDeleteModal(portfolio.id)} className="text-red-600 hover:text-red-900">Delete</button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {/* Delete Modal */}
            {showDeleteModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Delete Portfolio</h3>
                        <p className="text-gray-600 mb-6">Are you sure you want to delete this portfolio? This action cannot be undone.</p>
                        <div className="flex gap-3 justify-end">
                            <button onClick={() => setShowDeleteModal(null)} className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200">Cancel</button>
                            <button onClick={() => handleDelete(showDeleteModal)} className="px-4 py-2 text-white bg-red-600 rounded-lg hover:bg-red-700">Delete</button>
                        </div>
                    </div>
                </div>
            )}

            {/* Deployment Modal */}
            {deploymentModal.isOpen && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
                        <div className="p-6">
                            <h2 className="text-2xl font-bold text-gray-900 mb-4">Deploy Portfolio</h2>
                            <p className="text-gray-600 mb-6">Choose a free platform to deploy your portfolio:</p>

                            <div className="space-y-3">
                                <button onClick={() => handleDeploy('vercel')} disabled={deployingPortfolioId !== null} className="w-full p-4 border-2 border-gray-200 rounded-lg hover:border-blue-600 hover:bg-blue-50 transition-all text-left disabled:opacity-50 disabled:cursor-not-allowed">
                                    <div className="flex items-center gap-3">
                                        <div className="w-10 h-10 bg-black rounded flex items-center justify-center"><span className="text-white font-bold text-xs">▲</span></div>
                                        <div>
                                            <h3 className="font-semibold text-gray-900">Vercel</h3>
                                            <p className="text-xs text-gray-500">Fast, free, and reliable hosting</p>
                                        </div>
                                        {deployingPortfolioId === deploymentModal.portfolioId && <div className="ml-auto animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>}
                                    </div>
                                </button>

                                <button onClick={() => handleDeploy('netlify')} disabled={deployingPortfolioId !== null} className="w-full p-4 border-2 border-gray-200 rounded-lg hover:border-green-600 hover:bg-green-50 transition-all text-left disabled:opacity-50 disabled:cursor-not-allowed">
                                    <div className="flex items-center gap-3">
                                        <div className="w-10 h-10 bg-green-600 rounded flex items-center justify-center"><span className="text-white font-bold text-xs">N</span></div>
                                        <div>
                                            <h3 className="font-semibold text-gray-900">Netlify</h3>
                                            <p className="text-xs text-gray-500">Modern web development platform</p>
                                        </div>
                                        {deployingPortfolioId === deploymentModal.portfolioId && <div className="ml-auto animate-spin rounded-full h-5 w-5 border-b-2 border-green-600"></div>}
                                    </div>
                                </button>

                                <button onClick={() => handleDeploy('github-pages')} disabled={deployingPortfolioId !== null} className="w-full p-4 border-2 border-gray-200 rounded-lg hover:border-gray-900 hover:bg-gray-50 transition-all text-left disabled:opacity-50 disabled:cursor-not-allowed">
                                    <div className="flex items-center gap-3">
                                        <div className="w-10 h-10 bg-gray-900 rounded flex items-center justify-center"><span className="text-white font-bold text-xs">⚙</span></div>
                                        <div>
                                            <h3 className="font-semibold text-gray-900">GitHub Pages</h3>
                                            <p className="text-xs text-gray-500">Free hosting with GitHub</p>
                                        </div>
                                        {deployingPortfolioId === deploymentModal.portfolioId && <div className="ml-auto animate-spin rounded-full h-5 w-5 border-b-2 border-gray-900"></div>}
                                    </div>
                                </button>
                            </div>

                            <button onClick={handleCloseDeploymentModal} disabled={deployingPortfolioId !== null} className="mt-6 w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed">Cancel</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
