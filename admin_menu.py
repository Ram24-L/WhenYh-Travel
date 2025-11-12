# admin_menu.py
# Penanggung Jawab: Person B

import data_manager
import utils
import time

# # (WAJIB) Install library 'rich' ...
from rich.console import Console
from rich.table import Table
from rich import print as rprint # Menggunakan print dari rich
from rich.panel import Panel  # <--- TAMBAHKAN INI
from rich.text import Text    # <--- TAMBAHKAN INI

# Inisialisasi console dari rich
console = Console()

def _lihat_semua_paket(tunggu=True):
    """
    Menampilkan semua paket dalam bentuk tabel.
    Jika 'tunggu' == True, akan menunggu user menekan Enter.
    Mengembalikan True jika ada paket, False jika kosong.
    """
    utils.bersihkan_layar()
    rprint("--- [bold yellow]DAFTAR SEMUA PAKET[/bold yellow] ---")
    
    # 1. Ambil data dari data_manager (tugas Person A)
    paket_list = data_manager.dapatkan_semua_paket()
    
    if not paket_list:
        rprint("[italic]Belum ada data paket travel.[/italic]")
        time.sleep(2)
        return False

    # 2. Buat tabel
    table = Table(title="Paket Travel Tersedia", show_header=True, header_style="bold magenta")
    table.add_column("ID Paket", style="cyan", width=10)
    table.add_column("Nama Paket", style="green", min_width=20)
    table.add_column("Harga (Rp)", style="blue", justify="right")
    table.add_column("Sisa Kuota", justify="right")
    
    # 3. Isi tabel dengan data
    for paket in paket_list:
        table.add_row(
            paket['id_paket'],
            paket['nama'],
            f"{paket['harga']:,}", # Format angka dengan koma
            str(paket['kuota'])
        )
    
    console.print(table)
    
    if tunggu:
        input("\nTekan Enter untuk kembali ke menu...")
    
    return True # Sukses menampilkan paket

def _tambah_paket_baru():
    """
    Alur untuk menambahkan paket travel baru.
    (SUDAH DIPERBARUI DENGAN OPSI 'BATAL')
    """
    utils.bersihkan_layar()
    rprint("--- [bold yellow]TAMBAH PAKET BARU[/bold yellow] ---")
    rprint("Ketik [italic]'batal'[/italic] kapan saja untuk kembali ke menu.")
    
    # --- Input Nama ---
    nama = input("\nNama Paket: ").strip()
    if nama.lower() == 'batal':
        rprint("\n[italic]Penambahan paket dibatalkan.[/italic]")
        time.sleep(1)
        return

    # --- Input Harga ---
    while True:
        harga_str = input("Harga (contoh: 1500000): ").strip()
        if harga_str.lower() == 'batal':
            rprint("\n[italic]Penambahan paket dibatalkan.[/italic]")
            time.sleep(1)
            return
        try:
            harga = int(harga_str)
            break
        except ValueError:
            rprint("[bold red]ERROR: Harga harus berupa angka.[/bold red]")
            
    # --- Input Kuota ---
    while True:
        kuota_str = input("Jumlah Kuota: ").strip()
        if kuota_str.lower() == 'batal':
            rprint("\n[italic]Penambahan paket dibatalkan.[/italic]")
            time.sleep(1)
            return
        try:
            kuota = int(kuota_str)
            break
        except ValueError:
            rprint("[bold red]ERROR: Kuota harus berupa angka.[/bold red]")

    # --- Input Rundown ---
    rundown = []
    rprint("\nMasukkan Rundown (ketik 'selesai' untuk berhenti):")
    i = 1
    while True:
        item = input(f"  Item {i}: ").strip()
        
        if item.lower() == 'batal':
            rprint("\n[italic]Penambahan paket dibatalkan.[/italic]")
            time.sleep(1)
            return
            
        if item.lower() == 'selesai':
            if i == 1: # Jika item pertama sudah 'selesai'
                rprint("[italic]Rundown tidak boleh kosong. Minimal 1 item.[/italic]")
                rprint("[italic]Penambahan paket dibatalkan.[/italic]")
                time.sleep(2)
                return
            break # Keluar loop jika 'selesai' dan bukan item pertama
            
        if item: # Hanya tambahkan jika tidak kosong
            rundown.append(item)
            i += 1
    
    # Siapkan data untuk dikirim ke data_manager
    paket_baru = {
        "nama": nama,
        "harga": harga,
        "kuota": kuota,
        "rundown": rundown
    }
    
    data_manager.simpan_paket_baru(paket_baru)
    
    rprint(f"\n[bold green]SUKSES: Paket '{nama}' telah berhasil ditambahkan![/bold green]")
    time.sleep(2)

