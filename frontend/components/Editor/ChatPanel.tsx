'use client';

import { useState, useRef, useEffect } from 'react';
import { sendChatMessage } from '@/lib/api';

interface ChatPanelProps {
    sessionId: string;
    resumeData: any;
    currentFiles: Record<string, string>;
    onFilesChange: (files: Record<string, string>) => void;
}

interface ChatMessage {
    role: string;
    content: string;
    filesModified?: string[];
    codeSuggestions?: string[];
    tips?: string[];
    codeDetails?: any;
    strategyDetails?: any;
    approaches?: any[];
}

export default function ChatPanel({ sessionId, resumeData, currentFiles, onFilesChange }: ChatPanelProps) {
    const [messages, setMessages] = useState<ChatMessage[]>([
        { role: 'assistant', content: '✨ Hi! I can help you improve your portfolio with advanced AI features:\n\n💻 Code Changes: Modify colors, themes, layouts, fonts\n🎨 Design Tips: Get design enhancement suggestions\n⚡ Advanced Code: Production-quality code with accessibility & performance\n🎯 Design Strategy: Comprehensive design approach\n📋 Multiple Approaches: 3 implementation options\n\nTry: "Make it more modern" or pick an advanced feature!' }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [tabMode, setTabMode] = useState<'code' | 'design' | 'advanced-code' | 'strategy' | 'approaches'>('code');
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Scroll to bottom when messages change
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim() || loading) return;

        const userMessage: ChatMessage = { role: 'user', content: input };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setLoading(true);

        try {
            if (tabMode === 'code') {
                // Code modification mode
                const response = await sendChatMessage(
                    [...messages, userMessage],
                    sessionId,
                    currentFiles
                );

                // Check if AI modified any files
                const filesModified = response.file_changes ? Object.keys(response.file_changes) : undefined;

                // Apply file changes
                if (response.file_changes) {
                    const updatedFiles = { ...currentFiles };
                    Object.entries(response.file_changes).forEach(([filename, content]) => {
                        updatedFiles[filename] = content as string;
                    });
                    onFilesChange(updatedFiles);
                }

                setMessages(prev => [...prev, {
                    role: 'assistant',
                    content: response.response,
                    filesModified
                }]);
            } else if (tabMode === 'design') {
                // Design improvement mode using portfolio chat
                const response = await fetch('/api/chat/portfolio/improve', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        session_id: sessionId,
                        message: input,
                        user_data: resumeData
                    })
                });

                if (response.ok) {
                    const data = await response.json();
                    setMessages(prev => [...prev, {
                        role: 'assistant',
                        content: data.response,
                        codeSuggestions: data.code_suggestions,
                        tips: data.design_tips
                    }]);
                } else {
                    throw new Error('Failed to get design suggestions');
                }
            } else if (tabMode === 'advanced-code') {
                // Advanced production-quality code generation
                const response = await fetch('/api/chat/portfolio/advanced-code', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        session_id: sessionId,
                        request: input,
                        user_data: resumeData
                    })
                });

                if (response.ok) {
                    const data = await response.json();
                    setMessages(prev => [...prev, {
                        role: 'assistant',
                        content: data.explanation || 'Advanced code generated successfully!',
                        codeDetails: data
                    }]);
                } else {
                    throw new Error('Failed to generate advanced code');
                }
            } else if (tabMode === 'strategy') {
                // Design strategy generation
                const response = await fetch('/api/chat/portfolio/design-strategy', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        session_id: sessionId,
                        user_data: resumeData
                    })
                });

                if (response.ok) {
                    const data = await response.json();
                    setMessages(prev => [...prev, {
                        role: 'assistant',
                        content: 'Here\'s your comprehensive design strategy:',
                        strategyDetails: data
                    }]);
                } else {
                    throw new Error('Failed to get design strategy');
                }
            } else if (tabMode === 'approaches') {
                // Multiple implementation approaches
                const response = await fetch('/api/chat/portfolio/multiple-approaches', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        session_id: sessionId,
                        feature: input,
                        user_data: resumeData
                    })
                });

                if (response.ok) {
                    const data = await response.json();
                    setMessages(prev => [...prev, {
                        role: 'assistant',
                        content: `Here are ${data.approaches?.length || 3} implementation approaches:`,
                        approaches: data.approaches
                    }]);
                } else {
                    throw new Error('Failed to get implementation approaches');
                }
            }
        } catch (error) {
            console.error('Chat error:', error);
            setMessages(prev => [...prev, { role: 'assistant', content: '❌ Sorry, I encountered an error. Please try again.' }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="h-full flex flex-col bg-gradient-to-b from-gray-850 to-gray-900 border-l border-gray-700">
            {/* Header with tabs */}
            <div className="px-4 py-3 border-b border-gray-700 bg-gray-800/50">
                <h3 className="text-white font-semibold mb-2">✨ AI Assistant (Extensive)</h3>
                <div className="flex gap-2 flex-wrap">
                    <button
                        onClick={() => setTabMode('code')}
                        className={`text-xs px-3 py-1.5 rounded transition-all ${
                            tabMode === 'code'
                                ? 'bg-purple-600 text-white'
                                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                        }`}
                    >
                        💻 Code
                    </button>
                    <button
                        onClick={() => setTabMode('design')}
                        className={`text-xs px-3 py-1.5 rounded transition-all ${
                            tabMode === 'design'
                                ? 'bg-purple-600 text-white'
                                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                        }`}
                    >
                        🎨 Design
                    </button>
                    <button
                        onClick={() => setTabMode('advanced-code')}
                        className={`text-xs px-3 py-1.5 rounded transition-all ${
                            tabMode === 'advanced-code'
                                ? 'bg-purple-600 text-white'
                                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                        }`}
                    >
                        ⚡ Advanced
                    </button>
                    <button
                        onClick={() => setTabMode('strategy')}
                        className={`text-xs px-3 py-1.5 rounded transition-all ${
                            tabMode === 'strategy'
                                ? 'bg-purple-600 text-white'
                                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                        }`}
                    >
                        🎯 Strategy
                    </button>
                    <button
                        onClick={() => setTabMode('approaches')}
                        className={`text-xs px-3 py-1.5 rounded transition-all ${
                            tabMode === 'approaches'
                                ? 'bg-purple-600 text-white'
                                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                        }`}
                    >
                        📋 Approaches
                    </button>
                </div>
            </div>

            {/* Messages area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
                {messages.map((msg, idx) => (
                    <div
                        key={idx}
                        className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-slideIn`}
                    >
                        <div
                            className={`max-w-[85%] rounded-lg px-3 py-2 text-sm ${msg.role === 'user'
                                ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
                                : 'bg-gray-700 text-gray-100'
                                }`}
                        >
                            <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>

                            {/* Advanced Code Details */}
                            {msg.codeDetails && (
                                <div className="mt-3 pt-3 border-t border-gray-600 space-y-2">
                                    {msg.codeDetails.css && (
                                        <div>
                                            <p className="text-xs font-semibold text-blue-300 mb-1">🎨 CSS:</p>
                                            <div className="bg-black/40 rounded p-2 overflow-x-auto font-mono text-xs max-h-40">
                                                <pre className="text-gray-300">{msg.codeDetails.css.slice(0, 300)}...</pre>
                                            </div>
                                        </div>
                                    )}
                                    {msg.codeDetails.browser_support && (
                                        <div>
                                            <p className="text-xs font-semibold text-green-300">🌐 Browser Support:</p>
                                            <p className="text-xs text-gray-300">{msg.codeDetails.browser_support}</p>
                                        </div>
                                    )}
                                    {msg.codeDetails.accessibility_notes && (
                                        <div>
                                            <p className="text-xs font-semibold text-yellow-300">♿ Accessibility:</p>
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
                                            <p className="text-xs font-semibold text-blue-300">🎨 Color Strategy:</p>
                                            <p className="text-xs text-gray-300">{msg.strategyDetails.color_strategy}</p>
                                        </div>
                                    )}
                                    {msg.strategyDetails.typography && (
                                        <div>
                                            <p className="text-xs font-semibold text-purple-300">✍️ Typography:</p>
                                            <p className="text-xs text-gray-300">{msg.strategyDetails.typography}</p>
                                        </div>
                                    )}
                                    {msg.strategyDetails.animations && (
                                        <div>
                                            <p className="text-xs font-semibold text-pink-300">✨ Animations:</p>
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

                            {/* Design tips display */}
                            {msg.tips && msg.tips.length > 0 && (
                                <div className="mt-2 pt-2 border-t border-gray-600">
                                    <p className="text-xs font-semibold text-gray-200 mb-1">💡 Tips:</p>
                                    <ul className="space-y-1">
                                        {msg.tips.map((tip, i) => (
                                            <li key={i} className="text-xs text-gray-300">• {tip}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            {/* Code suggestions */}
                            {msg.codeSuggestions && msg.codeSuggestions.length > 0 && (
                                <div className="mt-2 pt-2 border-t border-gray-600">
                                    <p className="text-xs font-semibold text-gray-200 mb-1">📝 Code:</p>
                                    <div className="bg-black/30 rounded p-2 overflow-x-auto font-mono text-xs">
                                        <pre className="text-gray-300">{msg.codeSuggestions[0]}</pre>
                                    </div>
                                    <button
                                        onClick={() => {
                                            navigator.clipboard.writeText(msg.codeSuggestions![0]);
                                            alert('Code copied!');
                                        }}
                                        className="mt-1 text-xs bg-blue-600 hover:bg-blue-700 text-white px-2 py-1 rounded"
                                    >
                                        📋 Copy
                                    </button>
                                </div>
                            )}

                            {/* Files modified */}
                            {msg.filesModified && msg.filesModified.length > 0 && (
                                <div className="mt-2 pt-2 border-t border-gray-600">
                                    <p className="text-xs text-gray-300 font-semibold">✏️ Modified:</p>
                                    {msg.filesModified.map((file, i) => (
                                        <p key={i} className="text-xs text-green-400">• {file}</p>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                ))}

                {loading && (
                    <div className="flex justify-start">
                        <div className="bg-gray-700 text-gray-300 rounded-lg px-3 py-2">
                            <div className="flex gap-1.5">
                                <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0s' }}></div>
                                <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                                <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                            </div>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Input area */}
            <div className="p-4 border-t border-gray-700 bg-gray-800/50">
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                        placeholder={
                            tabMode === 'code' ? 'Ask code changes...' :
                            tabMode === 'design' ? 'Ask design suggestions...' :
                            tabMode === 'advanced-code' ? 'Describe what you need...' :
                            tabMode === 'strategy' ? 'Click send for strategy...' :
                            'Name a feature to implement...'
                        }
                        className="flex-1 bg-gray-700 text-white text-sm px-3 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600 placeholder-gray-400"
                        disabled={loading}
                    />
                    <button
                        onClick={handleSend}
                        disabled={loading || (!input.trim() && tabMode !== 'strategy')}
                        className="px-3 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white text-sm rounded-lg hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                    >
                        {loading ? '...' : '→'}
                    </button>
                </div>
            </div>

            <style jsx>{`
                @keyframes slideIn {
                    from {
                        opacity: 0;
                        transform: translateY(10px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
            `}</style>
        </div>
    );
}
