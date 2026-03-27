import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import MainLayout from '../components/MainLayout';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../lib/api';
import toast from 'react-hot-toast';

export default function Agents() {
    const router = useRouter();
    const { user } = useAuth();
    const [loading, setLoading] = useState(true);
    const [agents, setAgents] = useState([]);
    const [selectedAgent, setSelectedAgent] = useState(null);
    const [agentStats, setAgentStats] = useState({});
    const [agentLogs, setAgentLogs] = useState([]);

    useEffect(() => {
        if (!user) {
            router.push('/login');
            return;
        }
        loadAgents();
    }, [user]);

    const loadAgents = async () => {
        try {
            setLoading(true);
            const response = await api.get('/agents');
            setAgents(response.data.agents);
        } catch (error) {
            console.error('Error loading agents:', error);
            toast.error('Failed to load agents');
        } finally {
            setLoading(false);
        }
    };

    const loadAgentDetails = async (agentId) => {
        try {
            // Load stats
            const statsResponse = await api.get(`/agents/${agentId}/stats`);
            setAgentStats(statsResponse.data);

            // Load logs
            const logsResponse = await api.get(`/agents/${agentId}/logs?limit=20`);
            setAgentLogs(logsResponse.data.logs);
        } catch (error) {
            console.error('Error loading agent details:', error);
            toast.error('Failed to load agent details');
        }
    };

    const handleAgentClick = async (agent) => {
        setSelectedAgent(agent);
        await loadAgentDetails(agent.id);
    };

    if (loading) {
        return (
            <MainLayout>
                <div className="flex items-center justify-center h-screen">
                    <div className="text-center">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                        <p className="mt-4 text-gray-600 dark:text-gray-300">Loading agents...</p>
                    </div>
                </div>
            </MainLayout>
        );
    }

    return (
        <MainLayout>
            <div className="p-8">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">🤖 AI Agents</h1>
                    <p className="text-gray-600 dark:text-gray-300">
                        Multi-agent system powering BizIntel AI intelligence
                    </p>
                </div>

                {/* Agent Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                    {agents.map((agent) => (
                        <div
                            key={agent.id}
                            className="bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer p-6"
                            onClick={() => handleAgentClick(agent)}
                        >
                            <div className="flex items-start justify-between mb-4">
                                <div className="flex items-center">
                                    <span className="text-4xl mr-3">{agent.icon}</span>
                                    <div>
                                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                                            {agent.name}
                                        </h3>
                                        <p className="text-sm text-gray-500 dark:text-gray-400">{agent.role}</p>
                                    </div>
                                </div>
                            </div>

                            <p className="text-sm text-gray-600 dark:text-gray-300 mb-4 line-clamp-3">
                                {agent.description}
                            </p>

                            <div className="space-y-2">
                                <div className="flex items-center text-xs text-gray-500 dark:text-gray-400">
                                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                    </svg>
                                    {agent.capabilities.length} capabilities
                                </div>
                                <div className="flex items-center text-xs text-gray-500 dark:text-gray-400">
                                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
                                    </svg>
                                    {agent.databases.length} databases
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Selected Agent Details */}
                {selectedAgent && (
                    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
                        <div className="flex justify-between items-start mb-6">
                            <div className="flex items-center">
                                <span className="text-5xl mr-4">{selectedAgent.icon}</span>
                                <div>
                                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
                                        {selectedAgent.name}
                                    </h2>
                                    <p className="text-gray-600 dark:text-gray-300">{selectedAgent.role}</p>
                                </div>
                            </div>
                            <button
                                onClick={() => setSelectedAgent(null)}
                                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
                            >
                                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                        </div>

                        <p className="text-gray-700 dark:text-gray-300 mb-6">{selectedAgent.description}</p>

                        {/* Stats */}
                        {agentStats && (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                                <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                                    <div className="text-sm text-blue-600 dark:text-blue-400 mb-1">Total Executions</div>
                                    <div className="text-2xl font-bold text-blue-900 dark:text-blue-100">
                                        {agentStats.total_executions || 0}
                                    </div>
                                </div>
                                <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                                    <div className="text-sm text-green-600 dark:text-green-400 mb-1">Last 24 Hours</div>
                                    <div className="text-2xl font-bold text-green-900 dark:text-green-100">
                                        {agentStats.recent_executions_24h || 0}
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Capabilities */}
                        <div className="mb-6">
                            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">Capabilities</h3>
                            <div className="flex flex-wrap gap-2">
                                {selectedAgent.capabilities.map((capability, index) => (
                                    <span
                                        key={index}
                                        className="px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 text-sm rounded-full"
                                    >
                                        {capability}
                                    </span>
                                ))}
                            </div>
                        </div>

                        {/* Data Sources */}
                        <div className="mb-6">
                            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">Data Sources</h3>
                            <ul className="space-y-2">
                                {selectedAgent.data_sources.map((source, index) => (
                                    <li key={index} className="flex items-center text-gray-700 dark:text-gray-300">
                                        <svg className="w-4 h-4 mr-2 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                                        </svg>
                                        {source}
                                    </li>
                                ))}
                            </ul>
                        </div>

                        {/* Databases */}
                        <div className="mb-6">
                            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">Databases Used</h3>
                            <div className="flex flex-wrap gap-2">
                                {selectedAgent.databases.map((db, index) => (
                                    <span
                                        key={index}
                                        className="px-3 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-200 text-sm rounded-full"
                                    >
                                        {db}
                                    </span>
                                ))}
                            </div>
                        </div>

                        {/* Recent Logs */}
                        {agentLogs && agentLogs.length > 0 && (
                            <div>
                                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">Recent Activity</h3>
                                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 max-h-64 overflow-y-auto">
                                    {agentLogs.map((log, index) => (
                                        <div key={index} className="mb-2 text-sm text-gray-700 dark:text-gray-300">
                                            <span className="text-gray-500 dark:text-gray-400">
                                                {new Date(log.created_at).toLocaleString()}
                                            </span>
                                            <span className="ml-2">{log.message || 'Agent executed'}</span>
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
