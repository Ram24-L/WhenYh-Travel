
import admin_menu   
import user_menu    
import data_manager 
import utils        
import getpass      
import time
import stdiomask    
from rich import print as rprint 

def handle_login():
    utils.bersihkan_layar()
    print("--- LOGIN AKUN ---")
    username = input("Username: ")
    password = stdiomask.getpass(prompt="Password: ", mask="*")
    user_data = data_manager.dapatkan_user_by_username(username)

    if not user_data:
        rprint("\n[bold red][ERROR] Username tidak ditemukan![/bold red]")
        time.sleep(2)
        return None
    
    if utils.cek_password(password, user_data['password_hash']):
        rprint(f"\n[bold green]Login berhasil! Selamat datang, {username}.[/bold green]")
        time.sleep(1)
        return user_data 
    else:
        rprint("\n[bold red][ERROR] Password salah![/bold red]")
        time.sleep(2)
        return None

def handle_register():
    """
    Menangani alur logika untuk registrasi user baru (role 'user').
    (SUDAH DITAMBAHKAN INPUT EMAIL)
    """
    utils.bersihkan_layar()
    print("--- REGISTER AKUN BARU (USER) ---")
    username = input("Username baru: ").strip() 

    # Validasi username
    if not username:
        rprint("\n[bold red][ERROR] Username tidak boleh kosong![/bold red]")
        time.sleep(2)
        return

    # 1. Cek apakah username sudah ada
    if data_manager.dapatkan_user_by_username(username):
        rprint(f"\n[bold red][ERROR] Username '{username}' sudah terpakai. Silakan pilih yang lain.[/bold red]")
        time.sleep(2)
        return

    # --- TAMBAHAN BARU: INPUT EMAIL ---
    email = input("Alamat Email: ").strip()
    
    # Validasi sederhana email (harus ada '@' dan '.')
    if "@" not in email or "." not in email:
        rprint("\n[bold red][ERROR] Format email tidak valid (harus mengandung '@' dan '.').[/bold red]")
        time.sleep(2)
        return
    # ----------------------------------

    # 2. Input password
    while True:
        password = getpass.getpass("Password baru: ")
        konfirmasi_password = getpass.getpass("Konfirmasi password: ")

        if password != konfirmasi_password:
            rprint("\n[bold red][ERROR] Password dan konfirmasi tidak cocok. Silakan ulangi.[/bold red]")
        elif len(password) < 6: 
             rprint("\n[bold red][ERROR] Password minimal harus 6 karakter.[/bold red]")
        else:
            break 

    # 3. Hash password
    password_hashed = utils.hash_password(password)

    # 4. Buat objek user baru
    user_baru = {
        "username": username,
        "password_hash": password_hashed,
        "role": "user",
        "email": email  # <--- SIMPAN EMAIL DI SINI
    }

    # 5. Simpan ke data_manager
    data_manager.simpan_user_baru(user_baru)

    rprint(f"\n[bold green]Registrasi berhasil! Akun '{username}' telah dibuat.[/bold green]")
    time.sleep(2)

def main_menu():
    data_manager.inisialisasi_data_files() 
    
    while True:
        utils.bersihkan_layar()
        rprint("[yellow]"+"="*50+"[/yellow]")
        rprint(f"[bold white]{'Selamat Datang'.center(50)}[/bold white]")
        rprint(f"[bold white]{'Sistem Informasi When Yh Travel'.center(50)}[/bold white]")
        rprint("[yellow]"+"="*50+"[/yellow]")
        print("[1] Login")
        print("[2] Register Akun Baru")
        print("[3] Keluar Aplikasi")
        rprint("[yellow]"+"="*50+"[/yellow]")
        
        pilihan = input("Masukkan pilihan Anda (1-3): ")

        if pilihan == '1':
            user = handle_login()
            if user:
                if user['role'] == 'admin':
                    admin_menu.start(user) 
                elif user['role'] == 'user':
                    user_menu.start(user) 
        elif pilihan == '2':
            handle_register()
            
        elif pilihan == '3':
            
            rprint("\n[bold yellow]Terima kasih telah menggunakan aplikasi. Sampai jumpa![/bold yellow]")
            break 
            
        else:
            
            rprint("\n[bold red][ERROR] Pilihan tidak valid. Silakan coba lagi.[/bold red]")
            time.sleep(1)

if __name__ == "__main__":
    main_menu()