'use client';

import { useState, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { useAuth } from '@/components/AuthProvider';

export default function VerifyEmailPage() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const { verifyEmail, resendVerification } = useAuth();
    
    const [email, setEmail] = useState('');
    const [code, setCode] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [loading, setLoading] = useState(false);
    const [resending, setResending] = useState(false);
    const [resendCooldown, setResendCooldown] = useState(0);

    useEffect(() => {
        const emailParam = searchParams.get('email');
        if (emailParam) {
            setEmail(decodeURIComponent(emailParam));
        }
    }, [searchParams]);

    useEffect(() => {
        let interval: NodeJS.Timeout;
        if (resendCooldown > 0) {
            interval = setInterval(() => {
                setResendCooldown(prev => prev - 1);
            }, 1000);
        }
        return () => clearInterval(interval);
    }, [resendCooldown]);

    const handleCodeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value.replace(/\D/g, '').slice(0, 6);
        setCode(value);
    };

    const handleVerify = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setSuccess('');
        setLoading(true);

        if (code.length !== 6) {
            setError('Please enter a 6-digit code');
            setLoading(false);
            return;
        }

        try {
            await verifyEmail(email, code);
            setSuccess('Email verified successfully! Redirecting to login...');
            setTimeout(() => {
                router.push(`/auth/login?email=${encodeURIComponent(email)}`);
            }, 2000);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to verify email');
        } finally {
            setLoading(false);
        }
    };

    const handleResendCode = async () => {
        setError('');
        setSuccess('');
        setResending(true);

        try {
            await resendVerification(email);
            setSuccess('New verification code sent to your email');
            setResendCooldown(60);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to resend code');
        } finally {
            setResending(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-[#0d1117] via-[#161b22] to-[#010409] flex items-center justify-center px-4">
            <div className="w-full max-w-md">
                <div className="bg-[#161b22] rounded-2xl shadow-2xl shadow-black/50 p-8 border border-gray-800/50">
                    {/* Header */}
                    <div className="text-center mb-8">
                        <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-500 to-emerald-500 rounded-2xl mb-4 shadow-lg shadow-blue-500/30">
                            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                            </svg>
                        </div>
                        <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent mb-2">
                            Verify Email
                        </h1>
                        <p className="text-gray-400">Enter the 6-digit code sent to your email</p>
                    </div>

                    {/* Error Message */}
                    {error && (
                        <div className="mb-6 p-4 bg-red-500/10 border border-red-500/50 rounded-lg text-red-400 text-sm">
                            {error}
                        </div>
                    )}

                    {/* Success Message */}
                    {success && (
                        <div className="mb-6 p-4 bg-blue-500/10 border border-blue-500/50 rounded-lg text-blue-400 text-sm">
                            {success}
                        </div>
                    )}

                    {/* Form */}
                    <form onSubmit={handleVerify} className="space-y-5">
                        {/* Email Field (Disabled) */}
                        <div>
                            <label className="block text-sm font-semibold text-white mb-2">
                                Email
                            </label>
                            <input
                                type="email"
                                value={email}
                                disabled
                                className="w-full px-4 py-3 bg-[#0d1117] border-2 border-gray-800 rounded-lg text-gray-500 cursor-not-allowed"
                            />
                        </div>

                        {/* Verification Code Field */}
                        <div>
                            <label htmlFor="code" className="block text-sm font-semibold text-white mb-2">
                                Verification Code
                            </label>
                            <input
                                type="text"
                                id="code"
                                value={code}
                                onChange={handleCodeChange}
                                placeholder="000000"
                                maxLength={6}
                                className="w-full px-4 py-3 bg-[#0d1117] border-2 border-gray-700 rounded-lg text-white placeholder-gray-600 focus:outline-none focus:border-blue-500 text-center text-2xl tracking-[0.5em] font-mono transition"
                                disabled={loading}
                                autoFocus
                            />
                            <p className="text-xs text-gray-500 mt-2 text-center">Enter the 6-digit code from your email</p>
                        </div>

                        {/* Verify Button */}
                        <button
                            type="submit"
                            disabled={loading || code.length !== 6}
                            className="w-full py-3 px-4 bg-gradient-to-r from-blue-600 to-emerald-600 hover:from-blue-700 hover:to-emerald-700 text-white rounded-lg font-semibold transition shadow-lg shadow-blue-500/20 hover:shadow-blue-500/40 disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none"
                        >
                            {loading ? (
                                <span className="flex items-center justify-center gap-2">
                                    <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                    Verifying...
                                </span>
                            ) : (
                                'Verify Email'
                            )}
                        </button>
                    </form>

                    {/* Resend Section */}
                    <div className="mt-6 pt-6 border-t border-gray-800/50">
                        <p className="text-sm text-gray-400 mb-3 text-center">Didn't receive the code?</p>
                        <button
                            onClick={handleResendCode}
                            disabled={resending || resendCooldown > 0}
                            className="w-full py-3 px-4 bg-gray-800 text-gray-300 rounded-lg hover:bg-gray-700 transition font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {resending ? (
                                <span className="flex items-center justify-center gap-2">
                                    <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                    Sending...
                                </span>
                            ) : resendCooldown > 0 ? (
                                `Resend in ${resendCooldown}s`
                            ) : (
                                'Resend Code'
                            )}
                        </button>
                    </div>

                    {/* Sign Up Again Link */}
                    <p className="mt-6 text-center text-sm text-gray-400">
                        Wrong email?{' '}
                        <button
                            onClick={() => router.push('/auth/signup')}
                            className="text-blue-400 hover:text-Blue-300 font-semibold transition"
                        >
                            Sign up again
                        </button>
                    </p>
                </div>
            </div>
        </div>
    );
}
