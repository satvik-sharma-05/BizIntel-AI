import { useState, useEffect } from 'react';
import ProtectedRoute from '../components/ProtectedRoute';
import MainLayout from '../components/MainLayout';
import { CheckCircle, XCircle, AlertCircle, RefreshCw } from 'lucide-react';
import { api } from '../lib/api';
import toast from 'react-hot-toast';

export default function SystemStatus() {
    return (
        <ProtectedRoute>
            <MainLayout>
                <SystemStatusContent />
            </MainLayout>
        </ProtectedRoute>
    );
}

function SystemStatusContent() {
    const [status, setStatus] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        checkStatus();
    }, []);

    const checkStatus = async () => {
        setLoading(true);
        try {
            const response = await api.get('/system/check-apis');
            setStatus(response.data);
        } catch (error) {
            console.error('Error checking system status:', error);
            toast.error('Failed to check system status');
        } finally {
            setLoading(false);
        }
    };

    const getStatusIcon = (serviceStatus) => {
        if (serviceStatus === 'OK') {
            return <CheckCircle className="w-6 h-6 text-green-500" />;
        } else if (serviceStatus?.startsWith('Error')) {
            return <XCircle className="w-6 h-6 text-red-500" />;
        } else {
            return <AlertCircle className="w-6 h-6 text-yellow-500" />;
        }
    };

    const getStatusColor = (serviceStatus) => {
        if (serviceStatus === 'OK') {
            return 'bg-green-50 border-green-200';
        } else if (serviceStatus?.startsWith('Error')) {
            return 'bg-red-50 border-red-200';
        } else {
            return 'bg-yellow-50 border-yellow-200';
        }
    };

    const services = [
        { key: 'data_gov', name: 'Data.gov.in API', description: 'Indian government data portal' },
        { key: 'weather_api', name: 'Weather API', description: 'OpenWeather API for weather data' },
        { key: 'news_api', name: 'News API', description: 'News articles and sentiment' },
        { key: 'openrouter', name: 'OpenRouter', description: 'LLM API for AI features' },
        { key: 'mongodb', name: 'MongoDB', description: 'Document database' },
        { key: 'postgres', name: 'PostgreSQL', description: 'Relational database' },
        { key: 'redis', name: 'Redis', description: 'Cache and session store' },
        { key: 'neo4j', name: 'Neo4j', description: 'Graph database' },
    ];

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-center">
                    <RefreshCw className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-4" />
                    <p className="text-gray-600">Checking system status...</p>
                </div>
            </div>
        );
    }

    const allOk = status?.status === 'healthy';

    return (
        <div className="max-w-6xl mx-auto">
            {/* Header */}
            <div className="mb-8">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900 mb-2">System Status</h1>
                        <p className="text-gray-600">Monitor the health of all services and APIs</p>
                    </div>
                    <button
                        onClick={checkStatus}
                        className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                    >
                        <RefreshCw className="w-4 h-4" />
                        Refresh
                    </button>
                </div>
            </div>

            {/* Overall Status */}
            <div className={`p-6 rounded-xl border-2 mb-8 ${allOk ? 'bg-green-50 border-green-200' : 'bg-yellow-50 border-yellow-200'}`}>
                <div className="flex items-center gap-4">
                    {allOk ? (
                        <CheckCircle className="w-12 h-12 text-green-500" />
                    ) : (
                        <AlertCircle className="w-12 h-12 text-yellow-500" />
                    )}
                    <div>
                        <h2 className="text-2xl font-bold text-gray-900">
                            {allOk ? 'All Systems Operational' : 'Some Services Degraded'}
                        </h2>
                        <p className="text-gray-600">
                            {allOk
                                ? 'All services are running normally'
                                : 'Some services are experiencing issues'}
                        </p>
                    </div>
                </div>
            </div>

            {/* Service Cards */}
            <div className="grid md:grid-cols-2 gap-6">
                {services.map((service) => {
                    const serviceStatus = status?.services?.[service.key] || 'Unknown';
                    const isOk = serviceStatus === 'OK';

                    return (
                        <div
                            key={service.key}
                            className={`p-6 rounded-xl border-2 ${getStatusColor(serviceStatus)}`}
                        >
                            <div className="flex items-start justify-between mb-4">
                                <div className="flex items-center gap-3">
                                    {getStatusIcon(serviceStatus)}
                                    <div>
                                        <h3 className="text-lg font-semibold text-gray-900">
                                            {service.name}
                                        </h3>
                                        <p className="text-sm text-gray-600">{service.description}</p>
                                    </div>
                                </div>
                            </div>

                            <div className="mt-4">
                                <div className="flex items-center justify-between">
                                    <span className="text-sm font-medium text-gray-700">Status:</span>
                                    <span className={`text-sm font-semibold ${isOk ? 'text-green-700' : 'text-red-700'}`}>
                                        {serviceStatus}
                                    </span>
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Timestamp */}
            {status?.timestamp && (
                <div className="mt-8 text-center text-sm text-gray-500">
                    Last checked: {new Date(status.timestamp).toLocaleString()}
                </div>
            )}
        </div>
    );
}
