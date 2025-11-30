'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/components/AuthProvider';

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
        e.currentTarget.classList.add('border-blue-500', 'bg-blue-50');
    };

    const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
        e.currentTarget.classList.remove('border-blue-500', 'bg-blue-50');
    };

    const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        e.currentTarget.classList.remove('border-blue-500', 'bg-blue-50');
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
            const formData = new FormData();
            formData.append('file', file);
            formData.append('prompt', prompt);

            const response = await fetch('http://localhost:8000/api/resume/upload', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to upload resume');
            }

            const data = await response.json();
            
            console.log('📤 Resume upload response:', data);
            console.log('📝 Resume data:', data.data);
            
            // Extract just the parsed data, not the wrapper with confidence scores
            const resumeData = data.data;
            
            // Store session ID and resume data in sessionStorage for the next page
            sessionStorage.setItem('sessionId', data.session_id);
            sessionStorage.setItem('resumeData', JSON.stringify(resumeData));
            
            // Verify stored data
            console.log('✅ Stored sessionId:', sessionStorage.getItem('sessionId'));
            console.log('✅ Stored resumeData:', sessionStorage.getItem('resumeData'));
            
            // Navigate to stack selection
            router.push('/select-stack');
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-orange-50 via-pink-50 to-red-50 flex items-center justify-center px-6 py-12">
            <div className="max-w-2xl w-full">
                {/* Heading */}
                <div className="text-center mb-12">
                    <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-4">
                        What's stopping you?
                    </h1>
                    <p className="text-xl text-gray-600">
                        Upload your resume and describe your ideal portfolio
                    </p>
                </div>

                {/* Main Form Card */}
                <div className="bg-white rounded-2xl shadow-lg p-8 md:p-12 border border-gray-100">
                    <div className="space-y-6">
                        {/* Error Alert */}
                        {error && (
                            <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
                                <p className="text-red-800 text-sm font-medium">{error}</p>
                            </div>
                        )}

                        {/* Resume Upload */}
                        <div>
                            <label className="block text-sm font-semibold text-gray-900 mb-3">
                                Upload Resume {file && <span className="text-green-600">✓</span>}
                            </label>
                            <div
                                onDragOver={handleDragOver}
                                onDragLeave={handleDragLeave}
                                onDrop={handleDrop}
                                className="relative border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition cursor-pointer bg-gray-50 hover:bg-gray-100"
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
                                    <p className="text-sm font-medium text-gray-900">
                                        {file ? file.name : 'Click to upload or drag and drop'}
                                    </p>
                                    <p className="text-xs text-gray-500 mt-1">PDF, DOC, or DOCX</p>
                                </label>
                            </div>
                        </div>

                        {/* Prompt Input */}
                        <div>
                            <label className="block text-sm font-semibold text-gray-900 mb-3">
                                Portfolio Description
                            </label>
                            <div className="relative">
                                <textarea
                                    value={prompt}
                                    onChange={(e) => setPrompt(e.target.value)}
                                    placeholder="Tell us about the portfolio you want to create... (e.g., 'Modern dark theme with animated sections, showcase my 5 best projects, include testimonials, minimalist design')"
                                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none resize-none h-32 text-sm"
                                    disabled={loading}
                                />
                            </div>
                        </div>

                        {/* Action Buttons */}
                        <div className="flex gap-3 pt-4">
                            <button
                                onClick={handleGenerate}
                                disabled={loading || !file}
                                className="flex-1 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 disabled:from-gray-400 disabled:to-gray-400 text-white font-semibold py-3 rounded-lg transition shadow-md hover:shadow-lg disabled:cursor-not-allowed"
                            >
                                {loading ? (
                                    <span className="flex items-center justify-center gap-2">
                                        <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                        </svg>
                                        Generating...
                                    </span>
                                ) : (
                                    'Generate Portfolio'
                                )}
                            </button>
                            <button
                                onClick={() => setFile(null)}
                                disabled={loading}
                                className="px-4 py-3 border-2 border-gray-300 rounded-lg text-gray-700 font-semibold hover:bg-gray-50 transition disabled:opacity-50"
                            >
                                ⚙️
                            </button>
                        </div>

                        {/* Support Info */}
                        <div className="flex items-center gap-2 justify-center pt-2 text-sm text-gray-600">
                            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                            </svg>
                            <span>Max 10MB • Powered by AI</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
