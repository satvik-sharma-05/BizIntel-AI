import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import MainLayout from '../components/MainLayout';
import { Card, CardHeader, CardTitle, CardContent } from '../components/Card';
import { PageLoader, CardSkeleton, TableSkeleton } from '../components/LoadingState';
import { useBusiness } from '../contexts/BusinessContext';
import { api } from '../lib/api';
import {
    Upload,
    FileText,
    Trash2,
    Database,
    Layers,
    HardDrive,
    AlertCircle,
    CheckCircle,
    File
} from 'lucide-react';

export default function Documents() {
    const router = useRouter();
    const { currentBusiness, loading: businessLoading } = useBusiness();
    const [documents, setDocuments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [uploading, setUploading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState('');
    const [stats, setStats] = useState(null);
    const [selectedFile, setSelectedFile] = useState(null);

    useEffect(() => {
        // Redirect to business selection if no business after loading
        if (!businessLoading && !currentBusiness) {
            router.push('/select-business');
            return;
        }

        if (currentBusiness) {
            loadDocuments();
            loadStats();
        }
    }, [currentBusiness, businessLoading, router]);

    const loadDocuments = async () => {
        try {
            setLoading(true);
            const response = await api.get(`/documents/list/${currentBusiness.id}`);
            setDocuments(response.data.documents || []);
        } catch (error) {
            console.error('Error loading documents:', error);
        } finally {
            setLoading(false);
        }
    };

    const loadStats = async () => {
        try {
            const response = await api.get(`/documents/stats/${currentBusiness.id}`);
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
                toast.success(`Selected: ${file.name}`, {
                    icon: '📄',
                });
            } else {
                toast.error('Only PDF, DOCX, and TXT files are supported', {
                    icon: '⚠️',
                });
            }
        }
    };

    const pollDocumentStatus = async (documentId, uploadToast) => {
        const maxAttempts = 60; // Poll for up to 2 minutes
        let attempts = 0;

        const progressMessages = [
            '📄 Extracting text from document...',
            '✂️ Splitting into chunks...',
            '🧠 Generating embeddings...',
            '💾 Storing in vector database...',
            '✅ Finalizing...'
        ];

        const pollInterval = setInterval(async () => {
            attempts++;

            // Update progress message
            const messageIndex = Math.min(Math.floor(attempts / 10), progressMessages.length - 1);
            setUploadProgress(progressMessages[messageIndex]);

            try {
                const statusResponse = await api.get(`/documents/status/${documentId}`);
                const status = statusResponse.data.status;

                if (status === 'completed') {
                    clearInterval(pollInterval);
                    setUploadProgress('');
                    setUploading(false);

                    toast.success(
                        `✅ Document processed! ${statusResponse.data.chunk_count} chunks from ${statusResponse.data.total_pages} pages`,
                        {
                            id: uploadToast,
                            duration: 4000,
                        }
                    );

                    setSelectedFile(null);
                    loadDocuments();
                    loadStats();
                } else if (status === 'failed') {
                    clearInterval(pollInterval);
                    setUploadProgress('');
                    setUploading(false);

                    toast.error(
                        `❌ Processing failed: ${statusResponse.data.error || 'Unknown error'}`,
                        {
                            id: uploadToast,
                            duration: 5000,
                        }
                    );

                    setSelectedFile(null);
                    loadDocuments();
                } else if (attempts >= maxAttempts) {
                    clearInterval(pollInterval);
                    setUploadProgress('');
                    setUploading(false);

                    toast.error(
                        'Processing is taking longer than expected. Check back in a few minutes.',
                        {
                            id: uploadToast,
                            duration: 5000,
                        }
                    );

                    setSelectedFile(null);
                    loadDocuments();
                }
            } catch (error) {
                console.error('Status poll error:', error);
                // Continue polling even on error
            }
        }, 2000); // Poll every 2 seconds
    };

    const handleUpload = async () => {
        if (!selectedFile) return;

        const uploadToast = toast.loading('Uploading file...');

        try {
            setUploading(true);
            setUploadProgress('📤 Uploading file to server...');

            const formData = new FormData();
            formData.append('file', selectedFile);

            const response = await api.post(
                `/documents/upload/${currentBusiness.id}`,
                formData,
                {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                    },
                    timeout: 60000, // 60 seconds for file upload
                }
            );

            // Upload successful, now poll for processing status
            toast.success('File uploaded! Processing in background...', {
                id: uploadToast,
                duration: 2000,
            });

            // Start polling for status
            pollDocumentStatus(response.data.document_id, uploadToast);

        } catch (error) {
            console.error('Upload error:', error);
            setUploadProgress('');
            setUploading(false);

            let errorMessage = 'Upload failed. Please try again.';
            if (error.code === 'ECONNABORTED') {
                errorMessage = 'Upload timed out. Try a smaller file or try again later.';
            } else if (error.response?.data?.detail) {
                errorMessage = error.response.data.detail;
            }

            toast.error(errorMessage, {
                id: uploadToast,
                icon: '❌',
                duration: 5000,
            });
        }
    };

    const handleDelete = async (documentId, filename) => {
        const deleteToast = toast.loading(`Deleting ${filename}...`);

        try {
            await api.delete(`/documents/delete/${documentId}`);
            toast.success('Document deleted successfully', {
                id: deleteToast,
                icon: '🗑️',
            });
            loadDocuments();
            loadStats();
        } catch (error) {
            console.error('Delete error:', error);
            toast.error(error.response?.data?.detail || 'Delete failed. Please try again.', {
                id: deleteToast,
                icon: '❌',
            });
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

    if (businessLoading || loading) {
        return (
            <MainLayout>
                <PageLoader />
            </MainLayout>
        );
    }

    if (!currentBusiness) {
        return null;
    }

    return (
        <MainLayout>
            <div className="space-y-8">
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                >
                    <h1 className="text-3xl font-bold text-secondary-900">Document Management</h1>
                    <p className="text-secondary-600 mt-2">Upload documents for AI-powered analysis and insights</p>
                </motion.div>

                {/* Stats Cards */}
                {stats && (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.1 }}
                            className="bg-white rounded-xl border border-secondary-200 p-6 shadow-card hover:shadow-hover transition-shadow"
                        >
                            <div className="flex items-center gap-4">
                                <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl flex items-center justify-center">
                                    <FileText className="w-6 h-6 text-white" />
                                </div>
                                <div>
                                    <div className="text-sm font-medium text-secondary-600">Total Documents</div>
                                    <div className="text-3xl font-bold text-secondary-900">{stats.document_count}</div>
                                </div>
                            </div>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.2 }}
                            className="bg-white rounded-xl border border-secondary-200 p-6 shadow-card hover:shadow-hover transition-shadow"
                        >
                            <div className="flex items-center gap-4">
                                <div className="w-12 h-12 bg-gradient-to-br from-success-500 to-success-600 rounded-xl flex items-center justify-center">
                                    <Layers className="w-6 h-6 text-white" />
                                </div>
                                <div>
                                    <div className="text-sm font-medium text-secondary-600">Total Chunks</div>
                                    <div className="text-3xl font-bold text-secondary-900">{stats.chunk_count}</div>
                                </div>
                            </div>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.3 }}
                            className="bg-white rounded-xl border border-secondary-200 p-6 shadow-card hover:shadow-hover transition-shadow"
                        >
                            <div className="flex items-center gap-4">
                                <div className="w-12 h-12 bg-gradient-to-br from-info-500 to-info-600 rounded-xl flex items-center justify-center">
                                    <Database className="w-6 h-6 text-white" />
                                </div>
                                <div>
                                    <div className="text-sm font-medium text-secondary-600">Vector Store</div>
                                    <div className="text-3xl font-bold text-secondary-900">{stats.vector_store?.total_chunks || 0}</div>
                                </div>
                            </div>
                        </motion.div>
                    </div>
                )}

                {/* Upload Card */}
                <Card>
                    <CardHeader>
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center">
                                <Upload className="w-5 h-5 text-white" />
                            </div>
                            <div>
                                <CardTitle>Upload Document</CardTitle>
                                <p className="text-sm text-secondary-500 mt-1">
                                    Supported formats: PDF, DOCX, TXT (Max 10MB)
                                </p>
                            </div>
                        </div>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            <div className="flex items-center gap-4">
                                <label className="flex-1">
                                    <input
                                        type="file"
                                        accept=".pdf,.docx,.txt"
                                        onChange={handleFileSelect}
                                        className="block w-full text-sm text-secondary-600
                                            file:mr-4 file:py-2.5 file:px-4
                                            file:rounded-lg file:border-0
                                            file:text-sm file:font-medium
                                            file:bg-primary-50 file:text-primary-700
                                            hover:file:bg-primary-100
                                            file:cursor-pointer cursor-pointer
                                            border border-secondary-300 rounded-lg
                                            focus:outline-none focus:ring-2 focus:ring-primary-500"
                                    />
                                </label>
                                <motion.button
                                    whileHover={{ scale: 1.02 }}
                                    whileTap={{ scale: 0.98 }}
                                    onClick={handleUpload}
                                    disabled={!selectedFile || uploading}
                                    className="px-6 py-2.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:bg-secondary-300 disabled:cursor-not-allowed transition-colors font-medium shadow-sm flex items-center gap-2"
                                >
                                    {uploading ? (
                                        <>
                                            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                                            Uploading...
                                        </>
                                    ) : (
                                        <>
                                            <Upload className="w-4 h-4" />
                                            Upload
                                        </>
                                    )}
                                </motion.button>
                            </div>

                            {selectedFile && (
                                <motion.div
                                    initial={{ opacity: 0, y: -10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="flex items-center gap-3 p-4 bg-primary-50 border border-primary-200 rounded-lg"
                                >
                                    <File className="w-5 h-5 text-primary-600" />
                                    <div className="flex-1">
                                        <div className="text-sm font-medium text-secondary-900">{selectedFile.name}</div>
                                        <div className="text-xs text-secondary-500">{formatFileSize(selectedFile.size)}</div>
                                    </div>
                                    <CheckCircle className="w-5 h-5 text-success-600" />
                                </motion.div>
                            )}

                            {uploading && uploadProgress && (
                                <motion.div
                                    initial={{ opacity: 0, y: -10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="flex items-center gap-3 p-4 bg-info-50 border border-info-200 rounded-lg"
                                >
                                    <div className="w-5 h-5 border-2 border-info-600 border-t-transparent rounded-full animate-spin"></div>
                                    <div className="flex-1">
                                        <div className="text-sm font-medium text-info-900">{uploadProgress}</div>
                                        <div className="text-xs text-info-600">Please wait, this may take a moment...</div>
                                    </div>
                                </motion.div>
                            )}
                        </div>
                    </CardContent>
                </Card>

                {/* Documents Table */}
                <Card>
                    <CardHeader>
                        <CardTitle>Uploaded Documents</CardTitle>
                    </CardHeader>

                    {loading ? (
                        <div className="p-6">
                            <TableSkeleton rows={3} />
                        </div>
                    ) : documents.length === 0 ? (
                        <CardContent>
                            <div className="text-center py-12">
                                <div className="w-16 h-16 bg-secondary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                                    <FileText className="w-8 h-8 text-secondary-400" />
                                </div>
                                <p className="text-secondary-600 mb-2">No documents uploaded yet</p>
                                <p className="text-sm text-secondary-500">Upload your first document to get started with AI analysis</p>
                            </div>
                        </CardContent>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead className="bg-secondary-50 border-y border-secondary-200">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-xs font-semibold text-secondary-600 uppercase tracking-wider">Filename</th>
                                        <th className="px-6 py-3 text-left text-xs font-semibold text-secondary-600 uppercase tracking-wider">Type</th>
                                        <th className="px-6 py-3 text-left text-xs font-semibold text-secondary-600 uppercase tracking-wider">Size</th>
                                        <th className="px-6 py-3 text-left text-xs font-semibold text-secondary-600 uppercase tracking-wider">Status</th>
                                        <th className="px-6 py-3 text-left text-xs font-semibold text-secondary-600 uppercase tracking-wider">Pages</th>
                                        <th className="px-6 py-3 text-left text-xs font-semibold text-secondary-600 uppercase tracking-wider">Chunks</th>
                                        <th className="px-6 py-3 text-left text-xs font-semibold text-secondary-600 uppercase tracking-wider">Uploaded</th>
                                        <th className="px-6 py-3 text-left text-xs font-semibold text-secondary-600 uppercase tracking-wider">Actions</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-secondary-200">
                                    {documents.map((doc, index) => (
                                        <motion.tr
                                            key={doc.document_id}
                                            initial={{ opacity: 0, y: 10 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            transition={{ delay: index * 0.05 }}
                                            className="hover:bg-secondary-50 transition-colors"
                                        >
                                            <td className="px-6 py-4">
                                                <div className="flex items-center gap-3">
                                                    <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
                                                        <FileText className="w-4 h-4 text-primary-600" />
                                                    </div>
                                                    <span className="text-sm font-medium text-secondary-900">{doc.filename}</span>
                                                </div>
                                            </td>
                                            <td className="px-6 py-4">
                                                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-secondary-100 text-secondary-700">
                                                    {doc.file_type.toUpperCase()}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 text-sm text-secondary-600">{formatFileSize(doc.file_size)}</td>
                                            <td className="px-6 py-4">
                                                {doc.status === 'processing' ? (
                                                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-info-100 text-info-700">
                                                        <div className="w-2 h-2 bg-info-600 rounded-full animate-pulse mr-1.5"></div>
                                                        Processing
                                                    </span>
                                                ) : doc.status === 'failed' ? (
                                                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-danger-100 text-danger-700">
                                                        Failed
                                                    </span>
                                                ) : (
                                                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-success-100 text-success-700">
                                                        Ready
                                                    </span>
                                                )}
                                            </td>
                                            <td className="px-6 py-4 text-sm text-secondary-600">{doc.total_pages}</td>
                                            <td className="px-6 py-4 text-sm text-secondary-600">{doc.chunk_count}</td>
                                            <td className="px-6 py-4 text-sm text-secondary-600">{formatDate(doc.upload_date)}</td>
                                            <td className="px-6 py-4">
                                                <motion.button
                                                    whileHover={{ scale: 1.1 }}
                                                    whileTap={{ scale: 0.9 }}
                                                    onClick={() => handleDelete(doc.document_id, doc.filename)}
                                                    className="p-2 text-danger-600 hover:bg-danger-50 rounded-lg transition-colors"
                                                    title="Delete document"
                                                >
                                                    <Trash2 className="w-4 h-4" />
                                                </motion.button>
                                            </td>
                                        </motion.tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </Card>

                {/* How to Use Card */}
                <Card>
                    <CardHeader>
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-gradient-to-br from-info-500 to-info-600 rounded-lg flex items-center justify-center">
                                <AlertCircle className="w-5 h-5 text-white" />
                            </div>
                            <CardTitle>How to use RAG in Chat</CardTitle>
                        </div>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-3">
                            {[
                                'Upload your business documents (reports, plans, analysis)',
                                'Go to Chat page',
                                'Ask questions about your documents',
                                'AI will retrieve relevant information and provide answers with citations'
                            ].map((step, index) => (
                                <motion.div
                                    key={index}
                                    initial={{ opacity: 0, x: -10 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: index * 0.1 }}
                                    className="flex items-start gap-3"
                                >
                                    <div className="w-6 h-6 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center flex-shrink-0 text-sm font-semibold">
                                        {index + 1}
                                    </div>
                                    <p className="text-sm text-secondary-700 pt-0.5">{step}</p>
                                </motion.div>
                            ))}

                            <div className="mt-6 p-4 bg-secondary-50 rounded-lg border border-secondary-200">
                                <p className="text-xs font-semibold text-secondary-700 mb-2">Example questions:</p>
                                <div className="space-y-1">
                                    {[
                                        '"What does the report say about market demand?"',
                                        '"Summarize the business plan"',
                                        '"Find information about competitors"'
                                    ].map((example, index) => (
                                        <p key={index} className="text-xs text-secondary-600">• {example}</p>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </MainLayout>
    );
}
