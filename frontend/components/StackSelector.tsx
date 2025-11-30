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
            color: 'from-cyan-500 to-blue-500'
        },
        {
            id: 'nextjs',
            name: 'Next.js 14',
            icon: '▲',
            desc: 'Full-stack React framework',
            color: 'from-gray-700 to-gray-900'
        },
        {
            id: 'vue',
            name: 'Vue 3',
            icon: '💚',
            desc: 'Progressive framework',
            color: 'from-green-500 to-emerald-600'
        },
        {
            id: 'svelte',
            name: 'Svelte',
            icon: '🧡',
            desc: 'Cybernetically enhanced',
            color: 'from-orange-500 to-red-500'
        },
    ];

    return (
        <div className="min-h-screen bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 p-8">
            <div className="max-w-7xl mx-auto">
                <div className="text-center mb-16">
                    <h1 className="text-6xl font-bold text-white mb-4">
                        Choose Your Stack
                    </h1>
                    <p className="text-xl text-white/80">
                        Select the framework for your portfolio
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {stacks.map((stack) => (
                        <button
                            key={stack.id}
                            onClick={() => !loading && onSelect(stack.id)}
                            disabled={loading}
                            className={`group relative bg-white rounded-2xl p-8 shadow-xl hover:shadow-2xl transition-all transform hover:-translate-y-2 ${loading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
                                }`}
                        >
                            <div className={`absolute inset-0 bg-gradient-to-br ${stack.color} opacity-0 group-hover:opacity-10 rounded-2xl transition-opacity`} />
                            <div className="text-6xl mb-4 group-hover:scale-110 transition-transform">
                                {stack.icon}
                            </div>
                            <h3 className="text-2xl font-bold mb-2">{stack.name}</h3>
                            <p className="text-gray-600">{stack.desc}</p>
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
}
