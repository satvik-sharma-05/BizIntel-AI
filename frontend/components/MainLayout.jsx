'use client';

import { useState, useEffect, useRef } from 'react';
import { useBusiness } from '../contexts/BusinessContext';
import { useAuth } from '../contexts/AuthContext';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import ProtectedRoute from './ProtectedRoute';
import BusinessSwitcher from './BusinessSwitcher';
import { chatAPI } from '../lib/api';
import {
    LayoutDashboard,
    Lightbulb,
    TrendingUp,
    MapPin,
    BarChart3,
    FileText,
    FileStack,
    Bot,
    Settings,
    Bell,
    User,
    MessageSquare,
    X,
    Menu,
    LogOut,
    Send,
    Sparkles,
    ChevronLeft
} from 'lucide-react';

const menuItems = [
    { name: 'Overview', icon: LayoutDashboard, path: '/overview' },
    { name: 'Insights', icon: Lightbulb, path: '/insights' },
    { name: 'Market Analysis', icon: TrendingUp, path: '/market' },
    { name: 'Location Intel', icon: MapPin, path: '/location' },
    { name: 'Forecasting', icon: BarChart3, path: '/forecast' },
    { name: 'Documents', icon: FileStack, path: '/documents' },
    { name: 'AI Agents', icon: Bot, path: '/agents' },
    { name: 'Settings', icon: Settings, path: '/settings' },
];

export default function MainLayout({ children }) {
    return (
        <ProtectedRoute>
            <MainLayoutContent>{children}</MainLayoutContent>
        </ProtectedRoute>
    );
}

