import { useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import {
    TrendingUp,
    Brain,
    MapPin,
    BarChart3,
    FileText,
    Zap,
    Shield,
    Users,
    ArrowRight,
    Check
} from 'lucide-react';

export default function LandingPage() {
    const router = useRouter();

    useEffect(() => {
        // Check if user is already logged in
        const token = localStorage.getItem('token');
        if (token) {
            router.push('/dashboard');
        }
    }, []);

    const features = [
        {
            icon: Brain,
            title: 'AI-Powered Analysis',
            description: 'Multi-agent AI system analyzes your business from every angle'
        },
        {
            icon: TrendingUp,
            title: 'Market Intelligence',
            description: 'Real-time market data, trends, and economic indicators'
        },
        {
            icon: MapPin,
            title: 'Location Analysis',
            description: 'Evaluate location viability with demographic and competition data'
        },
        {
            icon: BarChart3,
            title: 'Revenue Forecasting',
            description: 'AI-powered revenue predictions and ROI calculations'
        },
        {
            icon: FileText,
            title: 'Automated Reports',
            description: 'Generate comprehensive business reports instantly'
        },
        {
            icon: Zap,
            title: 'Real-Time Insights',
            description: 'Get instant answers from your AI business consultant'
        }
    ];

    const howItWorks = [
        {
            step: '1',
            title: 'Create Your Business',
            description: 'Enter your business details, industry, location, and investment'
        },
        {
            step: '2',
            title: 'AI Analysis',
            description: 'Our multi-agent AI system analyzes market, competition, and opportunities'
        },
        {
            step: '3',
            title: 'Get Insights',
            description: 'Receive actionable recommendations, forecasts, and reports'
        },
        {
            step: '4',
            title: 'Make Decisions',
            description: 'Chat with AI consultant and make data-driven business decisions'
        }
    ];

    const pricing = [
        {
            name: 'Starter',
            price: '₹999',
            period: '/month',
            features: [
                '1 Business',
                'Market Analysis',
                'Basic Reports',
                'Email Support'
            ]
        },
        {
            name: 'Professional',
            price: '₹2,999',
            period: '/month',
            features: [
                '5 Businesses',
                'Advanced AI Analysis',
                'Revenue Forecasting',
                'Priority Support',
                'Custom Reports'
            ],
            popular: true
        },
        {
            name: 'Enterprise',
            price: 'Custom',
            period: '',
            features: [
                'Unlimited Businesses',
                'Full AI Suite',
                'API Access',
                'Dedicated Support',
                'Custom Integration'
            ]
        }
    ];

    return (
        <div className="min-h-screen bg-white">
            {/* Navigation */}
            <nav className="fixed top-0 w-full bg-white/80 backdrop-blur-md border-b border-gray-200 z-50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-center h-16">
                        <div className="flex items-center">
                            <Brain className="w-8 h-8 text-blue-600" />
                            <span className="ml-2 text-2xl font-bold text-gray-900">BizIntel AI</span>
                        </div>
                        <div className="flex items-center gap-4">
                            <Link
                                href="/login"
                                className="text-gray-700 hover:text-gray-900 font-medium"
                            >
                                Login
                            </Link>
                            <Link
                                href="/register"
                                className="px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 transition"
                            >
                                Get Started
                            </Link>
                        </div>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <section className="pt-32 pb-20 px-4 bg-gradient-to-br from-blue-50 to-purple-50">
                <div className="max-w-7xl mx-auto text-center">
                    <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
                        AI-Powered Business
                        <br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">
                            Intelligence Platform
                        </span>
                    </h1>
                    <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
                        Make smarter business decisions with AI-driven market analysis,
                        location intelligence, and revenue forecasting. All in one platform.
                    </p>
                    <div className="flex gap-4 justify-center">
                        <Link
                            href="/register"
                            className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-semibold text-lg hover:from-blue-700 hover:to-purple-700 transition inline-flex items-center gap-2"
                        >
                            Start Free Trial
                            <ArrowRight className="w-5 h-5" />
                        </Link>
                        <button className="px-8 py-4 bg-white text-gray-900 rounded-lg font-semibold text-lg hover:bg-gray-50 transition border-2 border-gray-200">
                            Watch Demo
                        </button>
                    </div>
                    <p className="mt-4 text-sm text-gray-500">
                        No credit card required • 14-day free trial
                    </p>
                </div>
            </section>

            {/* Features Section */}
            <section className="py-20 px-4">
                <div className="max-w-7xl mx-auto">
                    <div className="text-center mb-16">
                        <h2 className="text-4xl font-bold text-gray-900 mb-4">
                            Everything You Need to Succeed
                        </h2>
                        <p className="text-xl text-gray-600">
                            Powerful features to analyze and grow your business
                        </p>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                        {features.map((feature, idx) => {
                            const Icon = feature.icon;
                            return (
                                <div key={idx} className="p-6 bg-white rounded-xl border-2 border-gray-200 hover:border-blue-500 hover:shadow-lg transition">
                                    <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center mb-4">
                                        <Icon className="w-6 h-6 text-white" />
                                    </div>
                                    <h3 className="text-xl font-bold text-gray-900 mb-2">
                                        {feature.title}
                                    </h3>
                                    <p className="text-gray-600">
                                        {feature.description}
                                    </p>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </section>

            {/* How It Works */}
            <section className="py-20 px-4 bg-gray-50">
                <div className="max-w-7xl mx-auto">
                    <div className="text-center mb-16">
                        <h2 className="text-4xl font-bold text-gray-900 mb-4">
                            How It Works
                        </h2>
                        <p className="text-xl text-gray-600">
                            Get started in minutes, make decisions in seconds
                        </p>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                        {howItWorks.map((item, idx) => (
                            <div key={idx} className="text-center">
                                <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full flex items-center justify-center text-white text-2xl font-bold mx-auto mb-4">
                                    {item.step}
                                </div>
                                <h3 className="text-xl font-bold text-gray-900 mb-2">
                                    {item.title}
                                </h3>
                                <p className="text-gray-600">
                                    {item.description}
                                </p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Pricing */}
            <section className="py-20 px-4">
                <div className="max-w-7xl mx-auto">
                    <div className="text-center mb-16">
                        <h2 className="text-4xl font-bold text-gray-900 mb-4">
                            Simple, Transparent Pricing
                        </h2>
                        <p className="text-xl text-gray-600">
                            Choose the plan that fits your needs
                        </p>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                        {pricing.map((plan, idx) => (
                            <div
                                key={idx}
                                className={`p-8 rounded-2xl ${plan.popular
                                        ? 'bg-gradient-to-br from-blue-600 to-purple-600 text-white shadow-2xl scale-105'
                                        : 'bg-white border-2 border-gray-200'
                                    }`}
                            >
                                {plan.popular && (
                                    <div className="text-center mb-4">
                                        <span className="px-4 py-1 bg-white/20 rounded-full text-sm font-semibold">
                                            Most Popular
                                        </span>
                                    </div>
                                )}
                                <h3 className={`text-2xl font-bold mb-2 ${plan.popular ? 'text-white' : 'text-gray-900'}`}>
                                    {plan.name}
                                </h3>
                                <div className="mb-6">
                                    <span className={`text-4xl font-bold ${plan.popular ? 'text-white' : 'text-gray-900'}`}>
                                        {plan.price}
                                    </span>
                                    <span className={plan.popular ? 'text-white/80' : 'text-gray-600'}>
                                        {plan.period}
                                    </span>
                                </div>
                                <ul className="space-y-3 mb-8">
                                    {plan.features.map((feature, fidx) => (
                                        <li key={fidx} className="flex items-center gap-2">
                                            <Check className={`w-5 h-5 ${plan.popular ? 'text-white' : 'text-green-600'}`} />
                                            <span className={plan.popular ? 'text-white' : 'text-gray-700'}>
                                                {feature}
                                            </span>
                                        </li>
                                    ))}
                                </ul>
                                <button
                                    className={`w-full py-3 rounded-lg font-semibold transition ${plan.popular
                                            ? 'bg-white text-blue-600 hover:bg-gray-100'
                                            : 'bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700'
                                        }`}
                                >
                                    Get Started
                                </button>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="py-20 px-4 bg-gradient-to-r from-blue-600 to-purple-600">
                <div className="max-w-4xl mx-auto text-center text-white">
                    <h2 className="text-4xl font-bold mb-4">
                        Ready to Transform Your Business?
                    </h2>
                    <p className="text-xl mb-8 opacity-90">
                        Join thousands of entrepreneurs making smarter decisions with AI
                    </p>
                    <Link
                        href="/register"
                        className="inline-flex items-center gap-2 px-8 py-4 bg-white text-blue-600 rounded-lg font-semibold text-lg hover:bg-gray-100 transition"
                    >
                        Start Your Free Trial
                        <ArrowRight className="w-5 h-5" />
                    </Link>
                </div>
            </section>

            {/* Footer */}
            <footer className="py-12 px-4 bg-gray-900 text-white">
                <div className="max-w-7xl mx-auto">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
                        <div>
                            <div className="flex items-center mb-4">
                                <Brain className="w-8 h-8 text-blue-400" />
                                <span className="ml-2 text-xl font-bold">BizIntel AI</span>
                            </div>
                            <p className="text-gray-400">
                                AI-powered business intelligence for smarter decisions
                            </p>
                        </div>
                        <div>
                            <h4 className="font-semibold mb-4">Product</h4>
                            <ul className="space-y-2 text-gray-400">
                                <li><a href="#" className="hover:text-white">Features</a></li>
                                <li><a href="#" className="hover:text-white">Pricing</a></li>
                                <li><a href="#" className="hover:text-white">API</a></li>
                            </ul>
                        </div>
                        <div>
                            <h4 className="font-semibold mb-4">Company</h4>
                            <ul className="space-y-2 text-gray-400">
                                <li><a href="#" className="hover:text-white">About</a></li>
                                <li><a href="#" className="hover:text-white">Blog</a></li>
                                <li><a href="#" className="hover:text-white">Careers</a></li>
                            </ul>
                        </div>
                        <div>
                            <h4 className="font-semibold mb-4">Legal</h4>
                            <ul className="space-y-2 text-gray-400">
                                <li><a href="#" className="hover:text-white">Privacy</a></li>
                                <li><a href="#" className="hover:text-white">Terms</a></li>
                                <li><a href="#" className="hover:text-white">Security</a></li>
                            </ul>
                        </div>
                    </div>
                    <div className="border-t border-gray-800 pt-8 text-center text-gray-400">
                        <p>&copy; 2024 BizIntel AI. All rights reserved.</p>
                    </div>
                </div>
            </footer>
        </div>
    );
}
