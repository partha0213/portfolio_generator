'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/components/AuthProvider';
import { api, generatePortfolio } from '@/lib/api';

interface UploadResumeProps {
    onUpload?: (file: File, prompt: string) => void;
    loading?: boolean;
}

export default function UploadResume({ onUpload, loading: externalLoading }: UploadResumeProps) {
    const [file, setFile] = useState<File | null>(null);
    const [prompt, setPrompt] = useState('');
    const [loading, setLoading] = useState(externalLoading || false);
    const [error, setError] = useState('');
    const router = useRouter();
    const { user } = useAuth();

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files?.[0];
        if (selectedFile) {
            if (selectedFile.size > 10 * 1024 * 1024) {
                setError('File size must be less than 10MB');
                return;
            }
            setFile(selectedFile);
            setError('');
        }
    };

    const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        e.currentTarget.classList.add('border-blue-500', 'bg-gray-800/50');
    };

    const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
        e.currentTarget.classList.remove('border-blue-500', 'bg-gray-800/50');
    };

    const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        e.currentTarget.classList.remove('border-blue-500', 'bg-gray-800/50');
        const droppedFile = e.dataTransfer.files?.[0];
        if (droppedFile) {
            setFile(droppedFile);
            setError('');
        }
    };

    const handleGenerate = async () => {
        if (!file) {
            setError('Please upload a resume');
            return;
        }
        if (!prompt.trim()) {
            setError('Please enter a portfolio description');
            return;
        }

        setLoading(true);
        try {
            // Step 1: Upload resume
            const formData = new FormData();
            formData.append('file', file);
            formData.append('prompt', prompt);

            const response = await api.post('/api/resume/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });

            const data = response.data;

            console.log('📤 Resume upload response:', data);
            console.log('📝 Resume data:', data.data);

            // The response structure is: { session_id, data: resume_data, prompt }
            const resumeData = data.data;
            const sessionId = data.session_id;

            console.log('🚀 Auto-generating portfolio with Next.js...');

            // Step 2: Automatically generate portfolio with Next.js
            const result = await generatePortfolio(sessionId, 'nextjs', { prompt }, resumeData);

            console.log('✅ Generation successful:', result);

            // Store generated files, stack, and project_id
            sessionStorage.setItem('sessionId', sessionId);
            sessionStorage.setItem('resumeData', JSON.stringify(resumeData));
            sessionStorage.setItem('userPrompt', prompt);
            sessionStorage.setItem('generatedFiles', JSON.stringify(result.files));
            sessionStorage.setItem('selectedStack', 'nextjs');
            if (result.project_id) {
                sessionStorage.setItem('projectId', result.project_id);
                console.log('💾 Stored project_id:', result.project_id);
            }

            // Navigate directly to editor
            router.push('/editor');
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-[#0d1117] via-[#161b22] to-[#010409] flex items-center justify-center px-6 py-12">
            <div className="max-w-2xl w-full">
                {/* Heading */}
                <div className="text-center mb-12">
                    <h1 className="text-5xl md:text-6xl font-bold bg-gradient-to-r from-blue-400 via-cyan-400 to-purple-400 bg-clip-text text-transparent mb-4">
                        What's stopping you?
                    </h1>
                    <p className="text-xl text-gray-400">
                        Upload your resume and describe your ideal Next.js portfolio
                    </p>
                </div>

                {/* Main Form Card */}
                <div className="bg-[#161b22] rounded-2xl shadow-2xl shadow-black/50 p-8 md:p-12 border border-gray-800/50">
                    <div className="space-y-6">
                        {/* Error Alert */}
                        {error && (
                            <div className="bg-red-500/10 border-l-4 border-red-500 p-4 rounded-lg">
                                <p className="text-red-400 text-sm font-medium">{error}</p>
                            </div>
                        )}

                        {/* Resume Upload */}
                        <div>
                            <label className="block text-sm font-semibold text-white mb-3">
                                Upload Resume {file && <span className="text-green-400">✓</span>}
                            </label>
                            <div
                                onDragOver={handleDragOver}
                                onDragLeave={handleDragLeave}
                                onDrop={handleDrop}
                                className="relative border-2 border-dashed border-gray-700 rounded-lg p-8 text-center hover:border-blue-500 transition cursor-pointer bg-[#0d1117] hover:bg-gray-800/50"
                            >
                                <input
                                    type="file"
                                    accept=".pdf,.doc,.docx"
                                    onChange={handleFileSelect}
                                    className="hidden"
                                    id="resume-upload"
                                    disabled={loading}
                                />
                                <label htmlFor="resume-upload" className="cursor-pointer block">
                                    <div className="mb-2 text-3xl">📄</div>
                                    <p className="text-sm font-medium text-white">
                                        {file ? file.name : 'Click to upload or drag and drop'}
                                    </p>
                                    <p className="text-xs text-gray-500 mt-1">PDF, DOC, or DOCX</p>
                                </label>
                            </div>
                        </div>

                        {/* Prompt Input */}
                        <div>
                            <label className="block text-sm font-semibold text-white mb-3">
                                Portfolio Description
                            </label>
                            <div className="relative">
                                <textarea
                                    value={prompt}
                                    onChange={(e) => setPrompt(e.target.value)}
                                    placeholder="Tell us about the portfolio you want to create... (e.g., 'Modern dark theme with animated sections, showcase my 5 best projects, include testimonials, minimalist design')"
                                    className="w-full px-4 py-3 border-2 border-gray-700 rounded-lg bg-[#0d1117] text-white placeholder-gray-500 focus:border-blue-500 focus:outline-none resize-none h-32 text-sm transition"
                                    disabled={loading}
                                />
                            </div>
                        </div>

                        {/* Action Buttons */}
                        <div className="flex gap-3 pt-4">
                            <button
                                onClick={handleGenerate}
                                disabled={loading || !file}
                                className="flex-1 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-700 hover:to-blue-600 disabled:from-gray-600 disabled:to-gray-600 text-white font-semibold py-3 rounded-lg transition shadow-lg shadow-blue-500/20 hover:shadow-blue-500/40 disabled:cursor-not-allowed disabled:shadow-none"
                            >
                                {loading ? (
                                    <span className="flex items-center justify-center gap-2">
                                        <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                        </svg>
                                        Generating Next.js Portfolio...
                                    </span>
                                ) : (
                                    'Generate Next.js Portfolio'
                                )}
                            </button>
                            <button
                                onClick={() => setFile(null)}
                                disabled={loading}
                                className="px-4 py-3 border-2 border-gray-700 rounded-lg text-gray-300 font-semibold hover:bg-gray-800/50 hover:border-gray-600 transition disabled:opacity-50"
                            >
                                ⚙️
                            </button>
                        </div>

                        {/* Support Info */}
                        <div className="flex items-center gap-2 justify-center pt-2 text-sm text-gray-500">
                            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                            </svg>
                            <span>Max 10MB • Powered by AI • Next.js 15</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
