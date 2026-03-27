import { useBusiness } from '../contexts/BusinessContext';
import MainLayout from '../components/MainLayout';
import { Database, CheckCircle } from 'lucide-react';

export default function DataSources() {
    const { currentBusiness } = useBusiness();

    const sources = [
        { name: 'Data.gov.in', status: 'connected', type: 'Government Data' },
        { name: 'OpenWeather API', status: 'connected', type: 'Weather Data' },
        { name: 'News API', status: 'connected', type: 'News & Media' },
        { name: 'OpenStreetMap', status: 'connected', type: 'Maps & Location' },
        { name: 'MongoDB', status: 'connected', type: 'Database' },
        { name: 'Redis', status: 'connected', type: 'Cache' },
    ];

    return (
        <MainLayout>
            <div>
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900">Data Sources</h1>
                    <p className="text-gray-600 mt-2">Connected data sources and APIs</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {sources.map((source) => (
                        <div key={source.name} className="bg-white rounded-lg shadow p-6">
                            <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center space-x-3">
                                    <Database className="w-8 h-8 text-blue-500" />
                                    <div>
                                        <h3 className="font-semibold text-lg">{source.name}</h3>
                                        <p className="text-sm text-gray-600">{source.type}</p>
                                    </div>
                                </div>
                                <CheckCircle className="w-6 h-6 text-green-500" />
                            </div>
                            <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm">
                                {source.status}
                            </span>
                        </div>
                    ))}
                </div>
            </div>
        </MainLayout>
    );
}
