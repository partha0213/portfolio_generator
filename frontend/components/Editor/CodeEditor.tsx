'use client';

interface CodeEditorProps {
    file: string;
    content: string;
    onChange: (content: string) => void;
}

export default function CodeEditor({ file, content, onChange }: CodeEditorProps) {
    const getLanguage = (filename: string) => {
        if (filename.endsWith('.jsx') || filename.endsWith('.js')) return 'javascript';
        if (filename.endsWith('.tsx') || filename.endsWith('.ts')) return 'typescript';
        if (filename.endsWith('.css')) return 'css';
        if (filename.endsWith('.html')) return 'html';
        if (filename.endsWith('.json')) return 'json';
        return 'text';
    };

    const language = getLanguage(file);

    return (
        <div className="h-full flex flex-col bg-[#0a0a0a]">
            {/* Modern Header */}
            <div className="bg-[#111111] px-6 py-3 border-b border-gray-800 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <span className="text-sm font-medium text-gray-300">{file}</span>
                    <span className="px-2 py-0.5 bg-blue-500/10 text-blue-400 text-xs rounded border border-blue-500/20 uppercase">
                        {language}
                    </span>
                </div>
                <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-500">{content.split('\n').length} lines</span>
                </div>
            </div>

            {/* Code Area */}
            <div className="flex-1 relative overflow-hidden">
                <textarea
                    value={content}
                    onChange={(e) => onChange(e.target.value)}
                    className="w-full h-full p-6 bg-[#0a0a0a] text-gray-100 font-mono text-sm resize-none focus:outline-none leading-relaxed"
                    style={{
                        tabSize: 2,
                        lineHeight: '1.6',
                    }}
                    spellCheck={false}
                    placeholder="// Start editing..."
                />
            </div>
        </div>
    );
}
