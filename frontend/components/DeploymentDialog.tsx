'use client';

import { useState } from 'react';

interface DeploymentDialogProps {
    isOpen: boolean;
    onClose: () => void;
    files: Record<string, string>;
    projectId?: string;  // Project ID (preferred)
    sessionId?: string;  // Session ID (fallback)
}

export default function DeploymentDialog({ isOpen, onClose, files, projectId, sessionId }: DeploymentDialogProps) {
    const [projectName, setProjectName] = useState('my-portfolio');
    const [selectedPlatform, setSelectedPlatform] = useState<'vercel' | 'netlify'>('vercel');
    const [isDeploying, setIsDeploying] = useState(false);
    const [deployStatus, setDeployStatus] = useState<'idle' | 'deploying' | 'success' | 'error'>('idle');
    const [deployedUrl, setDeployedUrl] = useState('');
    const [errorMessage, setErrorMessage] = useState('');

    const handleDeploy = async () => {
        if (!projectName.trim()) {
            setErrorMessage('Project name is required');
            return;
        }

        setIsDeploying(true);
        setDeployStatus('deploying');
        setErrorMessage('');

        try {
            const token = localStorage.getItem('accessToken');
            if (!token) {
                setErrorMessage('Authentication required');
                setDeployStatus('error');
                setIsDeploying(false);
                return;
            }

            // Call backend deployment API
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/generate/lovable/deploy`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    project_id: projectId,
                    session_id: sessionId,
                    platform: selectedPlatform,
                    project_name: projectName
                })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Deployment failed' }));
                throw new Error(errorData.detail || `HTTP ${response.status}`);
            }

            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error || 'Deployment failed');
            }

            // Use the URL directly if available
            if (data.url) {
                setDeployedUrl(data.url);
                setDeployStatus('success');
            } else {
                // Generate URL from project name if not provided
                const domain = selectedPlatform === 'vercel' ? 'vercel.app' : 'netlify.app';
                const deployedLink = `https://${projectName.toLowerCase().replace(/\s+/g, '-')}.${domain}`;
                setDeployedUrl(deployedLink);
                setDeployStatus('success');
            }
        } catch (error) {
            console.error('Deployment error:', error);
            setErrorMessage(error instanceof Error ? error.message : 'Deployment failed. Please try again.');
            setDeployStatus('error');
        } finally {
            setIsDeploying(false);
        }
    };

    const copyToClipboard = () => {
        navigator.clipboard.writeText(deployedUrl);
        alert('URL copied to clipboard!');
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-[#161b22] border border-gray-800/50 rounded-2xl shadow-2xl shadow-black/50 max-w-md w-full p-6">
                {/* Header */}
                <div className="flex items-center justify-between mb-6">
                    <h2 className="text-2xl font-bold text-white">Deploy Portfolio</h2>
                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-white transition-colors"
                    >
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                {deployStatus === 'idle' && (
                    <>
                        {/* Platform Selection */}
                        <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-300 mb-2">
                                Deployment Platform
                            </label>
                            <div className="relative">
                                <select
                                    value={selectedPlatform}
                                    onChange={(e) => setSelectedPlatform(e.target.value as 'vercel' | 'netlify')}
                                    className="w-full bg-[#0d1117] border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none cursor-pointer"
                                >
                                    <option value="vercel">Vercel</option>
                                    <option value="netlify">Netlify</option>
                                </select>
                                <div className="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none">
                                    <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                    </svg>
                                </div>
                            </div>
                        </div>

                        {/* Project Name Input */}
                        <div className="mb-6">
                            <label className="block text-sm font-medium text-gray-300 mb-2">
                                Project Name
                            </label>
                            <input
                                type="text"
                                value={projectName}
                                onChange={(e) => setProjectName(e.target.value)}
                                placeholder="my-portfolio"
                                className="w-full bg-[#0d1117] border border-gray-700 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                            <p className="text-xs text-gray-500 mt-1">
                                Your site will be deployed to: {projectName.toLowerCase().replace(/\s+/g, '-')}.{selectedPlatform === 'vercel' ? 'vercel.app' : 'netlify.app'}
                            </p>
                        </div>

                        {/* Error Message */}
                        {errorMessage && (
                            <div className="mb-4 bg-red-500/10 border border-red-500/50 text-red-400 px-4 py-2 rounded-lg text-sm">
                                {errorMessage}
                            </div>
                        )}

                        {/* Deploy Button */}
                        <button
                            onClick={handleDeploy}
                            disabled={isDeploying}
                            className="w-full bg-gradient-to-r from-blue-600 to-blue-500 text-white rounded-lg px-4 py-3 font-medium hover:from-blue-700 hover:to-blue-600 transition-all shadow-lg shadow-blue-500/20 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                        >
                            {isDeploying ? (
                                <>
                                    <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                    Deploying...
                                </>
                            ) : (
                                <>
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                                    </svg>
                                    Deploy Now
                                </>
                            )}
                        </button>

                        {/* Info Message */}
                        <div className="mt-4 p-4 bg-blue-500/10 border border-blue-500/50 rounded-lg">
                            <p className="text-xs text-blue-300">
                                ℹ️ Your portfolio will be deployed to {selectedPlatform === 'vercel' ? 'Vercel' : 'Netlify'}. A new browser tab will open to complete the deployment.
                            </p>
                        </div>
                    </>
                )}

                {deployStatus === 'deploying' && (
                    <div className="text-center py-8">
                        <svg className="w-16 h-16 animate-spin text-blue-500 mx-auto mb-4" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        <p className="text-white font-medium">Deploying your portfolio...</p>
                        <p className="text-gray-400 text-sm mt-2">This may take a few moments</p>
                    </div>
                )}

                {deployStatus === 'success' && (
                    <div className="text-center py-8">
                        <div className="w-16 h-16 bg-green-500/20 border border-green-500 rounded-full flex items-center justify-center mx-auto mb-4">
                            <svg className="w-8 h-8 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                        </div>
                        <p className="text-white font-bold text-lg mb-2">Deployment Successful! 🎉</p>
                        <p className="text-gray-400 text-sm mb-4">Your portfolio is now live</p>

                        {/* Deployed URL */}
                        <div className="bg-[#0d1117] border border-gray-700 rounded-lg p-4 mb-4">
                            <p className="text-xs text-gray-400 mb-2">Your Portfolio URL:</p>
                            <div className="flex items-center gap-2">
                                <input
                                    type="text"
                                    value={deployedUrl}
                                    readOnly
                                    className="flex-1 bg-[#161b22] border border-gray-600 rounded px-3 py-2 text-sm text-blue-400 focus:outline-none"
                                />
                                <button
                                    onClick={copyToClipboard}
                                    className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded transition-colors flex items-center gap-1"
                                >
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                                    </svg>
                                    Copy
                                </button>
                            </div>
                        </div>

                        {/* Action Buttons */}
                        <div className="flex gap-3">
                            <a
                                href={deployedUrl}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex-1 bg-green-600 hover:bg-green-700 text-white rounded-lg px-4 py-2 font-medium transition-colors"
                            >
                                Visit Site
                            </a>
                            <button
                                onClick={onClose}
                                className="flex-1 bg-gray-700 hover:bg-gray-600 text-white rounded-lg px-4 py-2 font-medium transition-colors"
                            >
                                Close
                            </button>
                        </div>
                    </div>
                )}

                {deployStatus === 'error' && (
                    <div className="text-center py-8">
                        <div className="w-16 h-16 bg-red-500/20 border border-red-500 rounded-full flex items-center justify-center mx-auto mb-4">
                            <svg className="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </div>
                        <p className="text-white font-bold text-lg mb-2">Deployment Failed</p>
                        <p className="text-red-400 text-sm mb-4">{errorMessage}</p>

                        <button
                            onClick={() => setDeployStatus('idle')}
                            className="w-full bg-blue-600 hover:bg-blue-700 text-white rounded-lg px-4 py-2 font-medium transition-colors"
                        >
                            Try Again
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}
