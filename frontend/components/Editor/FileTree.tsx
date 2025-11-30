'use client';

interface FileTreeProps {
    files: string[];
    activeFile: string;
    onSelect: (file: string) => void;
}

export default function FileTree({ files, activeFile, onSelect }: FileTreeProps) {
    const getFileIcon = (filename: string) => {
        if (filename.endsWith('.jsx') || filename.endsWith('.js')) return '⚛️';
        if (filename.endsWith('.tsx') || filename.endsWith('.ts')) return '🔷';
        if (filename.endsWith('.css')) return '🎨';
        if (filename.endsWith('.html')) return '🌐';
        if (filename.endsWith('.json')) return '⚙️';
        if (filename === 'README.md') return '📖';
        if (filename.endsWith('.md')) return '📝';
        return '📄';
    };

    // Organize files into folders
    const organizedFiles: Record<string, string[]> = { root: [] };

    files.forEach(file => {
        const parts = file.split('/');
        if (parts.length > 1) {
            const folder = parts[0];
            if (!organizedFiles[folder]) organizedFiles[folder] = [];
            organizedFiles[folder].push(file);
        } else {
            organizedFiles['root'].push(file);
        }
    });

    return (
        <div className="py-2">
            {/* Root files */}
            {organizedFiles['root']?.map(file => (
                <button
                    key={file}
                    onClick={() => onSelect(file)}
                    className={`w-full text-left px-4 py-2 flex items-center gap-2.5 text-sm transition-all ${activeFile === file
                            ? 'bg-purple-500/20 text-purple-300 border-l-2 border-purple-500'
                            : 'text-gray-400 hover:bg-gray-800/50 hover:text-gray-200'
                        }`}
                >
                    <span className="text-base">{getFileIcon(file)}</span>
                    <span className="font-medium">{file}</span>
                </button>
            ))}

            {/* Folders */}
            {Object.entries(organizedFiles)
                .filter(([folder]) => folder !== 'root')
                .map(([folder, folderFiles]) => (
                    <div key={folder} className="mt-2">
                        <div className="px-4 py-1.5 text-xs font-semibold text-gray-500 uppercase tracking-wider flex items-center gap-2">
                            <span>📁</span>
                            <span>{folder}</span>
                        </div>
                        {folderFiles.map(file => {
                            const fileName = file.split('/').pop() || file;
                            return (
                                <button
                                    key={file}
                                    onClick={() => onSelect(file)}
                                    className={`w-full text-left px-4 py-2 pl-8 flex items-center gap-2.5 text-sm transition-all ${activeFile === file
                                            ? 'bg-purple-500/20 text-purple-300 border-l-2 border-purple-500'
                                            : 'text-gray-400 hover:bg-gray-800/50 hover:text-gray-200'
                                        }`}
                                >
                                    <span className="text-base">{getFileIcon(fileName)}</span>
                                    <span className="font-medium">{fileName}</span>
                                </button>
                            );
                        })}
                    </div>
                ))}
        </div>
    );
}
