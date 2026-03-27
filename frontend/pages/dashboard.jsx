import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { motion } from 'framer-motion';
import ProtectedRoute from '../components/ProtectedRoute';
import { useAuth } from '../contexts/AuthContext';
import { useBusiness } from '../contexts/BusinessContext';
import {
    Brain,
    Plus,
    Building2,
    TrendingUp,
    MapPin,
    FileText,
    LogOut,
    Settings,
    Sparkles,
    ArrowRight
} from 'lucide-react';
import Link from 'next/link';

export default function Dashboard() {
    return (
        <ProtectedRoute>
            <DashboardContent />
        </ProtectedRoute>
    );
}

function DashboardContent() {
    const { user, logout } = useAuth();
    const { businesses, currentBusiness, loading } = useBusiness();
    const router = useRouter();

    useEffect(() => {
        if (!loading && currentBusiness) {
            router.push('/overview');
        }
    }, [currentBusiness, loading, router]);

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-secondary-50">
                <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="text-center"
                >
                    <div className="relative w-16 h-16 mx-auto mb-4">
                        <div className="absolute inset-0 border-4 border-primary-200 rounded-full"></div>
                        <div className="absolute inset-0 border-4 border-primary-600 rounded-full border-t-transparent animate-spin"></div>
                    </div>
                    <p className="text-secondary-600 font-medium">Loading...</p>
                </motion.div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-secondary-50 via-white to-primary-50">
            {/* Header */}
            <header className="bg-white border-b border-secondary-200">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-center h-16">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-gradient-to-br from-primary-600 to-primary-700 rounded-xl flex items-center justify-center">
                                <Sparkles className="w-6 h-6 text-white" />
                            </div>
                            <div>
                                <span className="text-xl font-bold text-secondary-900">BizIntel AI</span>
                                <p className="text-xs text-secondary-500">Intelligence Platform</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-3">
                            <span className="text-sm text-secondary-600">Welcome, <span className="font-semibold">{user?.name}</span></span>
                            <Link href="/settings" className="p-2 hover:bg-secondary-50 rounded-lg transition-colors">
                                <Settings className="w-5 h-5 text-secondary-600" />
                            </Link>
                            <button
                                onClick={logout}
                                className="flex items-center gap-2 px-4 py-2 text-secondary-700 hover:bg-secondary-50 rounded-lg transition-colors"
                            >
                                <LogOut className="w-4 h-4" />
                                <span className="text-sm font-medium">Logout</span>
                            </button>
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                {businesses.length === 0 ? (
                    // No businesses - show welcome
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="text-center py-16"
                    >
                        <motion.div
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            transition={{ type: 'spring', delay: 0.2 }}
                            className="inline-flex items-center justify-center w-24 h-24 bg-gradient-to-br from-primary-100 to-primary-200 rounded-2xl mb-6"
                        >
                            <Building2 className="w-12 h-12 text-primary-600" />
                        </motion.div>
                        <h1 className="text-4xl font-bold text-secondary-900 mb-4">
                            Welcome to BizIntel AI
                        </h1>
                        <p className="text-lg text-secondary-600 mb-8 max-w-2xl mx-auto">
                            Get started by creating your first business. Our AI agents will analyze market opportunities,
                            location intelligence, economic trends, and provide actionable insights.
                        </p>
                        <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={() => router.push('/select-business')}
                            className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-xl font-semibold hover:from-primary-700 hover:to-primary-800 transition-all shadow-lg shadow-primary-200"
                        >
                            <Plus className="w-5 h-5" />
                            Create Your First Business
                        </motion.button>

                        {/* Features Preview */}
                        <div className="mt-20 grid md:grid-cols-3 gap-8 text-left">
                            {[
                                {
                                    icon: TrendingUp,
                                    title: 'Market Analysis',
                                    description: 'AI-powered market research, demand forecasting, and competition analysis',
                                    color: 'from-primary-500 to-primary-600'
                                },
                                {
                                    icon: MapPin,
                                    title: 'Location Intelligence',
                                    description: 'Geographic insights, logistics optimization, and local market conditions',
                                    color: 'from-success-500 to-success-600'
                                },
                                {
                                    icon: FileText,
                                    title: 'AI Reports',
                                    description: 'Automated forecasts, revenue projections, and comprehensive business reports',
                                    color: 'from-warning-500 to-warning-600'
                                }
                            ].map((feature, index) => (
                                <motion.div
                                    key={feature.title}
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: 0.4 + index * 0.1 }}
                                    whileHover={{ y: -4 }}
                                    className="bg-white p-6 rounded-xl shadow-card hover:shadow-hover transition-all border border-secondary-200"
                                >
                                    <div className={`w-12 h-12 bg-gradient-to-br ${feature.color} rounded-xl flex items-center justify-center mb-4`}>
                                        <feature.icon className="w-6 h-6 text-white" />
                                    </div>
                                    <h3 className="text-lg font-semibold text-secondary-900 mb-2">{feature.title}</h3>
                                    <p className="text-secondary-600 text-sm leading-relaxed">{feature.description}</p>
                                </motion.div>
                            ))}
                        </div>
                    </motion.div>
                ) : (
                    // Has businesses - show list
                    <div>
                        <div className="flex justify-between items-center mb-8">
                            <motion.div
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                            >
                                <h1 className="text-3xl font-bold text-secondary-900 mb-2">Your Businesses</h1>
                                <p className="text-secondary-600">Select a business to view insights and analysis</p>
                            </motion.div>
                            <motion.button
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                onClick={() => router.push('/select-business')}
                                className="flex items-center gap-2 px-4 py-2.5 bg-primary-600 text-white rounded-xl hover:bg-primary-700 transition-colors shadow-sm font-medium"
                            >
                                <Plus className="w-5 h-5" />
                                New Business
                            </motion.button>
                        </div>

                        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {businesses.map((business, index) => (
                                <motion.button
                                    key={business.id}
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: index * 0.1 }}
                                    whileHover={{ y: -4 }}
                                    onClick={() => {
                                        router.push(`/business/${business.id}/overview`);
                                    }}
                                    className="bg-white p-6 rounded-xl shadow-card hover:shadow-hover transition-all text-left border border-secondary-200 group"
                                >
                                    <div className="flex items-start justify-between mb-4">
                                        <div className="w-14 h-14 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center">
                                            <Building2 className="w-7 h-7 text-white" />
                                        </div>
                                        <ArrowRight className="w-5 h-5 text-secondary-400 group-hover:text-primary-600 group-hover:translate-x-1 transition-all" />
                                    </div>
                                    <h3 className="text-xl font-semibold text-secondary-900 mb-3">
                                        {business.name}
                                    </h3>
                                    <div className="space-y-2 text-sm text-secondary-600">
                                        <p className="flex items-center gap-2">
                                            <span className="w-2 h-2 bg-primary-500 rounded-full"></span>
                                            {business.industry}
                                        </p>
                                        <p className="flex items-center gap-2">
                                            <span className="w-2 h-2 bg-success-500 rounded-full"></span>
                                            {business.city}, {business.state}
                                        </p>
                                        <p className="flex items-center gap-2 font-semibold text-primary-600">
                                            <span className="w-2 h-2 bg-warning-500 rounded-full"></span>
                                            ₹{business.investment?.toLocaleString()} investment
                                        </p>
                                    </div>
                                </motion.button>
                            ))}
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}
