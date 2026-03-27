import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import MainLayout from '../../../components/MainLayout';
import { businessAPI, api } from '../../../lib/api';
import toast from 'react-hot-toast';

export default function BusinessLocationIntelligence() {
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
            const businessData = await businessAPI.get(businessId);
            setBusiness(businessData);

            const response = await api.get(`/location/analyze/${businessId}`);
            setAnalysis(response.data);
        } catch (error) {
            console.error('Error loading location analysis:', error);
            if (error.response?.status === 404) {
                router.push('/select-business');
            } else {
                toast.error('Failed to load location analysis');
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
                        <p className="mt-4 text-gray-600">Analyzing locations...</p>
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
                    <h1 className="text-2xl font-bold text-gray-900 mb-4">Location Intelligence</h1>
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

    return (
        <MainLayout>
            <div className="p-8">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">Location Intelligence</h1>
                    <p className="text-gray-600">Expansion recommendations for {business.name}</p>
                </div>

                <div className="bg-white rounded-lg shadow p-6 mb-6">
                    <h2 className="text-xl font-semibold text-gray-900 mb-4">Current Location</h2>
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <p className="text-sm text-gray-600">City</p>
                            <p className="text-lg font-medium">{analysis.current_location.city}</p>
                        </div>
                        <div>
                            <p className="text-sm text-gray-600">State</p>
                            <p className="text-lg font-medium">{analysis.current_location.state}</p>
                        </div>
                    </div>
                </div>

                <div className="bg-white rounded-lg shadow p-6 mb-6">
                    <div className="flex justify-between items-center mb-4">
                        <h2 className="text-xl font-semibold text-gray-900">Expansion Recommendations</h2>
                        <button
                            onClick={loadData}
                            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                        >
                            Refresh Analysis
                        </button>
                    </div>

                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">City</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">State</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Score</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Recommendation</th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {analysis.recommendations.map((rec, index) => (
                                    <tr key={index} className="hover:bg-gray-50">
                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{rec.city}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{rec.state}</td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className={`px-2 py-1 text-xs font-semibold rounded-full ${rec.overall_score > 75 ? 'bg-green-100 text-green-800' :
                                                    rec.overall_score > 60 ? 'bg-blue-100 text-blue-800' :
                                                        rec.overall_score > 45 ? 'bg-yellow-100 text-yellow-800' :
                                                            'bg-red-100 text-red-800'
                                                }`}>
                                                {rec.overall_score}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{rec.recommendation}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                {analysis.structured_analysis && (
                    <div className="bg-white rounded-lg shadow p-6 mb-6">
                        <h2 className="text-2xl font-bold text-gray-900 mb-6">{analysis.structured_analysis.title}</h2>
                        <div className="mb-6">
                            <h3 className="text-lg font-semibold text-gray-900 mb-2">Summary</h3>
                            <p className="text-gray-700">{analysis.structured_analysis.summary}</p>
                        </div>
                        {analysis.structured_analysis.key_insights && (
                            <div className="mb-6">
                                <h3 className="text-lg font-semibold text-gray-900 mb-2">Key Insights</h3>
                                <ul className="list-disc list-inside space-y-1 text-gray-700">
                                    {analysis.structured_analysis.key_insights.map((insight, idx) => (
                                        <li key={idx}>{insight}</li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {analysis.recommendations.slice(0, 4).map((rec, index) => (
                        <div key={index} className="bg-white rounded-lg shadow p-6">
                            <h3 className="text-lg font-semibold text-gray-900 mb-4">{rec.city}, {rec.state}</h3>
                            <div className="mb-4">
                                <h4 className="text-sm font-medium text-green-700 mb-2">Pros</h4>
                                <ul className="list-disc list-inside space-y-1">
                                    {rec.pros.map((pro, i) => (
                                        <li key={i} className="text-sm text-gray-600">{pro}</li>
                                    ))}
                                </ul>
                            </div>
                            <div>
                                <h4 className="text-sm font-medium text-red-700 mb-2">Cons</h4>
                                <ul className="list-disc list-inside space-y-1">
                                    {rec.cons.map((con, i) => (
                                        <li key={i} className="text-sm text-gray-600">{con}</li>
                                    ))}
                                </ul>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </MainLayout>
    );
}
