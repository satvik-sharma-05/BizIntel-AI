import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { useBusiness } from '../contexts/BusinessContext';

export default function ChatRedirect() {
    const router = useRouter();
    const { currentBusiness, loading } = useBusiness();

    useEffect(() => {
        if (!loading) {
            if (currentBusiness) {
                router.replace(`/business/${currentBusiness.id}/chat`);
            } else {
                router.replace('/select-business');
            }
        }
    }, [currentBusiness, loading, router]);

    return (
        <div className="flex items-center justify-center h-screen bg-gray-50">
            <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-gray-600">Redirecting to chat...</p>
            </div>
        </div>
    );
}
