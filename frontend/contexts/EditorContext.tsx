'use client';

import { createContext, useContext, useState, ReactNode } from 'react';

interface EditorContextType {
    activeTab: 'preview' | 'code';
    setActiveTab: (tab: 'preview' | 'code') => void;
    onExport: (() => void) | null;
    setOnExport: (callback: () => void) => void;
    onDeploy: (() => void) | null;
    setOnDeploy: (callback: () => void) => void;
    isDeployDialogOpen: boolean;
    setIsDeployDialogOpen: (open: boolean) => void;
}

const EditorContext = createContext<EditorContextType | undefined>(undefined);

export function EditorProvider({ children }: { children: ReactNode }) {
    const [activeTab, setActiveTab] = useState<'preview' | 'code'>('preview');
    const [onExport, setOnExport] = useState<(() => void) | null>(null);
    const [onDeploy, setOnDeploy] = useState<(() => void) | null>(null);
    const [isDeployDialogOpen, setIsDeployDialogOpen] = useState(false);

    return (
        <EditorContext.Provider
            value={{
                activeTab,
                setActiveTab,
                onExport,
                setOnExport,
                onDeploy,
                setOnDeploy,
                isDeployDialogOpen,
                setIsDeployDialogOpen,
            }}
        >
            {children}
        </EditorContext.Provider>
    );
}

export function useEditor() {
    const context = useContext(EditorContext);
    if (context === undefined) {
        throw new Error('useEditor must be used within EditorProvider');
    }
    return context;
}
