from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from main_app.models import Report
from datetime import date

# ─────────────────────────────────────────────────────────────────────────────
# PENJELASAN: get_user_model()
# ─────────────────────────────────────────────────────────────────────────────
# Django mendukung custom user model melalui setting AUTH_USER_MODEL.
# Pada proyek ini, user model kustom didefinisikan di usermanagement.User.
# Menggunakan get_user_model() memastikan kita selalu mereferensikan model
# user yang benar, bukan django.contrib.auth.models.User bawaan.
# ─────────────────────────────────────────────────────────────────────────────
User = get_user_model()

# =============================================================================
# MODUL 3: PENGUJIAN ALUR KERJA & ATURAN BISNIS STATUS LAPORAN
# =============================================================================
# Fokus: Memastikan transisi status laporan mengikuti aturan state machine:
#   DRAFT -> REPORTED -> VERIFIED -> IN_PROGRESS -> RESOLVED
#
# Aturan kunci:
#   - Hanya pemilik draf yang bisa memodifikasi laporan berstatus DRAFT
#   - Laporan yang sudah REPORTED tidak bisa diubah kontennya oleh warga
#   - Laporan RESOLVED bersifat read-only (tidak bisa diubah siapa pun)
#   - Admin hanya bisa melakukan transisi maju, BUKAN lompat status
# =============================================================================

