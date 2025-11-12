function getToken() {
    return localStorage.getItem('access_token');
}

function isAuthenticated() {
    return !!getToken();
}

function logout() {
    localStorage.removeItem('access_token');
    window.location.href = '/admin/login';
}

function requireAuth() {
    if (!isAuthenticated()) {
        window.location.href = '/admin/login';
    }
}

async function fetchWithAuth(url, options = {}) {
    const token = getToken();

    const headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`
    };

    const response = await fetch(url, { ...options, headers });

    if (response.status === 401) {
        logout();
        throw new Error('Unauthorized');
    }

    return response;
}
