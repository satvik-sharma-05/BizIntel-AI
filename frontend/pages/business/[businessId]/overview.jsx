import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { motion } from 'framer-motion';
import MainLayout from '../../../components/MainLayout';
import KPICard from '../../../components/KPICard';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/Card';
import { PageLoader, CardSkeleton } from '../../../components/LoadingState';
import { dashboardAPI, businessAPI } from '../../../lib/api';
import {
    TrendingUp,
    DollarSign,
    Briefcase,
    MapPin,
    Activity,
    ArrowRight,
    Sparkles,
    MessageSquare,
    Bot,
    Cloud,
    Users
} from 'lucide-react';

export default function BusinessOverview() {
    const router = useRouter();
    const { businessId } = router.query;
    const [business, setBusiness] = useState(null);
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (businessId) {
            loadBusinessData();
        }
    }, [businessId]);

    const loadBusinessData = async () => {
        try {
            const businessData = await businessAPI.get(businessId);
            setBusiness(businessData);

            const dashboardData = await dashboardAPI.getDashboard(businessId);
            setData(dashboardData);
        } catch (error) {
            console.error('Error loading business data:', error);
            if (error.response?.status === 404) {
                router.push('/select-business');
            }
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <MainLayout>
                <PageLoader />
            </MainLayout>
        );
    }

    if (!business) {
        return (
            <MainLayout>
                <div className="flex items-center justify-center h-full">
                    <div className="text-center">
                        <div className="text-xl text-secondary-600 mb-4">Business not found</div>
                        <button
                            onClick={() => router.push('/select-business')}
                            className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                        >
                            Select Business
                        </button>
                    </div>
                </div>
            </MainLayout>
        );
    }

    const economicData = data?.market?.economic_indicators || {};
    const gdpData = data?.market?.gdp || {};
    const locationData = data?.location || {};
    const weatherData = locationData?.weather || {};

    const formatNumber = (num) => {
        if (!num) return 'N/A';
        if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
        if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
        return num.toLocaleString();
    };

    const baseUrl = `/business/${businessId}`;

    return (
        <MainLayout>
            <div className="space-y-8">
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                >
                    <h1 className="text-3xl font-bold text-secondary-900">{business.name}</h1>
                    <p className="text-secondary-600 mt-2">Business Intelligence & Market Analysis</p>
                </motion.div>

                {/* Business Info Card */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-gradient-to-br from-primary-600 via-primary-700 to-primary-800 rounded-2xl shadow-lg p-8 text-white"
                >
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                        <div>
                            <div className="flex items-center gap-2 mb-2 opacity-90">
                                <Briefcase className="w-5 h-5" />
                                <span className="text-sm font-medium">Industry</span>
                            </div>
                            <div className="text-2xl font-bold">{business.industry}</div>
                        </div>
                        <div>
                            <div className="flex items-center gap-2 mb-2 opacity-90">
                                <MapPin className="w-5 h-5" />
                                <span className="text-sm font-medium">Location</span>
                            </div>
                            <div className="text-2xl font-bold">
                                {business.city}, {business.state}
                            </div>
                        </div>
                        <div>
                            <div className="flex items-center gap-2 mb-2 opacity-90">
                                <DollarSign className="w-5 h-5" />
                                <span className="text-sm font-medium">Investment</span>
                            </div>
                            <div className="text-2xl font-bold">
                                ₹{business.investment?.toLocaleString()}
                            </div>
                        </div>
                        <div>
                            <div className="flex items-center gap-2 mb-2 opacity-90">
                                <Cloud className="w-5 h-5" />
                                <span className="text-sm font-medium">Weather</span>
                            </div>
                            <div className="text-2xl font-bold">
                                {weatherData.temperature ? `${weatherData.temperature}°C` : 'Loading...'}
                            </div>
                        </div>
                    </div>
                    {business.description && (
                        <div className="mt-6 pt-6 border-t border-white border-opacity-20">
                            <p className="text-white opacity-90 leading-relaxed">{business.description}</p>
                        </div>
                    )}
                </motion.div>

                {/* KPI Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <KPICard
                        title="GDP Growth"
                        value={gdpData.growth ? `${gdpData.growth}%` : 'Loading...'}
                        icon={TrendingUp}
                        trend="up"
                        trendValue={gdpData.year || 'Latest'}
                        description="Economic growth indicator"
                        color="success"
                        index={0}
                    />
                    <KPICard
                        title={`MSMEs in ${business.state}`}
                        value={locationData.msme_count ? formatNumber(locationData.msme_count) : 'Loading...'}
                        icon={Users}
                        description="Active business ecosystem"
                        color="primary"
                        index={1}
                    />
                    <KPICard
                        title="Inflation Rate"
                        value={economicData.inflation ? `${economicData.inflation}%` : 'Loading...'}
                        icon={Activity}
                        description="Economic indicator"
                        color="warning"
                        index={2}
                    />
                    <KPICard
                        title="Weather"
                        value={weatherData.temp ? `${weatherData.temp}°C` : 'Loading...'}
                        icon={Cloud}
                        description={weatherData.description || business.city}
                        color="info"
                        index={3}
                    />
                </div>

                {/* Quick Actions & Market Insights */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Quick Actions */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Quick Actions</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-3">
                            <motion.button
                                whileHover={{ x: 4 }}
                                onClick={() => router.push(`${baseUrl}/market`)}
                                className="w-full flex items-center gap-3 p-4 bg-primary-50 hover:bg-primary-100 rounded-xl transition-colors text-left group"
                            >
                                <div className="w-12 h-12 bg-gradient-to-br from-primary-600 to-primary-700 rounded-xl flex items-center justify-center">
                                    <TrendingUp className="w-6 h-6 text-white" />
                                </div>
                                <div className="flex-1">
                                    <div className="font-semibold text-secondary-900">Analyze Market</div>
                                    <div className="text-sm text-secondary-600">Get {business.industry} insights</div>
                                </div>
                                <ArrowRight className="w-5 h-5 text-secondary-400 group-hover:text-primary-600 transition-colors" />
                            </motion.button>

                            <motion.button
                                whileHover={{ x: 4 }}
                                onClick={() => router.push(`${baseUrl}/forecast`)}
                                className="w-full flex items-center gap-3 p-4 bg-success-50 hover:bg-success-100 rounded-xl transition-colors text-left group"
                            >
                                <div className="w-12 h-12 bg-gradient-to-br from-success-600 to-success-700 rounded-xl flex items-center justify-center">
                                    <Activity className="w-6 h-6 text-white" />
                                </div>
                                <div className="flex-1">
                                    <div className="font-semibold text-secondary-900">Generate Forecast</div>
                                    <div className="text-sm text-secondary-600">Revenue & growth predictions</div>
                                </div>
                                <ArrowRight className="w-5 h-5 text-secondary-400 group-hover:text-success-600 transition-colors" />
                            </motion.button>

                            <motion.button
                                whileHover={{ x: 4 }}
                                onClick={() => router.push(`${baseUrl}/location`)}
                                className="w-full flex items-center gap-3 p-4 bg-info-50 hover:bg-info-100 rounded-xl transition-colors text-left group"
                            >
                                <div className="w-12 h-12 bg-gradient-to-br from-info-600 to-info-700 rounded-xl flex items-center justify-center">
                                    <MapPin className="w-6 h-6 text-white" />
                                </div>
                                <div className="flex-1">
                                    <div className="font-semibold text-secondary-900">Location Analysis</div>
                                    <div className="text-sm text-secondary-600">Analyze {business.city}</div>
                                </div>
                                <ArrowRight className="w-5 h-5 text-secondary-400 group-hover:text-info-600 transition-colors" />
                            </motion.button>
                        </CardContent>
                    </Card>

                    {/* Market Insights */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Market Insights</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <motion.div
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: 0.1 }}
                                className="flex items-start gap-3"
                            >
                                <div className="w-2 h-2 bg-success-600 rounded-full mt-2 flex-shrink-0"></div>
                                <div className="flex-1">
                                    <div className="text-sm font-medium text-secondary-900">
                                        {gdpData.growth ? 'Strong Economic Growth' : 'Economic Data Loading'}
                                    </div>
                                    <div className="text-xs text-secondary-500 mt-1">
                                        {gdpData.growth
                                            ? `GDP growing at ${gdpData.growth}% - favorable for ${business.industry}`
                                            : 'Fetching latest economic indicators...'
                                        }
                                    </div>
                                </div>
                            </motion.div>

                            <motion.div
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: 0.2 }}
                                className="flex items-start gap-3"
                            >
                                <div className="w-2 h-2 bg-primary-600 rounded-full mt-2 flex-shrink-0"></div>
                                <div className="flex-1">
                                    <div className="text-sm font-medium text-secondary-900">
                                        Active MSME Ecosystem
                                    </div>
                                    <div className="text-xs text-secondary-500 mt-1">
                                        {locationData.msme_count
                                            ? `${formatNumber(locationData.msme_count)} MSMEs in ${business.state}`
                                            : `Loading MSME data for ${business.state}...`
                                        }
                                    </div>
                                </div>
                            </motion.div>

                            <motion.div
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: 0.3 }}
                                className="flex items-start gap-3"
                            >
                                <div className="w-2 h-2 bg-info-600 rounded-full mt-2 flex-shrink-0"></div>
                                <div className="flex-1">
                                    <div className="text-sm font-medium text-secondary-900">
                                        Favorable Weather
                                    </div>
                                    <div className="text-xs text-secondary-500 mt-1">
                                        {weatherData.description || 'Pleasant'} conditions in {business.city}
                                    </div>
                                </div>
                            </motion.div>

                            <motion.div
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: 0.4 }}
                                className="flex items-start gap-3"
                            >
                                <div className="w-2 h-2 bg-warning-600 rounded-full mt-2 flex-shrink-0"></div>
                                <div className="flex-1">
                                    <div className="text-sm font-medium text-secondary-900">
                                        Industry News Available
                                    </div>
                                    <div className="text-xs text-secondary-500 mt-1">
                                        Latest {business.industry} trends and updates
                                    </div>
                                </div>
                            </motion.div>
                        </CardContent>
                    </Card>
                </div>

                {/* Get Started Banner */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-gradient-to-br from-primary-600 via-primary-700 to-secondary-800 rounded-2xl shadow-lg p-8 text-white"
                >
                    <div className="flex items-start gap-4">
                        <div className="w-14 h-14 bg-white bg-opacity-20 rounded-xl flex items-center justify-center flex-shrink-0">
                            <Sparkles className="w-7 h-7 text-white" />
                        </div>
                        <div className="flex-1">
                            <h2 className="text-2xl font-bold mb-2">Ready for AI Analysis?</h2>
                            <p className="mb-6 opacity-90 leading-relaxed">
                                Get personalized insights for {business.name} using our AI business analyst
                            </p>
                            <div className="flex flex-wrap gap-3">
                                <motion.button
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                    onClick={() => router.push(`${baseUrl}/chat`)}
                                    className="flex items-center gap-2 px-6 py-3 bg-white text-primary-600 rounded-xl font-medium hover:bg-secondary-50 transition-colors shadow-sm"
                                >
                                    <MessageSquare className="w-5 h-5" />
                                    Chat with AI
                                </motion.button>
                                <motion.button
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                    onClick={() => router.push(`${baseUrl}/agents`)}
                                    className="flex items-center gap-2 px-6 py-3 bg-white bg-opacity-20 hover:bg-opacity-30 rounded-xl font-medium transition-colors"
                                >
                                    <Bot className="w-5 h-5" />
                                    View Agents
                                </motion.button>
                            </div>
                        </div>
                    </div>
                </motion.div>
            </div>
        </MainLayout>
    );
}