class WorkflowStateTests(APITestCase):
    """
    Kelas pengujian untuk alur kerja dan transisi status laporan via REST API.

    Menguji aturan bisnis terkait kapan laporan boleh dimodifikasi dan
    bagaimana status berubah sesuai alur yang telah ditentukan.
    """

    def setUp(self):
        """
        Persiapan: Buat satu warga dan beberapa laporan dengan status berbeda
        untuk menguji aturan transisi status.
        """
        self.warga = User.objects.create_user(
            username='warga_wf', password='TestPass123!', is_admin=False
        )

        # Laporan berstatus DRAFT — bisa dimodifikasi oleh pemilik
        self.laporan_draft = Report.objects.create(
            title='Lampu Kampus Mati',
            category='Fasilitas Umum',
            description='Lampu di depan gedung rektorat tidak menyala.',
            location='Gedung Rektorat',
            incident_date=date.today(),
            status='DRAFT',
            reporter=self.warga,
        )

        # Laporan berstatus REPORTED — sudah masuk antrean, TIDAK bisa diubah
        self.laporan_reported = Report.objects.create(
            title='Saluran Air Tersumbat',
            category='Infrastruktur',
            description='Saluran air di samping kantin tersumbat.',
            location='Kantin Polinela',
            incident_date=date.today(),
            status='REPORTED',
            reporter=self.warga,
        )

        # Laporan berstatus RESOLVED — sudah selesai, bersifat READ-ONLY
        self.laporan_resolved = Report.objects.create(
            title='AC Rusak di Lab',
            category='Fasilitas Umum',
            description='AC di Lab CPS 1 sudah diperbaiki.',
            location='Lab CPS 1',
            incident_date=date.today(),
            status='RESOLVED',
            reporter=self.warga,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # WF-01: Warga Mengajukan Laporan (DRAFT → REPORTED)
    # ─────────────────────────────────────────────────────────────────────────
    def test_WF_01_warga_mengajukan_draf_menjadi_reported(self):
        """
        [WF-01] Warga menekan tombol ajukan laporan pada data berstatus DRAFT.

        SKENARIO:
            Warga melakukan PUT request untuk mengubah status laporan dari
            DRAFT menjadi REPORTED. Ini mensimulasikan aksi "Ajukan Laporan"
            pada antarmuka SPA.

        HASIL YANG DIHARAPKAN:
            Status laporan di basis data berubah menjadi REPORTED dan laporan
            masuk ke antrean peninjauan petugas.

        PENJELASAN TEKNIS:
            Pada kode SPA (app.js), fungsi kirimLaporan() mengirim PUT request
            dengan payload yang menyertakan status='REPORTED'. Permission
            IsOwnerAndDraftOrReadOnly mengizinkan modifikasi karena user adalah
            pemilik dan status saat ini masih DRAFT.
        """
        self.client.force_authenticate(user=self.warga)

        url = f'/api/report/{self.laporan_draft.pk}/'
        payload = {
            'title': self.laporan_draft.title,
            'category': self.laporan_draft.category,
            'description': self.laporan_draft.description,
            'location': self.laporan_draft.location,
            'incident_date': str(self.laporan_draft.incident_date),
            'status': 'REPORTED',  # Modifikasi dari DRAFT ke REPORTED
        }

        response = self.client.put(url, payload, format='json')

        # Verifikasi: PUT berhasil dengan HTTP 200
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Pengajuan draf ke REPORTED seharusnya berhasil (HTTP 200)"
        )

        # Verifikasi: Status di database benar-benar berubah
        self.laporan_draft.refresh_from_db()
        self.assertEqual(
            self.laporan_draft.status,
            'REPORTED',
            "Status laporan di database harus berubah menjadi 'REPORTED'"
        )

    # ─────────────────────────────────────────────────────────────────────────
    # WF-02: Warga Tidak Bisa Mengubah Konten Laporan yang Sudah REPORTED
    # ─────────────────────────────────────────────────────────────────────────
    def test_WF_02_tidak_bisa_edit_laporan_yang_sudah_reported(self):
        """
        [WF-02] Warga mencoba memperbarui teks konten laporan yang sudah
        berstatus REPORTED via API.

        SKENARIO:
            Warga mengirim PUT request untuk mengubah judul/deskripsi laporan
            yang sudah berstatus REPORTED.

        HASIL YANG DIHARAPKAN:
            Sistem menolak perubahan konten karena data sudah masuk ke tahap
            peninjauan (HTTP 403 Forbidden).

        PENJELASAN TEKNIS:
            Permission IsOwnerAndDraftOrReadOnly hanya mengizinkan modifikasi
            (PUT/PATCH/DELETE) jika:
              1. obj.reporter == request.user (pemilik)
              2. obj.status == 'DRAFT'
            Karena status REPORTED != DRAFT, permission menolak dengan 403.
        """
        # Arrange: login sebagai warga pemilik laporan
        self.client.force_authenticate(user=self.warga)

        # Arrange: simpan data asli sebelum dicoba diubah
        judul_asli = self.laporan_reported.title
        deskripsi_asli = self.laporan_reported.description

        url = f'/api/report/{self.laporan_reported.pk}/'
        payload = {
            'title': 'Judul REPORTED Dipaksa Diubah',
            'category': self.laporan_reported.category,
            'description': 'Deskripsi REPORTED dipaksa berubah.',
            'location': self.laporan_reported.location,
            'incident_date': str(self.laporan_reported.incident_date),
            'status': self.laporan_reported.status,
        }

        # Act: warga mencoba mengubah laporan yang sudah REPORTED
        response = self.client.put(url, payload, format='json')

        # Assert: request harus ditolak
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Laporan berstatus REPORTED seharusnya tidak boleh diedit oleh warga"
        )

        # Assert: data di database tidak boleh berubah
        self.laporan_reported.refresh_from_db()
        self.assertEqual(self.laporan_reported.title, judul_asli)
        self.assertEqual(self.laporan_reported.description, deskripsi_asli)

    # ─────────────────────────────────────────────────────────────────────────
    # WF-05: Laporan RESOLVED Bersifat Read-Only
    # ─────────────────────────────────────────────────────────────────────────
    def test_WF_05_laporan_resolved_tidak_bisa_diubah(self):
        """
        [WF-05] Pengguna (Admin maupun Warga) mencoba mengirimkan modifikasi
        data pada laporan yang sudah berstatus RESOLVED.

        SKENARIO:
            Warga mencoba mengirim PUT request untuk mengubah laporan yang
            sudah berstatus RESOLVED (selesai).

        HASIL YANG DIHARAPKAN:
            Sistem mengunci data tersebut sebagai berkas read-only dan
            mengembalikan respons HTTP 403 Forbidden.

        PENJELASAN TEKNIS:
            IsOwnerAndDraftOrReadOnly hanya mengizinkan modifikasi pada
            laporan berstatus DRAFT milik sendiri. Status RESOLVED != DRAFT,
            sehingga semua operasi tulis (PUT/PATCH/DELETE) ditolak.
        """
        # Arrange: login sebagai warga pemilik laporan
        self.client.force_authenticate(user=self.warga)

        # Arrange: simpan data asli laporan RESOLVED
        judul_asli = self.laporan_resolved.title
        deskripsi_asli = self.laporan_resolved.description

        url = f'/api/report/{self.laporan_resolved.pk}/'
        payload = {
            'title': 'Judul RESOLVED Dipaksa Diubah',
            'category': self.laporan_resolved.category,
            'description': 'Deskripsi laporan selesai dipaksa berubah.',
            'location': self.laporan_resolved.location,
            'incident_date': str(self.laporan_resolved.incident_date),
            'status': self.laporan_resolved.status,
        }

        # Act: warga mencoba mengubah laporan yang sudah RESOLVED
        response = self.client.put(url, payload, format='json')

        # Assert: laporan RESOLVED harus terkunci
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Laporan berstatus RESOLVED seharusnya bersifat read-only"
        )

        # Assert: data di database tidak boleh berubah
        self.laporan_resolved.refresh_from_db()
        self.assertEqual(self.laporan_resolved.title, judul_asli)
        self.assertEqual(self.laporan_resolved.description, deskripsi_asli)