def _edit_paket():
    """
    Alur untuk mengedit paket yang sudah ada (harga, kuota, nama).
    (SUDAH DIPERBARUI DENGAN OPSI 'BATAL' SAAT EDIT)
    """
    utils.bersihkan_layar()
    rprint("--- [bold yellow]EDIT PAKET[/bold yellow] ---")
    
    if not _lihat_semua_paket(tunggu=False):
        return

    id_paket = input("\nMasukkan ID Paket yang akan diedit (atau 'batal'): ").strip()
    if id_paket.lower() == 'batal':
        return

    paket_lama = data_manager.dapatkan_paket_by_id(id_paket)
    
    if not paket_lama:
        rprint(f"\n[bold red]ERROR: ID Paket '{id_paket}' tidak ditemukan.[/bold red]")
        time.sleep(2)
        return
        
    rprint(f"\nAnda mengedit: [bold magenta]{paket_lama['nama']}[/bold magenta]")
    rprint("Ketik [italic]'batal'[/italic] kapan saja untuk kembali.")
    rprint("(Tekan Enter untuk menggunakan data lama)")

    # --- Input Nama Baru ---
    nama_baru = input(f"Nama Paket [{paket_lama['nama']}]: ").strip()
    if nama_baru.lower() == 'batal':
        rprint("\n[italic]Edit paket dibatalkan.[/italic]")
        time.sleep(1)
        return

    # --- Input Harga Baru ---
    while True:
        harga_baru_str = input(f"Harga [{paket_lama['harga']:,}]: ").strip()
        if harga_baru_str.lower() == 'batal':
            rprint("\n[italic]Edit paket dibatalkan.[/italic]")
            time.sleep(1)
            return
            
        if not harga_baru_str: # Jika Enter (kosong)
            harga_baru = paket_lama['harga']
            break
        try:
            harga_baru = int(harga_baru_str)
            break
        except ValueError:
            rprint("[bold red]ERROR: Harga harus berupa angka.[/bold red]")

    # --- Input Kuota Baru ---
    while True:
        kuota_baru_str = input(f"Kuota [{paket_lama['kuota']}]: ").strip()
        if kuota_baru_str.lower() == 'batal':
            rprint("\n[italic]Edit paket dibatalkan.[/italic]")
            time.sleep(1)
            return
            
        if not kuota_baru_str: # Jika Enter (kosong)
            kuota_baru = paket_lama['kuota']
            break
        try:
            kuota_baru = int(kuota_baru_str)
            break
        except ValueError:
            rprint("[bold red]ERROR: Kuota harus berupa angka.[/bold red]")

    # Siapkan data update
    data_update = {
        "nama": nama_baru if nama_baru else paket_lama['nama'],
        "harga": harga_baru,
        "kuota": kuota_baru,
        "rundown": paket_lama['rundown'] # Asumsi rundown tidak diedit di sini
    }

    data_manager.update_paket(id_paket, data_update)
    rprint(f"\n[bold green]SUKSES: Paket '{data_update['nama']}' telah diperbarui.[/bold green]")
    rprint(f"([italic]Note: Untuk edit rundown, hapus dan buat ulang paket.[/italic])")
    time.sleep(3)
    
def _hapus_paket():
    """
    Alur untuk menghapus paket dari sistem.
    """
    utils.bersihkan_layar()
    rprint("--- [bold yellow]HAPUS PAKET[/bold yellow] ---")
    
    # Tampilkan daftar paket
    if not _lihat_semua_paket(tunggu=False):
        return

    id_paket = input("\nMasukkan ID Paket yang akan dihapus (atau 'batal'): ").strip()
    if id_paket.lower() == 'batal':
        return

    # Ambil data paket untuk konfirmasi (tugas Person A)
    paket = data_manager.dapatkan_paket_by_id(id_paket)
    
    if not paket:
        rprint(f"\n[bold red]ERROR: ID Paket '{id_paket}' tidak ditemukan.[/bold red]")
        time.sleep(2)
        return

    # Konfirmasi penghapusan
    rprint(f"\nAnda akan menghapus: [bold red]{paket['nama']} (ID: {id_paket})[/bold red]")
    konfirmasi = input("Apakah Anda YAKIN? (y/n): ").strip().lower()
    
    if konfirmasi == 'y':
        # Panggil data_manager untuk menghapus (tugas Person A)
        data_manager.hapus_paket_by_id(id_paket)
        rprint(f"\n[bold green]SUKSES: Paket '{paket['nama']}' telah dihapus.[/bold green]")
    else:
        # --- PERBAIKAN KEDUA ADA DI SINI ---
        rprint("\n[italic]Penghapusan dibatalkan.[/italic]")
        
    time.sleep(2)

def _tampilkan_menu_paket():
    """
    Menampilkan sub-menu untuk Manajemen Paket (CRUD).
    """
    while True:
        utils.bersihkan_layar()
        rprint("--- [bold yellow]MANAJEMEN PAKET[/bold yellow] ---")
        rprint("[1] Tambah Paket Baru")
        rprint("[2] Edit Paket")
        rprint("[3] Hapus Paket")
        rprint("[4] Lihat Detail & Rundown Paket")
        rprint("[5] Kembali ke Menu Admin")
        
        pilihan = input("Pilihan (1-5): ").strip()
        
        if pilihan == '1':
            _tambah_paket_baru()
        elif pilihan == '2':
            _edit_paket()
        elif pilihan == '3':
            _hapus_paket()
        elif pilihan == '4':
           _admin_lihat_detail_paket() # <--- PANGGIL FUNGSI BARU
        elif pilihan == '5':
            break # Kembali ke menu admin utama
        else:
            rprint("\n[bold red]ERROR: Pilihan tidak valid.[/bold red]")
            time.sleep(1)

