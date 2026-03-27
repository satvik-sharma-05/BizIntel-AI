import { motion } from 'framer-motion';

export function PageLoader() {
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
                <p className="text-secondary-600 font-medium">Loading...</p>
            </motion.div>
        </div>
    );
}

export function CardSkeleton() {
    return (
        <div className="bg-white rounded-xl border border-secondary-200 p-6 shadow-card animate-pulse">
            <div className="flex items-start justify-between mb-4">
                <div className="w-12 h-12 bg-secondary-200 rounded-lg"></div>
                <div className="w-16 h-6 bg-secondary-200 rounded-full"></div>
            </div>
            <div className="space-y-3">
                <div className="h-4 bg-secondary-200 rounded w-1/2"></div>
                <div className="h-8 bg-secondary-200 rounded w-3/4"></div>
                <div className="h-3 bg-secondary-200 rounded w-full"></div>
            </div>
        </div>
    );
}

export function TableSkeleton({ rows = 5 }) {
    return (
        <div className="bg-white rounded-xl border border-secondary-200 overflow-hidden">
            <div className="p-4 border-b border-secondary-200 animate-pulse">
                <div className="h-6 bg-secondary-200 rounded w-1/4"></div>
            </div>
            <div className="divide-y divide-secondary-200">
                {Array.from({ length: rows }).map((_, i) => (
                    <div key={i} className="p-4 animate-pulse">
                        <div className="flex items-center gap-4">
                            <div className="w-10 h-10 bg-secondary-200 rounded-lg"></div>
                            <div className="flex-1 space-y-2">
                                <div className="h-4 bg-secondary-200 rounded w-1/3"></div>
                                <div className="h-3 bg-secondary-200 rounded w-1/2"></div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

export function ChartSkeleton() {
    return (
        <div className="bg-white rounded-xl border border-secondary-200 p-6 shadow-card">
            <div className="animate-pulse">
                <div className="h-6 bg-secondary-200 rounded w-1/3 mb-6"></div>
                <div className="h-64 bg-secondary-100 rounded-lg flex items-end justify-around p-4 gap-2">
                    {Array.from({ length: 7 }).map((_, i) => (
                        <div
                            key={i}
                            className="bg-secondary-200 rounded-t"
                            style={{ height: `${Math.random() * 60 + 40}%`, width: '100%' }}
                        ></div>
                    ))}
                </div>
            </div>
        </div>
    );
}

export function Spinner({ size = 'md' }) {
    const sizeClasses = {
        sm: 'w-4 h-4 border-2',
        md: 'w-8 h-8 border-3',
        lg: 'w-12 h-12 border-4',
    };

    return (
        <div className={`${sizeClasses[size]} border-primary-200 border-t-primary-600 rounded-full animate-spin`}></div>
    );
}
