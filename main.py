import admin_menu
import user_menu
import data_manager
import utils
import getpass
import time
import stdiomask
from rich import print as rprint


# ============================================================
# LOGIN
# ============================================================

def handle_login():
    utils.bersihkan_layar()
    rprint("[bold white]--- LOGIN AKUN ---[/bold white]")

    username = input("Username: ")
    password = stdiomask.getpass(prompt="Password: ", mask="*")

    user_data = data_manager.dapatkan_user_by_username(username)

    if not user_data:
        rprint("\n[bold blue]Username tidak ditemukan![/bold blue]")
        time.sleep(2)
        return None

    if utils.cek_password(password, user_data["password_hash"]):
        rprint(f"\n[bold white]Login berhasil! Selamat datang, {username}.[/bold white]")
        time.sleep(1)
        return user_data
    else:
        rprint("\n[bold blue]Password salah![/bold blue]")
        time.sleep(2)
        return None


# ============================================================
# REGISTER
# ============================================================

def handle_register():
    utils.bersihkan_layar()
    rprint("[bold white]--- REGISTER AKUN BARU ---[/bold white]")

    username = input("Username baru: ").strip()

    if not username:
        rprint("\n[bold blue]Username tidak boleh kosong.[/bold blue]")
        time.sleep(2)
        return

    if data_manager.dapatkan_user_by_username(username):
        rprint(f"\n[bold blue]Username '{username}' sudah dipakai.[/bold blue]")
        time.sleep(2)
        return

    while True:
        password = getpass.getpass("Password baru: ")
        confirm = getpass.getpass("Konfirmasi password: ")

        if password != confirm:
            rprint("\n[bold blue]Password tidak cocok.[/bold blue]")
        elif len(password) < 6:
            rprint("\n[bold blue]Password minimal 6 karakter.[/bold blue]")
        else:
            break

    hashed = utils.hash_password(password)

    user_baru = {
        "username": username,
        "password_hash": hashed,
        "role": "user",
    }

    data_manager.simpan_user_baru(user_baru)
    rprint(f"\n[bold white]Registrasi berhasil! Akun '{username}' dibuat.[/bold white]")
    time.sleep(2)


# ============================================================
# MAIN MENU
# ============================================================

def main_menu():
    data_manager.inisialisasi_data_files()

    while True:
        utils.bersihkan_layar()
        rprint("[bold blue]" + "="*50 + "[/bold blue]")
        rprint(f"[bold white]{'SELAMAT DATANG'.center(50)}[/bold white]")
        rprint(f"[bold white]{'SISTEM INFORMASI WHEN YH TRAVEL'.center(50)}[/bold white]")
        rprint("[bold blue]" + "="*50 + "[/bold blue]")

        print("[1] Login")
        print("[2] Register Akun Baru")
        print("[3] Keluar Aplikasi")
        rprint("[bold blue]" + "="*50 + "[/bold blue]")

        pilihan = input("Masukkan pilihan (1-3): ")

        if pilihan == "1":
            user = handle_login()
            if user:
                if user["role"] == "admin":
                    admin_menu.start(user)
                else:
                    user_menu.start(user)

        elif pilihan == "2":
            handle_register()

        elif pilihan == "3":
            rprint("\n[bold white]Terima kasih telah menggunakan aplikasi![/bold white]")
            break

        else:
            rprint("\n[bold blue]Pilihan tidak valid.[/bold blue]")
            time.sleep(1)



if __name__ == "__main__":
    main_menu()
