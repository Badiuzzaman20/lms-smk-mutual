from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    Role, User, Jurusan, Kelas, PreRegisteredUser,
    Guru, Siswa, MataPelajaran, JadwalKBM, Pertemuan,
    MateriMedia, AktivitasPresensi, PresensiSiswa,
    ForumDiskusi, KomentarForum, LiveClass,
    TugasUjian, TugasSubmission, QuizSoal, QuizAttempt, QuizAnswer,
    PortofolioSiswa, MonitoringPKL, JurnalPKL
)

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'get_full_name', 'role', 'is_suspended', 'is_active')
    list_filter = ('role', 'is_suspended', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('LMS Info', {'fields': ('role', 'is_suspended')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('LMS Info', {'fields': ('role',)}),
    )

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Jurusan)
class JurusanAdmin(admin.ModelAdmin):
    list_display = ('kode', 'nama')

@admin.register(Kelas)
class KelasAdmin(admin.ModelAdmin):
    list_display = ('nama', 'tingkat', 'jurusan')
    list_filter = ('tingkat', 'jurusan')

@admin.register(PreRegisteredUser)
class PreRegisteredUserAdmin(admin.ModelAdmin):
    list_display = ('nip_nisn', 'nama', 'role', 'kelas')
    list_filter = ('role',)
    search_fields = ('nip_nisn', 'nama')

@admin.register(Guru)
class GuruAdmin(admin.ModelAdmin):
    list_display = ('get_nama', 'nip', 'jabatan')
    search_fields = ('nip', 'user__first_name', 'user__last_name')
    def get_nama(self, obj): return obj.user.get_full_name()
    get_nama.short_description = 'Nama'

@admin.register(Siswa)
class SiswaAdmin(admin.ModelAdmin):
    list_display = ('get_nama', 'nisn', 'kelas')
    list_filter = ('kelas',)
    search_fields = ('nisn', 'user__first_name', 'user__last_name')
    def get_nama(self, obj): return obj.user.get_full_name()
    get_nama.short_description = 'Nama'

@admin.register(MataPelajaran)
class MataPelajaranAdmin(admin.ModelAdmin):
    list_display = ('kode', 'nama', 'kategori', 'jurusan')
    list_filter = ('kategori', 'jurusan')

@admin.register(JadwalKBM)
class JadwalKBMAdmin(admin.ModelAdmin):
    list_display = ('mata_pelajaran', 'kelas', 'guru', 'hari', 'jam_mulai', 'jam_selesai')
    list_filter = ('hari', 'kelas', 'guru')

@admin.register(Pertemuan)
class PertemuanAdmin(admin.ModelAdmin):
    list_display = ('judul', 'urutan', 'jadwal')
    list_filter = ('jadwal__kelas',)

@admin.register(MateriMedia)
class MateriMediaAdmin(admin.ModelAdmin):
    list_display = ('judul', 'tipe', 'pertemuan')
    list_filter = ('tipe',)

@admin.register(TugasUjian)
class TugasUjianAdmin(admin.ModelAdmin):
    list_display = ('judul', 'tipe', 'deadline', 'pertemuan')
    list_filter = ('tipe',)

@admin.register(TugasSubmission)
class TugasSubmissionAdmin(admin.ModelAdmin):
    list_display = ('siswa', 'tugas', 'nilai', 'submitted_at')
    list_filter = ('nilai',)

@admin.register(QuizSoal)
class QuizSoalAdmin(admin.ModelAdmin):
    list_display = ('kuis', 'tipe', 'pertanyaan')
    list_filter = ('tipe',)

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('siswa', 'kuis', 'nilai', 'completed_at')

@admin.register(PortofolioSiswa)
class PortofolioAdmin(admin.ModelAdmin):
    list_display = ('judul', 'kategori', 'siswa', 'created_at')
    list_filter = ('kategori',)

@admin.register(MonitoringPKL)
class MonitoringPKLAdmin(admin.ModelAdmin):
    list_display = ('siswa', 'nama_industri', 'guru_pembimbing', 'tanggal_mulai', 'tanggal_selesai')

@admin.register(JurnalPKL)
class JurnalPKLAdmin(admin.ModelAdmin):
    list_display = ('pkl', 'minggu_ke', 'is_verified', 'status_absensi')
    list_filter = ('is_verified', 'status_absensi')

admin.site.register(AktivitasPresensi)
admin.site.register(PresensiSiswa)
admin.site.register(ForumDiskusi)
admin.site.register(KomentarForum)
admin.site.register(LiveClass)
admin.site.register(QuizAnswer)
