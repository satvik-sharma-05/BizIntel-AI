import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { useBusiness } from '../contexts/BusinessContext';
import MainLayout from '../components/MainLayout';
import { Lightbulb, TrendingUp, AlertCircle, CheckCircle, ArrowRight } from 'lucide-react';

export default function Insights() {
    const router = useRouter();
    const { currentBusiness } = useBusiness();

    useEffect(() => {
        if (!currentBusiness) {
            router.push('/select-business');
        }
    }, [currentBusiness, router]);

    if (!currentBusiness) {
        return (
            <MainLayout>
                <div className="flex items-center justify-center h-screen">
                    <div className="text-center">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                        <p className="mt-4 text-gray-600">Loading...</p>
                    </div>
                </div>
            </MainLayout>
        );
    }

    const insights = [
        {
            type: 'opportunity',
            icon: TrendingUp,
            color: 'bg-green-500',
            title: 'Growing Market Demand',
            description: `The ${currentBusiness.industry} sector in ${currentBusiness.city} is experiencing growth based on market analysis.`,
            action: 'View Market Analysis',
            link: '/market'
        },
        {
            type: 'recommendation',
            icon: Lightbulb,
            color: 'bg-blue-500',
            title: 'Optimal Location Identified',
            description: 'Based on real data analysis, we have identified prime expansion locations.',
            action: 'View Locations',
            link: '/location'
        },
        {
            type: 'warning',
            icon: AlertCircle,
            color: 'bg-yellow-500',
            title: 'Market Considerations',
            description: 'Review market conditions and competition levels for strategic planning.',
            action: 'View Forecast',
            link: '/forecast'
        },
        {
            type: 'success',
            icon: CheckCircle,
            color: 'bg-purple-500',
            title: 'ROI Potential',
            description: 'View detailed revenue projections based on real market data.',
            action: 'View Details',
            link: '/forecast'
        },
    ];

    return (
        <MainLayout>
            <div>
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900">AI Insights</h1>
                    <p className="text-gray-600 mt-2">
                        Intelligent recommendations for {currentBusiness.name}
                    </p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {insights.map((insight, idx) => {
                        const Icon = insight.icon;
                        return (
                            <div
                                key={idx}
                                className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition"
                            >
                                <div className="flex items-start gap-4">
                                    <div className={`${insight.color} p-3 rounded-lg flex-shrink-0`}>
                                        <Icon className="w-6 h-6 text-white" />
                                    </div>
                                    <div className="flex-1">
                                        <h3 className="text-xl font-bold text-gray-900 mb-2">
                                            {insight.title}
                                        </h3>
                                        <p className="text-gray-600 mb-4">
                                            {insight.description}
                                        </p>
                                        <button
                                            onClick={() => router.push(insight.link)}
                                            className="flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium"
                                        >
                                            {insight.action}
                                            <ArrowRight className="w-4 h-4" />
                                        </button>
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>
        </MainLayout>
    );
}
