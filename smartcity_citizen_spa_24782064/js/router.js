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
        <div class="row g-4">

            <aside class="col-12 col-lg-3">

                <div class="card border-0 p-3 shadow-sm sticky-top"
                     style="top:20px;">

                    <button
                        class="btn btn-primary w-100 fw-bold py-3 mb-3"
                        id="btnNewReport">
                        <i class="bi bi-plus-circle-fill me-2"></i>
                        Laporan Baru
                    </button>

        <div class="mt-3">

            <div class="stat-box">

                <div class="stat-icon draft-icon">
                    <i class="bi bi-file-earmark-text"></i>
                </div>

                <div class="stat-content">

                    <h6>Draft</h6>

                    <small>
                        Laporan tersimpan
                    </small>

                </div>

                <div
                    class="stat-number text-primary"
                    id="draftCount">

                    0

                </div>

            </div>

            <div class="stat-divider"></div>

            <div class="stat-box">

                <div class="stat-icon process-icon">
                    <i class="bi bi-clock-history"></i>
                </div>

                <div class="stat-content">

                    <h6>Diproses</h6>

                    <small>
                        Sedang ditangani
                    </small>

                </div>

                <div
                    class="stat-number text-warning"
                    id="processCount">

                    0

                </div>

            </div>

            <div class="stat-divider"></div>

            <div class="stat-box">

                <div class="stat-icon done-icon">
                    <i class="bi bi-check-circle"></i>
                </div>

                <div class="stat-content">

                    <h6>Selesai</h6>

                    <small>
                        Telah selesai
                    </small>

                </div>

                <div
                    class="stat-number text-success"
                    id="doneCount">

                    0

                </div>

            </div>

        </div>

                </div>

            </aside>

            <section class="col-12 col-lg-6">

                <div class="card border-0 shadow-sm">

                    <div class="card-body">

                        <div class="d-flex justify-content-center gap-0 mb-4">

                            <button
                                class="dashboard-tab active"
                                id="tabMyReports">

                                <i class="bi bi-person me-2"></i>
                                Laporan Saya

                            </button>

                            <button
                                class="dashboard-tab"
                                id="tabFeed">

                                <i class="bi bi-people me-2"></i>
                                Feed Kota

                            </button>

                        </div>

                            <div id="listContainer">

                            <div class="text-center text-muted p-5">
                                Memuat data...
                            </div>

                        </div>

                        <div id="paginationContainer"
                            class="mt-3">
                        </div>

                    </div>

                </div>

            </section>

            <aside class="col-12 col-lg-3 d-none d-lg-block">

                <div class="card border-0 p-3 shadow-sm sticky-top"
                     style="top:20px;">

                    <h6 class="fw-bold mb-3">
                        <i class="bi bi-info-circle-fill text-primary me-2"></i>
                        Pengumuman
                    </h6>

                    <hr>

                    <div class="text-center text-muted py-5">

                        <i class="bi bi-megaphone fs-1 d-block mb-3"></i>

                        <strong>
                            Belum ada pengumuman
                        </strong>

                        <div class="mt-2">
                            Pengumuman terbaru akan
                            ditampilkan di sini.
                        </div>

                    </div>

                </div>

            </aside>

        </div>
    `
};


function handleRouting() {

    const hash = window.location.hash || '#login';

    document.getElementById('app-content').innerHTML =
        routes[hash] || routes['#login'];

    if (
        hash === '#login' &&
        typeof setupLoginForm === 'function'
    ) {

        document.getElementById(
            'nav-menu'
        ).innerHTML = '';

        setupLoginForm();
    }

    if (
        hash === '#dashboard' &&
        typeof loadDashboardData === 'function'
    ) {

        const username =
            localStorage.getItem('username')
            || 'Warga';

        document.getElementById(
            'nav-menu'
        ).innerHTML = `

        <div class="dropdown">

            <button
                class="btn text-white fw-bold dropdown-toggle"
                data-bs-toggle="dropdown">

                <i class="bi bi-person-circle me-2"></i>
                 ${username}

            </button>

            <ul class="dropdown-menu dropdown-menu-end">

                <li>

                    <a
                        class="dropdown-item text-danger"
                        href="#logout">

                        <i class="bi bi-box-arrow-right me-2"></i>
                        Logout

                    </a>

                </li>

            </ul>

        </div>
        `;

        loadDashboardData(
            'my_reports',
            1
        );
    }
}

window.addEventListener(
    'hashchange',
    () => {

        if (
            location.hash === '#logout'
        ) {

            localStorage.clear();

            location.hash = '#login';

        }

    }
);

window.addEventListener(
    'hashchange',
    handleRouting
);

window.addEventListener(
    'DOMContentLoaded',
    handleRouting
);