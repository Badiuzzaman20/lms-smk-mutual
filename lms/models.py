# pyrefly: ignore [missing-import]
from django.db import models
# pyrefly: ignore [missing-import]
from django.contrib.auth.models import AbstractUser
# pyrefly: ignore [missing-import]
from django.utils import timezone

class Role(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('guru', 'Guru'),
        ('siswa', 'Siswa'),
    )
    name = models.CharField(max_length=10, choices=ROLE_CHOICES, unique=True)

    def __str__(self):
        return self.get_name_display()

class User(AbstractUser):
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    is_suspended = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} ({self.role.name if self.role else 'No Role'})"

class Jurusan(models.Model):
    nama = models.CharField(max_length=100)
    kode = models.CharField(max_length=10, unique=True) # e.g. TKJ, AKL

    def __str__(self):
        return f"{self.kode} - {self.nama}"

class Kelas(models.Model):
    TINGKAT_CHOICES = (
        ('X', 'Kelas X'),
        ('XI', 'Kelas XI'),
        ('XII', 'Kelas XII'),
    )
    tingkat = models.CharField(max_length=3, choices=TINGKAT_CHOICES)
    nama = models.CharField(max_length=50, unique=True) # e.g. XI TKJ 1
    jurusan = models.ForeignKey(Jurusan, on_delete=models.CASCADE, related_name='kelas_list')

    def __str__(self):
        return self.nama

class PreRegisteredUser(models.Model):
    ROLE_CHOICES = (
        ('guru', 'Guru'),
        ('siswa', 'Siswa'),
    )
    nip_nisn = models.CharField(max_length=30, unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    nama = models.CharField(max_length=100)
    kelas = models.ForeignKey(Kelas, on_delete=models.SET_NULL, null=True, blank=True) # Only for students

    def __str__(self):
        return f"{self.nip_nisn} - {self.nama} ({self.role})"

class Guru(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='guru_profile')
    nip = models.CharField(max_length=30, unique=True)
    jabatan = models.CharField(max_length=100, default='Guru Mata Pelajaran')

    def __str__(self):
        return f"Guru: {self.user.first_name} {self.user.last_name} (NIP: {self.nip})"

class Siswa(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='siswa_profile')
    nisn = models.CharField(max_length=30, unique=True)
    kelas = models.ForeignKey(Kelas, on_delete=models.CASCADE, related_name='siswa_list')

    def __str__(self):
        return f"Siswa: {self.user.first_name} {self.user.last_name} (NISN: {self.nisn})"

class MataPelajaran(models.Model):
    KATEGORI_CHOICES = (
        ('nasional', 'Muatan Nasional'),
        ('kewilayahan', 'Muatan Kewilayahan'),
        ('kejuruan', 'Muatan Kejuruan'),
    )
    nama = models.CharField(max_length=100)
    kode = models.CharField(max_length=20, unique=True)
    kategori = models.CharField(max_length=20, choices=KATEGORI_CHOICES)
    jurusan = models.ForeignKey(Jurusan, on_delete=models.SET_NULL, null=True, blank=True, related_name='mapel_list') # Null means general (all jurusans)

    def __str__(self):
        return f"{self.nama} ({self.get_kategori_display()})"

class JadwalKBM(models.Model):
    HARI_CHOICES = (
        ('Senin', 'Senin'),
        ('Selasa', 'Selasa'),
        ('Rabu', 'Rabu'),
        ('Kamis', 'Kamis'),
        ('Jumat', 'Jumat'),
        ('Sabtu', 'Sabtu'),
    )
    mata_pelajaran = models.ForeignKey(MataPelajaran, on_delete=models.CASCADE, related_name='jadwal_list')
    guru = models.ForeignKey(Guru, on_delete=models.CASCADE, related_name='jadwal_list')
    kelas = models.ForeignKey(Kelas, on_delete=models.CASCADE, related_name='jadwal_list')
    hari = models.CharField(max_length=10, choices=HARI_CHOICES)
    jam_mulai = models.TimeField()
    jam_selesai = models.TimeField()

    def __str__(self):
        return f"{self.kelas} - {self.mata_pelajaran.nama} ({self.hari}, {self.jam_mulai}-{self.jam_selesai})"

class Pertemuan(models.Model):
    jadwal = models.ForeignKey(JadwalKBM, on_delete=models.CASCADE, related_name='pertemuan_list')
    judul = models.CharField(max_length=200)
    deskripsi = models.TextField(blank=True, null=True)
    urutan = models.IntegerField(default=1)

    class Meta:
        ordering = ['urutan']

    def __str__(self):
        return f"Pertemuan {self.urutan}: {self.judul} ({self.jadwal.mata_pelajaran.nama} - {self.jadwal.kelas.nama})"

class MateriMedia(models.Model):
    TIPE_CHOICES = (
        ('modul', 'Modul Digital (PDF/Word/PPT)'),
        ('audiovisual', 'Media Audiovisual (Video Link/Embed)'),
        ('link', 'Link Eksternal (Artikel/Repositori)'),
    )
    pertemuan = models.ForeignKey(Pertemuan, on_delete=models.CASCADE, related_name='materi_list')
    tipe = models.CharField(max_length=20, choices=TIPE_CHOICES)
    judul = models.CharField(max_length=200)
    file = models.FileField(upload_to='materi_files/', blank=True, null=True)
    video_embed = models.TextField(blank=True, null=True, help_text='Embed code or direct YouTube URL')
    link_eksternal = models.URLField(blank=True, null=True)
    deskripsi = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.get_tipe_display()} - {self.judul}"

