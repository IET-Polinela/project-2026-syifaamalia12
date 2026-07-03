const routes = {

    '#login': `
        <div class="row justify-content-center mt-5">
            <div class="col-md-4 card shadow-sm border-0 p-4">

                <h4 class="text-center fw-bold mb-4">
                    Login Warga
                </h4>

                <form id="loginForm">

                    <input type="text"
                           id="loginUsername"
                           class="form-control mb-3"
                           placeholder="Username"
                           required>

                    <input type="password"
                           id="loginPassword"
                           class="form-control mb-3"
                           placeholder="Password"
                           required>

                    <button type="submit"
                            class="btn btn-primary w-100 fw-bold">
                        Masuk
                    </button>

                </form>

            </div>
        </div>
    `,

    '#dashboard': `
    <div class="row g-4 align-items-start">

        <aside class="col-12 col-lg-3">

            <div class="card border-0 p-3 shadow-sm sticky-top" style="top:20px;">

                <button class="btn btn-primary w-100 fw-bold py-3 mb-3" id="btnBukaModal">
                    <i class="bi bi-plus-circle-fill me-2"></i>
                    Laporan Baru
                </button>

                <div class="mt-3" id="summaryStats">

                    <div class="stat-box">
                        <div class="stat-icon draft-icon">
                            <i class="bi bi-file-earmark-text"></i>
                        </div>
                        <div class="stat-content">
                            <h6>Draft</h6>
                            <small>Laporan tersimpan</small>
                        </div>
                        <div class="stat-number badge bg-secondary" id="draftCount">0</div>
                    </div>

                    <div class="stat-divider"></div>

                    <div class="stat-box">
                        <div class="stat-icon">
                            <i class="bi bi-send"></i>
                        </div>
                        <div class="stat-content">
                            <h6>Ajukan</h6>
                            <small>Menunggu verifikasi</small>
                        </div>
                        <div class="stat-number" id="submitCount">0</div>
                    </div>

                    <div class="stat-divider"></div>

                    <div class="stat-box">
                        <div class="stat-icon">
                            <i class="bi bi-search"></i>
                        </div>
                        <div class="stat-content">
                            <h6>Verifikasi</h6>
                            <small>Sedang diverifikasi</small>
                        </div>
                        <div class="stat-number" id="verifyCount">0</div>
                    </div>

                    <div class="stat-divider"></div>

                    <div class="stat-box">
                        <div class="stat-icon process-icon">
                            <i class="bi bi-clock-history"></i>
                        </div>
                        <div class="stat-content">
                            <h6>Diproses</h6>
                            <small>Sedang ditangani</small>
                        </div>
                        <div class="stat-number" id="processCount">0</div>
                    </div>

                    <div class="stat-divider"></div>

                    <div class="stat-box">
                        <div class="stat-icon done-icon">
                            <i class="bi bi-check-circle"></i>
                        </div>
                        <div class="stat-content">
                            <h6>Selesai</h6>
                            <small>Telah selesai</small>
                        </div>
                        <div class="stat-number" id="doneCount">0</div>
                    </div>

                </div>

            </div>

        </aside>

        <section class="col-12 col-lg-6">

            <div class="card border-0 shadow-sm">

                <div class="card-body">

                    <div class="row g-3 mb-4">
                        <div class="col-12 col-md-6">
                            <canvas id="statusChart" height="180"></canvas>
                        </div>

                        <div class="col-12 col-md-6">
                            <canvas id="categoryChart" height="180"></canvas>
                        </div>
                    </div>

                    <input type="text"
                        id="searchInput"
                        class="form-control mb-3"
                        placeholder="Cari laporan...">

                    <div class="d-flex justify-content-center gap-0 mb-4">

                        <button class="dashboard-tab active" id="tabMyReports">
                            Laporan Saya
                        </button>

                        <button class="dashboard-tab" id="tabFeedKota">
                            Feed Kota
                        </button>

                    </div>

                    <div id="listContainer">
                        <div class="text-center text-muted p-5">
                            Memuat data...
                        </div>
                    </div>

                    <div id="paginationContainer" class="mt-3"></div>

                </div>

            </div>

        </section>

        <aside class="col-12 col-lg-3 d-none d-lg-block">

            <div class="card border-0 p-3 shadow-sm sticky-top" style="top:20px;">

                <h6 class="fw-bold mb-3">
                    <i class="bi bi-info-circle-fill text-primary me-2"></i>
                    Pengumuman
                </h6>

                <hr>

                <div class="text-center text-muted py-5">
                    <i class="bi bi-megaphone fs-1 d-block mb-3"></i>

                    <strong>Belum ada pengumuman</strong>

                    <div class="mt-2">
                        Pengumuman terbaru akan ditampilkan di sini.
                    </div>
                </div>

            </div>

        </aside>

    </div>
    `
};

