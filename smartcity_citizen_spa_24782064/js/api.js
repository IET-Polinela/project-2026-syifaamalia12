const API_BASE_URL = "http://localhost:8000";


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
        `http://localhost:8000${endpoint}`,
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

    const res = await fetch(url, {
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
