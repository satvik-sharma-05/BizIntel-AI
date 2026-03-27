import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import MainLayout from '../../../components/MainLayout';
import { businessAPI, api } from '../../../lib/api';
import toast from 'react-hot-toast';

export default function BusinessMarketAnalysis() {
    const router = useRouter();
    const { businessId } = router.query;
    const [business, setBusiness] = useState(null);
    const [loading, setLoading] = useState(true);
    const [analysis, setAnalysis] = useState(null);

    useEffect(() => {
        if (businessId) {
            loadData();
        }
    }, [businessId]);

    const loadData = async () => {
        try {
            setLoading(true);
            // Load business details
            const businessData = await businessAPI.get(businessId);
            setBusiness(businessData);

            // Load market analysis with timeout handling
            try {
                const response = await api.get(`/market/analyze/${businessId}`, {
                    timeout: 30000 // 30 seconds
                });
                setAnalysis(response.data);
            } catch (analysisError) {
                console.error('Market analysis error:', analysisError);
                if (analysisError.code === 'ECONNABORTED') {
                    toast.error('Market analysis is taking too long. Please try again later.');
                } else {
                    toast.error('Failed to load market analysis. Using cached data if available.');
                }
                // Set empty analysis to show UI
                setAnalysis({ market_analysis: null });
            }
        } catch (error) {
            console.error('Error loading data:', error);
            if (error.response?.status === 404) {
                router.push('/select-business');
            } else {
                toast.error('Failed to load business data');
            }
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <MainLayout>
                <div className="flex items-center justify-center h-screen">
                    <div className="text-center">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                        <p className="mt-4 text-gray-600">Analyzing market...</p>
                    </div>
                </div>
            </MainLayout>
        );
    }

    if (!business) {
        return (
            <MainLayout>
                <div className="flex items-center justify-center h-full">
                    <div className="text-center">
                        <div className="text-xl text-gray-600 mb-4">Business not found</div>
                        <button
                            onClick={() => router.push('/select-business')}
                            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                        >
                            Select Business
                        </button>
                    </div>
                </div>
            </MainLayout>
        );
    }

    if (!analysis) {
        return (
            <MainLayout>
                <div className="p-8">
                    <h1 className="text-2xl font-bold text-gray-900 mb-4">Market Analysis</h1>
                    <p className="text-gray-600">No analysis data available</p>
                    <button
                        onClick={loadData}
                        className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                        Generate Analysis
                    </button>
                </div>
            </MainLayout>
        );
    }

    const marketData = analysis.market_analysis;

    return (
        <MainLayout>
            <div className="p-8">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">Market Analysis</h1>
                    <p className="text-gray-600">
                        Comprehensive market intelligence for {business.name}
                    </p>
                    <p className="text-sm text-gray-500">{business.city}, {business.state}</p>
                </div>

                {/* Key Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
                    <div className="bg-white rounded-lg shadow p-6">
                        <h3 className="text-sm font-medium text-gray-600 mb-2">Demand Score</h3>
                        <p className="text-3xl font-bold text-blue-600">{marketData.demand_score}/100</p>
                    </div>

                    <div className="bg-white rounded-lg shadow p-6">
                        <h3 className="text-sm font-medium text-gray-600 mb-2">Market Opportunity</h3>
                        <p className={`text-2xl font-bold ${marketData.opportunity === 'High' ? 'text-green-600' :
                            marketData.opportunity === 'Medium' ? 'text-yellow-600' :
                                'text-red-600'
                            }`}>
                            {marketData.opportunity}
                        </p>
                    </div>

                    <div className="bg-white rounded-lg shadow p-6">
                        <h3 className="text-sm font-medium text-gray-600 mb-2">Competition</h3>
                        <p className={`text-2xl font-bold ${marketData.competition === 'Low' ? 'text-green-600' :
                            marketData.competition === 'Medium' ? 'text-yellow-600' :
                                'text-red-600'
                            }`}>
                            {marketData.competition}
                        </p>
                    </div>

                    <div className="bg-white rounded-lg shadow p-6">
                        <h3 className="text-sm font-medium text-gray-600 mb-2">Growth Trend</h3>
                        <p className={`text-2xl font-bold ${marketData.growth_trend === 'Growing' ? 'text-green-600' :
                            marketData.growth_trend === 'Stable' ? 'text-blue-600' :
                                'text-red-600'
                            }`}>
                            {marketData.growth_trend}
                        </p>
                    </div>
                </div>

                {/* Market Details */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                    <div className="bg-white rounded-lg shadow p-6">
                        <h2 className="text-xl font-semibold text-gray-900 mb-4">Market Overview</h2>
                        <div className="space-y-3">
                            <div className="flex justify-between">
                                <span className="text-gray-600">Market Size</span>
                                <span className="font-medium">{marketData.market_size}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">Entry Barrier</span>
                                <span className="font-medium">{marketData.entry_barrier}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">GDP Growth</span>
                                <span className="font-medium">{marketData.gdp_growth}%</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">Inflation Rate</span>
                                <span className="font-medium">{marketData.inflation}%</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">MSME Count</span>
                                <span className="font-medium">{marketData.msme_count.toLocaleString()}</span>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white rounded-lg shadow p-6">
                        <h2 className="text-xl font-semibold text-gray-900 mb-4">Market Sentiment</h2>
                        <div className="space-y-3">
                            <div className="flex justify-between">
                                <span className="text-gray-600">News Sentiment</span>
                                <span className={`font-medium ${marketData.news_sentiment === 'Positive' ? 'text-green-600' :
                                    marketData.news_sentiment === 'Neutral' ? 'text-gray-600' :
                                        'text-red-600'
                                    }`}>
                                    {marketData.news_sentiment}
                                </span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">News Articles</span>
                                <span className="font-medium">{marketData.news_count}</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* AI Insights - Structured Output */}
                {analysis.structured_analysis && (
                    <div className="bg-white rounded-lg shadow p-6 mb-6">
                        <div className="flex justify-between items-center mb-6">
                            <h2 className="text-2xl font-bold text-gray-900">{analysis.structured_analysis.title}</h2>
                            <button
                                onClick={loadData}
                                className="px-4 py-2 bg-white text-black border border-gray-300 rounded-lg hover:bg-gray-100"
                            >
                                Refresh Analysis
                            </button>
                        </div>

                        {/* Summary */}
                        <div className="mb-6">
                            <h3 className="text-lg font-semibold text-gray-900 mb-2">Summary</h3>
                            <p className="text-gray-700">{analysis.structured_analysis.summary}</p>
                        </div>

                        {/* Key Insights */}
                        {analysis.structured_analysis.key_insights && analysis.structured_analysis.key_insights.length > 0 && (
                            <div className="mb-6">
                                <h3 className="text-lg font-semibold text-gray-900 mb-2">Key Insights</h3>
                                <ul className="list-disc list-inside space-y-1 text-gray-700">
                                    {analysis.structured_analysis.key_insights.map((insight, idx) => (
                                        <li key={idx}>{insight}</li>
                                    ))}
                                </ul>
                            </div>
                        )}

                        {/* Risks */}
                        {analysis.structured_analysis.risks && analysis.structured_analysis.risks.length > 0 && (
                            <div className="mb-6">
                                <h3 className="text-lg font-semibold text-gray-900 mb-2">Risks</h3>
                                <ul className="list-disc list-inside space-y-1 text-gray-700">
                                    {analysis.structured_analysis.risks.map((risk, idx) => (
                                        <li key={idx}>{risk}</li>
                                    ))}
                                </ul>
                            </div>
                        )}

                        {/* Opportunities */}
                        {analysis.structured_analysis.opportunities && analysis.structured_analysis.opportunities.length > 0 && (
                            <div className="mb-6">
                                <h3 className="text-lg font-semibold text-gray-900 mb-2">Opportunities</h3>
                                <ul className="list-disc list-inside space-y-1 text-gray-700">
                                    {analysis.structured_analysis.opportunities.map((opp, idx) => (
                                        <li key={idx}>{opp}</li>
                                    ))}
                                </ul>
                            </div>
                        )}

                        {/* Recommendations */}
                        {analysis.structured_analysis.recommendations && analysis.structured_analysis.recommendations.length > 0 && (
                            <div className="mb-6">
                                <h3 className="text-lg font-semibold text-gray-900 mb-2">Recommendations</h3>
                                <ul className="list-disc list-inside space-y-1 text-gray-700">
                                    {analysis.structured_analysis.recommendations.map((rec, idx) => (
                                        <li key={idx}>{rec}</li>
                                    ))}
                                </ul>
                            </div>
                        )}

                        {/* Action Plan */}
                        {analysis.structured_analysis.action_plan && analysis.structured_analysis.action_plan.length > 0 && (
                            <div className="mb-6">
                                <h3 className="text-lg font-semibold text-gray-900 mb-2">Action Plan</h3>
                                <ol className="list-decimal list-inside space-y-1 text-gray-700">
                                    {analysis.structured_analysis.action_plan.map((action, idx) => (
                                        <li key={idx}>{action}</li>
                                    ))}
                                </ol>
                            </div>
                        )}

                        {/* Conclusion */}
                        <div className="mb-0">
                            <h3 className="text-lg font-semibold text-gray-900 mb-2">Conclusion</h3>
                            <p className="text-gray-700">{analysis.structured_analysis.conclusion}</p>
                        </div>
                    </div>
                )}

                {/* Economic Indicators */}
                {analysis.data_sources && (
                    <div className="bg-gray-50 rounded-lg p-6">
                        <h2 className="text-xl font-semibold text-gray-900 mb-4">Economic Indicators</h2>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            <div className="bg-white rounded-lg p-4">
                                <h3 className="text-sm font-medium text-gray-600 mb-2">GDP Growth</h3>
                                <p className="text-2xl font-bold text-gray-900">
                                    {analysis.data_sources?.gdp?.growth || 'N/A'}%
                                </p>
                            </div>
                            <div className="bg-white rounded-lg p-4">
                                <h3 className="text-sm font-medium text-gray-600 mb-2">MSME Businesses</h3>
                                <p className="text-2xl font-bold text-gray-900">
                                    {analysis.data_sources?.msme?.state?.toLocaleString() || 'N/A'}
                                </p>
                            </div>
                            <div className="bg-white rounded-lg p-4">
                                <h3 className="text-sm font-medium text-gray-600 mb-2">Inflation Rate</h3>
                                <p className="text-2xl font-bold text-gray-900">
                                    {analysis.data_sources?.economic_indicators?.inflation || 'N/A'}%
                                </p>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </MainLayout>
    );
}
