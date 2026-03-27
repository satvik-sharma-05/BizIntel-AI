import { createContext, useContext, useState, useEffect } from 'react';
import { businessAPI } from '../lib/api';
import toast from 'react-hot-toast';
import { useAuth } from './AuthContext';

const BusinessContext = createContext();

export function BusinessProvider({ children }) {
    const { user } = useAuth();
    const [businesses, setBusinesses] = useState([]);
    const [currentBusiness, setCurrentBusiness] = useState(null);
    const [loading, setLoading] = useState(true);
    const [initialized, setInitialized] = useState(false);
    const [lastUserId, setLastUserId] = useState(null);

    // Reset business context when user changes
    useEffect(() => {
        const currentUserId = user?.user_id;

        if (currentUserId !== lastUserId) {
            // User changed (login/logout/switch account)
            setBusinesses([]);
            setCurrentBusiness(null);
            setInitialized(false);
            localStorage.removeItem('currentBusinessId');
            setLastUserId(currentUserId);

            if (currentUserId) {
                // New user logged in, load their businesses
                loadBusinesses();
                setInitialized(true);
            } else {
                // User logged out
                setLoading(false);
            }
        }
    }, [user?.user_id, lastUserId]);

    useEffect(() => {
        // Only load businesses if user has a token and not already initialized
        const token = localStorage.getItem('token');
        if (token && !initialized && user) {
            loadBusinesses();
            setInitialized(true);
        } else if (!token) {
            // Clear business context when no token
            setBusinesses([]);
            setCurrentBusiness(null);
            setLoading(false);
        }
    }, [initialized, user]);

    const loadBusinesses = async () => {
        try {
            const data = await businessAPI.list();
            setBusinesses(data);

            // Load saved business from localStorage ONLY if it belongs to current user
            const savedBusinessId = localStorage.getItem('currentBusinessId');
            const savedBusiness = savedBusinessId ? data.find(b => b.id === parseInt(savedBusinessId)) : null;

            if (savedBusiness) {
                // Saved business exists and belongs to current user
                setCurrentBusiness(savedBusiness);
            } else {
                // Clear invalid saved business ID and use first business
                localStorage.removeItem('currentBusinessId');

                if (data.length > 0) {
                    setCurrentBusiness(data[0]);
                    localStorage.setItem('currentBusinessId', data[0].id.toString());
                } else {
                    // No businesses for this user
                    setCurrentBusiness(null);
                }
            }
        } catch (error) {
            console.error('Error loading businesses:', error);
            // Only show error if it's not a 401 (unauthorized) or 403 (forbidden)
            if (error.response?.status !== 401 && error.response?.status !== 403) {
                toast.error('Failed to load businesses');
            }
        } finally {
            setLoading(false);
        }
    };

    const switchBusiness = (business) => {
        setCurrentBusiness(business);
        localStorage.setItem('currentBusinessId', business.id.toString());
        toast.success(`Switched to ${business.name}`);
    };

    const createBusiness = async (businessData) => {
        try {
            const newBusiness = await businessAPI.create(businessData);
            setBusinesses([...businesses, newBusiness]);
            switchBusiness(newBusiness);
            toast.success('Business created successfully! 🎉');
            return newBusiness;
        } catch (error) {
            console.error('Error creating business:', error);
            toast.error('Failed to create business');
            throw error;
        }
    };

    const deleteBusiness = async (businessId) => {
        try {
            await businessAPI.delete(businessId);
            const updatedBusinesses = businesses.filter(b => b.id !== businessId);
            setBusinesses(updatedBusinesses);

            if (currentBusiness?.id === businessId) {
                setCurrentBusiness(updatedBusinesses[0] || null);
                if (updatedBusinesses[0]) {
                    localStorage.setItem('currentBusinessId', updatedBusinesses[0].id.toString());
                } else {
                    localStorage.removeItem('currentBusinessId');
                }
            }

            toast.success('Business deleted successfully');
        } catch (error) {
            console.error('Error deleting business:', error);
            toast.error('Failed to delete business');
            throw error;
        }
    };

    const clearBusinessContext = () => {
        setBusinesses([]);
        setCurrentBusiness(null);
        setInitialized(false);
        localStorage.removeItem('currentBusinessId');
    };

    return (
        <BusinessContext.Provider
            value={{
                businesses,
                currentBusiness,
                loading,
                switchBusiness,
                createBusiness,
                deleteBusiness,
                refreshBusinesses: loadBusinesses,
                clearBusinessContext,
            }}
        >
            {children}
        </BusinessContext.Provider>
    );
}

export function useBusiness() {
    const context = useContext(BusinessContext);
    if (!context) {
        throw new Error('useBusiness must be used within BusinessProvider');
    }
    return context;
}
