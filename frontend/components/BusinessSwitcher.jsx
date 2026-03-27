import { useState } from 'react';
import { useBusiness } from '../contexts/BusinessContext';
import { ChevronDown, Building2, Plus, Check } from 'lucide-react';
import { useRouter } from 'next/router';
import { motion, AnimatePresence } from 'framer-motion';

export default function BusinessSwitcher() {
    const { businesses, currentBusiness, switchBusiness } = useBusiness();
    const [isOpen, setIsOpen] = useState(false);
    const router = useRouter();

    const handleSwitch = (business) => {
        switchBusiness(business);
        setIsOpen(false);
    };

    const handleCreateNew = () => {
        router.push('/select-business');
        setIsOpen(false);
    };

    if (!currentBusiness) {
        return null;
    }

    return (
        <div className="relative">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center gap-3 px-4 py-2.5 bg-white border border-secondary-200 rounded-lg hover:bg-secondary-50 transition-all shadow-sm"
            >
                <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg flex items-center justify-center">
                    <Building2 className="w-4 h-4 text-white" />
                </div>
                <div className="text-left">
                    <div className="text-sm font-semibold text-secondary-900">
                        {currentBusiness.name || currentBusiness.business_name}
                    </div>
                    <div className="text-xs text-secondary-500">
                        {currentBusiness.industry} • {currentBusiness.city}
                    </div>
                </div>
                <ChevronDown className={`w-4 h-4 text-secondary-500 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
            </button>

            <AnimatePresence>
                {isOpen && (
                    <>
                        <div
                            className="fixed inset-0 z-40"
                            onClick={() => setIsOpen(false)}
                        />
                        <motion.div
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            className="absolute top-full left-0 mt-2 w-80 bg-white rounded-xl shadow-hover border border-secondary-200 py-2 z-50"
                        >
                            <div className="px-3 py-2 border-b border-secondary-200">
                                <p className="text-xs font-semibold text-secondary-500 uppercase tracking-wider">
                                    Your Businesses
                                </p>
                            </div>

                            <div className="max-h-64 overflow-y-auto py-1">
                                {businesses.map((business) => (
                                    <button
                                        key={business.id}
                                        onClick={() => handleSwitch(business)}
                                        className="w-full flex items-center gap-3 px-3 py-2.5 hover:bg-secondary-50 transition-colors"
                                    >
                                        <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg flex items-center justify-center flex-shrink-0">
                                            <Building2 className="w-5 h-5 text-white" />
                                        </div>
                                        <div className="flex-1 text-left">
                                            <div className="text-sm font-medium text-secondary-900">
                                                {business.name || business.business_name}
                                            </div>
                                            <div className="text-xs text-secondary-500">
                                                {business.industry} • {business.city}
                                            </div>
                                        </div>
                                        {currentBusiness.id === business.id && (
                                            <Check className="w-4 h-4 text-primary-600" />
                                        )}
                                    </button>
                                ))}
                            </div>

                            <div className="border-t border-secondary-200 pt-1 mt-1">
                                <button
                                    onClick={handleCreateNew}
                                    className="w-full flex items-center gap-2 px-3 py-2.5 text-primary-600 hover:bg-primary-50 transition-colors"
                                >
                                    <Plus className="w-4 h-4" />
                                    <span className="text-sm font-medium">Create New Business</span>
                                </button>
                            </div>
                        </motion.div>
                    </>
                )}
            </AnimatePresence>
        </div>
    );
}