function MainLayoutContent({ children }) {
    const { currentBusiness, loading: businessLoading } = useBusiness();
    const { user, logout } = useAuth();
    const router = useRouter();
    const [showAIPanel, setShowAIPanel] = useState(false);
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const [showUserMenu, setShowUserMenu] = useState(false);

    useEffect(() => {
        if (!businessLoading && !currentBusiness) {
            router.push('/select-business');
        }
    }, [currentBusiness, businessLoading, router]);

    if (businessLoading) {
        return (
            <div className="flex items-center justify-center h-screen bg-secondary-50">
                <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="text-center"
                >
                    <div className="relative w-16 h-16 mx-auto mb-4">
                        <div className="absolute inset-0 border-4 border-primary-200 rounded-full"></div>
                        <div className="absolute inset-0 border-4 border-primary-600 rounded-full border-t-transparent animate-spin"></div>
                    </div>
                    <p className="text-secondary-600 font-medium">Loading workspace...</p>
                </motion.div>
            </div>
        );
    }

    if (!currentBusiness) {
        return (
            <div className="flex items-center justify-center h-screen bg-secondary-50">
                <div className="text-xl text-secondary-600">Loading...</div>
            </div>
        );
    }

    return (
        <div className="flex h-screen bg-secondary-50">
            {/* Sidebar */}
            <AnimatePresence mode="wait">
                <motion.aside
                    initial={false}
                    animate={{ width: sidebarOpen ? 256 : 80 }}
                    className="bg-white border-r border-secondary-200 flex flex-col relative"
                >
                    {/* Logo */}
                    <div className="p-6 border-b border-secondary-200">
                        {sidebarOpen ? (
                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                            >
                                <div className="flex items-center gap-2">
                                    <div className="w-8 h-8 bg-gradient-to-br from-primary-600 to-primary-700 rounded-lg flex items-center justify-center">
                                        <Sparkles className="w-5 h-5 text-white" />
                                    </div>
                                    <div>
                                        <h1 className="text-lg font-bold text-secondary-900">BizIntel AI</h1>
                                        <p className="text-xs text-secondary-500">Intelligence Platform</p>
                                    </div>
                                </div>
                            </motion.div>
                        ) : (
                            <div className="w-8 h-8 bg-gradient-to-br from-primary-600 to-primary-700 rounded-lg flex items-center justify-center mx-auto">
                                <Sparkles className="w-5 h-5 text-white" />
                            </div>
                        )}
                    </div>

                    {/* Navigation */}
                    <nav className="flex-1 py-6 overflow-y-auto px-3">
                        {menuItems.map((item, index) => {
                            const Icon = item.icon;
                            const isActive = router.pathname === item.path;

                            return (
                                <motion.div
                                    key={item.path}
                                    initial={{ opacity: 0, x: -10 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: index * 0.05 }}
                                >
                                    <Link
                                        href={item.path}
                                        className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 mb-1 group ${isActive
                                            ? 'bg-primary-50 text-primary-700 font-medium'
                                            : 'text-secondary-700 hover:bg-secondary-50 hover:text-secondary-900'
                                            }`}
                                        title={!sidebarOpen ? item.name : ''}
                                    >
                                        <Icon className={`w-5 h-5 flex-shrink-0 transition-transform group-hover:scale-110 ${isActive ? 'text-primary-600' : 'text-secondary-500'
                                            }`} />
                                        {sidebarOpen && <span className="text-sm">{item.name}</span>}
                                    </Link>
                                </motion.div>
                            );
                        })}
                    </nav>

                    {/* Sidebar Toggle */}
                    <button
                        onClick={() => setSidebarOpen(!sidebarOpen)}
                        className="absolute -right-3 top-20 w-6 h-6 bg-white border border-secondary-200 rounded-full flex items-center justify-center hover:bg-secondary-50 transition-colors shadow-sm"
                    >
                        <ChevronLeft className={`w-4 h-4 text-secondary-600 transition-transform ${!sidebarOpen ? 'rotate-180' : ''}`} />
                    </button>
                </motion.aside>
            </AnimatePresence>

            {/* Main Content */}
            <div className="flex-1 flex flex-col overflow-hidden">
                {/* Top Navbar */}
                <header className="bg-white border-b border-secondary-200 px-6 py-4">
                    <div className="flex items-center justify-between">
                        <BusinessSwitcher />

                        <div className="flex items-center gap-3">
                            {/* AI Assistant Button */}
                            <motion.button
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                                onClick={() => setShowAIPanel(!showAIPanel)}
                                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-lg hover:from-primary-700 hover:to-primary-800 transition-all shadow-sm"
                            >
                                <MessageSquare className="w-4 h-4" />
                                <span className="text-sm font-medium">AI Assistant</span>
                            </motion.button>

                            {/* Notifications */}
                            <button className="p-2 hover:bg-secondary-50 rounded-lg transition-colors relative">
                                <Bell className="w-5 h-5 text-secondary-600" />
                                <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-danger-500 rounded-full"></span>
                            </button>

                            {/* Profile Menu */}
                            <div className="relative">
                                <button
                                    onClick={() => setShowUserMenu(!showUserMenu)}
                                    className="flex items-center gap-2 p-2 hover:bg-secondary-50 rounded-lg transition-colors"
                                >
                                    <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-700 rounded-full flex items-center justify-center">
                                        <User className="w-4 h-4 text-white" />
                                    </div>
                                    <span className="text-sm font-medium text-secondary-700">{user?.name}</span>
                                </button>

                                <AnimatePresence>
                                    {showUserMenu && (
                                        <motion.div
                                            initial={{ opacity: 0, y: -10 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            exit={{ opacity: 0, y: -10 }}
                                            className="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-hover border border-secondary-200 py-1 z-50"
                                        >
                                            <Link
                                                href="/settings"
                                                className="flex items-center gap-2 px-4 py-2.5 text-secondary-700 hover:bg-secondary-50 transition-colors"
                                            >
                                                <Settings className="w-4 h-4" />
                                                <span className="text-sm">Settings</span>
                                            </Link>
                                            <button
                                                onClick={logout}
                                                className="w-full flex items-center gap-2 px-4 py-2.5 text-danger-600 hover:bg-danger-50 transition-colors"
                                            >
                                                <LogOut className="w-4 h-4" />
                                                <span className="text-sm">Logout</span>
                                            </button>
                                        </motion.div>
                                    )}
                                </AnimatePresence>
                            </div>
                        </div>
                    </div>
                </header>

                {/* Content Area */}
                <main className="flex-1 overflow-y-auto">
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.3 }}
                        className="p-8"
                    >
                        {children}
                    </motion.div>
                </main>
            </div>

            {/* AI Assistant Panel */}
            <AnimatePresence>
                {showAIPanel && (
                    <AIAssistantPanel onClose={() => setShowAIPanel(false)} />
                )}
            </AnimatePresence>
        </div>
    );
}

function AIAssistantPanel({ onClose }) {
    const { currentBusiness } = useBusiness();
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    useEffect(() => {
        if (currentBusiness?.name) {
            setMessages([{
                role: 'assistant',
                content: `Hello! I'm your AI assistant for ${currentBusiness.name}. How can I help you today?`
            }]);
        }
    }, [currentBusiness]);

    const handleSend = async () => {
        if (!input.trim() || !currentBusiness) return;

        const userMessage = { role: 'user', content: input };
        setMessages([...messages, userMessage]);
        setInput('');
        setLoading(true);

        try {
            const response = await chatAPI.sendMessage(currentBusiness._id || currentBusiness.id, input);

            setMessages(prev => [...prev, {
                role: 'assistant',
                content: response.response
            }]);
        } catch (error) {
            console.error('Error sending message:', error);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: 'Sorry, I encountered an error. Please try again.'
            }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <motion.div
            initial={{ x: 400, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 400, opacity: 0 }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="w-96 bg-white border-l border-secondary-200 flex flex-col shadow-xl"
        >
            {/* Header */}
            <div className="p-4 border-b border-secondary-200 flex items-center justify-between bg-gradient-to-r from-primary-50 to-primary-100">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-primary-600 to-primary-700 rounded-xl flex items-center justify-center shadow-sm">
                        <Bot className="w-5 h-5 text-white" />
                    </div>
                    <div>
                        <div className="font-semibold text-secondary-900">AI Assistant</div>
                        <div className="text-xs text-secondary-600 flex items-center gap-1">
                            <span className="w-2 h-2 bg-success-500 rounded-full animate-pulse"></span>
                            Online
                        </div>
                    </div>
                </div>
                <button
                    onClick={onClose}
                    className="p-1.5 hover:bg-white rounded-lg transition-colors"
                >
                    <X className="w-5 h-5 text-secondary-500" />
                </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-secondary-50">
                {messages.map((msg, idx) => (
                    <motion.div
                        key={idx}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.3 }}
                        className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                        <div
                            className={`max-w-[85%] px-4 py-2.5 rounded-xl shadow-sm ${msg.role === 'user'
                                    ? 'bg-gradient-to-r from-primary-600 to-primary-700 text-white'
                                    : 'bg-white text-secondary-900 border border-secondary-200'
                                }`}
                        >
                            <p className="text-sm leading-relaxed">{msg.content}</p>
                        </div>
                    </motion.div>
                ))}
                {loading && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="flex justify-start"
                    >
                        <div className="bg-white px-4 py-3 rounded-xl border border-secondary-200 shadow-sm">
                            <div className="flex gap-1.5">
                                <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce"></div>
                                <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                                <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                            </div>
                        </div>
                    </motion.div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-4 border-t border-secondary-200 bg-white">
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
                        placeholder="Ask me anything..."
                        className="flex-1 px-4 py-2.5 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all text-sm"
                    />
                    <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={handleSend}
                        disabled={loading || !input.trim()}
                        className="px-4 py-2.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
                    >
                        <Send className="w-4 h-4" />
                    </motion.button>
                </div>
                <p className="text-xs text-secondary-500 mt-2">Press Enter to send</p>
            </div>
        </motion.div>
    );
}