# =============================================================================
# MODUL 3b: PENGUJIAN ADMIN PORTAL — TRANSISI STATUS
# =============================================================================
# Fokus: Menguji fungsi portal admin (Django monolitik) dalam mengelola
# transisi status laporan dan memastikan tombol aksi yang tersedia sesuai
# dengan aturan state machine.
#
# Catatan: Menggunakan Django TestCase (bukan APITestCase) karena menguji
# Django Views + Templates (monolitik), bukan REST API.
# =============================================================================

class AdminWorkflowTests(TestCase):
    """
    Kelas pengujian untuk portal admin (Django monolithic views).

    Menguji kemampuan admin untuk mengubah status laporan melalui
    antarmuka portal admin, serta memverifikasi pembatasan transisi status.
    """

    def setUp(self):
        """
        Persiapan: Buat admin user dan beberapa laporan untuk menguji
        transisi status di portal admin.
        """
        # Admin harus memiliki is_staff=True untuk lolos @staff_member_required
        self.admin = User.objects.create_user(
            username='admin_portal',
            password='AdminPass123!',
            is_admin=True,
            is_staff=True,
        )

        # Laporan REPORTED — menunggu verifikasi oleh admin
        self.laporan_reported = Report.objects.create(
            title='Jalan Rusak di Blok C',
            category='Infrastruktur',
            description='Jalan berlubang parah di area parkir Blok C.',
            location='Blok C Polinela',
            incident_date=date.today(),
            status='REPORTED',
            reporter=self.admin,  # Siapa reporter-nya tidak penting untuk admin test
        )

    # ─────────────────────────────────────────────────────────────────────────
    # WF-03: Admin Mengubah Status REPORTED menjadi VERIFIED
    # ─────────────────────────────────────────────────────────────────────────
    def test_WF_03_admin_mengubah_status_reported_ke_verified(self):
        """
        [WF-03] Admin mengubah status laporan dari REPORTED menjadi VERIFIED
        melalui UI Portal Admin.

        SKENARIO:
            Admin yang sudah login memodifikasi status dari REPORTED
            menjadi VERIFIED.

        HASIL YANG DIHARAPKAN:
            Perubahan status tersimpan dengan sukses ke basis data.

        PENJELASAN TEKNIS:
            View update_report_status di views.py menangani request
            dengan parameter 'new_status'. View memvalidasi bahwa transisi
            yang diminta ada di dalam daftar allowed_transitions sebelum
            menyimpan perubahan ke database.
        """
        # Arrange: login sebagai admin portal
        login_berhasil = self.client.login(
            username='admin_portal',
            password='AdminPass123!'
        )
        self.assertTrue(
            login_berhasil,
            "Admin harus berhasil login sebelum mengubah status laporan"
        )

        url = reverse('update_status', kwargs={'pk': self.laporan_reported.pk})

        # Act: admin mengubah status REPORTED menjadi VERIFIED
        response = self.client.post(url, {
            'status': 'VERIFIED',
            'new_status': 'VERIFIED',
        })

        # Assert: request berhasil, biasanya redirect 302 atau bisa 200
        self.assertIn(
            response.status_code,
            [status.HTTP_200_OK, status.HTTP_302_FOUND],
            "Perubahan status oleh admin seharusnya berhasil"
        )

        # Assert: status laporan di database berubah menjadi VERIFIED
        self.laporan_reported.refresh_from_db()
        self.assertEqual(
            self.laporan_reported.status,
            'VERIFIED',
            "Status laporan harus berubah dari REPORTED menjadi VERIFIED"
        )

    # ─────────────────────────────────────────────────────────────────────────
    # WF-04: Tidak Ada Tombol Langsung ke RESOLVED dari REPORTED
    # ─────────────────────────────────────────────────────────────────────────
    def test_WF_04_tidak_ada_transisi_langsung_ke_resolved_dari_reported(self):
        """
        [WF-04] Memeriksa ketersediaan tombol transisi status pada berkas
        Django Template ketika laporan baru berstatus REPORTED.

        SKENARIO:
            Halaman detail laporan diperiksa untuk memastikan bahwa tombol
            aksi menuju status RESOLVED tidak tersedia secara langsung.
            Status harus melalui jalur VERIFIED -> IN_PROGRESS -> RESOLVED.

        HASIL YANG DIHARAPKAN:
            Template TIDAK menampilkan tombol untuk langsung ke RESOLVED.
            Hanya tombol ke status VERIFIED yang tersedia.

        PENJELASAN TEKNIS:
            Pada views.py, pastikan terdapat mekanisme yang membatasi modifikasi status:
              - REPORTED  -> [VERIFIED]          (hanya VERIFIED)
              - VERIFIED  -> [IN_PROGRESS]       (hanya IN_PROGRESS)
              - IN_PROGRESS -> [RESOLVED]        (hanya RESOLVED)
            Ini memastikan laporan tidak bisa "lompat" status.
        """
        # Arrange: login sebagai admin portal
        login_berhasil = self.client.login(
            username='admin_portal',
            password='AdminPass123!'
        )
        self.assertTrue(
            login_berhasil,
            "Admin harus berhasil login sebelum membuka detail laporan"
        )

        url = reverse('report_detail', kwargs={'pk': self.laporan_reported.pk})

        # Act: admin membuka halaman detail laporan REPORTED
        response = self.client.get(url)
        html = response.content.decode('utf-8')

        # Assert: halaman detail berhasil dibuka
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert: transisi ke VERIFIED tersedia
        self.assertIn(
            'VERIFIED',
            html,
            "Laporan REPORTED seharusnya memiliki transisi berikutnya ke VERIFIED"
        )

        # Assert: tidak boleh ada tombol/input langsung menuju RESOLVED
        self.assertNotIn('value="RESOLVED"', html)
        self.assertNotIn("value='RESOLVED'", html)