import { useState, useEffect } from 'react';
import MainLayout from '../components/MainLayout';
import { systemAPI } from '../lib/api';
import { CheckCircle, XCircle, AlertCircle, RefreshCw, Database, Cloud, FileText, Map, Route } from 'lucide-react';

export default function SystemAPIs() {
    const [status, setStatus] = useState(null);
    const [loading, setLoading] = useState(true);
    const [lastChecked, setLastChecked] = useState(null);

    useEffect(() => {
        checkAPIs();
    }, []);

    const checkAPIs = async () => {
        setLoading(true);
        try {
            const result = await systemAPI.checkAPIs();
            setStatus(result);
            setLastChecked(new Date());
        } catch (error) {
            console.error('Error checking APIs:', error);
        } finally {
            setLoading(false);
        }
    };

    const getStatusIcon = (status) => {
        if (status === 'OK') {
            return <CheckCircle className="w-6 h-6 text-green-500" />;
        } else if (status && status.startsWith('Error')) {
            return <XCircle className="w-6 h-6 text-red-500" />;
        } else {
            return <AlertCircle className="w-6 h-6 text-yellow-500" />;
        }
    };

    const getStatusColor = (status) => {
        if (status === 'OK') return 'bg-green-50 border-green-200';
        if (status && status.startsWith('Error')) return 'bg-red-50 border-red-200';
        return 'bg-yellow-50 border-yellow-200';
    };

    const services = [
        { key: 'mongodb', name: 'MongoDB', description: 'Primary database', icon: Database },
        { key: 'neo4j', name: 'Neo4j', description: 'Graph database', icon: Database },
        { key: 'faiss', name: 'FAISS', description: 'Vector database', icon: FileText },
        { key: 'openrouter', name: 'OpenRouter', description: 'AI/LLM service', icon: Cloud },
        { key: 'data_gov', name: 'Data.gov.in', description: 'Government data', icon: Database },
        { key: 'weather_api', name: 'Weather API', description: 'Weather data', icon: Cloud },
        { key: 'news_api', name: 'News API', description: 'News data', icon: FileText },
        { key: 'overpass', name: 'Overpass API', description: 'OpenStreetMap data', icon: Map },
        { key: 'osrm', name: 'OSRM', description: 'Routing service', icon: Route },
    ];

    return (
        <MainLayout>
            <div>
                <div className="mb-8 flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900">System Status</h1>
                        <p className="text-gray-600 mt-2">Monitor all APIs and database connections</p>
                    </div>
                    <button
                        onClick={checkAPIs}
                        disabled={loading}
                        className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition"
                    >
                        <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                        Refresh
                    </button>
                </div>

                {/* Overall Status */}
                {status && (
                    <div className={`mb-8 p-6 rounded-lg border-2 ${status.status === 'healthy'
                            ? 'bg-green-50 border-green-200'
                            : 'bg-yellow-50 border-yellow-200'
                        }`}>
                        <div className="flex items-center gap-3">
                            {status.status === 'healthy' ? (
                                <CheckCircle className="w-8 h-8 text-green-600" />
                            ) : (
                                <AlertCircle className="w-8 h-8 text-yellow-600" />
                            )}
                            <div>
                                <h2 className="text-2xl font-bold text-gray-900">
                                    System {status.status === 'healthy' ? 'Healthy' : 'Degraded'}
                                </h2>
                                {lastChecked && (
                                    <p className="text-sm text-gray-600 mt-1">
                                        Last checked: {lastChecked.toLocaleTimeString()}
                                    </p>
                                )}
                            </div>
                        </div>
                    </div>
                )}

                {/* Service Status Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {services.map((service) => {
                        const serviceStatus = status?.services?.[service.key];
                        const Icon = service.icon;

                        return (
                            <div
                                key={service.key}
                                className={`p-6 rounded-lg border-2 transition ${loading ? 'animate-pulse' : ''
                                    } ${getStatusColor(serviceStatus)}`}
                            >
                                <div className="flex items-start justify-between mb-4">
                                    <div className="flex items-center gap-3">
                                        <div className="p-2 bg-white rounded-lg">
                                            <Icon className="w-6 h-6 text-gray-700" />
                                        </div>
                                        <div>
                                            <h3 className="font-bold text-gray-900">{service.name}</h3>
                                            <p className="text-sm text-gray-600">{service.description}</p>
                                        </div>
                                    </div>
                                    {serviceStatus && getStatusIcon(serviceStatus)}
                                </div>

                                <div className="mt-4 pt-4 border-t border-gray-200">
                                    <div className="text-sm">
                                        <span className="font-medium text-gray-700">Status: </span>
                                        <span className={`font-mono ${serviceStatus === 'OK'
                                                ? 'text-green-700'
                                                : 'text-red-700'
                                            }`}>
                                            {serviceStatus || 'Checking...'}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>

                {/* Info Section */}
                <div className="mt-8 bg-blue-50 border-2 border-blue-200 rounded-lg p-6">
                    <h3 className="font-bold text-gray-900 mb-2">About System Status</h3>
                    <p className="text-sm text-gray-700 mb-4">
                        This page monitors the health of all external APIs and database connections used by BizIntel AI.
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                        <div>
                            <h4 className="font-semibold text-gray-900 mb-2">Databases</h4>
                            <ul className="space-y-1 text-gray-700">
                                <li>• MongoDB: Primary data storage</li>
                                <li>• Neo4j: Graph relationships</li>
                                <li>• FAISS: Vector search (RAG)</li>
                            </ul>
                        </div>
                        <div>
                            <h4 className="font-semibold text-gray-900 mb-2">External APIs</h4>
                            <ul className="space-y-1 text-gray-700">
                                <li>• OpenRouter: AI/LLM responses</li>
                                <li>• Data.gov.in: Economic data</li>
                                <li>• Weather API: Weather data</li>
                                <li>• News API: Business news</li>
                                <li>• Overpass: OpenStreetMap data</li>
                                <li>• OSRM: Routing calculations</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </MainLayout>
    );
}
