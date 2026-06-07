from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from lms.models import User, Role, PreRegisteredUser, Guru, Siswa, Kelas


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_suspended:
                messages.error(request, 'Akun Anda telah ditangguhkan. Hubungi administrator.')
            else:
                login(request, user)
                return redirect('dashboard')
        else:
            messages.error(request, 'Username atau password salah.')
    return render(request, 'lms/auth/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def signup_view(request):
    kelas_list = Kelas.objects.all().select_related('jurusan')
    if request.method == 'POST':
        nama_lengkap = request.POST.get('nama_lengkap', '').strip()
        email = request.POST.get('email', '').strip()
        nip_nisn = request.POST.get('nip_nisn', '').strip()
        password = request.POST.get('password', '').strip()
        konfirmasi = request.POST.get('konfirmasi', '').strip()

        if password != konfirmasi:
            messages.error(request, 'Password dan konfirmasi password tidak cocok.')
            return render(request, 'lms/auth/signup.html', {'kelas_list': kelas_list})

        # Validate email or NIP/NISN
        is_email_valid = email.lower().endswith('@smkmutual.sch.id')
        pre_reg = None
        if nip_nisn:
            pre_reg = PreRegisteredUser.objects.filter(nip_nisn=nip_nisn).first()

        if not is_email_valid and not pre_reg:
            messages.error(request, 'Gunakan email institusi (@smkmutual.sch.id) atau masukkan NISN/NIP yang valid.')
            return render(request, 'lms/auth/signup.html', {'kelas_list': kelas_list})

        if User.objects.filter(email=email).exists() if email else False:
            messages.error(request, 'Email sudah terdaftar.')
            return render(request, 'lms/auth/signup.html', {'kelas_list': kelas_list})

        # Determine role
        role_name = 'siswa'
        if pre_reg:
            role_name = pre_reg.role
        elif is_email_valid:
            # Default to siswa if signed up with email; admin must assign guru role manually
            role_name = 'siswa'

        role_obj, _ = Role.objects.get_or_create(name=role_name)
        username = email.split('@')[0] if email else nip_nisn
        # Ensure unique username
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        first_name = ' '.join(nama_lengkap.split()[:-1]) if len(nama_lengkap.split()) > 1 else nama_lengkap
        last_name = nama_lengkap.split()[-1] if len(nama_lengkap.split()) > 1 else ''

        user = User.objects.create_user(
            username=username, email=email, password=password,
            first_name=first_name, last_name=last_name, role=role_obj
        )

        if role_name == 'siswa':
            kelas_id = request.POST.get('kelas_id') or (pre_reg.kelas_id if pre_reg else None)
            nisn_val = nip_nisn if pre_reg and pre_reg.role == 'siswa' else nip_nisn
            if kelas_id:
                kelas = Kelas.objects.get(id=kelas_id)
                Siswa.objects.create(user=user, nisn=nisn_val or f'NISN-{user.id}', kelas=kelas)
        elif role_name == 'guru':
            Guru.objects.create(user=user, nip=nip_nisn or f'NIP-{user.id}')

        messages.success(request, 'Akun berhasil dibuat! Silakan login.')
        return redirect('login')

    return render(request, 'lms/auth/signup.html', {'kelas_list': kelas_list})


def dashboard_redirect(request):
    if not request.user.is_authenticated:
        return redirect('login')
    role = request.user.role.name if request.user.role else None
    if role == 'admin':
        return redirect('admin_dashboard')
    elif role == 'guru':
        return redirect('guru_dashboard')
    elif role == 'siswa':
        return redirect('siswa_dashboard')
    else:
        logout(request)
        messages.error(request, 'Role akun tidak valid. Hubungi administrator.')
        return redirect('login')
