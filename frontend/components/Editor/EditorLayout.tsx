'use client';

import { useState, useEffect } from 'react';
import { useEditor } from '@/contexts/EditorContext';
import CodeEditor from './CodeEditor';
import Preview from './Preview';
import ChatPanel from './ChatPanel';
import FileTree from './FileTree';
import DeploymentDialog from '../DeploymentDialog';

// Dynamic import for jszip to avoid SSR issues
let JSZip: any = null;

if (typeof window !== 'undefined') {
    import('jszip').then((module) => {
        JSZip = module.default;
    });
}

interface EditorLayoutProps {
    stack: string;
    files: Record<string, string>;
    onFilesChange: (files: Record<string, string>) => void;
    sessionId: string;
    projectId?: string;  // Add projectId
    resumeData: any;
}

export default function EditorLayout({
    stack,
    files,
    onFilesChange,
    sessionId,
    projectId,
    resumeData
}: EditorLayoutProps) {
    const fileKeys = Object.keys(files);
    const [activeFile, setActiveFile] = useState<string>(
        fileKeys.find(f => f.includes('App.jsx')) || fileKeys[0] || 'src/App.jsx'
    );
    const { activeTab, setActiveTab: setContextActiveTab, setOnExport, setOnDeploy, isDeployDialogOpen, setIsDeployDialogOpen } = useEditor();

    const handleFileChange = (path: string, content: string) => {
        onFilesChange({ ...files, [path]: content });
    };

    const handleExportCode = async () => {
        try {
            // If jszip isn't loaded yet, wait for it
            if (!JSZip) {
                const module = await import('jszip');
                JSZip = module.default;
            }

            const zip = new JSZip();

            // Add all project files to the zip
            Object.entries(files).forEach(([path, content]) => {
                zip.file(path, content);
            });

            // Add a README file with instructions
            const readmeContent = `# Portfolio Project

This is your generated portfolio project. 

## How to use:

### For React/Vite projects:
\`\`\`bash
npm install
npm run dev
\`\`\`

### For Next.js projects:
\`\`\`bash
npm install
npm run dev
\`\`\`

## File Structure
- All necessary files are included in this project
- You can customize the code as needed
- Deploy to Vercel, Netlify, or any hosting platform

## Need help?
Check the documentation for your framework:
- React: https://react.dev
- Next.js: https://nextjs.org
- Vite: https://vitejs.dev

Happy coding! 🚀
`;
            zip.file('README.md', readmeContent);

            // Generate and download the zip file
            const content = await zip.generateAsync({ type: 'blob' });
            const url = URL.createObjectURL(content);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'portfolio-project.zip';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Export failed:', error);
            alert('Failed to export project. Please try again.');
        }
    };

    const handleDeploy = () => {
        setIsDeployDialogOpen(true);
    };

    // Update context with callbacks
    useEffect(() => {
        setOnExport(() => handleExportCode);
        setOnDeploy(() => handleDeploy);
    }, [files, setOnExport, setOnDeploy]);

    return (
        <>
            {/* Deployment Dialog */}
            <DeploymentDialog
                isOpen={isDeployDialogOpen}
                onClose={() => setIsDeployDialogOpen(false)}
                files={files}
                projectId={projectId}
                sessionId={sessionId}
            />

            <div className="h-[calc(100vh-4rem)] flex flex-col lg:flex-row bg-gradient-to-br from-[#0d1117] via-[#0d1117] to-[#010409] overflow-hidden">
                {/* LEFT SIDEBAR - Chat Interface with internal scrolling */}
                <div className="w-full lg:w-[500px] flex-shrink-0 flex flex-col border-b lg:border-b-0 lg:border-r border-gray-800/50 bg-[#010409] overflow-hidden">
                    <div className="flex-1 flex flex-col overflow-hidden bg-[#0d1117]">
                        <ChatPanel
                            sessionId={sessionId}
                            resumeData={resumeData}
                            currentFiles={files}
                            onFilesChange={onFilesChange}
                        />
                    </div>
                </div>

                {/* RIGHT PANEL - Preview/Code Area with internal scrolling */}
                <div className="w-full lg:flex-1 flex flex-col overflow-hidden">
                    {/* Content Area */}
                    <div className="flex-1 overflow-hidden">
                        {activeTab === 'preview' ? (
                            <Preview files={files} stack={stack} />
                        ) : (
                            <div className="h-full flex bg-[#0d1117] overflow-hidden">
                                <div className="w-64 border-r border-gray-800/50 bg-[#010409] flex flex-col overflow-hidden">
                                    <div className="px-4 py-3 border-b border-gray-800/50 flex-shrink-0">
                                        <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">File Explorer</h3>
                                    </div>
                                    <div className="flex-1 overflow-y-auto">
                                        <FileTree
                                            files={fileKeys}
                                            activeFile={activeFile}
                                            onSelect={setActiveFile}
                                        />
                                    </div>
                                </div>

                                <div className="flex-1 overflow-hidden">
                                    <CodeEditor
                                        file={activeFile}
                                        content={files[activeFile] || '// Select a file'}
                                        onChange={(content: string) => handleFileChange(activeFile, content)}
                                    />
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </>
    );
}
