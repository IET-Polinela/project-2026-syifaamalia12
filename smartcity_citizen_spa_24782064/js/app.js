let currentTab = 'my_reports';
let currentPage = 1;

let allReports = [];
let totalPages = 1;

let editingReportId = null;

async function loadDashboardData(
    tab = currentTab,
    page = currentPage
) {

    currentTab = tab;
    currentPage = page;

    try {

        const response = await requestAPI(
            `/api/report/?tab=${tab}&page=${page}`,
            'GET'
        );

        if (response.status === 200) {

            const data = await response.json();

            console.log(data);

            allReports = data.results || [];

            totalPages = Math.ceil(
                (data.count || 0) / 10
            );

            renderList();
            renderPagination();
            loadSummaryStats();

        } else {

            document.getElementById(
                'listContainer'
            ).innerHTML = `
                <div class="alert alert-danger">
                    Gagal memuat data laporan.
                </div>
            `;

        }

    } catch (error) {

        console.error(error);

    }
}

async function editDraft(id) {

    try {

        const response = await requestAPI(
            `/api/report/${id}/`,
            'GET'
        );

        if (response.status !== 200) {
            return;
        }

        const report = await response.json();

        document.getElementById('title').value =
            report.title || '';

        document.getElementById('description').value =
            report.description || '';

        document.getElementById('location').value =
            report.location || '';

        document.getElementById('category').value =
            report.category || '';

        document.getElementById('incident_date').value =
            report.incident_date || '';

        editingReportId = id;

        document.getElementById(
            'reportModalLabel'
        ).innerHTML =
            '<i class="bi bi-pencil-square me-2"></i>Edit Draft';

        const modal = new bootstrap.Modal(
            document.getElementById('reportModal')
        );

        modal.show();

    } catch (error) {

        console.error(error);

    }
}

async function submitReport(status) {

    const payload = {

        title:
            document.getElementById('title').value,

        description:
            document.getElementById('description').value,

        location:
            document.getElementById('location').value,

        category:
            document.getElementById('category').value,

        incident_date:
            document.getElementById('incident_date').value,

        status: status

    };

    let endpoint = '/api/report/';
    let method = 'POST';

    if (editingReportId !== null) {

        endpoint =
            `/api/report/${editingReportId}/`;

        method = 'PUT';

    }

    const response =
        await requestAPI(
            endpoint,
            method,
            payload
        );

    if (
        response.status === 201 ||
        response.status === 200
    ) {

        const modalElement =
            document.getElementById(
                'reportModal'
            );

        const modal =
            bootstrap.Modal.getInstance(
                modalElement
            );

        modal.hide();

        document.getElementById(
            'reportForm'
        ).reset();

        editingReportId = null;

        loadDashboardData(
            currentTab,
            currentPage
        );
    }
}

async function loadSummaryStats() {

    try {

        const response = await requestAPI(
            '/api/report/?tab=my_reports&page_size=1000',
            'GET'
        );

        if (response.status !== 200) {
            return;
        }

        const data = await response.json();

        const reports = data.results || [];

        const draftCount = reports.filter(
            report => report.status === 'DRAFT'
        ).length;

        const processCount = reports.filter(
            report =>
                report.status === 'REPORTED' ||
                report.status === 'VERIFIED' ||
                report.status === 'IN_PROGRESS'
        ).length;

        const doneCount = reports.filter(
            report => report.status === 'RESOLVED'
        ).length;

        document.getElementById('draftCount').textContent =
            draftCount;

        document.getElementById('processCount').textContent =
            processCount;

        document.getElementById('doneCount').textContent =
            doneCount;

    } catch (error) {

        console.error(error);

    }
}

