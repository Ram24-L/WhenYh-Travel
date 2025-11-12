# main.py
# Penanggung Jawab: Person A

import admin_menu   # Mengimpor file menu admin
import user_menu    # Mengimpor file menu user
import data_manager # Mengimpor file pengelola data (JSON)
import utils        # Mengimpor file utilitas (hash, clear screen)
import getpass      # Untuk menyembunyikan input password
import time
import stdiomask    # Untuk menyembunyikan input password dengan mask karakter
from rich import print as rprint # Menggunakan print dari rich

def handle_login():
    """
    Menangani alur logika untuk login.
    Mengembalikan data user jika berhasil, None jika gagal.
    """
    utils.bersihkan_layar()
    print("--- LOGIN AKUN ---")
    username = input("Username: ")
    # Gunakan getpass agar password tidak terlihat saat diketik
    # KODE BARU:
    password = stdiomask.getpass(prompt="Password: ", mask="*")

    # 1. Cari user di database (JSON)
    user_data = data_manager.dapatkan_user_by_username(username)

    # 2. Cek apakah user ada
    if not user_data:
        # --- PERBAIKAN ERROR ---
        rprint("\n[bold red][ERROR] Username tidak ditemukan![/bold red]")
        time.sleep(2)
        return None

    # 3. Cek apakah password cocok
    if utils.cek_password(password, user_data['password_hash']):
        # --- REKOMENDASI SUKSES ---
        rprint(f"\n[bold green]Login berhasil! Selamat datang, {username}.[/bold green]")
        time.sleep(1)
        return user_data # Kembalikan semua data user (termasuk role)
    else:
        # --- PERBAIKAN ERROR & BUG ---
        rprint("\n[bold red][ERROR] Password salah![/bold red]")
        time.sleep(2)
        return None

def handle_register():
    """
    Menangani alur logika untuk registrasi user baru (role 'user').
    """
    utils.bersihkan_layar()
    print("--- REGISTER AKUN BARU (USER) ---")
    username = input("Username baru: ").strip() # .strip() untuk hapus spasi

    # Validasi input
    if not username:
        # --- PERBAIKAN ERROR ---
        rprint("\n[bold red][ERROR] Username tidak boleh kosong![/bold red]")
        time.sleep(2)
        return

    # 1. Cek apakah username sudah ada
    if data_manager.dapatkan_user_by_username(username):
        # --- PERBAIKAN ERROR ---
        rprint(f"\n[bold red][ERROR] Username '{username}' sudah terpakai. Silakan pilih yang lain.[/bold red]")
        time.sleep(2)
        return

    # 2. Input password
    while True:
        password = getpass.getpass("Password baru: ")
        konfirmasi_password = getpass.getpass("Konfirmasi password: ")

        if password != konfirmasi_password:
            # --- PERBAIKAN ERROR ---
            rprint("\n[bold red][ERROR] Password dan konfirmasi tidak cocok. Silakan ulangi.[/bold red]")
        elif len(password) < 6: # Contoh validasi sederhana
             # --- PERBAIKAN ERROR ---
             rprint("\n[bold red][ERROR] Password minimal harus 6 karakter.[/bold red]")
        else:
            break # Password valid

    # 3. Hash password
    password_hashed = utils.hash_password(password)

    # 4. Buat objek user baru
    # Note: Registrasi dari sini SELALU 'user', bukan 'admin'
    user_baru = {
        "username": username,
        "password_hash": password_hashed,
        "role": "user"
        # Anda bisa tambahkan 'saldo': 0 jika pakai fitur dompet
    }

    # 5. Simpan ke data_manager
    data_manager.simpan_user_baru(user_baru)

    # --- REKOMENDASI SUKSES ---
    rprint(f"\n[bold green]Registrasi berhasil! Akun '{username}' telah dibuat.[/bold green]")
    time.sleep(2)


def main_menu():
    """
    Loop utama aplikasi yang menampilkan menu awal.
    """
    # Pastikan file-file data ada (dibuat oleh data_manager jika belum ada)
    data_manager.inisialisasi_data_files() 
    
    while True:
        utils.bersihkan_layar()
        # --- TAMPILAN (SUDAH DIPERBAIKI) ---
        rprint("[yellow]"+"="*50+"[/yellow]")
        # f-string { } digunakan agar .center() berjalan pada teks sebelum diberi warna
        rprint(f"[bold white]{'Selamat Datang'.center(50)}[/bold white]")
        rprint(f"[bold white]{'Sistem Informasi When Yh Travel'.center(50)}[/bold white]")
        rprint("[yellow]"+"="*50+"[/yellow]")
        print("[1] Login")
        print("[2] Register Akun Baru")
        print("[3] Keluar Aplikasi")
        rprint("[yellow]"+"="*50+"[/yellow]")
        
        pilihan = input("Masukkan pilihan Anda (1-3): ")

        if pilihan == '1':
            # Coba login. Jika berhasil, 'user' akan berisi data
            user = handle_login()
            
            if user:
                # Cek role dan arahkan ke menu yang sesuai
                if user['role'] == 'admin':
                    admin_menu.start(user) # Lempar ke menu admin
                elif user['role'] == 'user':
                    user_menu.start(user) # Lempar ke menu user
                
        elif pilihan == '2':
            handle_register()
            
        elif pilihan == '3':
            # --- REKOMENDASI INFO ---
            rprint("\n[bold yellow]Terima kasih telah menggunakan aplikasi. Sampai jumpa![/bold yellow]")
            break # Keluar dari loop while True
            
        else:
            # --- PERBAIKAN ERROR ---
            rprint("\n[bold red][ERROR] Pilihan tidak valid. Silakan coba lagi.[/bold red]")
            time.sleep(1)

# --- Titik Masuk Utama Program ---
if __name__ == "__main__":
    main_menu()