'use client';

interface StackSelectorProps {
    onSelect: (stack: string) => void;
    loading: boolean;
}

export default function StackSelector({ onSelect, loading }: StackSelectorProps) {
    const stacks = [
        {
            id: 'react',
            name: 'React + Vite',
            icon: '⚛️',
            desc: 'Fast refresh, modern React',
            color: 'from-cyan-500 to-blue-500',
            borderColor: 'border-cyan-500/50',
            hoverBorder: 'hover:border-cyan-500',
            shadowColor: 'shadow-cyan-500/20'
        },
        {
            id: 'nextjs',
            name: 'Next.js 14',
            icon: '▲',
            desc: 'Full-stack React framework',
            color: 'from-gray-500 to-gray-700',
            borderColor: 'border-gray-500/50',
            hoverBorder: 'hover:border-gray-400',
            shadowColor: 'shadow-gray-500/20'
        },
        {
            id: 'vue',
            name: 'Vue 3',
            icon: '💚',
            desc: 'Progressive framework',
            color: 'from-green-500 to-emerald-600',
            borderColor: 'border-green-500/50',
            hoverBorder: 'hover:border-green-500',
            shadowColor: 'shadow-green-500/20'
        },
        {
            id: 'svelte',
            name: 'Svelte',
            icon: '🧡',
            desc: 'Cybernetically enhanced',
            color: 'from-orange-500 to-red-500',
            borderColor: 'border-orange-500/50',
            hoverBorder: 'hover:border-orange-500',
            shadowColor: 'shadow-orange-500/20'
        },
    ];

    return (
        <div className="min-h-screen bg-gradient-to-br from-[#0d1117] via-[#161b22] to-[#010409] p-8">
            <div className="max-w-7xl mx-auto">
                {/* Header Section */}
                <div className="text-center mb-16">
                    <h1 className="text-5xl md:text-6xl font-bold bg-gradient-to-r from-blue-400 via-cyan-400 to-purple-400 bg-clip-text text-transparent mb-4">
                        Choose Your Stack
                    </h1>
                    <p className="text-xl text-gray-400">
                        Select the framework for your portfolio
                    </p>
                </div>

                {/* Stack Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {stacks.map((stack) => (
                        <button
                            key={stack.id}
                            onClick={() => !loading && onSelect(stack.id)}
                            disabled={loading}
                            className={`group relative bg-[#161b22] rounded-2xl p-8 border-2 ${stack.borderColor} ${stack.hoverBorder} shadow-xl ${stack.shadowColor} hover:shadow-2xl transition-all transform hover:-translate-y-2 ${
                                loading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
                            }`}
                        >
                            {/* Gradient Overlay on Hover */}
                            <div className={`absolute inset-0 bg-gradient-to-br ${stack.color} opacity-0 group-hover:opacity-10 rounded-2xl transition-opacity`} />
                            
                            {/* Icon */}
                            <div className="relative text-6xl mb-4 group-hover:scale-110 transition-transform">
                                {stack.icon}
                            </div>
                            
                            {/* Stack Name */}
                            <h3 className="relative text-2xl font-bold text-white mb-2">
                                {stack.name}
                            </h3>
                            
                            {/* Description */}
                            <p className="relative text-gray-400">
                                {stack.desc}
                            </p>
                        </button>
                    ))}
                </div>

                {/* Loading Indicator */}
                {loading && (
                    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
                        <div className="bg-[#161b22] rounded-xl p-8 border border-gray-800/50 shadow-2xl">
                            <div className="flex items-center gap-4">
                                <svg className="w-8 h-8 animate-spin text-blue-500" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                                <p className="text-white text-lg font-semibold">Generating your portfolio...</p>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
