'use client';
import { useState, useRef, useEffect } from 'react';
    import { Diff, parseDiff, Hunk, tokenize } from 'react-diff-view';
    import 'react-diff-view/style/index.css';
    import { api } from '@/lib/api';interface ChatPanelProps {
    sessionId: string;
    resumeData: any;
    currentFiles: Record<string, string>;
    onFilesChange: (files: Record<string, string>) => void;
}

interface ChatMessage {
    role: string;
    content: string;
    summary?: string; // Add summary field
    filesModified?: string[];
    thought?: string;
    thoughtTime?: number;
    toolsUsed?: any[];
    editsMade?: any[];
    codeSuggestions?: string[];
    tips?: string[];
    codeDetails?: any;
    strategyDetails?: any;
    approaches?: any[];
}

const CHAT_MODES = [
    {
        id: 'code',
        label: 'Code Changes',
        icon: (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
            </svg>
        )
    },
    {
        id: 'design',
        label: 'Design Tips',
        icon: (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
            </svg>
        )
    },
    {
        id: 'advanced-code',
        label: 'Advanced Code',
        icon: (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
        )
    },
    {
        id: 'strategy',
        label: 'Design Strategy',
        icon: (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
        )
    },
    {
        id: 'approaches',
        label: 'Multiple Options',
        icon: (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
            </svg>
        )
    }
];

// Helper function to generate unified diff format
const generateUnifiedDiff = (oldValue: string, newValue: string, filename: string): string => {
    const oldLines = oldValue.split('\n');
    const newLines = newValue.split('\n');

    let diff = `--- a/${filename}\n+++ b/${filename}\n`;
    diff += `@@ -1,${oldLines.length} +1,${newLines.length} @@\n`;

    // Simple line-by-line diff
    const maxLines = Math.max(oldLines.length, newLines.length);
    for (let i = 0; i < maxLines; i++) {
        const oldLine = oldLines[i];
        const newLine = newLines[i];

        if (oldLine === newLine) {
            diff += ` ${newLine || ''}\n`;
        } else {
            if (oldLine !== undefined) {
                diff += `-${oldLine}\n`;
            }
            if (newLine !== undefined) {
                diff += `+${newLine}\n`;
            }
        }
    }

    return diff;
};

// Helper function to get authorization headers
const getAuthHeaders = (additionalHeaders: Record<string, string> = {}) => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('accessToken') : null;
    return {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...additionalHeaders
    };
};