function renderList() {

    const container =
        document.getElementById('listContainer');

    if (!allReports.length) {

        container.innerHTML = `
            <div class="alert alert-info">
                Belum ada laporan.
            </div>
        `;

        return;
    }

    container.innerHTML = '';

    allReports.forEach(report => {

        let progress = 25;

        if (report.status === 'REPORTED')
            progress = 50;

        if (report.status === 'VERIFIED')
            progress = 75;

        if (
            report.status === 'IN_PROGRESS' ||
            report.status === 'RESOLVED'
        )
            progress = 100;

        container.innerHTML += `

        <div class="card report-card mb-4">

            <div class="card-body">

                <div class="d-flex justify-content-between align-items-start">

                    <div>

                        <h4 class="fw-bold mb-3">
                            ${report.title}
                        </h4>

                        <div class="text-muted mb-3">

                            <i class="bi bi-geo-alt-fill me-2"></i>

                            ${report.location}

                        </div>

                    </div>

                    <span class="category-badge">

                        ${report.category}

                    </span>

                </div>

                <p class="mb-4">

                    ${report.description}

                </p>

                <div class="text-muted mb-3">

                    <i class="bi bi-person-fill me-2"></i>

                    Pelapor : ${report.reporter}

                </div>

                ${report.status === 'DRAFT'
                    ? `
                    <button
                        class="btn btn-warning btn-sm mb-3"
                        onclick="editDraft(${report.id})">

                        Edit Draft

                    </button>
                    `
                    : ''
                }

                <div class="progress custom-progress">

                    <div
                        class="progress-bar custom-progress-bar"
                        style="width:${progress}%">

                        ${report.status}

                    </div>

                </div>

            </div>

        </div>
        `;
    });
}

function renderPagination() {

    const container =
        document.getElementById(
            'paginationContainer'
        );

    if (!container) return;

    container.innerHTML = '';

    if (totalPages <= 1) return;

    for (
        let i = 1;
        i <= totalPages;
        i++
    ) {

        container.innerHTML += `
            <button
                class="btn ${
                    i === currentPage
                        ? 'btn-primary'
                        : 'btn-outline-primary'
                } me-2 mb-2"
                onclick="loadDashboardData(
                    '${currentTab}',
                    ${i}
                )">

                ${i}

            </button>
        `;
    }
}

document.addEventListener(
    'DOMContentLoaded',
    function () {

        if (
            window.location.hash === '#dashboard'
        ) {

            loadDashboardData(
                'my_reports',
                1
            );
        }

    }
);

document.addEventListener(
    'click',
    function(e) {

        if (
            e.target.id === 'btnDraft'
        ) {

            submitReport(
                'DRAFT'
            );

        }

        if (
            e.target.id === 'btnSubmit'
        ) {

            submitReport(
                'REPORTED'
            );

        }

    }
);

document.addEventListener('click', function (e) {

    const btn = e.target.closest('#btnNewReport');

    if (!btn) return;

    const username =
        localStorage.getItem('username');

    if (username === 'min') {

        alert(
            'Admin tidak diperbolehkan membuat laporan'
        );

        return;
    }

    if (window.location.hash !== '#dashboard') {
        return;
    }

    editingReportId = null;

    document.getElementById('reportForm').reset();

    document.getElementById('reportModalLabel').innerHTML =
        '<i class="bi bi-pencil-square me-2"></i>Buat Laporan Baru';

    const modal = new bootstrap.Modal(
        document.getElementById('reportModal')
    );

    modal.show();
});

document.addEventListener(
    'click',
    function(e) {

        if (
            e.target.id === 'tabMyReports'
        ) {

            document
                .getElementById('tabMyReports')
                .classList.add('active');

            document
                .getElementById('tabFeed')
                .classList.remove('active');

            loadDashboardData(
                'my_reports',
                1
            );

        }

        if (
            e.target.id === 'tabFeed'
        ) {

            document
                .getElementById('tabFeed')
                .classList.add('active');

            document
                .getElementById('tabMyReports')
                .classList.remove('active');

            loadDashboardData(
                'feed',
                1
            );

        }

    }
);