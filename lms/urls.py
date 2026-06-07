from django.urls import path
from lms.views import auth_views, admin_views, guru_views, siswa_views

urlpatterns = [
    # Auth
    path('', auth_views.login_view, name='home'),
    path('login/', auth_views.login_view, name='login'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('signup/', auth_views.signup_view, name='signup'),

    # Dashboard Router
    path('dashboard/', auth_views.dashboard_redirect, name='dashboard'),

    # Admin
    path('admin-dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/users/', admin_views.manage_users, name='manage_users'),
    path('admin-dashboard/users/guru/tambah/', admin_views.tambah_guru, name='tambah_guru'),
    path('admin-dashboard/users/guru/edit/<int:guru_id>/', admin_views.edit_guru, name='edit_guru'),
    path('admin-dashboard/users/siswa/tambah/', admin_views.tambah_siswa, name='tambah_siswa'),
    path('admin-dashboard/users/siswa/edit/<int:siswa_id>/', admin_views.edit_siswa, name='edit_siswa'),
    path('admin-dashboard/users/suspend/<int:user_id>/', admin_views.toggle_suspend, name='toggle_suspend'),
    path('admin-dashboard/users/hapus/<int:user_id>/', admin_views.hapus_user, name='hapus_user'),
    path('admin-dashboard/akademik/', admin_views.manage_akademik, name='manage_akademik'),
    path('admin-dashboard/akademik/jurusan/edit/<int:jurusan_id>/', admin_views.edit_jurusan, name='edit_jurusan'),
    path('admin-dashboard/akademik/jurusan/hapus/<int:jurusan_id>/', admin_views.hapus_jurusan, name='hapus_jurusan'),
    path('admin-dashboard/akademik/kelas/edit/<int:kelas_id>/', admin_views.edit_kelas, name='edit_kelas'),
    path('admin-dashboard/akademik/kelas/hapus/<int:kelas_id>/', admin_views.hapus_kelas, name='hapus_kelas'),
    path('admin-dashboard/akademik/mapel/edit/<int:mapel_id>/', admin_views.edit_mapel, name='edit_mapel'),
    path('admin-dashboard/akademik/mapel/hapus/<int:mapel_id>/', admin_views.hapus_mapel, name='hapus_mapel'),
    path('admin-dashboard/jadwal/', admin_views.manage_jadwal, name='manage_jadwal'),
    path('admin-dashboard/jadwal/edit/<int:jadwal_id>/', admin_views.edit_jadwal, name='edit_jadwal'),
    path('admin-dashboard/jadwal/hapus/<int:jadwal_id>/', admin_views.hapus_jadwal, name='hapus_jadwal'),
    path('admin-dashboard/monitoring/', admin_views.monitoring, name='monitoring'),

    # Guru
    path('guru/', guru_views.guru_dashboard, name='guru_dashboard'),
    path('guru/kelas/<int:jadwal_id>/', guru_views.kelas_detail, name='guru_kelas_detail'),
    path('guru/kelas/<int:jadwal_id>/pertemuan/tambah/', guru_views.tambah_pertemuan, name='tambah_pertemuan'),
    path('guru/pertemuan/<int:pertemuan_id>/materi/tambah/', guru_views.tambah_materi, name='tambah_materi'),
    path('guru/pertemuan/<int:pertemuan_id>/presensi/buka/', guru_views.buka_presensi, name='buka_presensi'),
    path('guru/pertemuan/<int:pertemuan_id>/forum/tambah/', guru_views.tambah_forum, name='tambah_forum'),
    path('guru/pertemuan/<int:pertemuan_id>/live/tambah/', guru_views.tambah_live, name='tambah_live'),
    path('guru/pertemuan/<int:pertemuan_id>/tugas/tambah/', guru_views.tambah_tugas, name='tambah_tugas'),
    path('guru/pertemuan/<int:pertemuan_id>/kuis/tambah/', guru_views.tambah_kuis, name='tambah_kuis'),
    path('guru/kuis/<int:kuis_id>/soal/tambah/', guru_views.tambah_soal, name='tambah_soal'),
    path('guru/penilaian/', guru_views.penilaian, name='guru_penilaian'),
    path('guru/penilaian/nilai/<int:submission_id>/', guru_views.beri_nilai, name='beri_nilai'),
    path('guru/pkl/', guru_views.pkl_monitoring, name='guru_pkl_monitoring'),
    path('guru/pkl/jurnal/<int:jurnal_id>/verifikasi/', guru_views.verifikasi_jurnal, name='verifikasi_jurnal'),

    # Siswa
    path('siswa/', siswa_views.siswa_dashboard, name='siswa_dashboard'),
    path('siswa/kelas/<int:jadwal_id>/', siswa_views.kelas_detail, name='siswa_kelas_detail'),
    path('siswa/presensi/<int:presensi_id>/absen/', siswa_views.absen, name='absen'),
    path('siswa/forum/<int:forum_id>/komentar/', siswa_views.tambah_komentar, name='tambah_komentar'),
    path('siswa/tugas/<int:tugas_id>/submit/', siswa_views.submit_tugas, name='submit_tugas'),
    path('siswa/kuis/<int:kuis_id>/mulai/', siswa_views.mulai_kuis, name='mulai_kuis'),
    path('siswa/kuis/<int:kuis_id>/selesai/', siswa_views.selesai_kuis, name='selesai_kuis'),
    path('siswa/portofolio/', siswa_views.portofolio, name='siswa_portofolio'),
    path('siswa/portofolio/tambah/', siswa_views.tambah_portofolio, name='tambah_portofolio'),
    path('siswa/pkl/', siswa_views.pkl_jurnal, name='siswa_pkl'),
    path('siswa/pkl/tambah/', siswa_views.tambah_jurnal, name='tambah_jurnal'),
]
