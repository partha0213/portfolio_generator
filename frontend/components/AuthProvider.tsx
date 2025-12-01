'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import { api, auth } from '@/lib/api';

interface User {
    id: string;
    email: string;
    full_name: string;
}

interface AuthContextType {
    user: User | null;
    login: (token: string, refreshToken: string, user: User) => void;
    logout: () => void;
    signup: (email: string, password: string, full_name: string) => Promise<{ message: string; email: string }>;
    verifyEmail: (email: string, code: string) => Promise<{ message: string; email: string }>;
    resendVerification: (email: string) => Promise<{ message: string; email: string }>;
    isAuthenticated: boolean;
    loading: boolean;
    verificationEmail: string | null;
}

const AuthContext = createContext<AuthContextType>({
    user: null,
    login: () => { },
    logout: () => { },
    signup: async () => ({ message: '', email: '' }),
    verifyEmail: async () => ({ message: '', email: '' }),
    resendVerification: async () => ({ message: '', email: '' }),
    isAuthenticated: false,
    loading: true,
    verificationEmail: null,
});

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [verificationEmail, setVerificationEmail] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);
    const router = useRouter();

    useEffect(() => {
        // Check for existing token on mount
        const token = localStorage.getItem('accessToken');
        const userData = localStorage.getItem('user');
        const pendingVerificationEmail = localStorage.getItem('verificationEmail');

        if (token && userData) {
            setUser(JSON.parse(userData));
        }
        
        if (pendingVerificationEmail) {
            setVerificationEmail(pendingVerificationEmail);
        }
        
        setLoading(false);
    }, []);

    const login = (token: string, refreshToken: string, userData: User) => {
        localStorage.setItem('accessToken', token);
        localStorage.setItem('refreshToken', refreshToken);
        localStorage.setItem('user', JSON.stringify(userData));
        localStorage.removeItem('verificationEmail');
        setUser(userData);
        setVerificationEmail(null);
        router.push('/dashboard');
    };

    const logout = () => {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('user');
        localStorage.removeItem('verificationEmail');
        setUser(null);
        setVerificationEmail(null);
        router.push('/');
    };

    const signup = async (email: string, password: string, full_name: string) => {
        const response = await auth.signup({ email, password, full_name });
        localStorage.setItem('verificationEmail', email);
        setVerificationEmail(email);
        return response;
    };

    const verifyEmail = async (email: string, code: string) => {
        const response = await auth.verifyEmail(email, code);
        localStorage.removeItem('verificationEmail');
        setVerificationEmail(null);
        return response;
    };

    const resendVerification = async (email: string) => {
        return await auth.resendVerification(email);
    };

    return (
        <AuthContext.Provider value={{ 
            user, 
            login, 
            logout, 
            signup,
            verifyEmail,
            resendVerification,
            isAuthenticated: !!user, 
            loading,
            verificationEmail
        }}>
            {children}
        </AuthContext.Provider>
    );
}

export const useAuth = () => useContext(AuthContext);
