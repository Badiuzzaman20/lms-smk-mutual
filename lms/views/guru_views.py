from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from lms.models import (
    Guru, JadwalKBM, Pertemuan, MateriMedia, AktivitasPresensi,
    ForumDiskusi, LiveClass, TugasUjian, QuizSoal, TugasSubmission,
    MonitoringPKL, JurnalPKL, Siswa
)


def guru_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.role or request.user.role.name != 'guru':
            messages.error(request, 'Akses ditolak. Halaman ini hanya untuk Guru.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


@login_required
@guru_required
def guru_dashboard(request):
    guru = get_object_or_404(Guru, user=request.user)
    hari_map = {0: 'Senin', 1: 'Selasa', 2: 'Rabu', 3: 'Kamis', 4: 'Jumat', 5: 'Sabtu', 6: 'Senin'}
    hari_ini = hari_map[timezone.localtime(timezone.now()).weekday()]
    jadwal_hari_ini = JadwalKBM.objects.filter(guru=guru, hari=hari_ini).select_related('mata_pelajaran', 'kelas').order_by('jam_mulai')
    semua_jadwal = JadwalKBM.objects.filter(guru=guru).select_related('mata_pelajaran', 'kelas').order_by('hari', 'jam_mulai')

    # Pending submissions to grade
    pending_submissions = TugasSubmission.objects.filter(
        tugas__pertemuan__jadwal__guru=guru, nilai__isnull=True
    ).select_related('siswa__user', 'tugas').order_by('-submitted_at')[:10]

    context = {
        'guru': guru,
        'hari_ini': hari_ini,
        'jadwal_hari_ini': jadwal_hari_ini,
        'semua_jadwal': semua_jadwal,
        'pending_submissions': pending_submissions,
        'pending_count': TugasSubmission.objects.filter(tugas__pertemuan__jadwal__guru=guru, nilai__isnull=True).count(),
    }
    return render(request, 'lms/guru/dashboard.html', context)


@login_required
@guru_required
def kelas_detail(request, jadwal_id):
    guru = get_object_or_404(Guru, user=request.user)
    jadwal = get_object_or_404(JadwalKBM, id=jadwal_id, guru=guru)
    pertemuan_list = Pertemuan.objects.filter(jadwal=jadwal).prefetch_related(
        'materi_list', 'presensi_activity', 'forum_list', 'live_class', 'tugas_ujian_list'
    )
    siswa_list = Siswa.objects.filter(kelas=jadwal.kelas).select_related('user')
    context = {
        'jadwal': jadwal,
        'pertemuan_list': pertemuan_list,
        'siswa_list': siswa_list,
        'siswa_count': siswa_list.count(),
    }
    return render(request, 'lms/guru/kelas_detail.html', context)


@login_required
@guru_required
def tambah_pertemuan(request, jadwal_id):
    guru = get_object_or_404(Guru, user=request.user)
    jadwal = get_object_or_404(JadwalKBM, id=jadwal_id, guru=guru)
    if request.method == 'POST':
        judul = request.POST.get('judul', '').strip()
        deskripsi = request.POST.get('deskripsi', '').strip()
        urutan = Pertemuan.objects.filter(jadwal=jadwal).count() + 1
        Pertemuan.objects.create(jadwal=jadwal, judul=judul, deskripsi=deskripsi, urutan=urutan)
        messages.success(request, f'Pertemuan "{judul}" berhasil ditambahkan.')
    return redirect('guru_kelas_detail', jadwal_id=jadwal_id)


@login_required
@guru_required
def tambah_materi(request, pertemuan_id):
    guru = get_object_or_404(Guru, user=request.user)
    pertemuan = get_object_or_404(Pertemuan, id=pertemuan_id, jadwal__guru=guru)
    if request.method == 'POST':
        tipe = request.POST.get('tipe')
        judul = request.POST.get('judul', '').strip()
        deskripsi = request.POST.get('deskripsi', '').strip()
        file = request.FILES.get('file')
        video_embed = request.POST.get('video_embed', '').strip()
        link_eksternal = request.POST.get('link_eksternal', '').strip()
        MateriMedia.objects.create(
            pertemuan=pertemuan, tipe=tipe, judul=judul, deskripsi=deskripsi,
            file=file if file else None,
            video_embed=video_embed if video_embed else None,
            link_eksternal=link_eksternal if link_eksternal else None,
        )
        messages.success(request, f'Materi "{judul}" berhasil ditambahkan.')
    return redirect('guru_kelas_detail', jadwal_id=pertemuan.jadwal_id)


@login_required
@guru_required
def buka_presensi(request, pertemuan_id):
    guru = get_object_or_404(Guru, user=request.user)
    pertemuan = get_object_or_404(Pertemuan, id=pertemuan_id, jadwal__guru=guru)
    if request.method == 'POST':
        batas_menit = int(request.POST.get('batas_menit', 30))
        batas_waktu = timezone.now() + timezone.timedelta(minutes=batas_menit)
        AktivitasPresensi.objects.create(pertemuan=pertemuan, batas_waktu=batas_waktu)
        messages.success(request, f'Presensi dibuka selama {batas_menit} menit.')
    return redirect('guru_kelas_detail', jadwal_id=pertemuan.jadwal_id)


@login_required
@guru_required
def tambah_forum(request, pertemuan_id):
    guru = get_object_or_404(Guru, user=request.user)
    pertemuan = get_object_or_404(Pertemuan, id=pertemuan_id, jadwal__guru=guru)
    if request.method == 'POST':
        judul = request.POST.get('judul', '').strip()
        deskripsi = request.POST.get('deskripsi', '').strip()
        ForumDiskusi.objects.create(pertemuan=pertemuan, judul=judul, deskripsi=deskripsi)
        messages.success(request, f'Forum "{judul}" berhasil dibuat.')
    return redirect('guru_kelas_detail', jadwal_id=pertemuan.jadwal_id)


@login_required
@guru_required
def tambah_live(request, pertemuan_id):
    guru = get_object_or_404(Guru, user=request.user)
    pertemuan = get_object_or_404(Pertemuan, id=pertemuan_id, jadwal__guru=guru)
    if request.method == 'POST':
        platform = request.POST.get('platform', 'gmeet')
        link = request.POST.get('link', '').strip()
        waktu_mulai = request.POST.get('waktu_mulai')
        LiveClass.objects.create(pertemuan=pertemuan, platform=platform, link=link, waktu_mulai=waktu_mulai)
        messages.success(request, 'Link Live Class berhasil ditambahkan.')
    return redirect('guru_kelas_detail', jadwal_id=pertemuan.jadwal_id)


@login_required
@guru_required
def tambah_tugas(request, pertemuan_id):
    guru = get_object_or_404(Guru, user=request.user)
    pertemuan = get_object_or_404(Pertemuan, id=pertemuan_id, jadwal__guru=guru)
    if request.method == 'POST':
        judul = request.POST.get('judul', '').strip()
        deskripsi = request.POST.get('deskripsi', '').strip()
        deadline = request.POST.get('deadline')
        TugasUjian.objects.create(pertemuan=pertemuan, tipe='tugas', judul=judul, deskripsi=deskripsi, deadline=deadline)
        messages.success(request, f'Tugas "{judul}" berhasil dibuat.')
    return redirect('guru_kelas_detail', jadwal_id=pertemuan.jadwal_id)


@login_required
@guru_required
def tambah_kuis(request, pertemuan_id):
    guru = get_object_or_404(Guru, user=request.user)
    pertemuan = get_object_or_404(Pertemuan, id=pertemuan_id, jadwal__guru=guru)
    if request.method == 'POST':
        judul = request.POST.get('judul', '').strip()
        deskripsi = request.POST.get('deskripsi', '').strip()
        deadline = request.POST.get('deadline')
        waktu = int(request.POST.get('waktu_pengerjaan', 60))
        kuis = TugasUjian.objects.create(
            pertemuan=pertemuan, tipe='kuis', judul=judul,
            deskripsi=deskripsi, deadline=deadline, waktu_pengerjaan=waktu
        )
        messages.success(request, f'Kuis "{judul}" berhasil dibuat. Tambahkan soal sekarang.')
        return redirect('tambah_soal', kuis_id=kuis.id)
    return redirect('guru_kelas_detail', jadwal_id=pertemuan.jadwal_id)


@login_required
@guru_required
def tambah_soal(request, kuis_id):
    guru = get_object_or_404(Guru, user=request.user)
    kuis = get_object_or_404(TugasUjian, id=kuis_id, tipe='kuis', pertemuan__jadwal__guru=guru)
    soal_list = QuizSoal.objects.filter(kuis=kuis)
    if request.method == 'POST':
        tipe_soal = request.POST.get('tipe_soal', 'pilihan_ganda')
        pertanyaan = request.POST.get('pertanyaan', '').strip()
        opsi_a = request.POST.get('opsi_a', '').strip()
        opsi_b = request.POST.get('opsi_b', '').strip()
        opsi_c = request.POST.get('opsi_c', '').strip()
        opsi_d = request.POST.get('opsi_d', '').strip()
        opsi_e = request.POST.get('opsi_e', '').strip()
        jawaban_benar = request.POST.get('jawaban_benar', '').strip().upper()
        QuizSoal.objects.create(
            kuis=kuis, tipe=tipe_soal, pertanyaan=pertanyaan,
            opsi_a=opsi_a, opsi_b=opsi_b, opsi_c=opsi_c,
            opsi_d=opsi_d, opsi_e=opsi_e, jawaban_benar=jawaban_benar
        )
        messages.success(request, 'Soal berhasil ditambahkan.')
        return redirect('tambah_soal', kuis_id=kuis_id)
    context = {'kuis': kuis, 'soal_list': soal_list}
    return render(request, 'lms/guru/tambah_soal.html', context)


@login_required
@guru_required
def penilaian(request):
    guru = get_object_or_404(Guru, user=request.user)
    submissions = TugasSubmission.objects.filter(
        tugas__pertemuan__jadwal__guru=guru
    ).select_related('siswa__user', 'tugas__pertemuan__jadwal__mata_pelajaran', 'tugas__pertemuan__jadwal__kelas').order_by('nilai', '-submitted_at')
    context = {'submissions': submissions}
    return render(request, 'lms/guru/penilaian.html', context)


@login_required
@guru_required
def beri_nilai(request, submission_id):
    guru = get_object_or_404(Guru, user=request.user)
    submission = get_object_or_404(TugasSubmission, id=submission_id, tugas__pertemuan__jadwal__guru=guru)
    if request.method == 'POST':
        nilai = request.POST.get('nilai')
        feedback = request.POST.get('feedback', '').strip()
        submission.nilai = nilai
        submission.feedback = feedback
        submission.save()
        messages.success(request, f'Nilai untuk {submission.siswa.user.get_full_name()} berhasil disimpan.')
    return redirect('guru_penilaian')


@login_required
@guru_required
def pkl_monitoring(request):
    guru = get_object_or_404(Guru, user=request.user)
    pkl_list = MonitoringPKL.objects.filter(guru_pembimbing=guru).select_related('siswa__user', 'siswa__kelas')
    context = {'pkl_list': pkl_list}
    return render(request, 'lms/guru/pkl_monitoring.html', context)


@login_required
@guru_required
def verifikasi_jurnal(request, jurnal_id):
    guru = get_object_or_404(Guru, user=request.user)
    jurnal = get_object_or_404(JurnalPKL, id=jurnal_id, pkl__guru_pembimbing=guru)
    if request.method == 'POST':
        catatan = request.POST.get('catatan', '').strip()
        nilai_industri = request.POST.get('nilai_industri')
        jurnal.catatan_pembimbing = catatan
        if nilai_industri:
            jurnal.nilai_industri = nilai_industri
        jurnal.is_verified = True
        jurnal.save()
        messages.success(request, f'Jurnal Minggu {jurnal.minggu_ke} berhasil diverifikasi.')
    return redirect('guru_pkl_monitoring')
