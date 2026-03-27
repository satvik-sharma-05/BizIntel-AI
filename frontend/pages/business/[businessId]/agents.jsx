import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import MainLayout from '../../../components/MainLayout';
import { businessAPI, api } from '../../../lib/api';
import toast from 'react-hot-toast';

export default function BusinessAgents() {
    const router = useRouter();
    const { businessId } = router.query;
    const [business, setBusiness] = useState(null);
    const [loading, setLoading] = useState(true);
    const [agentStatuses, setAgentStatuses] = useState(null);
    const [selectedAgent, setSelectedAgent] = useState(null);

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

            const response = await api.get('/agents/status');
            setAgentStatuses(response.data.agents);
        } catch (error) {
            console.error('Error loading agents:', error);
            if (error.response?.status === 404) {
                router.push('/select-business');
            } else {
                toast.error('Failed to load agent statuses');
            }
        } finally {
            setLoading(false);
        }
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'completed':
                return 'bg-green-100 text-green-800';
            case 'running':
                return 'bg-blue-100 text-blue-800';
            case 'failed':
                return 'bg-red-100 text-red-800';
            default:
                return 'bg-gray-100 text-gray-800';
        }
    };

    if (loading) {
        return (
            <MainLayout>
                <div className="flex items-center justify-center h-screen">
                    <div className="text-center">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                        <p className="mt-4 text-gray-600">Loading agents...</p>
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

    if (!agentStatuses) {
        return (
            <MainLayout>
                <div className="p-8">
                    <h1 className="text-2xl font-bold text-gray-900 mb-4">AI Agents</h1>
                    <p className="text-gray-600">No agent data available</p>
                </div>
            </MainLayout>
        );
    }

    const agents = Object.entries(agentStatuses);

    return (
        <MainLayout>
            <div className="p-8">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">AI Agents</h1>
                    <p className="text-gray-600">Multi-agent system for {business.name}</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                    {agents.map(([agentId, agent]) => (
                        <div
                            key={agentId}
                            className="bg-white rounded-lg shadow p-6 cursor-pointer hover:shadow-lg transition-shadow"
                            onClick={() => setSelectedAgent(agent)}
                        >
                            <div className="flex justify-between items-start mb-4">
                                <h3 className="text-lg font-semibold text-gray-900">{agent.name}</h3>
                                <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(agent.status)}`}>
                                    {agent.status}
                                </span>
                            </div>

                            <p className="text-sm text-gray-600 mb-4">{agent.description}</p>

                            <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Executions</span>
                                    <span className="font-medium">{agent.execution_count}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Errors</span>
                                    <span className={`font-medium ${agent.error_count > 0 ? 'text-red-600' : 'text-green-600'}`}>
                                        {agent.error_count}
                                    </span>
                                </div>
                                {agent.last_execution && (
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">Last Run</span>
                                        <span className="font-medium text-xs">
                                            {new Date(agent.last_execution).toLocaleString()}
                                        </span>
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
                </div>

                <div className="flex justify-center mb-8">
                    <button
                        onClick={loadData}
                        className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                        Refresh Agent Status
                    </button>
                </div>

                {selectedAgent && (
                    <div className="bg-white rounded-lg shadow p-6">
                        <div className="flex justify-between items-start mb-6">
                            <div>
                                <h2 className="text-2xl font-bold text-gray-900 mb-2">{selectedAgent.name}</h2>
                                <p className="text-gray-600">{selectedAgent.description}</p>
                            </div>
                            <button
                                onClick={() => setSelectedAgent(null)}
                                className="text-gray-400 hover:text-gray-600"
                            >
                                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                        </div>

                        {selectedAgent.recent_logs && selectedAgent.recent_logs.length > 0 && (
                            <div className="mb-6">
                                <h3 className="text-lg font-semibold text-gray-900 mb-3">Recent Logs</h3>
                                <div className="bg-gray-50 rounded-lg p-4 max-h-64 overflow-y-auto">
                                    {selectedAgent.recent_logs.map((log, index) => (
                                        <div key={index} className="mb-2 text-sm">
                                            <span className="text-gray-500">{new Date(log.timestamp).toLocaleTimeString()}</span>
                                            <span className={`ml-2 font-medium ${log.level === 'error' ? 'text-red-600' :
                                                    log.level === 'warning' ? 'text-yellow-600' :
                                                        'text-gray-700'
                                                }`}>
                                                [{log.level.toUpperCase()}]
                                            </span>
                                            <span className="ml-2 text-gray-700">{log.message}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </MainLayout>
    );
}
