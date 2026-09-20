import axios from 'axios';

const API_BASE_URL = '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: Attach JWT Bearer and X-Access-Purpose header
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('sphinx_access_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }

    const userStr = localStorage.getItem('sphinx_user');
    let defaultPurpose = 'TREATMENT';
    if (userStr) {
      try {
        const u = JSON.parse(userStr);
        if (u.role === 'ADMIN' || u.role === 'RECEPTIONIST') {
          defaultPurpose = 'ADMINISTRATIVE';
        } else if (u.role === 'INSURANCE_OFFICER') {
          defaultPurpose = 'BILLING';
        }
      } catch (e) {}
    }

    const purpose = localStorage.getItem('sphinx_access_purpose') || defaultPurpose;
    if (purpose) {
      config.headers['X-Access-Purpose'] = purpose;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Auto refresh token on 401 Unauthorized
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (originalRequest.url.includes('/auth/login') || originalRequest.url.includes('/auth/refresh')) {
        return Promise.reject(error);
      }

      originalRequest._retry = true;

      const refreshToken = localStorage.getItem('sphinx_refresh_token');
      if (!refreshToken) {
        localStorage.removeItem('sphinx_access_token');
        localStorage.removeItem('sphinx_refresh_token');
        localStorage.removeItem('sphinx_user');
        window.location.href = '/login';
        return Promise.reject(error);
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers['Authorization'] = `Bearer ${token}`;
            return api(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      isRefreshing = true;

      try {
        const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {}, {
          headers: { Authorization: `Bearer ${refreshToken}` }
        });

        const newAccessToken = response.data?.data?.access_token;
        if (newAccessToken) {
          localStorage.setItem('sphinx_access_token', newAccessToken);
          api.defaults.headers.common['Authorization'] = `Bearer ${newAccessToken}`;
          originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
          processQueue(null, newAccessToken);
          return api(originalRequest);
        }
      } catch (refreshErr) {
        processQueue(refreshErr, null);
        localStorage.removeItem('sphinx_access_token');
        localStorage.removeItem('sphinx_refresh_token');
        localStorage.removeItem('sphinx_user');
        window.location.href = '/login';
        return Promise.reject(refreshErr);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export default api;
