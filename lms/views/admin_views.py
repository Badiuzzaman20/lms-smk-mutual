from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from lms.models import (
    User, Role, Guru, Siswa, Kelas, Jurusan, MataPelajaran,
    JadwalKBM, PreRegisteredUser, PresensiSiswa, TugasSubmission
)


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.role or request.user.role.name != 'admin':
            messages.error(request, 'Akses ditolak.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


@login_required
@admin_required
def admin_dashboard(request):
    total_siswa = Siswa.objects.count()
    total_guru = Guru.objects.count()
    total_kelas = Kelas.objects.count()
    total_mapel = MataPelajaran.objects.count()
    jadwal_hari_ini = JadwalKBM.objects.filter(
        hari=['Senin','Selasa','Rabu','Kamis','Jumat','Sabtu'][timezone.localtime(timezone.now()).weekday() % 6]
    ).select_related('guru__user', 'kelas', 'mata_pelajaran').order_by('jam_mulai')[:8]
    context = {
        'total_siswa': total_siswa,
        'total_guru': total_guru,
        'total_kelas': total_kelas,
        'total_mapel': total_mapel,
        'jadwal_hari_ini': jadwal_hari_ini,
    }
    return render(request, 'lms/admin/dashboard.html', context)


@login_required
@admin_required
def manage_users(request):
    guru_list = Guru.objects.all().select_related('user')
    siswa_list = Siswa.objects.all().select_related('user', 'kelas__jurusan')
    kelas_list = Kelas.objects.all().select_related('jurusan')
    context = {'guru_list': guru_list, 'siswa_list': siswa_list, 'kelas_list': kelas_list}
    return render(request, 'lms/admin/users.html', context)


@login_required
@admin_required
def tambah_guru(request):
    if request.method == 'POST':
        nama = request.POST.get('nama', '').strip()
        nip = request.POST.get('nip', '').strip()
        jabatan = request.POST.get('jabatan', 'Guru Mata Pelajaran').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        if Guru.objects.filter(nip=nip).exists():
            messages.error(request, f'NIP {nip} sudah terdaftar.')
            return redirect('manage_users')

        role_obj, _ = Role.objects.get_or_create(name='guru')
        username = email.split('@')[0] if email else nip
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        parts = nama.split()
        first_name = ' '.join(parts[:-1]) if len(parts) > 1 else nama
        last_name = parts[-1] if len(parts) > 1 else ''
        user = User.objects.create_user(username=username, email=email, password=password,
                                        first_name=first_name, last_name=last_name, role=role_obj)
        Guru.objects.create(user=user, nip=nip, jabatan=jabatan)
        PreRegisteredUser.objects.get_or_create(nip_nisn=nip, defaults={'role': 'guru', 'nama': nama})
        messages.success(request, f'Guru {nama} berhasil ditambahkan.')
    return redirect('manage_users')


@login_required
@admin_required
def edit_guru(request, guru_id):
    guru = get_object_or_404(Guru, id=guru_id)
    if request.method == 'POST':
        nama = request.POST.get('nama', '').strip()
        nip = request.POST.get('nip', '').strip()
        jabatan = request.POST.get('jabatan', '').strip()
        email = request.POST.get('email', '').strip()

        if Guru.objects.filter(nip=nip).exclude(id=guru_id).exists():
            messages.error(request, f'NIP {nip} sudah digunakan guru lain.')
            return redirect('manage_users')

        parts = nama.split()
        guru.user.first_name = ' '.join(parts[:-1]) if len(parts) > 1 else nama
        guru.user.last_name = parts[-1] if len(parts) > 1 else ''
        guru.user.email = email
        guru.user.save()
        guru.nip = nip
        guru.jabatan = jabatan
        guru.save()
        messages.success(request, f'Data guru {nama} berhasil diperbarui.')
    return redirect('manage_users')


@login_required
@admin_required
def tambah_siswa(request):
    if request.method == 'POST':
        nama = request.POST.get('nama', '').strip()
        nisn = request.POST.get('nisn', '').strip()
        kelas_id = request.POST.get('kelas_id')
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        if Siswa.objects.filter(nisn=nisn).exists():
            messages.error(request, f'NISN {nisn} sudah terdaftar.')
            return redirect('manage_users')

        kelas = get_object_or_404(Kelas, id=kelas_id)
        role_obj, _ = Role.objects.get_or_create(name='siswa')
        username = email.split('@')[0] if email else nisn
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        parts = nama.split()
        first_name = ' '.join(parts[:-1]) if len(parts) > 1 else nama
        last_name = parts[-1] if len(parts) > 1 else ''
        user = User.objects.create_user(username=username, email=email, password=password,
                                        first_name=first_name, last_name=last_name, role=role_obj)
        Siswa.objects.create(user=user, nisn=nisn, kelas=kelas)
        PreRegisteredUser.objects.get_or_create(nip_nisn=nisn, defaults={'role': 'siswa', 'nama': nama, 'kelas': kelas})
        messages.success(request, f'Siswa {nama} berhasil ditambahkan.')
    return redirect('manage_users')


@login_required
@admin_required
def edit_siswa(request, siswa_id):
    siswa = get_object_or_404(Siswa, id=siswa_id)
    if request.method == 'POST':
        nama = request.POST.get('nama', '').strip()
        nisn = request.POST.get('nisn', '').strip()
        kelas_id = request.POST.get('kelas_id')
        email = request.POST.get('email', '').strip()

        if Siswa.objects.filter(nisn=nisn).exclude(id=siswa_id).exists():
            messages.error(request, f'NISN {nisn} sudah digunakan siswa lain.')
            return redirect('manage_users')

        kelas = get_object_or_404(Kelas, id=kelas_id)
        parts = nama.split()
        siswa.user.first_name = ' '.join(parts[:-1]) if len(parts) > 1 else nama
        siswa.user.last_name = parts[-1] if len(parts) > 1 else ''
        siswa.user.email = email
        siswa.user.save()
        siswa.nisn = nisn
        siswa.kelas = kelas
        siswa.save()
        messages.success(request, f'Data siswa {nama} berhasil diperbarui.')
    return redirect('manage_users')


@login_required
@admin_required
def toggle_suspend(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_suspended = not user.is_suspended
    user.save()
    status = 'ditangguhkan' if user.is_suspended else 'diaktifkan kembali'
    messages.success(request, f'Akun {user.get_full_name()} berhasil {status}.')
    return redirect('manage_users')


@login_required
@admin_required
def hapus_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    nama = user.get_full_name()
    user.delete()
    messages.success(request, f'Akun {nama} berhasil dihapus.')
    return redirect('manage_users')


@login_required
@admin_required
def manage_akademik(request):
    jurusan_list = Jurusan.objects.all()
    kelas_list = Kelas.objects.all().select_related('jurusan')
    mapel_list = MataPelajaran.objects.all().select_related('jurusan')

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'tambah_jurusan':
            nama = request.POST.get('nama_jurusan', '').strip()
            kode = request.POST.get('kode_jurusan', '').strip().upper()
            if nama and kode:
                Jurusan.objects.get_or_create(kode=kode, defaults={'nama': nama})
                messages.success(request, f'Jurusan {nama} berhasil ditambahkan.')
        elif action == 'tambah_kelas':
            tingkat = request.POST.get('tingkat')
            nama_kelas = request.POST.get('nama_kelas', '').strip()
            jurusan_id = request.POST.get('jurusan_id')
            if tingkat and nama_kelas and jurusan_id:
                jurusan = get_object_or_404(Jurusan, id=jurusan_id)
                Kelas.objects.get_or_create(nama=nama_kelas, defaults={'tingkat': tingkat, 'jurusan': jurusan})
                messages.success(request, f'Kelas {nama_kelas} berhasil ditambahkan.')
        elif action == 'tambah_mapel':
            nama_mapel = request.POST.get('nama_mapel', '').strip()
            kode_mapel = request.POST.get('kode_mapel', '').strip().upper()
            kategori = request.POST.get('kategori')
            jurusan_id = request.POST.get('jurusan_id_mapel') or None
            jurusan = Jurusan.objects.filter(id=jurusan_id).first() if jurusan_id else None
            if nama_mapel and kode_mapel and kategori:
                MataPelajaran.objects.get_or_create(kode=kode_mapel, defaults={
                    'nama': nama_mapel, 'kategori': kategori, 'jurusan': jurusan
                })
                messages.success(request, f'Mata Pelajaran {nama_mapel} berhasil ditambahkan.')
        return redirect('manage_akademik')

    context = {
        'jurusan_list': jurusan_list,
        'kelas_list': kelas_list,
        'mapel_list': mapel_list,
    }
    return render(request, 'lms/admin/akademik.html', context)


@login_required
@admin_required
def edit_jurusan(request, jurusan_id):
    jurusan = get_object_or_404(Jurusan, id=jurusan_id)
    if request.method == 'POST':
        nama = request.POST.get('nama_jurusan', '').strip()
        kode = request.POST.get('kode_jurusan', '').strip().upper()
        if nama and kode:
            if Jurusan.objects.filter(kode=kode).exclude(id=jurusan_id).exists():
                messages.error(request, f'Kode {kode} sudah digunakan jurusan lain.')
            else:
                jurusan.nama = nama
                jurusan.kode = kode
                jurusan.save()
                messages.success(request, f'Jurusan {nama} berhasil diperbarui.')
    return redirect('manage_akademik')


@login_required
@admin_required
def hapus_jurusan(request, jurusan_id):
    jurusan = get_object_or_404(Jurusan, id=jurusan_id)
    nama = jurusan.nama
    jurusan.delete()
    messages.success(request, f'Jurusan {nama} berhasil dihapus.')
    return redirect('manage_akademik')


@login_required
@admin_required
def edit_kelas(request, kelas_id):
    kelas = get_object_or_404(Kelas, id=kelas_id)
    if request.method == 'POST':
        tingkat = request.POST.get('tingkat', '').strip()
        nama_kelas = request.POST.get('nama_kelas', '').strip()
        jurusan_id = request.POST.get('jurusan_id')
        if tingkat and nama_kelas and jurusan_id:
            jurusan = get_object_or_404(Jurusan, id=jurusan_id)
            kelas.tingkat = tingkat
            kelas.nama = nama_kelas
            kelas.jurusan = jurusan
            kelas.save()
            messages.success(request, f'Kelas {nama_kelas} berhasil diperbarui.')
    return redirect('manage_akademik')


@login_required
@admin_required
def hapus_kelas(request, kelas_id):
    kelas = get_object_or_404(Kelas, id=kelas_id)
    nama = kelas.nama
    kelas.delete()
    messages.success(request, f'Kelas {nama} berhasil dihapus.')
    return redirect('manage_akademik')


@login_required
@admin_required
def edit_mapel(request, mapel_id):
    mapel = get_object_or_404(MataPelajaran, id=mapel_id)
    if request.method == 'POST':
        nama_mapel = request.POST.get('nama_mapel', '').strip()
        kode_mapel = request.POST.get('kode_mapel', '').strip().upper()
        kategori = request.POST.get('kategori', '').strip()
        jurusan_id = request.POST.get('jurusan_id_mapel') or None
        jurusan = Jurusan.objects.filter(id=jurusan_id).first() if jurusan_id else None
        if nama_mapel and kode_mapel and kategori:
            if MataPelajaran.objects.filter(kode=kode_mapel).exclude(id=mapel_id).exists():
                messages.error(request, f'Kode mapel {kode_mapel} sudah digunakan.')
            else:
                mapel.nama = nama_mapel
                mapel.kode = kode_mapel
                mapel.kategori = kategori
                mapel.jurusan = jurusan
                mapel.save()
                messages.success(request, f'Mata Pelajaran {nama_mapel} berhasil diperbarui.')
    return redirect('manage_akademik')


@login_required
@admin_required
def hapus_mapel(request, mapel_id):
    mapel = get_object_or_404(MataPelajaran, id=mapel_id)
    nama = mapel.nama
    mapel.delete()
    messages.success(request, f'Mata Pelajaran {nama} berhasil dihapus.')
    return redirect('manage_akademik')


@login_required
@admin_required
def manage_jadwal(request):
    jadwal_list = JadwalKBM.objects.all().select_related('guru__user', 'kelas', 'mata_pelajaran')
    guru_list = Guru.objects.all().select_related('user')
    kelas_list = Kelas.objects.all().select_related('jurusan')
    mapel_list = MataPelajaran.objects.all()

    if request.method == 'POST':
        mapel_id = request.POST.get('mapel_id')
        guru_id = request.POST.get('guru_id')
        kelas_id = request.POST.get('kelas_id')
        hari = request.POST.get('hari')
        jam_mulai = request.POST.get('jam_mulai')
        jam_selesai = request.POST.get('jam_selesai')
        if all([mapel_id, guru_id, kelas_id, hari, jam_mulai, jam_selesai]):
            JadwalKBM.objects.create(
                mata_pelajaran_id=mapel_id, guru_id=guru_id,
                kelas_id=kelas_id, hari=hari,
                jam_mulai=jam_mulai, jam_selesai=jam_selesai
            )
            messages.success(request, 'Jadwal KBM berhasil ditambahkan.')
        return redirect('manage_jadwal')

    context = {
        'jadwal_list': jadwal_list,
        'guru_list': guru_list,
        'kelas_list': kelas_list,
        'mapel_list': mapel_list,
        'hari_choices': ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu'],
    }
    return render(request, 'lms/admin/jadwal.html', context)


@login_required
@admin_required
def edit_jadwal(request, jadwal_id):
    jadwal = get_object_or_404(JadwalKBM, id=jadwal_id)
    if request.method == 'POST':
        mapel_id = request.POST.get('mapel_id')
        guru_id = request.POST.get('guru_id')
        kelas_id = request.POST.get('kelas_id')
        hari = request.POST.get('hari')
        jam_mulai = request.POST.get('jam_mulai')
        jam_selesai = request.POST.get('jam_selesai')
        if all([mapel_id, guru_id, kelas_id, hari, jam_mulai, jam_selesai]):
            jadwal.mata_pelajaran_id = mapel_id
            jadwal.guru_id = guru_id
            jadwal.kelas_id = kelas_id
            jadwal.hari = hari
            jadwal.jam_mulai = jam_mulai
            jadwal.jam_selesai = jam_selesai
            jadwal.save()
            messages.success(request, 'Jadwal KBM berhasil diperbarui.')
    return redirect('manage_jadwal')


@login_required
@admin_required
def hapus_jadwal(request, jadwal_id):
    jadwal = get_object_or_404(JadwalKBM, id=jadwal_id)
    jadwal.delete()
    messages.success(request, 'Jadwal KBM berhasil dihapus.')
    return redirect('manage_jadwal')


@login_required
@admin_required
def monitoring(request):
    semua_siswa = Siswa.objects.all().select_related('user', 'kelas__jurusan')
    presensi_data = []
    for siswa in semua_siswa:
        total_absen = PresensiSiswa.objects.filter(siswa=siswa).count()
        hadir = PresensiSiswa.objects.filter(siswa=siswa, status='hadir').count()
        persen_hadir = round((hadir / total_absen * 100), 1) if total_absen > 0 else 0
        avg_nilai = list(TugasSubmission.objects.filter(
            siswa=siswa, nilai__isnull=False
        ).values_list('nilai', flat=True))
        rata_nilai = round(sum(avg_nilai) / len(avg_nilai), 2) if avg_nilai else '-'
        presensi_data.append({
            'siswa': siswa,
            'total_absen': total_absen,
            'hadir': hadir,
            'persen_hadir': persen_hadir,
            'rata_nilai': rata_nilai,
        })
    all_users = User.objects.all().order_by('-date_joined')[:20]
    context = {'presensi_data': presensi_data, 'all_users': all_users}
    return render(request, 'lms/admin/monitoring.html', context)
