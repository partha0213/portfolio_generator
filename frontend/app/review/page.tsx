'use client';

import { useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';
import ReviewData from '@/components/ReviewData';

export default function ReviewPage() {
    const router = useRouter();
    const [resumeData, setResumeData] = useState<any>(null);
    const [confidence, setConfidence] = useState<any>(null);

    useEffect(() => {
        // Load data from sessionStorage
        const data = sessionStorage.getItem('resumeData');
        const conf = sessionStorage.getItem('confidence');

        if (!data) {
            // Redirect to upload if no data
            router.push('/resume');
            return;
        }

        setResumeData(JSON.parse(data));
        setConfidence(JSON.parse(conf || '{}'));
    }, [router]);

    const handleReviewComplete = (editedData: any) => {
        // Update resume data in sessionStorage
        sessionStorage.setItem('resumeData', JSON.stringify(editedData));

        // Navigate to stack selection
        router.push('/select-stack');
    };

    const handleBack = () => {
        router.push('/resume');
    };

    if (!resumeData) {
        return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
    }

    return (
        <ReviewData
            parsedData={resumeData}
            confidence={confidence}
            onConfirm={handleReviewComplete}
            onBack={handleBack}
        />
    );
}
