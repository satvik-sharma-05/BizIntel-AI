import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import MainLayout from '../../../components/MainLayout';
import { businessAPI, api } from '../../../lib/api';
import toast from 'react-hot-toast';

export default function BusinessForecast() {
    const router = useRouter();
    const { businessId } = router.query;
    const [business, setBusiness] = useState(null);
    const [loading, setLoading] = useState(true);
    const [forecast, setForecast] = useState(null);

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

            const response = await api.get(`/forecast/${businessId}`);
            setForecast(response.data);
        } catch (error) {
            console.error('Error loading forecast:', error);
            if (error.response?.status === 404) {
                router.push('/select-business');
            } else {
                toast.error('Failed to load forecast');
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
                        <p className="mt-4 text-gray-600">Generating forecast...</p>
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

    if (!forecast) {
        return (
            <MainLayout>
                <div className="p-8">
                    <h1 className="text-2xl font-bold text-gray-900 mb-4">Revenue Forecasting</h1>
                    <p className="text-gray-600">No forecast data available</p>
                    <button
                        onClick={loadData}
                        className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                        Generate Forecast
                    </button>
                </div>
            </MainLayout>
        );
    }

    return (
        <MainLayout>
            <div className="p-8">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900">Revenue Forecasting</h1>
                    <p className="text-gray-600 mt-2">AI-powered predictions for {business.name}</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
                    <div className="bg-white rounded-lg shadow p-6">
                        <p className="text-sm text-gray-600">Annual Revenue</p>
                        <p className="text-2xl font-bold text-blue-600">
                            ₹{(forecast.annual_revenue / 100000).toFixed(2)}L
                        </p>
                    </div>
                    <div className="bg-white rounded-lg shadow p-6">
                        <p className="text-sm text-gray-600">Annual Profit</p>
                        <p className="text-2xl font-bold text-green-600">
                            ₹{(forecast.annual_profit / 100000).toFixed(2)}L
                        </p>
                    </div>
                    <div className="bg-white rounded-lg shadow p-6">
                        <p className="text-sm text-gray-600">ROI</p>
                        <p className="text-2xl font-bold text-purple-600">{forecast.roi}%</p>
                    </div>
                    <div className="bg-white rounded-lg shadow p-6">
                        <p className="text-sm text-gray-600">Breakeven</p>
                        <p className="text-2xl font-bold text-orange-600">{forecast.breakeven_months} months</p>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                    <div className="bg-white rounded-lg shadow p-6">
                        <h2 className="text-xl font-semibold text-gray-900 mb-4">Monthly Performance</h2>
                        <div className="space-y-3">
                            <div className="flex justify-between">
                                <span className="text-gray-600">Monthly Revenue</span>
                                <span className="font-medium">₹{forecast.monthly_revenue.toLocaleString()}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">Monthly Profit</span>
                                <span className="font-medium">₹{forecast.monthly_profit.toLocaleString()}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">Profit Margin</span>
                                <span className="font-medium">{forecast.profit_margin}%</span>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white rounded-lg shadow p-6">
                        <h2 className="text-xl font-semibold text-gray-900 mb-4">Market Conditions</h2>
                        <div className="space-y-3">
                            <div className="flex justify-between">
                                <span className="text-gray-600">GDP Growth</span>
                                <span className="font-medium">{forecast.market_conditions.gdp_growth}%</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">Competition</span>
                                <span className="font-medium">{forecast.market_conditions.competition_level}</span>
                            </div>
                        </div>
                    </div>
                </div>

                {forecast.structured_forecast && (
                    <div className="bg-white rounded-lg shadow p-6 mb-6">
                        <div className="flex justify-between items-center mb-6">
                            <h2 className="text-2xl font-bold text-gray-900">{forecast.structured_forecast.title}</h2>
                            <button
                                onClick={loadData}
                                className="px-4 py-2 bg-white text-black border border-gray-300 rounded-lg hover:bg-gray-100"
                            >
                                Refresh Forecast
                            </button>
                        </div>
                        <div className="mb-6">
                            <h3 className="text-lg font-semibold text-gray-900 mb-2">Summary</h3>
                            <p className="text-gray-700">{forecast.structured_forecast.summary}</p>
                        </div>
                        {forecast.structured_forecast.key_insights && (
                            <div className="mb-6">
                                <h3 className="text-lg font-semibold text-gray-900 mb-2">Key Insights</h3>
                                <ul className="list-disc list-inside space-y-1 text-gray-700">
                                    {forecast.structured_forecast.key_insights.map((insight, idx) => (
                                        <li key={idx}>{insight}</li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </MainLayout>
    );
}
