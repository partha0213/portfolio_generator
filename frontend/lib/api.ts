import axios from 'axios';

// API base URL - points to the FastAPI backend
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
    baseURL: API_URL,  // Points to backend API (localhost:8000 by default)
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to add token
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Response interceptor to handle refresh token
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                const refreshToken = localStorage.getItem('refreshToken');
                if (!refreshToken) throw new Error('No refresh token');

                // ✅ FIX: Changed from '/auth/refresh' to '/api/auth/refresh'
                const { data } = await axios.post('/api/auth/refresh', {
                    refresh_token: refreshToken
                });

                localStorage.setItem('accessToken', data.access_token);
                localStorage.setItem('refreshToken', data.refresh_token);

                originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
                return api(originalRequest);
            } catch (refreshError) {
                // Logout if refresh fails
                localStorage.removeItem('accessToken');
                localStorage.removeItem('refreshToken');
                localStorage.removeItem('user');
                window.location.href = '/auth/login';
                return Promise.reject(refreshError);
            }
        }
        return Promise.reject(error);
    }
);

export const auth = {
    login: async (credentials: { email: string; password: string }) => {
        const { data } = await api.post('/api/auth/login', credentials);
        return data;
    },
    signup: async (userData: { email: string; password: string; full_name: string }) => {
        const { data } = await api.post('/api/auth/signup', {
            email: userData.email,
            password: userData.password,
            full_name: userData.full_name,
        });
        return data;
    },
    verifyEmail: async (email: string, verificationCode: string) => {
        const { data } = await api.post('/api/auth/verify-email', {
            email,
            verification_code: verificationCode,
        });
        return data;
    },
    resendVerification: async (email: string) => {
        const { data } = await api.post('/api/auth/resend-verification', null, {
            params: { email }
        });
        return data;
    },
    getHistory: async () => {
        const { data } = await api.get('/api/history/');
        return data;
    }
};

export const uploadResume = async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    const { data } = await api.post('/api/resume/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    });

    return data;
};

export const generatePortfolio = async (sessionId: string, stack: string, options: any = {}, resumeData: any = null) => {
    const { data } = await api.post('/api/generate/lovable', {
        session_id: sessionId,
        prompt: options.prompt || "Create a modern, professional portfolio",
        resume_data: resumeData,
        framework: stack || "nextjs",
    });

    return data;
};

export const sendChatMessage = async (
    messages: any[],
    sessionId: string,
    currentFiles?: Record<string, string>
) => {
    const { data } = await api.post('/api/chat', {
        messages,
        session_id: sessionId,
        current_files: currentFiles,
    });

    return data;
};

export const getChatHistory = async (sessionId: string) => {
    const { data } = await api.get(`/api/chat/${sessionId}/history`);
    return data;
};

export const initChat = async (sessionId: string) => {
    const { data } = await api.post(`/api/chat/${sessionId}/init`);
    return data;
};
