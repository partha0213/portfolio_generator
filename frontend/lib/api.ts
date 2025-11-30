import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
    baseURL: API_URL,
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

                const { data } = await axios.post(`${API_URL}/api/auth/refresh`, {
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
    login: async (credentials: any) => {
        const { data } = await api.post('/api/auth/login', credentials);
        return data;
    },
    signup: async (userData: any) => {
        const { data } = await api.post('/api/auth/signup', userData);
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
    const { data } = await api.post('/api/generate/generate', {
        session_id: sessionId,
        stack,
        options,
        resume_data: resumeData,
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
