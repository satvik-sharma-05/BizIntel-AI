import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import MainLayout from '../../../components/MainLayout';
import { businessAPI } from '../../../lib/api';
import { Save, AlertCircle, CheckCircle, Trash2 } from 'lucide-react';
import toast from 'react-hot-toast';

export default function BusinessSettings() {
    const router = useRouter();
    const { businessId } = router.query;
    const [business, setBusiness] = useState(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
    const [formData, setFormData] = useState({
        name: '',
        industry: '',
        city: '',
        state: '',
        investment: '',
        description: ''
    });
    const [hasChanges, setHasChanges] = useState(false);

    useEffect(() => {
        if (businessId) {
            loadBusiness();
        }
    }, [businessId]);

    const loadBusiness = async () => {
        try {
            const data = await businessAPI.get(businessId);
            setBusiness(data);
            setFormData({
                name: data.name,
                industry: data.industry,
                city: data.city,
                state: data.state,
                investment: data.investment.toString(),
                description: data.description || ''
            });
            setLoading(false);
        } catch (error) {
            console.error('Error loading business:', error);
            toast.error('Failed to load business');
            router.push('/select-business');
        }
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
        setHasChanges(true);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSaving(true);

        try {
            const result = await businessAPI.update(businessId, {
                name: formData.name,
                industry: formData.industry,
                city: formData.city,
                state: formData.state,
                investment: parseFloat(formData.investment),
                description: formData.description
            });

            setBusiness(result);
            setHasChanges(false);
            toast.success(result.message || 'Business updated successfully!');

            // Reload business data
            await loadBusiness();
        } catch (error) {
            console.error('Error updating business:', error);
            toast.error('Failed to update business');
        } finally {
            setSaving(false);
        }
    };

    const handleDelete = async () => {
        try {
            await businessAPI.delete(businessId);
            toast.success('Business deleted successfully');
            router.push('/select-business');
        } catch (error) {
            console.error('Error deleting business:', error);
            toast.error('Failed to delete business');
        }
    };

    if (loading) {
        return (
            <MainLayout>
                <div className="flex items-center justify-center h-full">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                </div>
            </MainLayout>
        );
    }

    return (
        <MainLayout>
            <div className="max-w-4xl mx-auto">
                <div className="mb-6">
                    <h1 className="text-3xl font-bold text-gray-900">Business Settings</h1>
                    <p className="text-gray-600 mt-2">
                        Update your business details. Changes will trigger re-analysis of market data.
                    </p>
                </div>

                {hasChanges && (
                    <div className="mb-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-start gap-3">
                        <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                        <div>
                            <p className="text-sm font-medium text-yellow-800">Unsaved Changes</p>
                            <p className="text-sm text-yellow-700 mt-1">
                                You have unsaved changes. Click "Save Changes" to update your business.
                            </p>
                        </div>
                    </div>
                )}

                <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-6 space-y-6">
                    {/* Business Name */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Business Name *
                        </label>
                        <input
                            type="text"
                            name="name"
                            value={formData.name}
                            onChange={handleChange}
                            required
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            placeholder="Enter business name"
                        />
                    </div>

                    {/* Industry */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Industry *
                        </label>
                        <select
                            name="industry"
                            value={formData.industry}
                            onChange={handleChange}
                            required
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        >
                            <option value="">Select Industry</option>
                            <option value="Retail">Retail</option>
                            <option value="Food & Beverage">Food & Beverage</option>
                            <option value="Technology">Technology</option>
                            <option value="Healthcare">Healthcare</option>
                            <option value="Education">Education</option>
                            <option value="Manufacturing">Manufacturing</option>
                            <option value="Services">Services</option>
                            <option value="E-commerce">E-commerce</option>
                            <option value="Gaming">Gaming</option>
                            <option value="Entertainment">Entertainment</option>
                            <option value="Real Estate">Real Estate</option>
                            <option value="Agriculture">Agriculture</option>
                            <option value="Other">Other</option>
                        </select>
                    </div>

                    {/* Location */}
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                City *
                            </label>
                            <input
                                type="text"
                                name="city"
                                value={formData.city}
                                onChange={handleChange}
                                required
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                placeholder="Enter city"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                State *
                            </label>
                            <input
                                type="text"
                                name="state"
                                value={formData.state}
                                onChange={handleChange}
                                required
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                placeholder="Enter state"
                            />
                        </div>
                    </div>

                    {/* Investment */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Initial Investment (₹) *
                        </label>
                        <input
                            type="number"
                            name="investment"
                            value={formData.investment}
                            onChange={handleChange}
                            required
                            min="0"
                            step="1000"
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            placeholder="Enter investment amount"
                        />
                    </div>

                    {/* Description */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Description
                        </label>
                        <textarea
                            name="description"
                            value={formData.description}
                            onChange={handleChange}
                            rows="4"
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            placeholder="Describe your business..."
                        />
                    </div>

                    {/* Info Box */}
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start gap-3">
                        <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                        <div>
                            <p className="text-sm font-medium text-blue-800">Re-analysis Trigger</p>
                            <p className="text-sm text-blue-700 mt-1">
                                Changing city, state, or industry will clear existing analysis data and trigger
                                re-analysis on your next visit to Market Analysis, Location Intelligence, or Forecasting pages.
                            </p>
                        </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex items-center justify-between pt-4 border-t">
                        <button
                            type="button"
                            onClick={() => setShowDeleteConfirm(true)}
                            className="flex items-center gap-2 px-4 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition"
                        >
                            <Trash2 className="w-4 h-4" />
                            Delete Business
                        </button>

                        <div className="flex gap-3">
                            <button
                                type="button"
                                onClick={() => router.back()}
                                className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
                            >
                                Cancel
                            </button>
                            <button
                                type="submit"
                                disabled={!hasChanges || saving}
                                className="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition"
                            >
                                {saving ? (
                                    <>
                                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                                        Saving...
                                    </>
                                ) : (
                                    <>
                                        <Save className="w-4 h-4" />
                                        Save Changes
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                </form>

                {/* Delete Confirmation Modal */}
                {showDeleteConfirm && (
                    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                        <div className="bg-white rounded-xl p-6 max-w-md w-full mx-4 shadow-2xl">
                            <h3 className="text-xl font-bold text-gray-900 mb-2">Delete Business?</h3>
                            <p className="text-gray-600 mb-6">
                                This will permanently delete <strong>{business.name}</strong> and all associated data
                                including conversations, documents, and analysis. This action cannot be undone.
                            </p>
                            <div className="flex gap-3 justify-end">
                                <button
                                    onClick={() => setShowDeleteConfirm(false)}
                                    className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={handleDelete}
                                    className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
                                >
                                    Delete Business
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </MainLayout>
    );
}
