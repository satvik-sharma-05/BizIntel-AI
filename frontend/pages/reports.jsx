import { useBusiness } from '../contexts/BusinessContext';
import MainLayout from '../components/MainLayout';
import { FileText, Download } from 'lucide-react';

export default function Reports() {
    const { currentBusiness } = useBusiness();

    const reports = [
        {
            id: 1,
            title: 'Grocery Store Analysis - Delhi',
            date: '2026-03-25',
            type: 'Market Analysis',
        },
        {
            id: 2,
            title: 'Restaurant Business Plan - Mumbai',
            date: '2026-03-24',
            type: 'Business Plan',
        },
    ];

    return (
        <MainLayout>
            <div>
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900">Reports</h1>
                    <p className="text-gray-600 mt-2">Generated business intelligence reports</p>
                </div>

                <div className="bg-white rounded-lg shadow">
                    <div className="p-6 border-b">
                        <h2 className="text-xl font-bold">Recent Reports</h2>
                    </div>
                    <div className="divide-y">
                        {reports.map((report) => (
                            <div key={report.id} className="p-6 hover:bg-gray-50 transition">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-start space-x-4">
                                        <div className="bg-blue-100 p-3 rounded-lg">
                                            <FileText className="w-6 h-6 text-blue-600" />
                                        </div>
                                        <div>
                                            <h3 className="font-semibold text-lg">{report.title}</h3>
                                            <p className="text-sm text-gray-600 mt-1">{report.date} • {report.type}</p>
                                        </div>
                                    </div>
                                    <button className="flex items-center space-x-2 bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition">
                                        <Download className="w-4 h-4" />
                                        <span>Download</span>
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </MainLayout>
    );
}