function isAuthenticated() {
    const token = localStorage.getItem("access_token");
    return token && token !== "null" && token !== "undefined";
}

function guardRoute(hash) {

    const auth = isAuthenticated();

    if (!auth && hash === "#dashboard") {
        location.hash = "#login";
        return false;
    }

    if (auth && hash === "#login") {
        location.hash = "#dashboard";
        return false;
    }

    return true;
}

/* =========================
   GLOBAL SAFE FIX (WAJIB)
========================= */
window.currentPage = 1;

window.changePage = function(page) {
    window.currentPage = page;
    if (typeof loadDashboardData === 'function') {
        loadDashboardData('my_reports', page);
    }
};

window.apiInterceptor = function(response) {
    if (response && response.status === 401) {
        localStorage.clear();
        window.location.hash = '#login';
    }
};

async function apiFetch(url, options = {}) {

    const token = localStorage.getItem('access_token');

    const response = await fetch(url, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...(token ? { Authorization: `Bearer ${token}` } : {})
        }
    });

    if (response.status === 401) {
        localStorage.clear();
        window.location.hash = '#login';
    }

    return response;
}

/* =========================
   ROUTER
========================= */
function bootRouter() {

    const run = () => {
        handleRouting();
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', run);
    } else {
        run();
    }
}

bootRouter();

window.addEventListener('hashchange', handleRouting);

function renderDashboardPage(app) {

    app.innerHTML = routes['#dashboard'];

    if (typeof loadDashboardData === 'function') {
        loadDashboardData('my_reports', 1);
    }

    setTimeout(() => {
        if (typeof initDashboard === 'function') {
            initDashboard();
        }

        if (typeof renderChart === 'function') {
            renderChart();
        }
    }, 50);
}

function handleRouting() {

    const hash = window.location.hash || '#login';

    const token = localStorage.getItem('access_token');
    const hasToken = token && token !== 'null' && token !== 'undefined';

    const app = document.getElementById('app-content');
    const nav = document.getElementById('nav-menu');

    if (!app) return;

    if (!hasToken && hash === '#dashboard') {
        localStorage.clear();
        window.location.hash = '#login';
        app.innerHTML = routes['#login'];

        if (nav) nav.innerHTML = '';

        if (typeof setupLoginForm === 'function') {
            setupLoginForm();
        }

        return;
    }

    if (hasToken && hash === '#login') {
        window.location.hash = '#dashboard';
        renderDashboardPage(app);
        return;
    }

    const safeRoute = hasToken ? hash : '#login';

    if (safeRoute === '#login') {
        app.innerHTML = routes['#login'];

        if (nav) nav.innerHTML = '';

        if (typeof setupLoginForm === 'function') {
            setupLoginForm();
        }

        return;
    }

    if (safeRoute === '#dashboard') {
        renderDashboardPage(app);
        return;
    }

    if (hasToken) {
        window.location.hash = '#dashboard';
        renderDashboardPage(app);
        return;
    }

    window.location.hash = '#login';
    app.innerHTML = routes['#login'];

    if (nav) nav.innerHTML = '';

    if (typeof setupLoginForm === 'function') {
        setupLoginForm();
    }
}

/* =========================
   EVENTS
========================= */
window.addEventListener('hashchange', () => {

    if (location.hash === '#logout') {
        localStorage.clear();
        window.location.hash = '#login';
        return;
    }

    handleRouting();
});