export default function ChatPanel({ sessionId, resumeData, currentFiles, onFilesChange }: ChatPanelProps) {
    const [messages, setMessages] = useState<ChatMessage[]>([
        { role: 'assistant', content: 'Hi! I can help you improve your portfolio with advanced AI features:\n\n• Code Changes: Modify colors, themes, layouts, fonts\n• Design Tips: Get design enhancement suggestions\n• Advanced Code: Production-quality code with accessibility & performance\n• Design Strategy: Comprehensive design approach\n• Multiple Approaches: 3 implementation options\n\nTry: "Make it more modern" or pick an advanced feature!' }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [tabMode, setTabMode] = useState<'code' | 'design' | 'advanced-code' | 'strategy' | 'approaches'>('code');
    const [showModeDropdown, setShowModeDropdown] = useState(false);
    const [expandedThoughts, setExpandedThoughts] = useState<Record<number, boolean>>({});
    const [expandedDiffs, setExpandedDiffs] = useState<Record<string, boolean>>({});
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const dropdownRef = useRef<HTMLDivElement>(null);

    // Undo/Redo State
    const [history, setHistory] = useState<string[]>([]);
    const [currentHistoryIndex, setCurrentHistoryIndex] = useState(-1);

    // Scroll to bottom when messages change
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // Load initial history and chat messages
    useEffect(() => {
        if (sessionId) {
            fetchHistory();
            loadChatMessages();
        }
    }, [sessionId]);

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setShowModeDropdown(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const fetchHistory = async () => {
        try {
            const response = await api.get(`/api/history/sessions/${sessionId}/snapshots`);
            if (response.status === 200) {
                const snapshots = response.data;
                const ids = snapshots.map((s: any) => s.id).reverse();
                setHistory(ids);
                setCurrentHistoryIndex(ids.length - 1);
            }
        } catch (e) {
            console.error("Failed to fetch history", e);
        }
    };

    const loadChatMessages = async () => {
        try {
            const response = await api.get(`/api/chat/portfolio/history/${sessionId}`);
            if (response.status === 200) {
                const data = response.data;
                if (data.messages && Array.isArray(data.messages)) {
                    setMessages(data.messages);
                }
            }
        } catch (e) {
            console.error("Failed to load chat messages", e);
        }
    };

    const saveSnapshot = async (files: Record<string, string>, description: string) => {
        try {
            const response = await api.post(`/api/history/sessions/${sessionId}/snapshot`, { files, description });
            if (response.status === 200) {
                const snapshot = response.data;
                setHistory(prev => [...prev, snapshot.id]);
                setCurrentHistoryIndex(prev => prev + 1);
            }
        } catch (e) {
            console.error("Failed to save snapshot", e);
        }
    };

    const handleUndo = async () => {
        if (currentHistoryIndex <= 0) return;

        const prevIndex = currentHistoryIndex - 1;
        const snapshotId = history[prevIndex];

        try {
            const response = await api.get(`/api/history/sessions/${sessionId}/snapshot/${snapshotId}`);
            if (response.status === 200) {
                const data = response.data;
                onFilesChange(data.files);
                setCurrentHistoryIndex(prevIndex);

                setMessages(prev => [...prev, {
                    role: 'assistant',
                    content: '↺ Undid changes. Restored previous version.'
                }]);
            }
        } catch (e) {
            console.error("Failed to undo", e);
        }
    };

    const handleRedo = async () => {
        if (currentHistoryIndex >= history.length - 1) return;

        const nextIndex = currentHistoryIndex + 1;
        const snapshotId = history[nextIndex];

        try {
            const response = await api.get(`/api/history/sessions/${sessionId}/snapshot/${snapshotId}`);
            if (response.status === 200) {
                const data = response.data;
                onFilesChange(data.files);
                setCurrentHistoryIndex(nextIndex);

                setMessages(prev => [...prev, {
                    role: 'assistant',
                    content: '↻ Redid changes. Restored next version.'
                }]);
            }
        } catch (e) {
            console.error("Failed to redo", e);
        }
    };

    const toggleThought = (index: number) => {
        setExpandedThoughts(prev => ({ ...prev, [index]: !prev[index] }));
    };

    const toggleDiff = (id: string) => {
        setExpandedDiffs(prev => ({ ...prev, [id]: !prev[id] }));
    };

    const handleSend = async () => {
        if (!input.trim() || loading) return;

        const userMessage: ChatMessage = { role: 'user', content: input };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setLoading(true);

        try {
            if (tabMode === 'code') {
                const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/chat/stream`, {
                    method: 'POST',
                    headers: getAuthHeaders(),
                    body: JSON.stringify({
                        messages: [...messages, userMessage],
                        session_id: sessionId,
                        current_files: currentFiles,
                        mode: tabMode
                    })
                });

                if (!response.ok) throw new Error('Stream failed');
                if (!response.body) throw new Error('No response body');

                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';

                setMessages(prev => [...prev, {
                    role: 'assistant',
                    content: '',
                    thought: '',
                    summary: '',
                    toolsUsed: [],
                    editsMade: []
                }]);

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split('\n\n');
                    buffer = lines.pop() || '';

                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            try {
                                const data = JSON.parse(line.slice(6));

                                setMessages(prev => {
                                    const newMessages = [...prev];
                                    const lastMsg = newMessages[newMessages.length - 1];

                                    if (data.type === 'thought_start') {
                                        if (!lastMsg.thought) lastMsg.thought = '';
                                    } else if (data.type === 'thought') {
                                        lastMsg.thought = (lastMsg.thought || '') + data.content;
                                    } else if (data.type === 'token') {
                                        lastMsg.content += data.content;
                                    } else if (data.type === 'tool') {
                                        const tools = lastMsg.toolsUsed || [];
                                        const existingIdx = tools.findIndex(t => t.name === data.data.name && t.status === 'running');
                                        if (existingIdx >= 0) {
                                            tools[existingIdx] = { ...tools[existingIdx], ...data.data };
                                        } else {
                                            tools.push(data.data);
                                        }
                                        lastMsg.toolsUsed = tools;
                                    } else if (data.type === 'result') {
                                        lastMsg.editsMade = data.data.edits_made;
                                        lastMsg.filesModified = Object.keys(data.data.refined_files);
                                        lastMsg.summary = data.data.summary || ''; // Store summary separately

                                        if (data.data.refined_files) {
                                            const updatedFiles = { ...currentFiles };
                                            Object.entries(data.data.refined_files).forEach(([filename, content]) => {
                                                updatedFiles[filename] = content as string;
                                            });
                                            onFilesChange(updatedFiles);
                                            saveSnapshot(updatedFiles, `Auto-save after: ${input.slice(0, 20)}...`);
                                        }
                                    } else if (data.type === 'error') {
                                        lastMsg.content += `\n\n❌ Error: ${data.message}`;
                                    }

                                    return newMessages;
                                });
                            } catch (e) {
                                console.error('Error parsing SSE:', e);
                            }
                        }
                    }
                }
            } else if (tabMode === 'design') {
                const response = await api.post('/api/chat/portfolio/improve', {
                    session_id: sessionId,
                    message: input,
                    user_data: resumeData
                });

                const data = response.data;
                setMessages(prev => [...prev, {
                    role: 'assistant',
                    content: data.response,
                    codeSuggestions: data.code_suggestions,
                    tips: data.design_tips
                }]);
            } else if (tabMode === 'advanced-code') {
                const response = await api.post('/api/chat/portfolio/advanced-code', {
                    session_id: sessionId,
                    request: input,
                    user_data: resumeData
                });

                const data = response.data;
                setMessages(prev => [...prev, {
                    role: 'assistant',
                    content: data.explanation,
                    codeDetails: data
                }]);
            } else if (tabMode === 'strategy') {
                const response = await api.post('/api/chat/portfolio/design-strategy', {
                    session_id: sessionId,
                    user_data: resumeData
                });

                const data = response.data;
                setMessages(prev => [...prev, {
                    role: 'assistant',
                    content: "Here is a comprehensive design strategy for your portfolio:",
                    strategyDetails: data
                }]);
            } else if (tabMode === 'approaches') {
                const response = await api.post('/api/chat/portfolio/multiple-approaches', {
                    session_id: sessionId,
                    request: input,
                    user_data: resumeData
                });

                const data = response.data;
                setMessages(prev => [...prev, {
                    role: 'assistant',
                    content: "I've generated 3 different approaches for you:",
                    approaches: data.approaches
                }]);
            }
        } catch (error) {
            console.error('Chat error:', error);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: 'Sorry, I encountered an error processing your request.'
            }]);
        } finally {
            setLoading(false);
        }
    };

    const currentMode = CHAT_MODES.find(m => m.id === tabMode) || CHAT_MODES[0];

    return (
        <div className="flex flex-col h-full bg-gray-900 text-gray-100 border-l border-gray-800">
            {/* Header with Undo/Redo only */}
            <div className="p-4 border-b border-gray-800 bg-gray-900/50 backdrop-blur-sm">
                <div className="flex justify-between items-center">
                    <h2 className="text-lg font-semibold flex items-center gap-2">
                        <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                        </svg>
                        AI Assistant
                    </h2>
                    <div className="flex gap-2">
                        <button
                            onClick={handleUndo}
                            disabled={currentHistoryIndex <= 0}
                            className={`p-2 rounded-lg hover:bg-gray-800 transition-colors ${currentHistoryIndex <= 0 ? 'opacity-30 cursor-not-allowed' : 'opacity-70 hover:opacity-100'}`}
                            title="Undo"
                        >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
                            </svg>
                        </button>
                        <button
                            onClick={handleRedo}
                            disabled={currentHistoryIndex >= history.length - 1}
                            className={`p-2 rounded-lg hover:bg-gray-800 transition-colors ${currentHistoryIndex >= history.length - 1 ? 'opacity-30 cursor-not-allowed' : 'opacity-70 hover:opacity-100'}`}
                            title="Redo"
                        >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 10h-10a8 8 0 00-8 8v2m18-10l-6 6m6-6l-6-6" />
                            </svg>
                        </button>
                    </div>
                </div>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-6">
                {messages.map((msg, idx) => (
                    <div key={idx} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                        <div className={`max-w-[90%] rounded-2xl p-4 ${msg.role === 'user'
                            ? 'bg-blue-600 text-white rounded-tr-none shadow-lg shadow-blue-500/10'
                            : 'bg-gray-800 text-gray-100 rounded-tl-none border border-gray-700 shadow-xl'
                            }`}>
                            {/* Thought Process Section */}
                            {msg.thought && (
                                <div className="mb-3 border-b border-gray-700 pb-3">
                                    <button
                                        onClick={() => toggleThought(idx)}
                                        className="flex items-center gap-2 text-xs font-medium text-gray-400 hover:text-blue-400 transition-colors w-full"
                                    >
                                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                                        </svg>
                                        <span>Thought for {msg.thoughtTime || 0}s</span>
                                        <span className={`transform transition-transform ${expandedThoughts[idx] ? 'rotate-180' : ''}`}>▼</span>
                                    </button>

                                    {expandedThoughts[idx] && (
                                        <div className="mt-2 p-3 bg-gray-900/50 rounded-lg text-sm text-gray-300 font-mono leading-relaxed">
                                            {msg.thought}
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* Tool Usage Section */}
                            {msg.toolsUsed && msg.toolsUsed.length > 0 && (
                                <div className="mb-3">
                                    <div className="text-xs font-medium text-gray-500 mb-1">Used {msg.toolsUsed.length} tools</div>
                                    <div className="flex flex-wrap gap-2">
                                        {msg.toolsUsed.map((tool, i) => (
                                            <div key={i} className="flex items-center gap-1.5 px-2 py-1 bg-gray-900/50 rounded text-xs text-gray-400 border border-gray-700/50">
                                                <span className={`w-1.5 h-1.5 rounded-full ${tool.status === 'success' ? 'bg-green-500' : 'bg-red-500'}`}></span>
                                                {tool.name} ({tool.duration}s)
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Main Content - Show Summary if available, otherwise content */}
                            {msg.summary ? (
                                <div className="whitespace-pre-wrap leading-relaxed text-gray-100">
                                    {msg.summary}
                                </div>
                            ) : msg.content ? (
                                <div className="whitespace-pre-wrap leading-relaxed">{msg.content}</div>
                            ) : null}

                            {/* File Edits Section with Diffs - Collapsible */}
                            {msg.editsMade && msg.editsMade.length > 0 && (
                                <div className="mt-4 pt-3 border-t border-gray-700">
                                    <button
                                        onClick={() => toggleThought(idx + 10000)} // Use different index for edits
                                        className="text-xs font-medium text-gray-400 mb-2 flex items-center gap-2 hover:text-blue-400 transition-colors w-full"
                                    >
                                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                        </svg>
                                        <span>{msg.editsMade.length} edits made</span>
                                        <span className={`transform transition-transform text-gray-500 text-xs ${expandedThoughts[idx + 10000] ? 'rotate-180' : ''}`}>▼</span>
                                    </button>
                                    {expandedThoughts[idx + 10000] && (
                                        <div className="space-y-2 mt-2">
                                            {msg.editsMade.map((edit, i) => {
                                                const diffId = `${idx}-${i}`;
                                                const oldContent = edit.old_content || '';
                                                const newContent = edit.new_content || '';

                                                // Generate unified diff
                                                const diffText = generateUnifiedDiff(oldContent, newContent, edit.file);
                                                const parsedDiff = parseDiff(diffText);

                                                return (
                                                    <div key={i} className="rounded border border-gray-700/30 overflow-hidden">
                                                        <div
                                                            className="flex items-center justify-between px-3 py-2 bg-gray-900/30 cursor-pointer hover:bg-gray-800/50 transition-colors"
                                                            onClick={() => toggleDiff(diffId)}
                                                        >
                                                            <div className="flex items-center gap-2">
                                                                <span className={`transform transition-transform text-gray-500 text-xs ${expandedDiffs[diffId] ? 'rotate-90' : ''}`}>▶</span>
                                                                <span className="text-blue-400 font-mono text-xs">{edit.file}</span>
                                                            </div>
                                                            <div className="flex gap-2 text-gray-500 text-xs">
                                                                <span className="text-green-500">+{edit.lines_added}</span>
                                                                <span className="text-red-500">-{edit.lines_removed}</span>
                                                            </div>
                                                        </div>

                                                        {expandedDiffs[diffId] && parsedDiff[0] && (
                                                            <div className="bg-gray-950 p-2 overflow-x-auto">
                                                                <Diff
                                                                    viewType="split"
                                                                    diffType={parsedDiff[0].type}
                                                                    hunks={parsedDiff[0].hunks || []}
                                                                >
                                                                    {(hunks) => hunks.map((hunk) => (
                                                                        <Hunk key={hunk.content} hunk={hunk} />
                                                                    ))}
                                                                </Diff>
                                                            </div>
                                                        )}
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* Legacy File Changes Display (Fallback) */}
                            {!msg.editsMade && msg.filesModified && msg.filesModified.length > 0 && (
                                <div className="mt-3 pt-3 border-t border-gray-700">
                                    <p className="text-xs font-medium text-gray-400 mb-1">Modified files:</p>
                                    <div className="flex flex-wrap gap-1">
                                        {msg.filesModified.map((file, i) => (
                                            <span key={i} className="px-2 py-1 bg-gray-900/50 rounded text-xs text-blue-400 font-mono border border-gray-700/50">
                                                {file}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Other Rich Content */}
                            {msg.codeSuggestions && (
                                <div className="mt-4 space-y-2">
                                    <p className="text-sm font-semibold text-blue-400">Suggestions:</p>
                                    <ul className="list-disc list-inside text-sm space-y-1 text-gray-300">
                                        {msg.codeSuggestions.map((s, i) => <li key={i}>{s}</li>)}
                                    </ul>
                                </div>
                            )}

                            {msg.tips && (
                                <div className="mt-4 p-3 bg-blue-900/20 rounded-lg border border-blue-800/30">
                                    <p className="text-sm font-semibold text-blue-300 mb-2">Design Tips:</p>
                                    <ul className="list-disc list-inside text-sm space-y-1 text-blue-200/80">
                                        {msg.tips.map((t, i) => <li key={i}>{t}</li>)}
                                    </ul>
                                </div>
                            )}

                            {/* Advanced Code Details */}
                            {msg.codeDetails && (
                                <div className="mt-3 pt-3 border-t border-gray-600 space-y-2">
                                    {msg.codeDetails.css && (
                                        <div>
                                            <p className="text-xs font-semibold text-blue-300 mb-1">CSS:</p>
                                            <div className="bg-black/40 rounded p-2 overflow-x-auto font-mono text-xs max-h-40">
                                                <pre className="text-gray-300">{msg.codeDetails.css.slice(0, 300)}...</pre>
                                            </div>
                                        </div>
                                    )}
                                    {msg.codeDetails.browser_support && (
                                        <div>
                                            <p className="text-xs font-semibold text-green-300">Browser Support:</p>
                                            <p className="text-xs text-gray-300">{msg.codeDetails.browser_support}</p>
                                        </div>
                                    )}
                                    {msg.codeDetails.accessibility_notes && (
                                        <div>
                                            <p className="text-xs font-semibold text-yellow-300">Accessibility:</p>
                                            <p className="text-xs text-gray-300">{msg.codeDetails.accessibility_notes}</p>
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* Design Strategy Details */}
                            {msg.strategyDetails && (
                                <div className="mt-3 pt-3 border-t border-gray-600 space-y-2">
                                    {msg.strategyDetails.color_strategy && (
                                        <div>
                                            <p className="text-xs font-semibold text-blue-300">Color Strategy:</p>
                                            <p className="text-xs text-gray-300">{msg.strategyDetails.color_strategy}</p>
                                        </div>
                                    )}
                                    {msg.strategyDetails.typography && (
                                        <div>
                                            <p className="text-xs font-semibold text-purple-300">Typography:</p>
                                            <p className="text-xs text-gray-300">{msg.strategyDetails.typography}</p>
                                        </div>
                                    )}
                                    {msg.strategyDetails.animations && (
                                        <div>
                                            <p className="text-xs font-semibold text-pink-300">Animations:</p>
                                            <p className="text-xs text-gray-300">{msg.strategyDetails.animations}</p>
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* Multiple Approaches */}
                            {msg.approaches && msg.approaches.length > 0 && (
                                <div className="mt-3 pt-3 border-t border-gray-600">
                                    {msg.approaches.map((approach, i) => (
                                        <div key={i} className="mb-2 pb-2 border-b border-gray-600 last:border-0">
                                            <p className="text-xs font-semibold text-cyan-300">{approach.level?.toUpperCase()} ({approach.time_estimate})</p>
                                            <p className="text-xs text-gray-300">{approach.description}</p>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                ))}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area with Mode Selector */}
            <div className="p-4 border-t border-gray-800 bg-gray-900/50 backdrop-blur-sm">
                <div className="flex gap-2 items-end">
                    {/* Mode Selector Dropdown */}
                    <div className="relative" ref={dropdownRef}>
                        <button
                            onClick={() => setShowModeDropdown(!showModeDropdown)}
                            className="p-3 rounded-xl bg-gray-800 hover:bg-gray-700 border border-gray-700 transition-all flex items-center justify-center text-gray-300 hover:text-white"
                            title={currentMode.label}
                        >
                            {currentMode.icon}
                        </button>

                        {/* Dropdown Menu */}
                        {showModeDropdown && (
                            <div className="absolute bottom-full left-0 mb-2 w-64 bg-gray-800 border border-gray-700 rounded-xl shadow-2xl overflow-hidden z-50">
                                <div className="p-2">
                                    <div className="text-xs font-medium text-gray-500 px-3 py-2">Select Mode</div>
                                    {CHAT_MODES.map((mode) => (
                                        <button
                                            key={mode.id}
                                            onClick={() => {
                                                setTabMode(mode.id as any);
                                                setShowModeDropdown(false);
                                            }}
                                            className={`w-full text-left px-3 py-2.5 rounded-lg transition-all flex items-center gap-3 ${tabMode === mode.id
                                                    ? 'bg-blue-600/20 border border-blue-500/30 text-blue-400'
                                                    : 'hover:bg-gray-700/50 text-gray-300'
                                                }`}
                                        >
                                            <div className="flex-shrink-0">
                                                {mode.icon}
                                            </div>
                                            <span className="text-sm font-medium flex-1">{mode.label}</span>
                                            {tabMode === mode.id && (
                                                <svg className="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                                </svg>
                                            )}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Input Field */}
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                        placeholder={
                            tabMode === 'code' ? "Describe changes (e.g., 'Make the background dark blue')..." :
                                tabMode === 'design' ? "Ask for design advice..." :
                                    "Ask the AI assistant..."
                        }
                        className="flex-1 bg-gray-800 text-white rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 border border-gray-700 placeholder-gray-500"
                        disabled={loading}
                    />

                    {/* Send Button */}
                    <button
                        onClick={handleSend}
                        disabled={loading}
                        className={`px-5 py-3 rounded-xl font-medium transition-all flex items-center gap-2 ${loading
                            ? 'bg-gray-700 text-gray-400 cursor-not-allowed'
                            : 'bg-blue-600 text-white hover:bg-blue-500 shadow-lg shadow-blue-500/20'
                            }`}
                    >
                        {loading ? (
                            <>
                                <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                                <span>Thinking...</span>
                            </>
                        ) : (
                            <>
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                                </svg>
                                <span>Send</span>
                            </>
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
}
