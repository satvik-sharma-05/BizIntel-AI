import { useBusiness } from '../contexts/BusinessContext';
import MainLayout from '../components/MainLayout';
import { User, Bell, Shield } from 'lucide-react';

export default function Settings() {
    const { currentBusiness } = useBusiness();

    return (
        <MainLayout>
            <div>
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
                    <p className="text-gray-600 mt-2">Manage your preferences</p>
                </div>

                <div className="space-y-6">
                    <div className="bg-white rounded-lg shadow p-6">
                        <div className="flex items-center space-x-3 mb-4">
                            <User className="w-6 h-6 text-blue-500" />
                            <h2 className="text-xl font-bold">Profile</h2>
                        </div>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Name</label>
                                <input
                                    type="text"
                                    defaultValue="Business User"
                                    className="w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                                <input
                                    type="email"
                                    defaultValue="user@bizintel.ai"
                                    className="w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                        </div>
                    </div>

                    <div className="bg-white rounded-lg shadow p-6">
                        <div className="flex items-center space-x-3 mb-4">
                            <Bell className="w-6 h-6 text-blue-500" />
                            <h2 className="text-xl font-bold">Notifications</h2>
                        </div>
                        <div className="space-y-3">
                            <label className="flex items-center space-x-3">
                                <input type="checkbox" defaultChecked className="w-4 h-4" />
                                <span>Email notifications</span>
                            </label>
                            <label className="flex items-center space-x-3">
                                <input type="checkbox" defaultChecked className="w-4 h-4" />
                                <span>Report generation alerts</span>
                            </label>
                        </div>
                    </div>

                    <div className="bg-white rounded-lg shadow p-6">
                        <div className="flex items-center space-x-3 mb-4">
                            <Shield className="w-6 h-6 text-blue-500" />
                            <h2 className="text-xl font-bold">Security</h2>
                        </div>
                        <button className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 transition">
                            Change Password
                        </button>
                    </div>
                </div>
            </div>
        </MainLayout>
    );
}
