import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import MainLayout from '../../../components/MainLayout';
import { businessAPI } from '../../../lib/api';
import { FileText, Download, Calendar, TrendingUp } from 'lucide-react';

export default function BusinessReports() {
    const router = useRouter();
    const { businessId } = router.query;
    const [business, setBusiness] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (businessId) {
            loadData();
        }
    }, [businessId]);

    const loadData = async () => {
        try {
            const businessData = await businessAPI.get(businessId);
            setBusiness(businessData);
        } catch (error) {
            console.error('Error loading business:', error);
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
                <div className="flex items-center justify-center h-full">
                    <div className="flex flex-col items-center gap-4">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                        <div className="text-xl text-gray-600">Loading...</div>
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

    const reportTypes = [
        {
            title: 'Market Analysis Report',
            description: 'Comprehensive market intelligence and competitive analysis',
            icon: TrendingUp,
            color: 'bg-blue-500',
            available: true
        },
        {
            title: 'Location Intelligence Report',
            description: 'Expansion opportunities and location recommendations',
            icon: FileText,
            color: 'bg-green-500',
            available: true
        },
        {
            title: 'Financial Forecast Report',
            description: 'Revenue projections and financial analysis',
            icon: Calendar,
            color: 'bg-purple-500',
            available: true
        },
        {
            title: 'Executive Summary',
            description: 'Complete business intelligence overview',
            icon: Download,
            color: 'bg-orange-500',
            available: false
        },
    ];

    return (
        <MainLayout>
            <div className="p-8">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">Reports</h1>
                    <p className="text-gray-600">Generate and download reports for {business.name}</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                    {reportTypes.map((report, index) => {
                        const Icon = report.icon;
                        return (
                            <div
                                key={index}
                                className={`bg-white rounded-lg shadow p-6 ${report.available ? 'hover:shadow-lg cursor-pointer' : 'opacity-60'
                                    } transition-shadow`}
                            >
                                <div className="flex items-start gap-4">
                                    <div className={`${report.color} p-3 rounded-lg`}>
                                        <Icon className="w-6 h-6 text-white" />
                                    </div>
                                    <div className="flex-1">
                                        <h3 className="text-lg font-semibold text-gray-900 mb-2">
                                            {report.title}
                                        </h3>
                                        <p className="text-sm text-gray-600 mb-4">
                                            {report.description}
                                        </p>
                                        {report.available ? (
                                            <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm">
                                                Generate Report
                                            </button>
                                        ) : (
                                            <span className="text-sm text-gray-500">Coming Soon</span>
                                        )}
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>

                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Report Generation</h3>
                    <p className="text-gray-700 text-sm">
                        Reports will compile data from market analysis, location intelligence, and forecasting modules.
                        PDF export functionality coming soon.
                    </p>
                </div>
            </div>
        </MainLayout>
    );
}