class AktivitasPresensi(models.Model):
    pertemuan = models.ForeignKey(Pertemuan, on_delete=models.CASCADE, related_name='presensi_activity')
    created_at = models.DateTimeField(default=timezone.now)
    batas_waktu = models.DateTimeField()

    def __str__(self):
        return f"Presensi Pertemuan {self.pertemuan.urutan} (Batas: {self.batas_waktu})"

class PresensiSiswa(models.Model):
    STATUS_CHOICES = (
        ('hadir', 'Hadir'),
        ('izin', 'Izin'),
        ('sakit', 'Sakit'),
        ('alpa', 'Alpa'),
    )
    presensi = models.ForeignKey(AktivitasPresensi, on_delete=models.CASCADE, related_name='absensi_list')
    siswa = models.ForeignKey(Siswa, on_delete=models.CASCADE, related_name='absensi_list')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    waktu_absen = models.DateTimeField(default=timezone.now)
    keterangan = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('presensi', 'siswa')

    def __str__(self):
        return f"{self.siswa.user.get_full_name()} - {self.status}"

class ForumDiskusi(models.Model):
    pertemuan = models.ForeignKey(Pertemuan, on_delete=models.CASCADE, related_name='forum_list')
    judul = models.CharField(max_length=200)
    deskripsi = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.judul

class KomentarForum(models.Model):
    forum = models.ForeignKey(ForumDiskusi, on_delete=models.CASCADE, related_name='komentar_list')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_komentar_list')
    konten = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Komentar {self.user.username} di {self.forum.judul}"

class LiveClass(models.Model):
    PLATFORM_CHOICES = (
        ('gmeet', 'Google Meet'),
        ('zoom', 'Zoom'),
    )
    pertemuan = models.ForeignKey(Pertemuan, on_delete=models.CASCADE, related_name='live_class')
    platform = models.CharField(max_length=10, choices=PLATFORM_CHOICES)
    link = models.URLField()
    waktu_mulai = models.DateTimeField()

    def __str__(self):
        return f"Live {self.get_platform_display()} - {self.pertemuan.judul}"

class TugasUjian(models.Model):
    TIPE_CHOICES = (
        ('tugas', 'Penugasan'),
        ('kuis', 'Kuis / CBT'),
    )
    pertemuan = models.ForeignKey(Pertemuan, on_delete=models.CASCADE, related_name='tugas_ujian_list')
    tipe = models.CharField(max_length=10, choices=TIPE_CHOICES)
    judul = models.CharField(max_length=200)
    deskripsi = models.TextField()
    deadline = models.DateTimeField()
    waktu_pengerjaan = models.IntegerField(default=60, help_text='Duration in minutes for quiz/CBT')

    def __str__(self):
        return f"{self.get_tipe_display()} - {self.judul}"

class TugasSubmission(models.Model):
    tugas = models.ForeignKey(TugasUjian, on_delete=models.CASCADE, related_name='submissions')
    siswa = models.ForeignKey(Siswa, on_delete=models.CASCADE, related_name='submissions')
    file = models.FileField(upload_to='submission_files/', blank=True, null=True)
    link = models.URLField(blank=True, null=True, help_text='Link GitHub or Google Drive')
    jawaban_teks = models.TextField(blank=True, null=True)
    nilai = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('tugas', 'siswa')

    def __str__(self):
        return f"Submission: {self.siswa.user.get_full_name()} - {self.tugas.judul}"

