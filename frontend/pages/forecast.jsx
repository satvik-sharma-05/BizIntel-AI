import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { useBusiness } from '../contexts/BusinessContext';

export default function ForecastRedirect() {
    const router = useRouter();
    const { currentBusiness } = useBusiness();

    useEffect(() => {
        if (currentBusiness?.id) {
            router.replace(`/business/${currentBusiness.id}/forecast`);
        } else {
            router.replace('/select-business');
        }
    }, [currentBusiness, router]);

    return (
        <div className="flex items-center justify-center h-screen bg-gray-50">
            <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                <p className="mt-4 text-gray-600">Redirecting to Forecasting...</p>
            </div>
        </div>
    );
}
