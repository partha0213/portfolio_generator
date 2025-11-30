'use client';

import { useRouter } from 'next/navigation';
import { uploadResume } from '@/lib/api';
import UploadResume from '@/components/UploadResume';
import { useState } from 'react';

export default function ResumePage() {
    const router = useRouter();
    const [loading, setLoading] = useState(false);

    const handleResumeUpload = async (file: File) => {
        try {
            setLoading(true);
            const result = await uploadResume(file);

            // Store session data in sessionStorage
            sessionStorage.setItem('sessionId', result.session_id);
            sessionStorage.setItem('resumeData', JSON.stringify(result.data.data || result.data));
            sessionStorage.setItem('confidence', JSON.stringify(result.data.confidence || {}));

            // Navigate to review page
            router.push('/review');
        } catch (error) {
            console.error('Upload failed:', error);
            alert('Failed to upload resume. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return <UploadResume onUpload={handleResumeUpload} loading={loading} />;
}
