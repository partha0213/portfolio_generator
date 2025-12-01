'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import EditorLayout from '@/components/Editor/EditorLayout';

export default function EditorPage() {
    const router = useRouter();
    const [files, setFiles] = useState<Record<string, string>>({});
    const [stack, setStack] = useState<string | null>(null);
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [projectId, setProjectId] = useState<string | null>(null);
    const [resumeData, setResumeData] = useState<any>(null);

    useEffect(() => {
        const filesData = sessionStorage.getItem('generatedFiles');
        const stackData = sessionStorage.getItem('selectedStack');
        const id = sessionStorage.getItem('sessionId');
        const projId = sessionStorage.getItem('projectId');
        const data = sessionStorage.getItem('resumeData');

        if (!filesData || !stackData || !id) {
            router.push('/resume');
            return;
        }

        setFiles(JSON.parse(filesData));
        setStack(stackData);
        setSessionId(id);
        setProjectId(projId);
        setResumeData(data ? JSON.parse(data) : null);
    }, [router]);

    if (!stack || !sessionId) {
        return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
    }

    return (
        <EditorLayout
            files={files}
            onFilesChange={setFiles}
            stack={stack}
            sessionId={sessionId}
            projectId={projectId || undefined}
            resumeData={resumeData}
        />
    );
}
