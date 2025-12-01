'use client';

import { useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';
import { generatePortfolio } from '@/lib/api';
import StackSelector from '@/components/StackSelector';

export default function SelectStackPage() {
    const router = useRouter();
    const [loading, setLoading] = useState(false);
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [resumeData, setResumeData] = useState<any>(null);
    const [userPrompt, setUserPrompt] = useState<string | null>(null);

    useEffect(() => {
        const id = sessionStorage.getItem('sessionId');
        const data = sessionStorage.getItem('resumeData');
        const prompt = sessionStorage.getItem('userPrompt');

        console.log('📖 SessionStorage sessionId:', id);
        console.log('📖 SessionStorage resumeData:', data);
        console.log('📖 SessionStorage prompt:', prompt);

        if (!id || !data) {
            console.warn('⚠️ Missing session data, redirecting to resume page');
            router.push('/resume');
            return;
        }

        setSessionId(id);
        setUserPrompt(prompt);

        // Safe JSON parsing with error handling
        try {
            const parsedData = JSON.parse(data);
            console.log('✅ Parsed resume data:', parsedData);

            // The data structure from backend is already the parsed resume data
            setResumeData(parsedData);
        } catch (error) {
            console.error('❌ Failed to parse resume data:', error);
            alert('Invalid session data. Please upload your resume again.');
            router.push('/resume');
        }
    }, [router]);

    const handleStackSelect = async (stack: string) => {
        try {
            setLoading(true);
            console.log('🚀 Generating portfolio with:');
            console.log('  Stack:', stack);
            console.log('  SessionId:', sessionId);
            console.log('  UserPrompt:', userPrompt);
            console.log('  ResumeData:', resumeData);

            // Use resume data directly as received from backend
            const dataToSend = resumeData;
            console.log('📦 Data being sent to generate:', dataToSend);

            // Pass user prompt to backend for dynamic generation
            const options = {
                prompt: userPrompt,
            };

            console.log('🎨 Using dynamic generation with prompt:', userPrompt);

            const result = await generatePortfolio(sessionId!, stack, options, dataToSend);

            console.log('✅ Generation successful:', result);

            // Store generated files, stack, and project_id
            sessionStorage.setItem('generatedFiles', JSON.stringify(result.files));
            sessionStorage.setItem('selectedStack', stack);
            if (result.project_id) {
                sessionStorage.setItem('projectId', result.project_id);
                console.log('💾 Stored project_id:', result.project_id);
            }

            // Navigate to editor
            router.push('/editor');
        } catch (error) {
            console.error('❌ Generation failed:', error);
            alert('Failed to generate portfolio. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    if (!sessionId) {
        return (
            <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-[#0d1117] via-[#161b22] to-[#010409]">
                <div className="text-center">
                    <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mb-4"></div>
                    <p className="text-white text-lg">Loading...</p>
                </div>
            </div>
        );
    }

    return <StackSelector onSelect={handleStackSelect} loading={loading} />;
}
