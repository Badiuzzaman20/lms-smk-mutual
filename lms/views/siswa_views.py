from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from lms.models import (
    Siswa, JadwalKBM, Pertemuan, AktivitasPresensi, PresensiSiswa,
    ForumDiskusi, KomentarForum, TugasUjian, TugasSubmission,
    QuizSoal, QuizAttempt, QuizAnswer, PortofolioSiswa,
    MonitoringPKL, JurnalPKL
)


def siswa_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.role or request.user.role.name != 'siswa':
            messages.error(request, 'Akses ditolak. Halaman ini hanya untuk Siswa.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


@login_required
@siswa_required
def siswa_dashboard(request):
    siswa = get_object_or_404(Siswa, user=request.user)
    jadwal_list = JadwalKBM.objects.filter(kelas=siswa.kelas).select_related('mata_pelajaran', 'guru__user')

    # Progress per mata pelajaran
    mapel_progress = []
    for jadwal in jadwal_list:
        total_pertemuan = Pertemuan.objects.filter(jadwal=jadwal).count()
        if total_pertemuan == 0:
            progress = 0
        else:
            # Count pertemuan where student submitted or attended
            attended = PresensiSiswa.objects.filter(siswa=siswa, presensi__pertemuan__jadwal=jadwal, status='hadir').count()
            progress = min(round((attended / total_pertemuan) * 100), 100)
        mapel_progress.append({
            'jadwal': jadwal,
            'progress': progress,
            'total_pertemuan': total_pertemuan,
        })

    # Upcoming tasks/quizzes
    tugas_upcoming = TugasUjian.objects.filter(
        pertemuan__jadwal__kelas=siswa.kelas,
        deadline__gte=timezone.now()
    ).exclude(
        submissions__siswa=siswa
    ).order_by('deadline')[:6]

    context = {
        'siswa': siswa,
        'mapel_progress': mapel_progress,
        'tugas_upcoming': tugas_upcoming,
    }
    return render(request, 'lms/siswa/dashboard.html', context)


@login_required
@siswa_required
def kelas_detail(request, jadwal_id):
    siswa = get_object_or_404(Siswa, user=request.user)
    jadwal = get_object_or_404(JadwalKBM, id=jadwal_id, kelas=siswa.kelas)
    pertemuan_list = []
    for p in Pertemuan.objects.filter(jadwal=jadwal).prefetch_related(
        'materi_list', 'presensi_activity', 'forum_list__komentar_list__user',
        'live_class', 'tugas_ujian_list'
    ):
        # Presensi
        presensi_aktif = p.presensi_activity.filter(batas_waktu__gte=timezone.now()).first()
        sudah_absen = PresensiSiswa.objects.filter(presensi__pertemuan=p, siswa=siswa).first()
        # Submissions
        submissions_saya = {
            s.tugas_id: s for s in TugasSubmission.objects.filter(tugas__pertemuan=p, siswa=siswa)
        }
        sudah_submit_ids = set(str(k) for k in submissions_saya.keys())
        pertemuan_list.append({
            'pertemuan': p,
            'presensi_aktif': presensi_aktif,
            'sudah_absen': sudah_absen,
            'submissions_saya': submissions_saya,
            'sudah_submit_ids': sudah_submit_ids,
        })
    context = {
        'jadwal': jadwal,
        'siswa': siswa,
        'pertemuan_list': pertemuan_list,
    }
    return render(request, 'lms/siswa/kelas_detail.html', context)


@login_required
@siswa_required
def absen(request, presensi_id):
    siswa = get_object_or_404(Siswa, user=request.user)
    presensi = get_object_or_404(AktivitasPresensi, id=presensi_id)
    jadwal_id = presensi.pertemuan.jadwal_id

    if presensi.pertemuan.jadwal.kelas != siswa.kelas:
        messages.error(request, 'Akses ditolak.')
        return redirect('siswa_dashboard')

    if timezone.now() > presensi.batas_waktu:
        messages.warning(request, 'Waktu presensi telah habis.')
        return redirect('siswa_kelas_detail', jadwal_id=jadwal_id)

    if PresensiSiswa.objects.filter(presensi=presensi, siswa=siswa).exists():
        messages.warning(request, 'Kamu sudah melakukan absensi.')
        return redirect('siswa_kelas_detail', jadwal_id=jadwal_id)

    if request.method == 'POST':
        status = request.POST.get('status', 'hadir')
        keterangan = request.POST.get('keterangan', '').strip()
        PresensiSiswa.objects.create(presensi=presensi, siswa=siswa, status=status, keterangan=keterangan)
        messages.success(request, f'Absensi "{status.title()}" berhasil dicatat.')
    return redirect('siswa_kelas_detail', jadwal_id=jadwal_id)


@login_required
@siswa_required
def tambah_komentar(request, forum_id):
    siswa = get_object_or_404(Siswa, user=request.user)
    forum = get_object_or_404(ForumDiskusi, id=forum_id)
    jadwal_id = forum.pertemuan.jadwal_id

    if forum.pertemuan.jadwal.kelas != siswa.kelas:
        messages.error(request, 'Akses ditolak.')
        return redirect('siswa_dashboard')

    if request.method == 'POST':
        konten = request.POST.get('konten', '').strip()
        if konten:
            KomentarForum.objects.create(forum=forum, user=request.user, konten=konten)
            messages.success(request, 'Komentar berhasil ditambahkan.')
    return redirect('siswa_kelas_detail', jadwal_id=jadwal_id)


@login_required
@siswa_required
def submit_tugas(request, tugas_id):
    siswa = get_object_or_404(Siswa, user=request.user)
    tugas = get_object_or_404(TugasUjian, id=tugas_id, tipe='tugas')
    jadwal_id = tugas.pertemuan.jadwal_id

    if tugas.pertemuan.jadwal.kelas != siswa.kelas:
        messages.error(request, 'Akses ditolak.')
        return redirect('siswa_dashboard')

    if timezone.now() > tugas.deadline:
        messages.warning(request, 'Waktu pengumpulan tugas telah habis.')
        return redirect('siswa_kelas_detail', jadwal_id=jadwal_id)

    if TugasSubmission.objects.filter(tugas=tugas, siswa=siswa).exists():
        messages.warning(request, 'Kamu sudah mengumpulkan tugas ini.')
        return redirect('siswa_kelas_detail', jadwal_id=jadwal_id)

    if request.method == 'POST':
        file = request.FILES.get('file')
        link = request.POST.get('link', '').strip()
        jawaban = request.POST.get('jawaban_teks', '').strip()
        TugasSubmission.objects.create(
            tugas=tugas, siswa=siswa,
            file=file if file else None,
            link=link if link else None,
            jawaban_teks=jawaban if jawaban else None,
        )
        messages.success(request, 'Tugas berhasil dikumpulkan!')
    return redirect('siswa_kelas_detail', jadwal_id=jadwal_id)


@login_required
@siswa_required
def mulai_kuis(request, kuis_id):
    siswa = get_object_or_404(Siswa, user=request.user)
    kuis = get_object_or_404(TugasUjian, id=kuis_id, tipe='kuis')

    if kuis.pertemuan.jadwal.kelas != siswa.kelas:
        messages.error(request, 'Akses ditolak.')
        return redirect('siswa_dashboard')

    if QuizAttempt.objects.filter(kuis=kuis, siswa=siswa, completed_at__isnull=False).exists():
        messages.warning(request, 'Kamu sudah mengerjakan kuis ini.')
        return redirect('siswa_kelas_detail', jadwal_id=kuis.pertemuan.jadwal_id)

    attempt, created = QuizAttempt.objects.get_or_create(kuis=kuis, siswa=siswa, completed_at__isnull=True)
    soal_list = list(QuizSoal.objects.filter(kuis=kuis))

    context = {
        'kuis': kuis,
        'soal_list': soal_list,
        'attempt': attempt,
        'durasi_detik': kuis.waktu_pengerjaan * 60,
    }
    return render(request, 'lms/siswa/kuis_cbt.html', context)


@login_required
@siswa_required
def selesai_kuis(request, kuis_id):
    siswa = get_object_or_404(Siswa, user=request.user)
    kuis = get_object_or_404(TugasUjian, id=kuis_id, tipe='kuis')
    attempt = get_object_or_404(QuizAttempt, kuis=kuis, siswa=siswa, completed_at__isnull=True)
    jadwal_id = kuis.pertemuan.jadwal_id

    if request.method == 'POST':
        soal_list = QuizSoal.objects.filter(kuis=kuis)
        benar = 0
        for soal in soal_list:
            jawaban = request.POST.get(f'soal_{soal.id}', '').strip().upper()
            is_correct = (soal.tipe == 'pilihan_ganda' and jawaban == soal.jawaban_benar)
            QuizAnswer.objects.update_or_create(
                attempt=attempt, soal=soal,
                defaults={'jawaban_siswa': jawaban, 'is_correct': is_correct}
            )
            if is_correct:
                benar += 1

        total = soal_list.count()
        nilai = round((benar / total) * 100, 2) if total > 0 else 0
        attempt.nilai = nilai
        attempt.completed_at = timezone.now()
        attempt.save()
        messages.success(request, f'Kuis selesai! Nilai kamu: {nilai}')
    return redirect('siswa_kelas_detail', jadwal_id=jadwal_id)


@login_required
@siswa_required
def portofolio(request):
    siswa = get_object_or_404(Siswa, user=request.user)
    porto_list = PortofolioSiswa.objects.filter(siswa=siswa).order_by('-created_at')
    context = {'siswa': siswa, 'porto_list': porto_list}
    return render(request, 'lms/siswa/portofolio.html', context)


@login_required
@siswa_required
def tambah_portofolio(request):
    siswa = get_object_or_404(Siswa, user=request.user)
    if request.method == 'POST':
        judul = request.POST.get('judul', '').strip()
        kategori = request.POST.get('kategori', 'proyek')
        deskripsi = request.POST.get('deskripsi', '').strip()
        file_dok = request.FILES.get('file_dokumentasi')
        link = request.POST.get('link_tautan', '').strip()
        PortofolioSiswa.objects.create(
            siswa=siswa, judul=judul, kategori=kategori, deskripsi=deskripsi,
            file_dokumentasi=file_dok if file_dok else None,
            link_tautan=link if link else None,
        )
        messages.success(request, f'Portofolio "{judul}" berhasil diunggah!')
    return redirect('siswa_portofolio')


@login_required
@siswa_required
def pkl_jurnal(request):
    siswa = get_object_or_404(Siswa, user=request.user)
    pkl = MonitoringPKL.objects.filter(siswa=siswa).first()
    jurnal_list = JurnalPKL.objects.filter(pkl=pkl).order_by('minggu_ke') if pkl else []
    context = {'siswa': siswa, 'pkl': pkl, 'jurnal_list': jurnal_list}
    return render(request, 'lms/siswa/pkl_jurnal.html', context)


@login_required
@siswa_required
def tambah_jurnal(request):
    siswa = get_object_or_404(Siswa, user=request.user)
    pkl = get_object_or_404(MonitoringPKL, siswa=siswa)
    if request.method == 'POST':
        minggu_ke = int(request.POST.get('minggu_ke', 1))
        tanggal_awal = request.POST.get('tanggal_awal')
        tanggal_akhir = request.POST.get('tanggal_akhir')
        kegiatan = request.POST.get('kegiatan', '').strip()
        status_absensi = request.POST.get('status_absensi', 'hadir')
        file_laporan = request.FILES.get('file_laporan')
        JurnalPKL.objects.update_or_create(
            pkl=pkl, minggu_ke=minggu_ke,
            defaults={
                'tanggal_awal': tanggal_awal, 'tanggal_akhir': tanggal_akhir,
                'kegiatan': kegiatan, 'status_absensi': status_absensi,
                'file_laporan': file_laporan if file_laporan else None,
                'is_verified': False,
            }
        )
        messages.success(request, f'Jurnal Minggu ke-{minggu_ke} berhasil disimpan.')
    return redirect('siswa_pkl')
