"""
Seed Data Script - LMS SMK Mutual Kota Magelang
Run with: python seed_data.py

Populates the database with sample data for testing:
- Roles (admin, guru, siswa)
- Admin user
- Jurusan (TKJ, AKL, RPL, BDP)
- Kelas (X/XI/XII for each jurusan)
- Pre-registered users (NIP/NISN tokens)
- Guru accounts
- Siswa accounts
- Mata Pelajaran
- Jadwal KBM
- Sample PKL data
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smk_lms.settings')
django.setup()

from django.contrib.auth import get_user_model
from lms.models import (
    Role, Jurusan, Kelas, PreRegisteredUser, Guru, Siswa,
    MataPelajaran, JadwalKBM, MonitoringPKL
)

User = get_user_model()

print("🌱 Starting LMS SMK Mutual seed data...")

# --- Roles ---
admin_role, _ = Role.objects.get_or_create(name='admin')
guru_role, _ = Role.objects.get_or_create(name='guru')
siswa_role, _ = Role.objects.get_or_create(name='siswa')
print("✅ Roles created")

# --- Super Admin ---
if not User.objects.filter(username='admin').exists():
    admin_user = User.objects.create_superuser(
        username='admin', email='admin@smkmutual.sch.id',
        password='Admin@123', first_name='Super', last_name='Admin',
        role=admin_role
    )
    print("✅ Admin user created (username: admin, password: Admin@123)")
else:
    print("ℹ️  Admin user already exists")

# --- Jurusan ---
jurusan_data = [
    ('TO', 'Teknik Otomotif'),
    ('BDP', 'Bisnis Daring Pemasaran'),
    ('DM', 'Digital Marketing'),
    ('AKL', 'Akuntansi Keuangan Lembaga'),
    ('DKV', 'Desain Komunikasi Visual'),
]
jurusan_objs = {}
for kode, nama in jurusan_data:
    j, _ = Jurusan.objects.get_or_create(kode=kode, defaults={'nama': nama})
    jurusan_objs[kode] = j
print("✅ Jurusan created:", list(jurusan_objs.keys()))

# --- Kelas ---
kelas_objs = {}
for kode, jurusan in jurusan_objs.items():
    for tingkat in ['X', 'XI', 'XII']:
        for nomor in ['1', '2']:
            nama_kelas = f"{tingkat} {kode} {nomor}"
            k, _ = Kelas.objects.get_or_create(nama=nama_kelas, defaults={'tingkat': tingkat, 'jurusan': jurusan})
            kelas_objs[nama_kelas] = k
print(f"✅ {len(kelas_objs)} Kelas created")

# --- Guru Accounts ---
guru_data = [
    ('197805012005011001', 'Budi Santoso', 'Guru Produktif TO'),
    ('198203152006042002', 'Sri Wahyuni', 'Guru Matematika'),
    ('197612201999031003', 'Ahmad Fauzi', 'Guru Bahasa Indonesia'),
    ('198506102010011004', 'Dewi Rahayu', 'Guru Produktif DKV'),
    ('199001252015041005', 'Eko Prasetyo', 'Kepala Program TO'),
]
guru_objs = {}
for nip, nama, jabatan in guru_data:
    PreRegisteredUser.objects.get_or_create(nip_nisn=nip, defaults={'role': 'guru', 'nama': nama})
    email = nip + '@smkmutual.sch.id'
    username = f"guru_{nip[-4:]}"
    parts = nama.split()
    first_name = ' '.join(parts[:-1]) if len(parts) > 1 else nama
    last_name = parts[-1] if len(parts) > 1 else ''
    if not User.objects.filter(username=username).exists():
        u = User.objects.create_user(username=username, email=email, password='Guru@123',
                                     first_name=first_name, last_name=last_name, role=guru_role)
        g = Guru.objects.create(user=u, nip=nip, jabatan=jabatan)
        guru_objs[nip] = g
    else:
        try:
            guru_objs[nip] = Guru.objects.get(nip=nip)
        except Guru.DoesNotExist:
            pass
print(f"✅ {len(guru_data)} Guru accounts created (password: Guru@123)")

# --- Siswa Accounts ---
siswa_data = [
    ('0058123456', 'Andi Kurniawan', 'XI TO 1'),
    ('0058123457', 'Bela Putri Sari', 'XI TO 1'),
    ('0058123458', 'Candra Wijaya', 'XI TO 2'),
    ('0058123459', 'Dina Maharani', 'XI DKV 1'),
    ('0058123460', 'Eko Firmansyah', 'XII TO 1'),
    ('0058123461', 'Fika Anggraeni', 'X AKL 1'),
    ('0058123462', 'Galih Purnomo', 'XII DKV 1'),
    ('0058123463', 'Hana Syafitri', 'X TO 1'),
]
for nisn, nama, kelas_nama in siswa_data:
    kelas = kelas_objs.get(kelas_nama)
    if not kelas:
        continue
    PreRegisteredUser.objects.get_or_create(nip_nisn=nisn, defaults={'role': 'siswa', 'nama': nama, 'kelas': kelas})
    username = f"siswa_{nisn[-5:]}"
    parts = nama.split()
    first_name = ' '.join(parts[:-1]) if len(parts) > 1 else nama
    last_name = parts[-1] if len(parts) > 1 else ''
    if not User.objects.filter(username=username).exists():
        u = User.objects.create_user(username=username, password='Siswa@123',
                                     first_name=first_name, last_name=last_name, role=siswa_role)
        Siswa.objects.create(user=u, nisn=nisn, kelas=kelas)
print(f"✅ {len(siswa_data)} Siswa accounts created (password: Siswa@123)")

# --- Mata Pelajaran ---
mapel_data = [
    ('MTK', 'Matematika', 'nasional', None),
    ('BIN', 'Bahasa Indonesia', 'nasional', None),
    ('PKn', 'Pendidikan Pancasila', 'nasional', None),
    ('PJOK', 'Pendidikan Jasmani & OR', 'nasional', None),
    ('ING', 'Bahasa Inggris', 'kewilayahan', None),
    ('PROD-TO', 'Teknik Otomotif', 'kejuruan', 'TO'),
    ('PROD-DKV', 'Desain Komunikasi Visual', 'kejuruan', 'DKV'),
    ('PROD-AKL', 'Akuntansi Dasar', 'kejuruan', 'AKL'),
    ('PROD-BDP', 'Pemasaran Digital', 'kejuruan', 'BDP'),
    ('PROD-DM', 'Pemasaran Digital & Social Media', 'kejuruan', 'DM'),
]
for kode, nama, kategori, jur_kode in mapel_data:
    jurusan = jurusan_objs.get(jur_kode) if jur_kode else None
    MataPelajaran.objects.get_or_create(kode=kode, defaults={'nama': nama, 'kategori': kategori, 'jurusan': jurusan})
print(f"✅ {len(mapel_data)} Mata Pelajaran created")

# --- Jadwal KBM ---
if guru_objs and kelas_objs:
    mapel_to = MataPelajaran.objects.filter(kode='PROD-TO').first()
    mapel_mtk = MataPelajaran.objects.filter(kode='MTK').first()
    mapel_dkv = MataPelajaran.objects.filter(kode='PROD-DKV').first()
    guru1 = list(guru_objs.values())[0]
    guru2 = list(guru_objs.values())[1] if len(guru_objs) > 1 else guru1
    guru4 = list(guru_objs.values())[3] if len(guru_objs) > 3 else guru1
    kelas_xi_to1 = kelas_objs.get('XI TO 1')
    kelas_xi_dkv1 = kelas_objs.get('XI DKV 1')

    jadwal_samples = [
        (mapel_to, guru1, kelas_xi_to1, 'Senin', '08:00', '09:30'),
        (mapel_mtk, guru2, kelas_xi_to1, 'Selasa', '07:00', '08:30'),
        (mapel_dkv, guru4, kelas_xi_dkv1, 'Rabu', '09:45', '11:15'),
    ]
    for mapel, guru, kelas, hari, jam_mulai, jam_selesai in jadwal_samples:
        if mapel and guru and kelas:
            JadwalKBM.objects.get_or_create(
                mata_pelajaran=mapel, guru=guru, kelas=kelas, hari=hari,
                defaults={'jam_mulai': jam_mulai, 'jam_selesai': jam_selesai}
            )
    print("✅ Sample Jadwal KBM created")

# --- Sample PKL ---
siswa_pkl = Siswa.objects.filter(kelas__tingkat='XI').first()
guru_pembimbing = list(guru_objs.values())[0] if guru_objs else None
if siswa_pkl and guru_pembimbing:
    MonitoringPKL.objects.get_or_create(
        siswa=siswa_pkl,
        defaults={
            'nama_industri': 'PT. Teknologi Maju Bersama',
            'alamat_industri': 'Jl. Tentara Pelajar No. 45, Magelang',
            'tanggal_mulai': '2024-07-01',
            'tanggal_selesai': '2024-09-30',
            'guru_pembimbing': guru_pembimbing,
        }
    )
    print("✅ Sample PKL monitoring created")

print()
print("=" * 55)
print("🎉 SEED DATA COMPLETED!")
print("=" * 55)
print()
print("LOGIN CREDENTIALS:")
print(f"  🔑 Admin    → username: admin       | password: Admin@123")
print(f"  👩‍🏫 Guru     → username: guru_XXXX   | password: Guru@123")
print(f"  👨‍🎓 Siswa    → username: siswa_XXXXX | password: Siswa@123")
print()
print("  (Replace XXXX with last 4 digits of NIP, XXXXX with last 5 of NISN)")
print()
print("Run: python manage.py runserver")
print("Open: http://127.0.0.1:8000/")
