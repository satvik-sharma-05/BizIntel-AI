import Link from 'next/link';
import { useRouter } from 'next/router';
import { useBusiness } from '../contexts/BusinessContext';
import { motion } from 'framer-motion';
import {
    LayoutDashboard,
    MessageSquare,
    TrendingUp,
    MapPin,
    BarChart3,
    FileText,
    Database,
    Settings,
    Activity,
    Bot,
    FileBarChart,
    Sparkles
} from 'lucide-react';

export default function Sidebar() {
    const router = useRouter();
    const { currentBusiness } = useBusiness();

    // Get businessId from URL or current business
    const { businessId } = router.query;
    const activeBusinessId = businessId || currentBusiness?.id;

    // Business-scoped menu items
    const businessMenuItems = activeBusinessId ? [
        { name: 'Overview', icon: LayoutDashboard, path: `/business/${activeBusinessId}/overview` },
        { name: 'AI Chat', icon: MessageSquare, path: `/business/${activeBusinessId}/chat` },
        { name: 'Market Analysis', icon: TrendingUp, path: `/business/${activeBusinessId}/market` },
        { name: 'Location Intel', icon: MapPin, path: `/business/${activeBusinessId}/location` },
        { name: 'Forecasting', icon: BarChart3, path: `/business/${activeBusinessId}/forecast` },
        { name: 'Documents', icon: FileText, path: `/business/${activeBusinessId}/documents` },
        { name: 'Agents', icon: Bot, path: `/business/${activeBusinessId}/agents` },
        { name: 'Reports', icon: FileBarChart, path: `/business/${activeBusinessId}/reports` },
        { name: 'Settings', icon: Settings, path: `/business/${activeBusinessId}/settings` },
    ] : [];

    // Global menu items (always available)
    const globalMenuItems = [
        { name: 'System Status', icon: Activity, path: '/system-apis' },
        { name: 'Data Sources', icon: Database, path: '/data' },
    ];

    const isPathActive = (path) => {
        if (path.includes('/business/')) {
            return router.pathname.startsWith(path.split('?')[0]);
        }
        return router.pathname === path;
    };

    return (
        <div className="w-64 bg-white border-r border-secondary-200 h-screen fixed left-0 top-0 overflow-y-auto flex flex-col">
            {/* Logo */}
            <div className="p-6 border-b border-secondary-200">
                <div className="flex items-center gap-2">
                    <div className="w-8 h-8 bg-gradient-to-br from-primary-600 to-primary-700 rounded-lg flex items-center justify-center">
                        <Sparkles className="w-5 h-5 text-white" />
                    </div>
                    <div>
                        <h1 className="text-lg font-bold text-secondary-900">BizIntel AI</h1>
                        <p className="text-xs text-secondary-500">Intelligence Platform</p>
                    </div>
                </div>
            </div>

            {/* Business Menu */}
            {activeBusinessId && (
                <div className="flex-1 py-4">
                    <div className="px-4 mb-2">
                        <p className="text-xs font-semibold text-secondary-500 uppercase tracking-wider">
                            Workspace
                        </p>
                    </div>
                    <nav className="space-y-1 px-3">
                        {businessMenuItems.map((item, index) => {
                            const Icon = item.icon;
                            const isActive = isPathActive(item.path);

                            return (
                                <motion.div
                                    key={item.path}
                                    initial={{ opacity: 0, x: -10 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: index * 0.05 }}
                                >
                                    <Link
                                        href={item.path}
                                        className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group ${isActive
                                                ? 'bg-primary-50 text-primary-700 font-medium'
                                                : 'text-secondary-700 hover:bg-secondary-50 hover:text-secondary-900'
                                            }`}
                                    >
                                        <Icon className={`w-5 h-5 transition-transform group-hover:scale-110 ${isActive ? 'text-primary-600' : 'text-secondary-500'
                                            }`} />
                                        <span className="text-sm">{item.name}</span>
                                    </Link>
                                </motion.div>
                            );
                        })}
                    </nav>
                </div>
            )}

            {/* No Business Selected */}
            {!activeBusinessId && (
                <div className="flex-1 px-4 py-6">
                    <div className="bg-warning-50 border border-warning-200 rounded-xl p-4">
                        <p className="text-sm font-medium text-warning-800 mb-2">No business selected</p>
                        <Link
                            href="/select-business"
                            className="text-xs text-primary-600 hover:text-primary-700 font-medium inline-flex items-center gap-1"
                        >
                            Select a business →
                        </Link>
                    </div>
                </div>
            )}

            {/* Global Menu */}
            <div className="border-t border-secondary-200 py-4">
                <div className="px-4 mb-2">
                    <p className="text-xs font-semibold text-secondary-500 uppercase tracking-wider">
                        System
                    </p>
                </div>
                <nav className="space-y-1 px-3">
                    {globalMenuItems.map((item) => {
                        const Icon = item.icon;
                        const isActive = isPathActive(item.path);

                        return (
                            <Link
                                key={item.path}
                                href={item.path}
                                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group ${isActive
                                        ? 'bg-primary-50 text-primary-700 font-medium'
                                        : 'text-secondary-700 hover:bg-secondary-50 hover:text-secondary-900'
                                    }`}
                            >
                                <Icon className={`w-5 h-5 transition-transform group-hover:scale-110 ${isActive ? 'text-primary-600' : 'text-secondary-500'
                                    }`} />
                                <span className="text-sm">{item.name}</span>
                            </Link>
                        );
                    })}
                </nav>
            </div>
        </div>
    );
}
