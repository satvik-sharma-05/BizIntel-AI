import { useState } from 'react';
import { useBusiness } from '../contexts/BusinessContext';
import { useRouter } from 'next/router';
import { Plus, Building2, TrendingUp, MapPin, Calendar, Trash2 } from 'lucide-react';
import toast from 'react-hot-toast';

export default function SelectBusiness() {
    const { businesses, loading, switchBusiness, createBusiness, deleteBusiness } = useBusiness();
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [deleteConfirm, setDeleteConfirm] = useState(null);
    const router = useRouter();

    const handleSelectBusiness = (business) => {
        switchBusiness(business);
        // Redirect to business-scoped overview
        router.push(`/business/${business.id}/overview`);
    };

    const handleDeleteBusiness = async (businessId, businessName) => {
        if (deleteConfirm !== businessId) {
            setDeleteConfirm(businessId);
            toast('Click delete again to confirm', { icon: '⚠️' });
            setTimeout(() => setDeleteConfirm(null), 3000);
            return;
        }

        try {
            await deleteBusiness(businessId);
            setDeleteConfirm(null);
        } catch (error) {
            console.error('Error deleting business:', error);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center">
                <div className="text-xl text-gray-600">Loading businesses...</div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
            <div className="max-w-7xl mx-auto px-4 py-12">
                {/* Header */}
                <div className="text-center mb-12">
                    <h1 className="text-5xl font-bold text-gray-900 mb-4">
                        BizIntel <span className="text-blue-600">AI</span>
                    </h1>
                    <p className="text-xl text-gray-600">
                        Select a business or create a new one
                    </p>
                </div>

                {/* Business Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                    {/* Create New Business Card */}
                    <button
                        onClick={() => setShowCreateModal(true)}
                        className="bg-white rounded-xl shadow-lg p-8 border-2 border-dashed border-blue-300 hover:border-blue-500 hover:shadow-xl transition-all duration-200 flex flex-col items-center justify-center min-h-[280px] group"
                    >
                        <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4 group-hover:bg-blue-200 transition">
                            <Plus className="w-8 h-8 text-blue-600" />
                        </div>
                        <h3 className="text-xl font-semibold text-gray-900 mb-2">
                            Create New Business
                        </h3>
                        <p className="text-gray-600 text-center">
                            Start analyzing a new business opportunity
                        </p>
                    </button>

                    {/* Existing Business Cards */}
                    {businesses.map((business) => (
                        <div
                            key={business.id}
                            className="bg-white rounded-xl shadow-lg p-8 hover:shadow-2xl transition-all duration-200 text-left group border-2 border-transparent hover:border-blue-500 relative"
                        >
                            {/* Delete Button */}
                            <button
                                onClick={(e) => {
                                    e.stopPropagation();
                                    handleDeleteBusiness(business.id, business.name);
                                }}
                                className={`absolute top-4 right-4 p-2 rounded-lg transition ${deleteConfirm === business.id
                                    ? 'bg-red-500 text-white'
                                    : 'bg-gray-100 text-gray-600 hover:bg-red-100 hover:text-red-600'
                                    }`}
                                title={deleteConfirm === business.id ? 'Click again to confirm' : 'Delete business'}
                            >
                                <Trash2 className="w-4 h-4" />
                            </button>

                            <button
                                onClick={() => handleSelectBusiness(business)}
                                className="w-full text-left"
                            >
                                <div className="flex items-start justify-between mb-4 pr-8">
                                    <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                                        <Building2 className="w-6 h-6 text-white" />
                                    </div>
                                    <span className="text-xs bg-blue-100 text-blue-700 px-3 py-1 rounded-full">
                                        {business.industry}
                                    </span>
                                </div>

                                <h3 className="text-xl font-bold text-gray-900 mb-2 group-hover:text-blue-600 transition">
                                    {business.name}
                                </h3>

                                <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                                    {business.description || 'No description provided'}
                                </p>

                                <div className="space-y-2">
                                    <div className="flex items-center text-sm text-gray-500">
                                        <MapPin className="w-4 h-4 mr-2" />
                                        {business.city}, {business.state}
                                    </div>
                                    <div className="flex items-center text-sm text-gray-500">
                                        <TrendingUp className="w-4 h-4 mr-2" />
                                        ₹{business.investment?.toLocaleString()} investment
                                    </div>
                                    <div className="flex items-center text-sm text-gray-500">
                                        <Calendar className="w-4 h-4 mr-2" />
                                        Created {new Date(business.created_at).toLocaleDateString()}
                                    </div>
                                </div>
                            </button>
                        </div>
                    ))}
                </div>

                {businesses.length === 0 && (
                    <div className="text-center py-12">
                        <p className="text-gray-600 mb-4">No businesses yet. Create your first one!</p>
                    </div>
                )}
            </div>

            {/* Create Business Modal */}
            {showCreateModal && (
                <CreateBusinessModal
                    onClose={() => setShowCreateModal(false)}
                    onCreate={createBusiness}
                />
            )}
        </div>
    );
}

function CreateBusinessModal({ onClose, onCreate }) {
    const router = useRouter();
    const [formData, setFormData] = useState({
        name: '',
        industry: '',
        city: '',
        state: '',
        description: '',
        investment: '',
    });
    const [loading, setLoading] = useState(false);

    const industries = [
        'Retail', 'Food & Beverage', 'Technology', 'Healthcare',
        'Education', 'Manufacturing', 'Real Estate', 'Services',
        'E-commerce', 'Agriculture', 'Tourism', 'Other'
    ];

    const handleSubmit = async (e) => {
        e.preventDefault();

        // Validate investment
        const investmentAmount = parseFloat(formData.investment);
        if (isNaN(investmentAmount) || investmentAmount <= 0) {
            toast.error('Please enter a valid investment amount');
            return;
        }

        setLoading(true);

        try {
            await onCreate({
                name: formData.name,
                industry: formData.industry,
                city: formData.city,
                state: formData.state,
                description: formData.description,
                investment: investmentAmount,
            });
            onClose();
            // Note: onCreate already handles navigation via switchBusiness
        } catch (error) {
            console.error('Error creating business:', error);
            // Error toast is already shown by BusinessContext
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
                <div className="p-8">
                    <h2 className="text-3xl font-bold text-gray-900 mb-6">
                        Create New Business
                    </h2>

                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Business Name *
                            </label>
                            <input
                                type="text"
                                required
                                value={formData.name}
                                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                placeholder="e.g., Cafe Delight"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Industry *
                            </label>
                            <select
                                required
                                value={formData.industry}
                                onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
                                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            >
                                <option value="">Select industry</option>
                                {industries.map((ind) => (
                                    <option key={ind} value={ind}>{ind}</option>
                                ))}
                            </select>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    City *
                                </label>
                                <input
                                    type="text"
                                    required
                                    value={formData.city}
                                    onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                    placeholder="e.g., Mumbai"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    State *
                                </label>
                                <input
                                    type="text"
                                    required
                                    value={formData.state}
                                    onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                    placeholder="e.g., Maharashtra"
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Initial Investment (₹) *
                            </label>
                            <input
                                type="number"
                                required
                                min="0"
                                step="1000"
                                value={formData.investment}
                                onChange={(e) => setFormData({ ...formData, investment: e.target.value })}
                                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                placeholder="e.g., 500000"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Description
                            </label>
                            <textarea
                                value={formData.description}
                                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                rows={4}
                                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                placeholder="Describe your business idea..."
                            />
                        </div>

                        <div className="flex gap-4 pt-4">
                            <button
                                type="button"
                                onClick={onClose}
                                disabled={loading}
                                className="flex-1 px-6 py-3 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50 transition disabled:opacity-50"
                            >
                                Cancel
                            </button>
                            <button
                                type="submit"
                                disabled={loading}
                                className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 transition disabled:opacity-50"
                            >
                                {loading ? 'Creating...' : 'Create Business'}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
}
