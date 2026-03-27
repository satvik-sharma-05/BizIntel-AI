import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import MainLayout from '../../../components/MainLayout';
import { businessAPI, api } from '../../../lib/api';
import toast from 'react-hot-toast';

export default function BusinessDocuments() {
    const router = useRouter();
    const { businessId } = router.query;
    const [business, setBusiness] = useState(null);
    const [documents, setDocuments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [uploading, setUploading] = useState(false);
    const [stats, setStats] = useState(null);
    const [selectedFile, setSelectedFile] = useState(null);

    useEffect(() => {
        if (businessId) {
            loadData();
        }
    }, [businessId]);

    const loadData = async () => {
        try {
            setLoading(true);
            const businessData = await businessAPI.get(businessId);
            setBusiness(businessData);

            await loadDocuments();
            await loadStats();
        } catch (error) {
            console.error('Error loading data:', error);
            if (error.response?.status === 404) {
                router.push('/select-business');
            }
        } finally {
            setLoading(false);
        }
    };

    const loadDocuments = async () => {
        try {
            const response = await api.get(`/documents/list/${businessId}`);
            setDocuments(response.data.documents || []);
        } catch (error) {
            console.error('Error loading documents:', error);
        }
    };

    const loadStats = async () => {
        try {
            const response = await api.get(`/documents/stats/${businessId}`);
            setStats(response.data);
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    };

    const handleFileSelect = (e) => {
        const file = e.target.files[0];
        if (file) {
            const ext = file.name.split('.').pop().toLowerCase();
            if (['pdf', 'docx', 'txt'].includes(ext)) {
                setSelectedFile(file);
            } else {
                toast.error('Only PDF, DOCX, and TXT files are supported');
            }
        }
    };

    const handleUpload = async () => {
        if (!selectedFile) return;

        try {
            setUploading(true);
            const formData = new FormData();
            formData.append('file', selectedFile);

            await api.post(`/documents/upload/${businessId}`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });

            toast.success('Document uploaded successfully!');
            setSelectedFile(null);
            loadDocuments();
            loadStats();
        } catch (error) {
            console.error('Upload error:', error);
            toast.error('Upload failed: ' + (error.response?.data?.detail || error.message));
        } finally {
            setUploading(false);
        }
    };

    const handleDelete = async (documentId) => {
        if (!confirm('Are you sure you want to delete this document?')) return;

        try {
            await api.delete(`/documents/delete/${documentId}`);
            toast.success('Document deleted successfully');
            loadDocuments();
            loadStats();
        } catch (error) {
            console.error('Delete error:', error);
            toast.error('Delete failed');
        }
    };

    const formatFileSize = (bytes) => {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString('en-IN', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    if (loading) {
        return (
            <MainLayout>
                <div className="flex items-center justify-center h-full">
                    <div className="flex flex-col items-center gap-4">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                        <div className="text-xl text-gray-600">Loading...</div>
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
            <div className="p-8">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">Document Management</h1>
                    <p className="text-gray-600">Upload documents for {business.name}</p>
                </div>

                {stats && (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                        <div className="bg-white p-6 rounded-lg shadow">
                            <div className="text-gray-600 text-sm mb-2">Total Documents</div>
                            <div className="text-3xl font-bold text-gray-900">{stats.document_count}</div>
                        </div>
                        <div className="bg-white p-6 rounded-lg shadow">
                            <div className="text-gray-600 text-sm mb-2">Total Chunks</div>
                            <div className="text-3xl font-bold text-gray-900">{stats.chunk_count}</div>
                        </div>
                        <div className="bg-white p-6 rounded-lg shadow">
                            <div className="text-gray-600 text-sm mb-2">Vector Store</div>
                            <div className="text-3xl font-bold text-gray-900">{stats.vector_store?.total_chunks || 0}</div>
                        </div>
                    </div>
                )}

                <div className="bg-white p-6 rounded-lg shadow mb-8">
                    <h2 className="text-xl font-bold text-gray-900 mb-4">Upload Document</h2>
                    <p className="text-gray-600 text-sm mb-4">
                        Supported formats: PDF, DOCX, TXT (Max 10MB)
                    </p>

                    <div className="flex items-center gap-4">
                        <input
                            type="file"
                            accept=".pdf,.docx,.txt"
                            onChange={handleFileSelect}
                            className="flex-1 bg-white text-gray-900 px-4 py-2 rounded border border-gray-300"
                        />
                        <button
                            onClick={handleUpload}
                            disabled={!selectedFile || uploading}
                            className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                        >
                            {uploading ? 'Uploading...' : 'Upload'}
                        </button>
                    </div>

                    {selectedFile && (
                        <div className="mt-4 text-sm text-gray-600">
                            Selected: {selectedFile.name} ({formatFileSize(selectedFile.size)})
                        </div>
                    )}
                </div>

                <div className="bg-white rounded-lg shadow">
                    <div className="p-6 border-b border-gray-200">
                        <h2 className="text-xl font-bold text-gray-900">Uploaded Documents</h2>
                    </div>

                    {documents.length === 0 ? (
                        <div className="p-8 text-center text-gray-600">
                            No documents uploaded yet. Upload your first document to get started.
                        </div>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead className="bg-gray-50">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Filename</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Size</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Chunks</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Uploaded</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-200">
                                    {documents.map((doc) => (
                                        <tr key={doc.document_id} className="hover:bg-gray-50">
                                            <td className="px-6 py-4 text-sm text-gray-900">{doc.filename}</td>
                                            <td className="px-6 py-4 text-sm text-gray-600">{doc.file_type.toUpperCase()}</td>
                                            <td className="px-6 py-4 text-sm text-gray-600">{formatFileSize(doc.file_size)}</td>
                                            <td className="px-6 py-4 text-sm text-gray-600">{doc.chunk_count}</td>
                                            <td className="px-6 py-4 text-sm text-gray-600">{formatDate(doc.upload_date)}</td>
                                            <td className="px-6 py-4 text-sm">
                                                <button
                                                    onClick={() => handleDelete(doc.document_id)}
                                                    className="text-red-600 hover:text-red-800"
                                                >
                                                    Delete
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>

                <div className="mt-8 bg-blue-50 p-6 rounded-lg border border-blue-200">
                    <h3 className="text-lg font-bold text-gray-900 mb-3">How to use RAG in Chat</h3>
                    <div className="text-gray-700 text-sm space-y-2">
                        <p>1. Upload your business documents (reports, plans, analysis)</p>
                        <p>2. Go to Chat page</p>
                        <p>3. Ask questions about your documents</p>
                        <p>4. AI will retrieve relevant information and provide answers with citations</p>
                    </div>
                </div>
            </div>
        </MainLayout>
    );
}