def _lihat_semua_booking():
    """
    Menampilkan semua data booking yang dilakukan oleh user.
    """
    utils.bersihkan_layar()
    rprint("--- [bold yellow]DAFTAR SEMUA BOOKING[/bold yellow] ---")
    
    # Ambil data dari data_manager (tugas Person A)
    bookings = data_manager.dapatkan_semua_booking()
    
    if not bookings:
        rprint("[italic]Belum ada data booking dari user.[/italic]")
        time.sleep(2)
        return

    # Buat tabel
    table = Table(title="Data Booking User", show_header=True, header_style="bold magenta")
    table.add_column("ID Booking", style="cyan", width=10)
    table.add_column("Username User", style="green")
    table.add_column("ID Paket", style="cyan")
    table.add_column("Jml Tiket", justify="right")
    table.add_column("Total Bayar (Rp)", style="blue", justify="right")
    
    total_pendapatan = 0
    
    # Isi tabel
    for booking in bookings:
        table.add_row(
            booking['id_booking'],
            booking['username_user'],
            booking['id_paket'],
            str(booking['jumlah_tiket']),
            f"{booking['total_bayar']:,}"
        )
        total_pendapatan += booking['total_bayar']
        
    console.print(table)
    rprint(f"\n[bold]Total Pendapatan: Rp {total_pendapatan:,}[/bold]")
    input("\nTekan Enter untuk kembali ke menu...")


def _admin_lihat_detail_paket():
    """
    (FUNGSI BARU)
    Alur untuk admin melihat detail rundown paket.
    """
    utils.bersihkan_layar()
    rprint("--- [bold yellow]DETAIL & RUNDOWN PAKET[/bold yellow] ---")

    # Tampilkan daftar paket dulu agar admin tahu ID-nya
    # Panggil dengan tunggu=False
    if not _lihat_semua_paket(tunggu=False):
        return # Kembali jika tidak ada paket

    id_paket = input("\nMasukkan ID Paket yang ingin dilihat detailnya (atau 'batal'): ").strip()
    if id_paket.lower() == 'batal':
        return

    paket = data_manager.dapatkan_paket_by_id(id_paket)

    if not paket:
        rprint(f"\n[bold red]ERROR: ID Paket '{id_paket}' tidak ditemukan.[/bold red]")
        time.sleep(2)
        return

    # Tampilkan detail menggunakan Rich Panel
    utils.bersihkan_layar()
    
    # Buat teks rundown
    rundown_text = Text()
    if paket['rundown']:
        for i, item in enumerate(paket['rundown'], 1):
            rundown_text.append(f"  {i}. {item}\n")
    else:
        rundown_text.append("[italic]Rundown tidak tersedia.[/italic]")

    panel_content = Text()
    panel_content.append(f"ID Paket: {paket['id_paket']}\n", style="cyan")
    panel_content.append(f"Harga: Rp {paket['harga']:,}\n", style="blue")
    panel_content.append(f"Sisa Kuota: {paket['kuota']} orang\n\n", style="bold")
    panel_content.append("--- RUNDOWN PERJALANAN ---\n", style="bold yellow")
    panel_content.append(rundown_text)

    # Tampilkan panel
    console.print(Panel(panel_content, title=f"[bold green]{paket['nama']}[/bold green]", border_style="yellow"))
    
    input("\nTekan Enter untuk kembali...")

# --- FUNGSI UTAMA (ENTRY POINT) ---

def start(admin_user):
    """
    Fungsi utama yang dipanggil oleh main.py saat admin login.
    'admin_user' berisi data admin yang sedang login (misal: {'username': 'admin', ...})
    """
    utils.bersihkan_layar()
    rprint(f"[bold green]Selamat datang, {admin_user['username']}! (Role: Admin)[/bold green]")
    time.sleep(2)

    while True:
        utils.bersihkan_layar()
        rprint("\n--- [bold yellow]MENU UTAMA ADMIN[/bold yellow] ---")
        rprint("[1] Manajemen Paket Travel (CRUD)")
        rprint("[2] Lihat Data Booking User")
        rprint("[3] Logout")
        
        pilihan = input("Masukkan pilihan (1-3): ").strip()
        
        if pilihan == '1':
            _tampilkan_menu_paket() # Masuk ke sub-menu
        elif pilihan == '2':
            _lihat_semua_booking()
        elif pilihan == '3':
            # --- PERBAIKAN PERTAMA ADA DI SINI ---
            rprint("\n[cyan]Logout berhasil. Kembali ke menu utama...[/cyan]")
            time.sleep(1)
            break # Keluar dari loop admin, kembali ke main.py
        else:
            rprint("\n[bold red]ERROR: Pilihan tidak valid.[/bold red]")
            time.sleep(1)