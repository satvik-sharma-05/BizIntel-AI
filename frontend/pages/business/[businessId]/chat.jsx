import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/router';
import MainLayout from '../../../components/MainLayout';
import ChatMessage from '../../../components/ChatMessage';
import ChatModeSelector from '../../../components/ChatModeSelector';
import { chatAPI, businessAPI } from '../../../lib/api';
import { Send, Bot, Trash2, RefreshCw, Sparkles } from 'lucide-react';
import toast from 'react-hot-toast';

export default function BusinessChat() {
    const router = useRouter();
    const { businessId } = router.query;
    const [business, setBusiness] = useState(null);
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [showClearConfirm, setShowClearConfirm] = useState(false);
    const [initialLoading, setInitialLoading] = useState(true);
    const [chatMode, setChatMode] = useState('full_intelligence'); // Default mode
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    useEffect(() => {
        if (businessId) {
            loadBusinessAndChat();
        }
    }, [businessId]);

    const loadBusinessAndChat = async () => {
        try {
            // Load business details
            const businessData = await businessAPI.get(businessId);
            setBusiness(businessData);

            // Load chat history
            await loadChatHistory();
        } catch (error) {
            console.error('Error loading business/chat:', error);
            if (error.response?.status === 404) {
                router.push('/select-business');
            }
        } finally {
            setInitialLoading(false);
        }
    };

    const loadChatHistory = async () => {
        try {
            const response = await chatAPI.getHistory(businessId, 50);
            if (response.conversations && response.conversations.length > 0) {
                const historyMessages = [];
                response.conversations.reverse().forEach(conv => {
                    historyMessages.push({
                        role: 'user',
                        content: conv.message,
                        timestamp: conv.timestamp
                    });
                    historyMessages.push({
                        role: 'assistant',
                        content: conv.response,
                        citations: conv.citations || [],
                        rag_used: conv.rag_used || false,
                        sources: conv.sources || {},
                        timestamp: conv.timestamp
                    });
                });
                setMessages(historyMessages);
            } else if (business) {
                // Set welcome message
                setMessages([
                    {
                        role: 'assistant',
                        content: `# Welcome to ${business.name} AI Assistant! 👋

I'm your **intelligent business advisor** with access to multiple sources of knowledge:

## My Capabilities

### 📄 Your Documents
I can read and analyze your uploaded documents:
- Business plans and strategies
- Financial projections
- Market research reports
- Any PDF, DOCX, or TXT files you upload

### 🤖 Live Market Intelligence
I have access to real-time data through specialized agents:
- Market analysis and competition
- Location intelligence
- Economic indicators
- Industry trends

### 🧠 Business Expertise
I bring general business knowledge:
- Industry best practices
- Strategic recommendations
- Growth strategies
- Problem-solving approaches

## How I Work

I **automatically combine** all relevant sources to give you comprehensive answers:
- If you have documents → I'll cite them
- If you need market data → I'll fetch it
- Always → I'll add expert analysis

## Try Asking Me

**About Your Documents:**
- "What are my revenue targets for Q2?"
- "Summarize my business plan"

**About Markets:**
- "Should I expand to Bangalore?"
- "What's the competition in my area?"

**General Business:**
- "How can I improve customer retention?"
- "What's the best marketing strategy for my industry?"

**Combined Analysis:**
- "Compare my projections with market trends"
- "Is my expansion plan realistic given current conditions?"

## 💡 Pro Tip
I'm not limited to just documents - I can help with any business question by combining your data, live market intelligence, and expert knowledge!

**What would you like to know?**`,
                        sources: {
                            documents: false,
                            agents: false,
                            ai_knowledge: true
                        }
                    },
                ]);
            }
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    };

    const sendMessage = async () => {
        if (!input.trim() || !businessId) return;

        const userMessage = { role: 'user', content: input, timestamp: new Date().toISOString() };
        setMessages((prev) => [...prev, userMessage]);
        setInput('');
        setLoading(true);

        try {
            const response = await chatAPI.sendMessage(businessId, input, chatMode); // Pass mode

            const assistantMessage = {
                role: 'assistant',
                content: response.response,
                citations: response.citations || [],
                rag_used: response.rag_used || false,
                sources: response.structured_response?.sources || {},
                mode: chatMode,
                timestamp: new Date().toISOString()
            };

            setMessages((prev) => [...prev, assistantMessage]);
        } catch (error) {
            console.error('Chat error:', error);
            const errorMessage = {
                role: 'assistant',
                content: '❌ Sorry, I encountered an error. Please try again or contact support if the issue persists.',
                timestamp: new Date().toISOString()
            };
            setMessages((prev) => [...prev, errorMessage]);
            toast.error('Failed to send message');
        } finally {
            setLoading(false);
        }
    };

    const clearChat = async () => {
        try {
            await chatAPI.clearHistory(businessId);
            setMessages([
                {
                    role: 'assistant',
                    content: `# Chat Cleared! ✨

How can I help you today?`,
                    timestamp: new Date().toISOString()
                },
            ]);
            setShowClearConfirm(false);
            toast.success('Chat history cleared');
        } catch (error) {
            console.error('Error clearing chat:', error);
            toast.error('Failed to clear chat');
        }
    };

    if (initialLoading) {
        return (
            <MainLayout>
                <div className="flex items-center justify-center h-full">
                    <div className="flex flex-col items-center gap-4">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                        <div className="text-xl text-gray-600">Loading chat...</div>
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

    return (
        <MainLayout>
            <div className="h-[calc(100vh-12rem)]">
                <div className="mb-4 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="bg-gradient-to-br from-purple-500 to-indigo-600 p-3 rounded-xl">
                            <Sparkles className="w-6 h-6 text-white" />
                        </div>
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900">AI Assistant</h1>
                            <p className="text-gray-600 mt-1">Intelligent insights for {business.name}</p>
                        </div>
                    </div>
                    <div className="flex gap-2 items-center">
                        <ChatModeSelector
                            currentMode={chatMode}
                            onModeChange={setChatMode}
                        />
                        <button
                            onClick={loadChatHistory}
                            className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition"
                            title="Refresh chat"
                        >
                            <RefreshCw className="w-4 h-4" />
                            Refresh
                        </button>
                        <button
                            onClick={() => setShowClearConfirm(true)}
                            className="flex items-center gap-2 px-4 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition"
                        >
                            <Trash2 className="w-4 h-4" />
                            Clear Chat
                        </button>
                    </div>
                </div>

                {/* Clear Confirmation Modal */}
                {showClearConfirm && (
                    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                        <div className="bg-white rounded-xl p-6 max-w-md w-full mx-4 shadow-2xl">
                            <h3 className="text-xl font-bold text-gray-900 mb-2">Clear Chat History?</h3>
                            <p className="text-gray-600 mb-6">
                                This will permanently delete all chat messages for this business. This action cannot be undone.
                            </p>
                            <div className="flex gap-3 justify-end">
                                <button
                                    onClick={() => setShowClearConfirm(false)}
                                    className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={clearChat}
                                    className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
                                >
                                    Clear Chat
                                </button>
                            </div>
                        </div>
                    </div>
                )}

                <div className="bg-gradient-to-b from-gray-50 to-white rounded-xl shadow-lg h-[calc(100%-8rem)] flex flex-col border border-gray-200">
                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto p-6">
                        {messages.map((message, idx) => (
                            <ChatMessage
                                key={idx}
                                message={message}
                                isUser={message.role === 'user'}
                            />
                        ))}
                        {loading && (
                            <div className="flex justify-start mb-6">
                                <div className="flex items-start max-w-[85%]">
                                    <div className="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center bg-gradient-to-br from-purple-500 to-indigo-600 mr-3">
                                        <Bot className="w-5 h-5 text-white" />
                                    </div>
                                    <div className="bg-white border border-gray-200 rounded-2xl px-5 py-4 shadow-sm">
                                        <div className="flex space-x-2">
                                            <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce"></div>
                                            <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                                            <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input */}
                    <div className="border-t border-gray-200 p-4 bg-white rounded-b-xl">
                        <div className="flex space-x-3">
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
                                placeholder="Ask me anything about your business..."
                                className="flex-1 border border-gray-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition"
                                disabled={loading}
                            />
                            <button
                                onClick={sendMessage}
                                disabled={loading || !input.trim()}
                                className="bg-gradient-to-r from-purple-500 to-indigo-600 text-white px-6 py-3 rounded-xl hover:from-purple-600 hover:to-indigo-700 disabled:from-gray-300 disabled:to-gray-400 disabled:cursor-not-allowed transition shadow-md hover:shadow-lg flex items-center gap-2"
                            >
                                <Send className="w-5 h-5" />
                                <span className="font-medium">Send</span>
                            </button>
                        </div>
                        <div className="mt-2 text-xs text-gray-500 text-center">
                            Press Enter to send • Shift + Enter for new line
                        </div>
                    </div>
                </div>
            </div>
        </MainLayout>
    );
}