class QuizSoal(models.Model):
    SOAL_CHOICES = (
        ('pilihan_ganda', 'Pilihan Ganda'),
        ('esai', 'Esai'),
    )
    kuis = models.ForeignKey(TugasUjian, on_delete=models.CASCADE, related_name='soal_list')
    tipe = models.CharField(max_length=20, choices=SOAL_CHOICES, default='pilihan_ganda')
    pertanyaan = models.TextField()
    opsi_a = models.CharField(max_length=255, blank=True, null=True)
    opsi_b = models.CharField(max_length=255, blank=True, null=True)
    opsi_c = models.CharField(max_length=255, blank=True, null=True)
    opsi_d = models.CharField(max_length=255, blank=True, null=True)
    opsi_e = models.CharField(max_length=255, blank=True, null=True)
    jawaban_benar = models.CharField(max_length=5, help_text='A/B/C/D/E for multiple choice, or text for esai key', blank=True, null=True)

    def __str__(self):
        return f"Soal {self.id} ({self.kuis.judul})"

class QuizAttempt(models.Model):
    kuis = models.ForeignKey(TugasUjian, on_delete=models.CASCADE, related_name='attempts')
    siswa = models.ForeignKey(Siswa, on_delete=models.CASCADE, related_name='attempts')
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    nilai = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Attempt: {self.siswa.user.get_full_name()} - {self.kuis.judul}"

class QuizAnswer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    soal = models.ForeignKey(QuizSoal, on_delete=models.CASCADE)
    jawaban_siswa = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Jawaban Soal {self.soal.id} - Attempt {self.attempt.id}"

class PortofolioSiswa(models.Model):
    KATEGORI_CHOICES = (
        ('proyek', 'Karya Proyek'),
        ('source_code', 'Source Code / Git Repositori'),
        ('sertifikat', 'Sertifikat Kompetensi'),
        ('praktik', 'Dokumentasi Praktik Kejuruan'),
    )
    siswa = models.ForeignKey(Siswa, on_delete=models.CASCADE, related_name='portofolio_list')
    judul = models.CharField(max_length=200)
    kategori = models.CharField(max_length=20, choices=KATEGORI_CHOICES)
    deskripsi = models.TextField()
    file_dokumentasi = models.FileField(upload_to='portofolio_files/', blank=True, null=True)
    link_tautan = models.URLField(blank=True, null=True, help_text='Link to project live version, GitHub, or YouTube video')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Portofolio: {self.judul} - {self.siswa.user.get_full_name()}"

class MonitoringPKL(models.Model):
    siswa = models.OneToOneField(Siswa, on_delete=models.CASCADE, related_name='pkl_profile')
    nama_industri = models.CharField(max_length=150)
    alamat_industri = models.TextField()
    tanggal_mulai = models.DateField()
    tanggal_selesai = models.DateField()
    guru_pembimbing = models.ForeignKey(Guru, on_delete=models.SET_NULL, null=True, related_name='pkl_bimbingan')

    def __str__(self):
        return f"PKL: {self.siswa.user.get_full_name()} di {self.nama_industri}"

class JurnalPKL(models.Model):
    STATUS_ABSENSI = (
        ('hadir', 'Hadir'),
        ('izin', 'Izin'),
        ('sakit', 'Sakit'),
        ('alpa', 'Alpa'),
    )
    pkl = models.ForeignKey(MonitoringPKL, on_delete=models.CASCADE, related_name='jurnal_list')
    minggu_ke = models.IntegerField()
    tanggal_awal = models.DateField()
    tanggal_akhir = models.DateField()
    kegiatan = models.TextField(help_text='Deskripsi kegiatan praktik mingguan')
    status_absensi = models.CharField(max_length=10, choices=STATUS_ABSENSI, default='hadir')
    file_laporan = models.FileField(upload_to='pkl_files/', blank=True, null=True, help_text='Dokumentasi foto kegiatan / file PDF laporan mingguan')
    nilai_industri = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text='Nilai dari pembimbing industri')
    catatan_pembimbing = models.TextField(blank=True, null=True, help_text='Catatan umpan balik guru pembimbing')
    is_verified = models.BooleanField(default=False)

    class Meta:
        unique_together = ('pkl', 'minggu_ke')

    def __str__(self):
        return f"Jurnal Minggu {self.minggu_ke} - {self.pkl.siswa.user.get_full_name()}"

