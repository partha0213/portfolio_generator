'use client';

import Link from 'next/link';
import { useAuth } from '@/components/AuthProvider';

export default function LandingPage() {
  const { user } = useAuth();

  const features = [
    {
      icon: '⚡',
      title: 'AI-Powered Generation',
      description: 'Upload your resume and our AI instantly generates a professional portfolio tailored to your skills'
    },
    {
      icon: '🎨',
      title: 'Modern Themes',
      description: 'Choose from multiple beautiful, customizable themes that reflect your personal style'
    },
    {
      icon: '📱',
      title: 'Fully Responsive',
      description: 'Your portfolio looks perfect on desktop, tablet, and mobile devices'
    },
    {
      icon: '✏️',
      title: 'Live Editor',
      description: 'Edit your portfolio in real-time with instant preview of all changes'
    },
    {
      icon: '💾',
      title: 'Export & Deploy',
      description: 'Get production-ready code and deploy directly to Vercel, Netlify, or your own hosting'
    },
    {
      icon: '🤖',
      title: 'AI Chat Assistant',
      description: 'Get intelligent suggestions and improvements from our AI portfolio expert'
    }
  ];

  const steps = [
    {
      number: '1',
      title: 'Sign Up',
      description: 'Create a free account in minutes with just your email'
    },
    {
      number: '2',
      title: 'Upload Resume',
      description: 'Upload your resume (PDF, DOC, or DOCX format)'
    },
    {
      number: '3',
      title: 'Describe Your Vision',
      description: 'Tell us what kind of portfolio you want - style, layout, features'
    },
    {
      number: '4',
      title: 'AI Generates',
      description: 'Our AI creates a professional portfolio based on your input'
    },
    {
      number: '5',
      title: 'Edit & Customize',
      description: 'Fine-tune your portfolio with our intuitive live editor'
    },
    {
      number: '6',
      title: 'Deploy',
      description: 'Export your code and deploy to your preferred hosting platform'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0d1117] via-[#161b22] to-[#010409]">
      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-6 py-20 text-center">
        <h2 className="text-5xl md:text-6xl font-bold bg-gradient-to-r from-blue-400 via-cyan-400 to-purple-400 bg-clip-text text-transparent mb-6">
          Create Your Professional Portfolio in Minutes
        </h2>
        <p className="text-xl text-gray-400 mb-8 max-w-3xl mx-auto">
          Upload your resume, tell us your vision, and let our AI generate a stunning, customizable portfolio. No coding required.
        </p>
        <div className="flex gap-4 justify-center flex-wrap">
          {user ? (
            <Link href="/dashboard" className="px-8 py-3 bg-gradient-to-r from-blue-600 to-blue-500 text-white rounded-lg hover:from-blue-700 hover:to-blue-600 transition font-semibold shadow-lg shadow-blue-500/20 hover:shadow-blue-500/40">
              Go to Dashboard
            </Link>
          ) : (
            <>
              <Link href="/auth/signup" className="px-8 py-3 bg-gradient-to-r from-blue-600 to-blue-500 text-white rounded-lg hover:from-blue-700 hover:to-blue-600 transition font-semibold shadow-lg shadow-blue-500/20 hover:shadow-blue-500/40">
                Start Creating
              </Link>
              <Link href="#how-it-works" className="px-8 py-3 border-2 border-gray-700 text-gray-300 rounded-lg hover:bg-gray-800/50 hover:border-gray-600 transition font-semibold">
                Learn More
              </Link>
            </>
          )}
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="max-w-7xl mx-auto px-6 py-20">
        <h3 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent text-center mb-12">
          Powerful Features
        </h3>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, idx) => (
            <div key={idx} className="bg-[#161b22] rounded-xl p-8 shadow-xl shadow-black/50 hover:shadow-2xl hover:shadow-black/60 transition border border-gray-800/50 hover:border-gray-700">
              <div className="text-4xl mb-4">{feature.icon}</div>
              <h4 className="text-xl font-bold text-white mb-2">{feature.title}</h4>
              <p className="text-gray-400">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="bg-[#0d1117] py-20 border-y border-gray-800/50">
        <div className="max-w-7xl mx-auto px-6">
          <h3 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent text-center mb-12">
            How It Works
          </h3>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {steps.map((step, idx) => (
              <div key={idx} className="relative">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0">
                    <div className="flex items-center justify-center h-12 w-12 rounded-full bg-gradient-to-br from-blue-500 to-cyan-500 text-white font-bold text-lg shadow-lg shadow-blue-500/30">
                      {step.number}
                    </div>
                  </div>
                  <div>
                    <h4 className="text-xl font-bold text-white mb-2">{step.title}</h4>
                    <p className="text-gray-400">{step.description}</p>
                  </div>
                </div>
                {idx < steps.length - 1 && (
                  <div className="hidden lg:block absolute top-12 -right-4 w-8 h-0.5 bg-gray-700" />
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="max-w-7xl mx-auto px-6 py-20">
        <h3 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent text-center mb-12">
          Why Choose Portfolio AI?
        </h3>
        <div className="grid md:grid-cols-2 gap-8">
          <div className="bg-gradient-to-br from-blue-500/10 to-blue-600/5 rounded-xl p-8 border border-blue-500/20 hover:border-blue-500/40 transition">
            <h4 className="text-2xl font-bold text-white mb-4">⏱️ Save Time</h4>
            <p className="text-gray-400">Create a professional portfolio in minutes instead of hours or days of manual design and coding.</p>
          </div>
          <div className="bg-gradient-to-br from-purple-500/10 to-purple-600/5 rounded-xl p-8 border border-purple-500/20 hover:border-purple-500/40 transition">
            <h4 className="text-2xl font-bold text-white mb-4">🎯 Stand Out</h4>
            <p className="text-gray-400">Use AI-powered design and copy suggestions to make your portfolio truly unique and impressive.</p>
          </div>
          <div className="bg-gradient-to-br from-pink-500/10 to-pink-600/5 rounded-xl p-8 border border-pink-500/20 hover:border-pink-500/40 transition">
            <h4 className="text-2xl font-bold text-white mb-4">💻 Full Control</h4>
            <p className="text-gray-400">Export production-ready code and customize everything to match your exact specifications.</p>
          </div>
          <div className="bg-gradient-to-br from-green-500/10 to-green-600/5 rounded-xl p-8 border border-green-500/20 hover:border-green-500/40 transition">
            <h4 className="text-2xl font-bold text-white mb-4">🚀 Deploy Anywhere</h4>
            <p className="text-gray-400">Deploy your portfolio to Vercel, Netlify, GitHub Pages, or your own server with just a few clicks.</p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-gradient-to-r from-blue-600 via-cyan-600 to-purple-600 py-20 border-y border-gray-800/50">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h3 className="text-4xl font-bold text-white mb-6">Ready to Build Your Portfolio?</h3>
          <p className="text-xl text-blue-100 mb-8">Join thousands of professionals who've created stunning portfolios with Portfolio AI.</p>
          {user ? (
            <Link href="/dashboard" className="inline-block px-8 py-3 bg-white text-blue-600 rounded-lg hover:bg-gray-100 transition font-semibold shadow-lg">
              Go to Dashboard
            </Link>
          ) : (
            <Link href="/auth/signup" className="inline-block px-8 py-3 bg-white text-blue-600 rounded-lg hover:bg-gray-100 transition font-semibold shadow-lg">
              Get Started Free
            </Link>
          )}
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-[#0d1117] text-gray-400 py-12 border-t border-gray-800/50">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <p>&copy; 2025 Portfolio AI. All rights reserved.</p>
          <div className="flex justify-center gap-6 mt-4">
            <a href="#" className="hover:text-white transition">Privacy Policy</a>
            <a href="#" className="hover:text-white transition">Terms of Service</a>
            <a href="#" className="hover:text-white transition">Contact</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
