import { useState } from 'react';
import { FileText, Brain, Database, Zap, BookOpen } from 'lucide-react';

const CHAT_MODES = {
    KNOWLEDGE_BASE_ONLY: {
        id: 'knowledge_base_only',
        name: 'Knowledge Base Only',
        icon: FileText,
        description: 'Answers strictly from your uploaded documents',
        color: 'blue',
        badge: '📄'
    },
    AI_KNOWLEDGE_BASE: {
        id: 'ai_knowledge_base',
        name: 'AI + Knowledge Base',
        icon: BookOpen,
        description: 'Combines documents with AI analysis',
        color: 'purple',
        badge: '🔄'
    },
    AI_ONLY: {
        id: 'ai_only',
        name: 'AI Only',
        icon: Brain,
        description: 'General business expertise and best practices',
        color: 'green',
        badge: '🧠'
    },
    BUSINESS_DATA_ONLY: {
        id: 'business_data_only',
        name: 'Business Data Only',
        icon: Database,
        description: 'Real-time market, location, and competition data',
        color: 'orange',
        badge: '📊'
    },
    FULL_INTELLIGENCE: {
        id: 'full_intelligence',
        name: 'Full Intelligence',
        icon: Zap,
        description: 'Everything: Documents + Agents + AI + Data',
        color: 'indigo',
        badge: '⚡'
    }
};

export default function ChatModeSelector({ currentMode, onModeChange }) {
    const [isOpen, setIsOpen] = useState(false);

    const currentModeConfig = Object.values(CHAT_MODES).find(m => m.id === currentMode) || CHAT_MODES.FULL_INTELLIGENCE;
    const Icon = currentModeConfig.icon;

    return (
        <div className="relative">
            {/* Current Mode Button */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition shadow-sm"
            >
                <span className="text-xl">{currentModeConfig.badge}</span>
                <div className="text-left">
                    <div className="text-sm font-medium text-gray-900">
                        {currentModeConfig.name}
                    </div>
                    <div className="text-xs text-gray-500">
                        Click to change mode
                    </div>
                </div>
                <svg
                    className={`w-4 h-4 text-gray-500 transition-transform ${isOpen ? 'rotate-180' : ''}`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
            </button>

            {/* Dropdown Menu */}
            {isOpen && (
                <>
                    {/* Backdrop */}
                    <div
                        className="fixed inset-0 z-10"
                        onClick={() => setIsOpen(false)}
                    />

                    {/* Menu */}
                    <div className="absolute top-full mt-2 w-96 bg-white border border-gray-200 rounded-lg shadow-xl z-20 max-h-[80vh] overflow-y-auto">
                        <div className="p-3 border-b border-gray-200 bg-gray-50">
                            <h3 className="font-semibold text-gray-900">Select Intelligence Mode</h3>
                            <p className="text-xs text-gray-600 mt-1">
                                Choose how the AI should respond to your questions
                            </p>
                        </div>

                        <div className="p-2">
                            {Object.values(CHAT_MODES).map((mode) => {
                                const ModeIcon = mode.icon;
                                const isActive = mode.id === currentMode;

                                return (
                                    <button
                                        key={mode.id}
                                        onClick={() => {
                                            onModeChange(mode.id);
                                            setIsOpen(false);
                                        }}
                                        className={`w-full text-left p-3 rounded-lg transition mb-2 ${isActive
                                                ? 'bg-blue-50 border-2 border-blue-500'
                                                : 'hover:bg-gray-50 border-2 border-transparent'
                                            }`}
                                    >
                                        <div className="flex items-start gap-3">
                                            <div className={`p-2 rounded-lg ${isActive ? 'bg-blue-100' : 'bg-gray-100'
                                                }`}>
                                                <span className="text-2xl">{mode.badge}</span>
                                            </div>
                                            <div className="flex-1">
                                                <div className="flex items-center gap-2">
                                                    <span className="font-medium text-gray-900">
                                                        {mode.name}
                                                    </span>
                                                    {isActive && (
                                                        <span className="px-2 py-0.5 bg-blue-500 text-white text-xs rounded-full">
                                                            Active
                                                        </span>
                                                    )}
                                                </div>
                                                <p className="text-sm text-gray-600 mt-1">
                                                    {mode.description}
                                                </p>

                                                {/* Mode-specific details */}
                                                <div className="mt-2 text-xs text-gray-500">
                                                    {mode.id === 'knowledge_base_only' && (
                                                        <div className="flex flex-wrap gap-1">
                                                            <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded">Documents</span>
                                                        </div>
                                                    )}
                                                    {mode.id === 'ai_knowledge_base' && (
                                                        <div className="flex flex-wrap gap-1">
                                                            <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded">Documents</span>
                                                            <span className="px-2 py-0.5 bg-green-100 text-green-700 rounded">AI Analysis</span>
                                                        </div>
                                                    )}
                                                    {mode.id === 'ai_only' && (
                                                        <div className="flex flex-wrap gap-1">
                                                            <span className="px-2 py-0.5 bg-green-100 text-green-700 rounded">AI Knowledge</span>
                                                        </div>
                                                    )}
                                                    {mode.id === 'business_data_only' && (
                                                        <div className="flex flex-wrap gap-1">
                                                            <span className="px-2 py-0.5 bg-orange-100 text-orange-700 rounded">Market Data</span>
                                                            <span className="px-2 py-0.5 bg-orange-100 text-orange-700 rounded">Location Intel</span>
                                                            <span className="px-2 py-0.5 bg-orange-100 text-orange-700 rounded">Competition</span>
                                                        </div>
                                                    )}
                                                    {mode.id === 'full_intelligence' && (
                                                        <div className="flex flex-wrap gap-1">
                                                            <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded">Documents</span>
                                                            <span className="px-2 py-0.5 bg-purple-100 text-purple-700 rounded">Agents</span>
                                                            <span className="px-2 py-0.5 bg-orange-100 text-orange-700 rounded">Live Data</span>
                                                            <span className="px-2 py-0.5 bg-green-100 text-green-700 rounded">AI</span>
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                    </button>
                                );
                            })}
                        </div>

                        <div className="p-3 border-t border-gray-200 bg-gray-50">
                            <p className="text-xs text-gray-600">
                                💡 <strong>Tip:</strong> Use "Full Intelligence" for comprehensive analysis,
                                or "Knowledge Base Only" for strict document-based answers.
                            </p>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}

export { CHAT_MODES };
