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

    useEffect(() => {
        const id = sessionStorage.getItem('sessionId');
        const data = sessionStorage.getItem('resumeData');

        console.log('📖 SessionStorage sessionId:', id);
        console.log('📖 SessionStorage resumeData:', data);

        if (!id || !data) {
            router.push('/resume');
            return;
        }

        setSessionId(id);
        const parsedData = JSON.parse(data);
        console.log('✅ Parsed resume data:', parsedData);
        setResumeData(parsedData);
    }, [router]);

    const handleStackSelect = async (stack: string) => {
        try {
            setLoading(true);
            console.log('🚀 Generating portfolio with:');
            console.log('  Stack:', stack);
            console.log('  SessionId:', sessionId);
            console.log('  ResumeData:', resumeData);
            
            // Make sure we're sending the actual resume data, not the wrapper object
            const dataToSend = resumeData && resumeData.data ? resumeData.data : resumeData;
            console.log('📦 Data being sent to generate:', dataToSend);
            
            const result = await generatePortfolio(sessionId!, stack, {}, dataToSend);

            console.log('✅ Generation successful:', result);

            // Store generated files and stack
            sessionStorage.setItem('generatedFiles', JSON.stringify(result.files));
            sessionStorage.setItem('selectedStack', stack);

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
        return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
    }

    return <StackSelector onSelect={handleStackSelect} loading={loading} />;
}
