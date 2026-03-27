import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Bot, User, FileText, Copy, Check, Sparkles } from 'lucide-react';
import { useState } from 'react';
import { motion } from 'framer-motion';

export default function ChatMessage({ message, isUser }) {
    const [copied, setCopied] = useState(false);

    const copyToClipboard = () => {
        navigator.clipboard.writeText(message.content);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-6`}
        >
            <div className={`flex items-start max-w-[85%] ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
                {/* Avatar */}
                <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ type: 'spring', delay: 0.1 }}
                    className={`flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center shadow-sm ${isUser
                            ? 'bg-gradient-to-br from-primary-500 to-primary-600 ml-3'
                            : 'bg-gradient-to-br from-secondary-700 to-secondary-900 mr-3'
                        }`}
                >
                    {isUser ? (
                        <User className="w-5 h-5 text-white" />
                    ) : (
                        <Sparkles className="w-5 h-5 text-white" />
                    )}
                </motion.div>

                {/* Message Content */}
                <div className="flex-1 min-w-0">
                    <div
                        className={`rounded-2xl px-5 py-4 shadow-sm ${isUser
                                ? 'bg-gradient-to-br from-primary-600 to-primary-700 text-white'
                                : 'bg-white border border-secondary-200'
                            }`}
                    >
                        {isUser ? (
                            <div className="text-white whitespace-pre-wrap break-words leading-relaxed">
                                {message.content}
                            </div>
                        ) : (
                            <div className="prose prose-sm max-w-none">
                                <ReactMarkdown
                                    remarkPlugins={[remarkGfm]}
                                    components={{
                                        h1: ({ node, ...props }) => (
                                            <h1 className="text-2xl font-bold text-secondary-900 mt-4 mb-3" {...props} />
                                        ),
                                        h2: ({ node, ...props }) => (
                                            <h2 className="text-xl font-bold text-secondary-900 mt-4 mb-2" {...props} />
                                        ),
                                        h3: ({ node, ...props }) => (
                                            <h3 className="text-lg font-semibold text-secondary-800 mt-3 mb-2" {...props} />
                                        ),
                                        p: ({ node, ...props }) => (
                                            <p className="text-secondary-700 mb-3 leading-relaxed" {...props} />
                                        ),
                                        ul: ({ node, ...props }) => (
                                            <ul className="list-disc list-inside mb-3 space-y-1 text-secondary-700" {...props} />
                                        ),
                                        ol: ({ node, ...props }) => (
                                            <ol className="list-decimal list-inside mb-3 space-y-1 text-secondary-700" {...props} />
                                        ),
                                        li: ({ node, ...props }) => (
                                            <li className="ml-2 text-secondary-700" {...props} />
                                        ),
                                        strong: ({ node, ...props }) => (
                                            <strong className="font-bold text-secondary-900" {...props} />
                                        ),
                                        code: ({ node, inline, ...props }) =>
                                            inline ? (
                                                <code
                                                    className="bg-secondary-100 text-primary-600 px-1.5 py-0.5 rounded text-sm font-mono"
                                                    {...props}
                                                />
                                            ) : (
                                                <code
                                                    className="block bg-secondary-900 text-secondary-100 p-4 rounded-lg overflow-x-auto text-sm font-mono my-3"
                                                    {...props}
                                                />
                                            ),
                                        table: ({ node, ...props }) => (
                                            <div className="overflow-x-auto my-4">
                                                <table className="min-w-full divide-y divide-secondary-200 border border-secondary-200 rounded-lg" {...props} />
                                            </div>
                                        ),
                                        thead: ({ node, ...props }) => (
                                            <thead className="bg-secondary-50" {...props} />
                                        ),
                                        th: ({ node, ...props }) => (
                                            <th className="px-4 py-2 text-left text-xs font-semibold text-secondary-700 uppercase tracking-wider" {...props} />
                                        ),
                                        td: ({ node, ...props }) => (
                                            <td className="px-4 py-2 text-sm text-secondary-700 border-t border-secondary-200" {...props} />
                                        ),
                                        blockquote: ({ node, ...props }) => (
                                            <blockquote className="border-l-4 border-primary-500 pl-4 italic text-secondary-600 my-3 bg-primary-50 py-2 rounded-r" {...props} />
                                        ),
                                        a: ({ node, ...props }) => (
                                            <a className="text-primary-600 hover:text-primary-700 underline" {...props} />
                                        ),
                                    }}
                                >
                                    {message.content}
                                </ReactMarkdown>
                            </div>
                        )}

                        {/* Citations */}
                        {!isUser && message.citations && message.citations.length > 0 && (
                            <div className="mt-4 pt-4 border-t border-secondary-200">
                                <div className="flex items-center gap-2 text-xs font-semibold text-secondary-600 mb-2">
                                    <FileText className="w-4 h-4" />
                                    <span>Sources from your documents:</span>
                                </div>
                                <div className="space-y-1">
                                    {message.citations.map((citation, idx) => (
                                        <div
                                            key={idx}
                                            className="text-xs text-secondary-600 bg-secondary-50 px-3 py-2 rounded-lg flex items-center justify-between hover:bg-secondary-100 transition-colors"
                                        >
                                            <span>
                                                📄 {citation.filename} - Page {citation.page_number}
                                            </span>
                                            {citation.similarity && (
                                                <span className="text-success-600 font-medium">
                                                    {(citation.similarity * 100).toFixed(0)}% match
                                                </span>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Sources Used Badge */}
                        {!isUser && message.sources && (
                            <div className="mt-3 flex flex-wrap gap-2">
                                {message.sources.documents && (
                                    <span className="inline-flex items-center gap-1 px-2 py-1 bg-primary-50 text-primary-700 text-xs rounded-full font-medium">
                                        📄 Documents
                                    </span>
                                )}
                                {message.sources.agents && (
                                    <span className="inline-flex items-center gap-1 px-2 py-1 bg-secondary-100 text-secondary-700 text-xs rounded-full font-medium">
                                        🤖 Live Data
                                    </span>
                                )}
                                {message.sources.ai_knowledge && (
                                    <span className="inline-flex items-center gap-1 px-2 py-1 bg-success-50 text-success-700 text-xs rounded-full font-medium">
                                        🧠 AI Analysis
                                    </span>
                                )}
                            </div>
                        )}
                    </div>

                    {/* Copy Button for AI messages */}
                    {!isUser && (
                        <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={copyToClipboard}
                            className="mt-2 ml-2 text-xs text-secondary-500 hover:text-secondary-700 flex items-center gap-1 transition-colors"
                            title="Copy message"
                        >
                            {copied ? (
                                <>
                                    <Check className="w-3 h-3 text-success-600" />
                                    <span className="text-success-600">Copied!</span>
                                </>
                            ) : (
                                <>
                                    <Copy className="w-3 h-3" />
                                    Copy
                                </>
                            )}
                        </motion.button>
                    )}

                    {/* Timestamp */}
                    {message.timestamp && (
                        <div className={`text-xs text-secondary-400 mt-1 ${isUser ? 'text-right mr-2' : 'ml-2'}`}>
                            {new Date(message.timestamp).toLocaleTimeString([], {
                                hour: '2-digit',
                                minute: '2-digit',
                            })}
                        </div>
                    )}
                </div>
            </div>
        </motion.div>
    );
}
