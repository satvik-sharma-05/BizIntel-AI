import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown } from 'lucide-react';

export default function KPICard({
    title,
    value,
    icon: Icon,
    trend,
    trendValue,
    description,
    color = 'primary',
    index = 0
}) {
    const colorClasses = {
        primary: 'from-primary-500 to-primary-600',
        success: 'from-success-500 to-success-600',
        warning: 'from-warning-500 to-warning-600',
        danger: 'from-danger-500 to-danger-600',
        info: 'from-info-500 to-info-600',
    };

    const bgColorClasses = {
        primary: 'bg-primary-50',
        success: 'bg-success-50',
        warning: 'bg-warning-50',
        danger: 'bg-danger-50',
        info: 'bg-info-50',
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ y: -4 }}
            className="bg-white rounded-xl border border-secondary-200 p-6 shadow-card hover:shadow-hover transition-all duration-200"
        >
            <div className="flex items-start justify-between mb-4">
                <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${colorClasses[color]} flex items-center justify-center`}>
                    <Icon className="w-6 h-6 text-white" />
                </div>
                {trend && (
                    <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${trend === 'up'
                            ? 'bg-success-50 text-success-700'
                            : 'bg-danger-50 text-danger-700'
                        }`}>
                        {trend === 'up' ? (
                            <TrendingUp className="w-3 h-3" />
                        ) : (
                            <TrendingDown className="w-3 h-3" />
                        )}
                        {trendValue}
                    </div>
                )}
            </div>

            <div className="space-y-1">
                <p className="text-sm font-medium text-secondary-600">{title}</p>
                <motion.p
                    initial={{ scale: 0.5 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: index * 0.1 + 0.2, type: 'spring' }}
                    className="text-3xl font-bold text-secondary-900"
                >
                    {value}
                </motion.p>
                {description && (
                    <p className="text-xs text-secondary-500 mt-2">{description}</p>
                )}
            </div>
        </motion.div>
    );
}
