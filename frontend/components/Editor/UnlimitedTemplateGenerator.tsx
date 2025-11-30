'use client';

import { useState } from 'react';

interface UnlimitedTemplateGeneratorProps {
    stack: string;
    resumeData: any;
    onTemplateGenerated: (files: Record<string, string>) => void;
}

export default function UnlimitedTemplateGenerator({
    stack,
    resumeData,
    onTemplateGenerated
}: UnlimitedTemplateGeneratorProps) {
    const [isOpen, setIsOpen] = useState(false);
    const [styleDescription, setStyleDescription] = useState('');
    const [loading, setLoading] = useState(false);
    const [activeTab, setActiveTab] = useState<'custom' | 'variations'>('custom');

    const frameworkMap: Record<string, string> = {
        'react': 'react',
        'nextjs': 'nextjs',
        'vue': 'vue',
        'svelte': 'svelte'
    };

    const handleGenerateUnlimited = async () => {
        if (!styleDescription.trim()) {
            alert('Please describe your desired template style');
            return;
        }

        setLoading(true);
        try {
            const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const response = await fetch(`${API_URL}/api/generate/unlimited-template`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    framework: frameworkMap[stack] || stack,
                    style_description: styleDescription,
                    resume_data: resumeData,
                    options: {
                        primaryColor: '#667eea',
                        secondaryColor: '#764ba2'
                    }
                })
            });

            if (response.ok) {
                const data = await response.json();
                onTemplateGenerated(data.files);
                setIsOpen(false);
                setStyleDescription('');
                alert('✨ Unlimited template generated successfully!');
            } else {
                throw new Error('Failed to generate template');
            }
        } catch (error) {
            console.error('Template generation error:', error);
            alert('Failed to generate template. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleGenerateVariations = async () => {
        setLoading(true);
        try {
            const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const response = await fetch(`${API_URL}/api/generate/theme-variations`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    framework: frameworkMap[stack] || stack,
                    num_variations: 5
                })
            });

            if (response.ok) {
                const data = await response.json();
                alert(`✨ Generated ${data.total_variations} unique theme variations!`);
                // Display variations to user for selection
                console.log('Generated variations:', data.variations);
            } else {
                throw new Error('Failed to generate variations');
            }
        } catch (error) {
            console.error('Variations generation error:', error);
            alert('Failed to generate variations. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            {/* Toggle Button */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg text-sm font-medium hover:from-purple-700 hover:to-pink-700 transition-all shadow-lg hover:shadow-purple-500/50 flex items-center gap-2"
            >
                ✨ Unlimited Templates
            </button>

            {/* Modal */}
            {isOpen && (
                <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
                    <div className="bg-gray-900 rounded-lg border border-gray-800 max-w-2xl w-full mx-4 shadow-2xl">
                        {/* Header */}
                        <div className="bg-gradient-to-r from-purple-600/10 to-pink-600/10 border-b border-gray-800 px-6 py-4 flex items-center justify-between">
                            <div>
                                <h2 className="text-xl font-bold text-white">AI-Powered Unlimited Templates</h2>
                                <p className="text-sm text-gray-400 mt-1">Generate completely unique templates, no limits</p>
                            </div>
                            <button
                                onClick={() => setIsOpen(false)}
                                className="text-gray-400 hover:text-white text-2xl"
                            >
                                ✕
                            </button>
                        </div>

                        {/* Tabs */}
                        <div className="flex gap-4 px-6 pt-6 border-b border-gray-800">
                            <button
                                onClick={() => setActiveTab('custom')}
                                className={`px-4 py-2 font-medium transition-all ${activeTab === 'custom'
                                    ? 'text-purple-400 border-b-2 border-purple-400'
                                    : 'text-gray-400 hover:text-gray-300'
                                    }`}
                            >
                                🎨 Custom Template
                            </button>
                            <button
                                onClick={() => setActiveTab('variations')}
                                className={`px-4 py-2 font-medium transition-all ${activeTab === 'variations'
                                    ? 'text-purple-400 border-b-2 border-purple-400'
                                    : 'text-gray-400 hover:text-gray-300'
                                    }`}
                            >
                                🎭 Theme Variations
                            </button>
                        </div>

                        {/* Content */}
                        <div className="px-6 py-6">
                            {activeTab === 'custom' && (
                                <div className="space-y-4">
                                    <div>
                                        <label className="block text-sm font-semibold text-white mb-2">
                                            Describe your ideal portfolio style
                                        </label>
                                        <textarea
                                            value={styleDescription}
                                            onChange={(e) => setStyleDescription(e.target.value)}
                                            placeholder="e.g., 'Dark modern minimalist with glassmorphism effects, smooth animations, vibrant neon accents'..."
                                            className="w-full bg-gray-800 text-white rounded-lg border border-gray-700 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"
                                            rows={4}
                                        />
                                    </div>
                                    <p className="text-xs text-gray-400">
                                        💡 Tip: Be descriptive! Mention colors, style, mood, components, animations you want.
                                    </p>
                                </div>
                            )}

                            {activeTab === 'variations' && (
                                <div className="space-y-4">
                                    <div className="bg-gray-800/50 rounded-lg border border-gray-700 p-4">
                                        <p className="text-white font-medium mb-2">🎭 Available Themes:</p>
                                        <ul className="grid grid-cols-2 gap-2 text-sm text-gray-300">
                                            <li>✓ Minimalist Elegant</li>
                                            <li>✓ Vibrant Colorful</li>
                                            <li>✓ Dark Modern</li>
                                            <li>✓ Glassmorphism</li>
                                            <li>✓ Retro Vintage</li>
                                            <li>✓ Corporate Pro</li>
                                            <li>✓ Artistic Creative</li>
                                            <li>✓ Cyberpunk Neon</li>
                                        </ul>
                                    </div>
                                    <p className="text-xs text-gray-400">
                                        Each variation is completely unique and AI-generated for maximum variety.
                                    </p>
                                </div>
                            )}
                        </div>

                        {/* Footer */}
                        <div className="border-t border-gray-800 px-6 py-4 flex gap-3 justify-end">
                            <button
                                onClick={() => setIsOpen(false)}
                                className="px-4 py-2 text-gray-300 hover:text-white transition-colors"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={activeTab === 'custom' ? handleGenerateUnlimited : handleGenerateVariations}
                                disabled={loading || (activeTab === 'custom' && !styleDescription.trim())}
                                className="px-6 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg font-medium hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2"
                            >
                                {loading ? (
                                    <>
                                        <span className="animate-spin">⚙️</span>
                                        Generating...
                                    </>
                                ) : (
                                    <>
                                        ✨ Generate
                                        {activeTab === 'custom' ? ' Template' : ' Variations'}
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
