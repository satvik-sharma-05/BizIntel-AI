import axios from 'axios';
import toast from 'react-hot-toast';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
    baseURL: `${API_URL}/api`,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add token to requests if available
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Handle 401 errors
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('token');
            localStorage.removeItem('currentBusinessId');
            if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
                toast.error('Session expired. Please login again.');
                window.location.href = '/login';
            }
        }
        return Promise.reject(error);
    }
);

// Business APIs
export const businessAPI = {
    create: async (businessData) => {
        const response = await api.post('/business/create', {
            business_name: businessData.name,
            industry: businessData.industry,
            city: businessData.city,
            state: businessData.state,
            description: businessData.description,
            initial_investment: businessData.investment
        });
        // Transform response to match frontend naming
        const data = response.data;
        return {
            id: data.id,
            name: data.business_name,
            industry: data.industry,
            city: data.city,
            state: data.state,
            description: data.description,
            investment: data.initial_investment,
            created_at: data.created_at
        };
    },

    update: async (businessId, businessData) => {
        const response = await api.put(`/business/${businessId}`, {
            business_name: businessData.name,
            industry: businessData.industry,
            city: businessData.city,
            state: businessData.state,
            description: businessData.description,
            initial_investment: businessData.investment
        });
        const data = response.data;
        return {
            id: data.id,
            name: data.business_name,
            industry: data.industry,
            city: data.city,
            state: data.state,
            description: data.description,
            investment: data.initial_investment,
            created_at: data.created_at,
            updated_at: data.updated_at,
            message: data.message
        };
    },

    list: async () => {
        const response = await api.get('/business/list');
        // Transform response to match frontend naming
        return response.data.map(b => ({
            id: b.id,
            name: b.business_name,
            industry: b.industry,
            city: b.city,
            state: b.state,
            description: b.description,
            investment: b.initial_investment,
            created_at: b.created_at
        }));
    },

    get: async (businessId) => {
        const response = await api.get(`/business/${businessId}`);
        // Transform response to match frontend naming
        const data = response.data;
        return {
            id: data.id,
            name: data.business_name,
            industry: data.industry,
            city: data.city,
            state: data.state,
            description: data.description,
            investment: data.initial_investment,
            created_at: data.created_at
        };
    },

    delete: async (businessId) => {
        const response = await api.delete(`/business/${businessId}`);
        return response.data;
    },
};

// Chat APIs
export const chatAPI = {
    sendMessage: async (businessId, message, mode = 'full_intelligence') => {
        const response = await api.post('/chat', {
            business_id: businessId,
            message: message,
            mode: mode, // Add mode parameter
        });
        return response.data;
    },

    getHistory: async (businessId, limit = 10) => {
        const response = await api.get(`/chat/history/${businessId}?limit=${limit}`);
        return response.data;
    },

    clearHistory: async (businessId) => {
        const response = await api.delete(`/chat/clear/${businessId}`);
        return response.data;
    },

    analyzeBusiness: async (businessId) => {
        const response = await api.post(`/chat/analyze-business?business_id=${businessId}`);
        return response.data;
    },
};

// System APIs
export const systemAPI = {
    checkAPIs: async () => {
        const response = await api.get('/system/check-apis');
        return response.data;
    },

    health: async () => {
        const response = await api.get('/system/health');
        return response.data;
    },
};

// Dashboard APIs
export const dashboardAPI = {
    getDashboard: async (businessId) => {
        const response = await api.get(`/dashboard?business_id=${businessId}`);
        return response.data;
    },

    getGDP: async () => {
        const response = await api.get('/data/gdp');
        return response.data;
    },

    getMSME: async () => {
        const response = await api.get('/data/msme');
        return response.data;
    },

    getWeather: async (city) => {
        const response = await api.get(`/data/weather/${city}`);
        return response.data;
    },

    getNews: async (query = 'business india') => {
        const response = await api.get(`/data/news?query=${query}`);
        return response.data;
    },

    getIndustryNews: async (industry) => {
        const response = await api.get(`/data/industry-news/${industry}`);
        return response.data;
    },
};
