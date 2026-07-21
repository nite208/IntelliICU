import axios from "axios";
import config from "../config";

const api = axios.create({
    baseURL: config.API_BASE_URL,
    timeout: 30000,
    headers: {
        "Content-Type": "application/json",
    },
});

api.interceptors.request.use((config) => {
    const token = localStorage.getItem("access_token");

    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
});

let isRefreshing = false;
let failedQueue = [];

function processQueue(error, token = null) {
    failedQueue.forEach((promise) => {
        if (error) promise.reject(error);
        else promise.resolve(token);
    });

    failedQueue = [];
}

api.interceptors.response.use(
    (response) => response,

    async (error) => {
        const originalRequest = error.config;

        const isNetworkError =
            !error.response ||
            error.code === "ECONNABORTED" ||
            error.message === "Network Error";

        const isAuthEndpoint =
            originalRequest.url?.includes("/auth/login") ||
            originalRequest.url?.includes("/auth/refresh");

        // Retry network failures
        if (isNetworkError && !originalRequest.__retryCount) {
            originalRequest.__retryCount = 1;

            await new Promise((resolve) => setTimeout(resolve, 2000));

            return api(originalRequest);
        }

        if (
            isNetworkError &&
            originalRequest.__retryCount < 3
        ) {
            originalRequest.__retryCount++;

            await new Promise((resolve) =>
                setTimeout(resolve, originalRequest.__retryCount * 3000)
            );

            return api(originalRequest);
        }

        if (
            error.response?.status === 401 &&
            !originalRequest._retry &&
            !isAuthEndpoint
        ) {
            if (isRefreshing) {
                return new Promise((resolve, reject) => {
                    failedQueue.push({ resolve, reject });
                }).then((token) => {
                    originalRequest.headers.Authorization =
                        `Bearer ${token}`;

                    return api(originalRequest);
                });
            }

            originalRequest._retry = true;

            isRefreshing = true;

            const refreshToken =
                localStorage.getItem("refresh_token");

            if (!refreshToken) {
                localStorage.clear();
                window.dispatchEvent(new Event("auth_logout"));
                isRefreshing = false;
                return Promise.reject(error);
            }

            try {
                const response = await axios.post(
                    `${config.API_BASE_URL}/auth/refresh`,
                    {
                        refresh_token: refreshToken,
                    }
                );

                const {
                    access_token,
                    refresh_token,
                } = response.data;

                localStorage.setItem(
                    "access_token",
                    access_token
                );

                localStorage.setItem(
                    "refresh_token",
                    refresh_token
                );

                processQueue(null, access_token);

                originalRequest.headers.Authorization =
                    `Bearer ${access_token}`;

                isRefreshing = false;

                return api(originalRequest);
            } catch (refreshError) {
                processQueue(refreshError);

                isRefreshing = false;

                localStorage.clear();

                window.dispatchEvent(
                    new Event("auth_logout")
                );

                return Promise.reject(refreshError);
            }
        }

        return Promise.reject(error);
    }
);

export default api;