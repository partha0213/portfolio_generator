'use client';

import Link from 'next/link';
import { useAuth } from '@/components/AuthProvider';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import UploadResume from '@/components/UploadResume';

export default function LandingPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [showUploadModal, setShowUploadModal] = useState(false);

  const handleStartCreating = () => {
    if (user) {
      setShowUploadModal(true);
    } else {
      router.push('/auth/signup');
    }
  };

  if (showUploadModal && user) {
    return <UploadResume />;
  }

  const features = [
    {
      icon: '⚡',
      title: 'AI-Powered',
      description: 'Instantly generate portfolios with AI analysis'
    },
    {
      icon: '🎨',
      title: 'Customizable',
      description: 'Choose from multiple modern themes'
    },
    {
      icon: '📱',
      title: 'Responsive',
      description: 'Perfect on all devices and screen sizes'
    },
    {
      icon: '🚀',
      title: 'Deploy Fast',
      description: 'One-click deployment to Vercel, Netlify'
    },
    {
      icon: '💾',
      title: 'Export Code',
      description: 'Get clean, production-ready source code'
    },
    {
      icon: '🔄',
      title: 'Live Updates',
      description: 'Real-time preview as you edit'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-pink-50 to-red-50">
      {/* Enhanced Header */}
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => router.push('/')}>
            <div className="w-10 h-10 bg-gradient-to-br from-orange-500 to-red-500 rounded-lg flex items-center justify-center shadow-md">
              <span className="text-white font-bold text-lg">P</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">Portfolio AI</h1>
              <p className="text-xs text-gray-500">Build in Minutes</p>
            </div>
          </div>
          
          <nav className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-gray-600 hover:text-gray-900 font-medium transition">Features</a>
            <a href="#how-it-works" className="text-gray-600 hover:text-gray-900 font-medium transition">How it Works</a>
          </nav>

          <div className="flex items-center gap-3">
            {user ? (
              <>
                <Link href="/dashboard" className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition font-medium">
                  Dashboard
                </Link>
                <Link href="/api/auth/logout" className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition">
                  Sign Out
                </Link>
              </>
            ) : (
              <>
                <Link href="/auth/login" className="px-4 py-2 text-gray-600 hover:text-gray-900 font-medium transition">
                  Sign In
                </Link>
                <Link href="/auth/signup" className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium shadow-md">
                  Get Started Free
                </Link>
              </>
            )}
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar with Features */}
        <aside className="hidden lg:flex w-72 bg-white/50 backdrop-blur-sm border-r border-gray-200 flex-col p-8 gap-8 max-h-[calc(100vh-80px)] overflow-y-auto">
          <div>
            <h2 className="text-sm font-bold text-gray-900 uppercase tracking-wide mb-6">Why Choose Us</h2>
            <div className="space-y-4">
              {features.slice(0, 3).map((feature, idx) => (
                <div key={idx} className="group cursor-pointer">
                  <div className="flex items-start gap-3 p-3 rounded-lg hover:bg-gradient-to-r hover:from-orange-50 hover:to-pink-50 transition">
                    <span className="text-2xl flex-shrink-0">{feature.icon}</span>
                    <div>
                      <h3 className="font-semibold text-gray-900 text-sm">{feature.title}</h3>
                      <p className="text-xs text-gray-600 mt-1">{feature.description}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="border-t border-gray-200 pt-6">
            <h2 className="text-sm font-bold text-gray-900 uppercase tracking-wide mb-6">Advanced Features</h2>
            <div className="space-y-4">
              {features.slice(3, 6).map((feature, idx) => (
                <div key={idx} className="group cursor-pointer">
                  <div className="flex items-start gap-3 p-3 rounded-lg hover:bg-gradient-to-r hover:from-blue-50 hover:to-cyan-50 transition">
                    <span className="text-2xl flex-shrink-0">{feature.icon}</span>
                    <div>
                      <h3 className="font-semibold text-gray-900 text-sm">{feature.title}</h3>
                      <p className="text-xs text-gray-600 mt-1">{feature.description}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-gradient-to-r from-blue-50 to-cyan-50 rounded-lg p-4 border border-blue-200">
            <p className="text-xs text-gray-700 font-medium">
              <span className="text-blue-600 font-bold">💡 Pro Tip:</span> Add detailed portfolio descriptions for better AI-generated results
            </p>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 flex items-center justify-center min-h-[calc(100vh-80px)] px-6 py-12">
          <div className="max-w-2xl w-full">
            {/* Heading */}
            <div className="text-center mb-12">
              <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-4">
                What's stopping you?
              </h1>
              <p className="text-xl text-gray-600">
                Upload your resume and describe your ideal portfolio
              </p>
            </div>

            {/* Upload Area */}
            <div className="bg-white rounded-2xl shadow-lg p-8 md:p-12 border border-gray-100">
              <div className="space-y-6">
                {/* Resume Upload */}
                <div>
                  <label className="block text-sm font-semibold text-gray-900 mb-3">
                    Upload Resume
                  </label>
                  <div className="relative">
                    <input
                      type="file"
                      accept=".pdf,.doc,.docx"
                      id="landing-resume"
                      className="w-full px-4 py-3 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-400 transition cursor-pointer file:cursor-pointer file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                      placeholder="Choose file or drag here"
                    />
                  </div>
                </div>

                {/* Prompt Input */}
                <div>
                  <label className="block text-sm font-semibold text-gray-900 mb-3">
                    Portfolio Description
                  </label>
                  <textarea
                    id="landing-prompt"
                    placeholder="Tell us about the portfolio you want to create... (e.g., 'Modern dark theme with animated sections, showcase my 5 best projects, include testimonials')"
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none resize-none h-32"
                  />
                </div>

                {/* Action Buttons */}
                <div className="flex gap-3 pt-4">
                  <button
                    onClick={handleStartCreating}
                    className="flex-1 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-semibold py-3 rounded-lg transition shadow-md hover:shadow-lg"
                  >
                    Generate Portfolio
                  </button>
                  <button className="px-4 py-3 border-2 border-gray-300 rounded-lg text-gray-700 font-semibold hover:bg-gray-50 transition">
                    ⚙️
                  </button>
                </div>

                {/* Additional Options */}
                <div className="flex items-center gap-2 justify-center pt-2 text-sm text-gray-600">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  Supports PDF, DOC, and DOCX formats
                </div>
              </div>
            </div>

            {/* Bottom CTA */}
            <div className="text-center mt-8">
              <p className="text-gray-600 mb-4">
                {user ? "Ready to create your portfolio?" : "Already have an account?"}
              </p>
              {!user && (
                <Link href="/auth/login" className="text-blue-600 hover:text-blue-700 font-semibold">
                  Sign in here →
                </Link>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
