'use client';

import { useState } from 'react';
import FileTree from './FileTree';
import CodeEditor from './CodeEditor';
import Preview from './Preview';
import ChatPanel from './ChatPanel';
import UnlimitedTemplateGenerator from './UnlimitedTemplateGenerator';

interface EditorLayoutProps {
    stack: string;
    files: Record<string, string>;
    onFilesChange: (files: Record<string, string>) => void;
    sessionId: string;
    resumeData: any;
}

export default function EditorLayout({
    stack,
    files,
    onFilesChange,
    sessionId,
    resumeData
}: EditorLayoutProps) {
    const fileKeys = Object.keys(files);
    const [activeFile, setActiveFile] = useState<string>(
        fileKeys.find(f => f.includes('App.jsx')) || fileKeys[0] || 'src/App.jsx'
    );
    const [showChat, setShowChat] = useState(true);
    const [showPreview, setShowPreview] = useState(true);

    const handleFileChange = (path: string, content: string) => {
        onFilesChange({ ...files, [path]: content });
    };

    const handleUnlimitedTemplate = (newFiles: Record<string, string>) => {
        onFilesChange(newFiles);
    };

    return (
        <div className="h-screen flex flex-col bg-[#0a0a0a]">
            {/* Modern Header */}
            <header className="bg-[#111111] border-b border-gray-800 px-6 py-3.5 flex items-center justify-between shadow-lg">
                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                            <span className="text-white font-bold text-sm">PG</span>
                        </div>
                        <div>
                            <h1 className="text-lg font-semibold text-white">Portfolio Generator V2</h1>
                            <p className="text-xs text-gray-400">AI-Powered Development</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-2 ml-4">
                        <span className="px-3 py-1 bg-purple-500/10 text-purple-400 text-xs font-medium rounded-full border border-purple-500/20">
                            {stack.toUpperCase()}
                        </span>
                        <span className="px-3 py-1 bg-green-500/10 text-green-400 text-xs font-medium rounded-full border border-green-500/20 flex items-center gap-1.5">
                            <span className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse"></span>
                            Live
                        </span>
                    </div>
                </div>
                <div className="flex items-center gap-3">
                    <UnlimitedTemplateGenerator
                        stack={stack}
                        resumeData={resumeData}
                        onTemplateGenerated={handleUnlimitedTemplate}
                    />
                    <button
                        onClick={() => setShowPreview(!showPreview)}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${showPreview
                            ? 'bg-gray-700 text-white'
                            : 'bg-transparent text-gray-400 hover:bg-gray-800'
                            }`}
                    >
                        👁️ Preview
                    </button>
                    <button
                        onClick={() => setShowChat(!showChat)}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${showChat
                            ? 'bg-gray-700 text-white'
                            : 'bg-transparent text-gray-400 hover:bg-gray-800'
                            }`}
                    >
                        💬 AI Chat
                    </button>
                    <button className="px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg text-sm font-medium hover:from-purple-700 hover:to-pink-700 transition-all shadow-lg hover:shadow-purple-500/50">
                        💾 Export
                    </button>
                </div>
            </header>

            {/* Main Editor Area */}
            <div className="flex-1 flex overflow-hidden">
                {/* File Tree - Lovable style */}
                <div className="w-56 bg-[#0f0f0f] border-r border-gray-800 flex flex-col">
                    <div className="px-4 py-3 border-b border-gray-800">
                        <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Files</h3>
                    </div>
                    <div className="flex-1 overflow-y-auto">
                        <FileTree
                            files={fileKeys}
                            activeFile={activeFile}
                            onSelect={setActiveFile}
                        />
                    </div>
                </div>

                {/* Code Editor - Lovable style */}
                <div className="flex-1 flex flex-col min-w-0">
                    <CodeEditor
                        file={activeFile}
                        content={files[activeFile] || '// Select a file from the tree'}
                        onChange={(content: string) => handleFileChange(activeFile, content)}
                    />
                </div>

                {/* Preview - Lovable style */}
                {showPreview && (
                    <div className="flex-1 border-l border-gray-800 min-w-0">
                        <Preview files={files} stack={stack} />
                    </div>
                )}

                {/* Chat Panel - Lovable style */}
                {showChat && (
                    <div className="w-96 border-l border-gray-800">
                        <ChatPanel
                            sessionId={sessionId}
                            resumeData={resumeData}
                            currentFiles={files}
                            onFilesChange={onFilesChange}
                        />
                    </div>
                )}
            </div>
        </div>
    );
}
