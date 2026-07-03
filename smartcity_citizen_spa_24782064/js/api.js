const LOCAL_BACKEND_URL = "http://localhost:8000";
const SERVER_BACKEND_URL = "http://103.151.63.87:8001";

const isLocalFrontend =
    window.location.hostname === "127.0.0.1" ||
    window.location.hostname === "localhost";

const API_BASE_URL = isLocalFrontend
    ? LOCAL_BACKEND_URL
    : SERVER_BACKEND_URL;


async function requestAPI(endpoint, method = 'GET', bodyData = null) {

    const accessToken = localStorage.getItem('access_token');

    const headers = {
        'Content-Type': 'application/json'
    };

    if (accessToken) {
        headers['Authorization'] = `Bearer ${accessToken}`;
    }

    const config = {
        method,
        headers
    };

    if (bodyData) {
        config.body = JSON.stringify(bodyData);
    }

    const response = await fetch(
        `${API_BASE_URL}${endpoint}`,
        config
    );

    if (response.status === 401) {
        localStorage.clear();
        window.location.hash = '#login';

        // FORCE SPA RESET (INI YANG KURANG)
        setTimeout(() => {
            window.location.reload();
        }, 50);
    }

    return response;
}

async function apiFetch(url, options = {}) {

    const token = localStorage.getItem('access_token');

    const finalUrl = url.startsWith('http')
        ? url
        : `${API_BASE_URL}${url}`;

    const res = await fetch(finalUrl, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...(token ? { Authorization: `Bearer ${token}` } : {})
        }
    });

    if (res.status === 401) {
        localStorage.clear();
        window.location.hash = '#login';
        return null;
    }

    return res;
}