import '../styles/globals.css';
import { AuthProvider } from '../contexts/AuthContext';
import { BusinessProvider } from '../contexts/BusinessContext';
import { Toaster } from 'react-hot-toast';

export default function App({ Component, pageProps }) {
    return (
        <AuthProvider>
            <BusinessProvider>
                <Toaster
                    position="top-right"
                    toastOptions={{
                        duration: 4000,
                        style: {
                            background: '#ffffff',
                            color: '#0f172a',
                            border: '1px solid #e2e8f0',
                            borderRadius: '0.75rem',
                            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.08)',
                            padding: '12px 16px',
                        },
                        success: {
                            duration: 3000,
                            iconTheme: {
                                primary: '#16a34a',
                                secondary: '#ffffff',
                            },
                            style: {
                                background: '#f0fdf4',
                                color: '#15803d',
                                border: '1px solid #bbf7d0',
                            },
                        },
                        error: {
                            duration: 4000,
                            iconTheme: {
                                primary: '#dc2626',
                                secondary: '#ffffff',
                            },
                            style: {
                                background: '#fef2f2',
                                color: '#b91c1c',
                                border: '1px solid #fecaca',
                            },
                        },
                        loading: {
                            iconTheme: {
                                primary: '#2563eb',
                                secondary: '#ffffff',
                            },
                            style: {
                                background: '#eff6ff',
                                color: '#1d4ed8',
                                border: '1px solid #bfdbfe',
                            },
                        },
                    }}
                />
                <Component {...pageProps} />
            </BusinessProvider>
        </AuthProvider>
    );
}
