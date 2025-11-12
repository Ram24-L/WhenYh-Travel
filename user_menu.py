# user_menu.py
# Penanggung Jawab: Person C

import data_manager
import utils
import time

# (WAJIB) Install library 'rich' untuk tampilan yang lebih baik
# jalankan di terminal: pip install rich
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from rich.panel import Panel
from rich.text import Text

# Inisialisasi console dari rich
console = Console()

# --- FUNGSI UNTUK FITUR UNIK (PDF/QR) ---
def _cetak_tiket(user, booking_data, paket):
    """
    (Fitur Unik) Placeholder untuk men-generate tiket.
    Person C dapat mengimplementasikan ini.
    """
    rprint(f"\n[bold yellow]Mencoba men-generate tiket untuk {booking_data['id_booking']}...[/bold yellow]")
    
    # LANGKAH-LANGKAH IMPLEMENTASI (oleh Person C):
    # 1. Install library: pip install reportlab qrcode
    # 2. Import: from reportlab.pdfgen import canvas
    #            import qrcode
    #            import os
    # 3. Generate QR Code:
    #    - data_qr = f"Booking:{booking_data['id_booking']},User:{user['username']},Paket:{paket['nama']}"
    #    - img_qr = qrcode.make(data_qr)
    #    - nama_file_qr = f"qr_{booking_data['id_booking']}.png"
    #    - img_qr.save(nama_file_qr)
    #
    # 4. Buat PDF (menggunakan reportlab):
    #    - nama_file_pdf = f"tiket_{booking_data['id_booking']}.pdf"
    #    - c = canvas.Canvas(nama_file_pdf)
    #    - c.drawString(100, 800, "--- E-TIKET TRAVEL ---")
    #    - c.drawString(100, 780, f"Nama: {user['username']}")
    #    - c.drawString(100, 760, f"Paket: {paket['nama']}")
    #    - c.drawString(100, 740, f"Jumlah: {booking_data['jumlah_tiket']} tiket")
    #    - c.drawString(100, 720, f"Total Bayar: Rp {booking_data['total_bayar']:,}")
    #    - c.drawImage(nama_file_qr, 100, 500, width=200, height=200) # Masukkan QR ke PDF
    #    - c.save()
    # 5. Hapus file QR sementara: os.remove(nama_file_qr)

    # Simulasi sukses
    nama_file_pdf = f"tiket_{booking_data['id_booking']}.pdf"
    rprint(f"[bold green]SUKSES! Tiket telah disimpan sebagai '{nama_file_pdf}'[/bold green]")
    rprint("[italic](Implementasi PDF/QR code oleh Person C)[/italic]")
    time.sleep(3)


# --- FUNGSI MENU UTAMA USER ---

def _lihat_semua_paket(tunggu=True):
    """
    Menampilkan semua paket yang tersedia dalam tabel.
    """
    utils.bersihkan_layar()
    rprint("--- [bold yellow]DAFTAR PAKET TRAVEL TERSEDIA[/bold yellow] ---")
    
    paket_list = data_manager.dapatkan_semua_paket()
    
    if not paket_list:
        rprint("[italic]Belum ada paket travel yang tersedia saat ini.[/italic]")
        time.sleep(2)
        return False

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID Paket", style="cyan", width=10)
    table.add_column("Nama Paket", style="green", min_width=20)
    table.add_column("Harga (Rp)", style="blue", justify="right")
    table.add_column("Sisa Kuota", justify="right")
    
    for paket in paket_list:
        # Hanya tampilkan jika kuota masih ada
        if paket['kuota'] > 0:
            table.add_row(
                paket['id_paket'],
                paket['nama'],
                f"{paket['harga']:,}",
                str(paket['kuota'])
            )
    
    console.print(table)
    
    if tunggu:
        input("\nTekan Enter untuk kembali...")
    
    return True

def _lihat_detail_paket():
    """
    Menampilkan detail rundown dari satu paket.
    """
    utils.bersihkan_layar()
    rprint("--- [bold yellow]DETAIL & RUNDOWN PAKET[/bold yellow] ---")

    # Tampilkan daftar paket dulu agar user tahu ID-nya
    if not _lihat_semua_paket(tunggu=False):
        return

    id_paket = input("\nMasukkan ID Paket yang ingin dilihat detailnya: ").strip()
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

    console.print(Panel(panel_content, title=f"[bold green]{paket['nama']}[/bold green]", border_style="yellow"))
    
    input("\nTekan Enter untuk kembali...")

def _beli_tiket(user):
    """
    Alur logika untuk user membeli tiket.
    """
    utils.bersihkan_layar()
    rprint("--- [bold yellow]PEMBELIAN TIKET[/bold yellow] ---")

    if not _lihat_semua_paket(tunggu=False):
        return

    # 1. Pilih Paket
    id_paket = input("\nMasukkan ID Paket yang ingin dibeli: ").strip()
    paket = data_manager.dapatkan_paket_by_id(id_paket)

    if not paket:
        rprint(f"\n[bold red]ERROR: ID Paket '{id_paket}' tidak ditemukan.[/bold red]")
        time.sleep(2)
        return
        
    if paket['kuota'] == 0:
        rprint(f"\n[bold red]MAAF: Kuota untuk paket '{paket['nama']}' sudah habis.[/bold red]")
        time.sleep(2)
        return

    # 2. Masukkan Jumlah
    while True:
        try:
            jumlah_tiket = int(input(f"Jumlah tiket (Sisa kuota: {paket['kuota']}): "))
            if jumlah_tiket <= 0:
                rprint("[bold red]Jumlah tiket harus lebih dari 0.[/bold red]")
            elif jumlah_tiket > paket['kuota']:
                rprint(f"[bold red]MAAF: Jumlah tiket melebihi sisa kuota ({paket['kuota']}).[/bold red]")
            else:
                break # Jumlah valid
        except ValueError:
            rprint("[bold red]ERROR: Masukkan harus berupa angka.[/bold red]")

    # 3. Konfirmasi
    total_bayar = paket['harga'] * jumlah_tiket
    utils.bersihkan_layar()
    rprint("--- [bold yellow]KONFIRMASI PEMBELIAN[/bold yellow] ---")
    rprint(f"Paket      : [bold green]{paket['nama']}[/bold green]")
    rprint(f"Harga Satuan : Rp {paket['harga']:,}")
    rprint(f"Jumlah Tiket : {jumlah_tiket}")
    rprint("--------------------------------- +")
    rprint(f"Total Bayar  : [bold blue]Rp {total_bayar:,}[/bold blue]")
    
    konfirmasi = input("\nLanjutkan pembayaran? (y/n): ").strip().lower()

    if konfirmasi == 'y':
        # 4. Proses Transaksi
        
        # a. Buat data booking
        booking_data = {
            "username_user": user['username'],
            "id_paket": id_paket,
            "jumlah_tiket": jumlah_tiket,
            "total_bayar": total_bayar
            # 'id_booking' akan di-generate oleh data_manager
        }
        # Simpan booking (tugas Person A)
        booking_tersimpan = data_manager.simpan_booking_baru(booking_data)

        # b. Kurangi kuota paket
        sisa_kuota = paket['kuota'] - jumlah_tiket
        data_update = {"kuota": sisa_kuota}
        # Update paket (tugas Person A)
        data_manager.update_paket(id_paket, data_update)

        rprint(f"\n[bold green]SUKSES! Pembelian berhasil (ID Booking: {booking_tersimpan['id_booking']}).[/bold green]")
        
        # Panggil fitur unik (tugas Person C)
        _cetak_tiket(user, booking_tersimpan, paket)
        
    else:
        rprint("\nPembelian dibatalkan.", style="italic")
        time.sleep(2)


def _lihat_histori(user, tunggu=True):
    """
    Menampilkan histori pembelian user.
    """
    if tunggu:
        utils.bersihkan_layar()
        rprint("--- [bold yellow]RIWAYAT BOOKING SAYA[/bold yellow] ---")

    # Ambil data (tugas Person A)
    bookings = data_manager.dapatkan_booking_by_user(user['username'])
    
    if not bookings:
        rprint("[italic]Anda belum memiliki riwayat booking.[/italic]")
        if tunggu:
            time.sleep(2)
        return False

    table = Table(title=f"Histori Booking - {user['username']}", show_header=True, header_style="bold magenta")
    table.add_column("ID Booking", style="cyan")
    table.add_column("ID Paket", style="cyan")
    table.add_column("Nama Paket", style="green") # Tambahan: lebih informatif
    table.add_column("Jml Tiket", justify="right")
    table.add_column("Total Bayar (Rp)", style="blue", justify="right")

    for booking in bookings:
        # Ambil nama paket agar lebih jelas
        paket = data_manager.dapatkan_paket_by_id(booking['id_paket'])
        nama_paket = paket['nama'] if paket else "[Paket Dihapus]"
        
        table.add_row(
            booking['id_booking'],
            booking['id_paket'],
            nama_paket,
            str(booking['jumlah_tiket']),
            f"{booking['total_bayar']:,}"
        )
        
    console.print(table)
    
    if tunggu:
        input("\nTekan Enter untuk kembali...")
    return True

def _beri_rating(user):
    """
    Alur untuk user memberikan rating pada paket yang sudah dibeli.
    """
    utils.bersihkan_layar()
    rprint("--- [bold yellow]BERI RATING & ULASAN[/bold yellow] ---")
    
    # Tampilkan histori dulu
    if not _lihat_histori(user, tunggu=False):
        rprint(f"\n[bold red]ERROR: Anda harus membeli tiket terlebih dahulu.[/bold red]")
        time.sleep(3) # <--- TAMBAHKAN BARIS INI
        return # Kembali jika belum punya histori
        

    # Dapatkan daftar paket yg *sudah dibeli*
    bookings = data_manager.dapatkan_booking_by_user(user['username'])
    paket_dibeli_ids = {b['id_paket'] for b in bookings} # Pakai set agar unik

    id_paket = input("\nMasukkan ID Paket yang ingin diberi rating: ").strip()

    # Validasi: Hanya boleh rating paket yang sudah dibeli
    if id_paket not in paket_dibeli_ids:
        rprint(f"\n[bold red]ERROR: Anda hanya bisa memberi rating untuk paket yang sudah Anda beli.[/bold red]")
        time.sleep(2)
        return

    # Validasi: Cek apakah paketnya masih ada
    paket = data_manager.dapatkan_paket_by_id(id_paket)
    if not paket:
        rprint(f"\n[bold red]ERROR: Paket ini (ID: {id_paket}) sepertinya sudah tidak ada.[/bold red]")
        time.sleep(2)
        return

    rprint(f"\nMemberi rating untuk: [bold green]{paket['nama']}[/bold green]")
    
    # Input Skor
    while True:
        try:
            skor = int(input("Skor (1-5): "))
            if 1 <= skor <= 5:
                break
            else:
                rprint("[bold red]Skor harus antara 1 sampai 5.[/bold red]")
        except ValueError:
            rprint("[bold red]ERROR: Masukkan harus berupa angka.[/bold red]")
            
    komentar = input("Komentar singkat (opsional): ").strip()

    # Siapkan data
    data_rating = {
        "username_user": user['username'],
        "id_paket": id_paket,
        "skor": skor,
        "komentar": komentar
    }
    
    # Simpan (tugas Person A)
    data_manager.simpan_rating_baru(data_rating)
    
    rprint(f"\n[bold green]SUKSES! Terima kasih atas ulasan Anda untuk '{paket['nama']}'.[/bold green]")
    time.sleep(2)


def _tampilkan_menu_riwayat(user):
    """
    Layar sub-menu untuk Riwayat dan Rating.
    """
    while True:
        utils.bersihkan_layar()
        rprint("--- [bold yellow]RIWAYAT SAYA[/bold yellow] ---")
        rprint("[1] Lihat Histori Pembelian")
        rprint("[2] Beri Rating & Ulasan")
        rprint("[3] Kembali ke Menu Utama")
        
        pilihan = input("Pilihan (1-3): ").strip()
        
        if pilihan == '1':
            _lihat_histori(user, tunggu=True)
        elif pilihan == '2':
            _beri_rating(user)
        elif pilihan == '3':
            break
        else:
            rprint("\n[bold red]ERROR: Pilihan tidak valid.[/bold red]")
            time.sleep(1)


# --- FUNGSI UTAMA (ENTRY POINT) ---
#
# INI ADALAH BAGIAN YANG MEMPERBAIKI ERROR ANDA
# Pastikan ini ada dan TIDAK TER-INDENTASI (rata kiri)
#
def start(user):
    """
    Fungsi utama yang dipanggil oleh main.py saat user login.
    'user' berisi data user yang sedang login (misal: {'username': 'budi', 'role': 'user', ...})
    """
    utils.bersihkan_layar()
    
    # "Dashboard" Sederhana (Fitur Unik)
    bookings_user = data_manager.dapatkan_booking_by_user(user['username'])
    jumlah_booking = len(bookings_user)
    
    rprint(f"[bold green]Selamat datang, {user['username']}![/bold green]")
    rprint(f"Anda memiliki [bold yellow]{jumlah_booking}[/bold yellow] riwayat booking.")
    time.sleep(2)

    while True:
        utils.bersihkan_layar()
        rprint("\n--- [bold yellow]MENU UTAMA USER[/bold yellow] ---")
        rprint("[1] Lihat Semua Paket Travel")
        rprint("[2] Lihat Detail & Rundown Paket")
        rprint("[3] Beli Tiket")
        rprint("[4] Riwayat Saya (Histori & Rating)")
        rprint("[5] Logout")
        
        pilihan = input("Masukkan pilihan (1-5): ").strip()
        
        if pilihan == '1':
            _lihat_semua_paket(tunggu=True)
        elif pilihan == '2':
            _lihat_detail_paket()
        elif pilihan == '3':
            _beli_tiket(user) # Perlu 'user' untuk tahu siapa yg beli
        elif pilihan == '4': #<- Sepertinya ada typo di kode sebelumnya, saya perbaiki jadi '4'
            _tampilkan_menu_riwayat(user) # Masuk ke sub-menu
        elif pilihan == '5':
           # BENAR (KODE BARU)
            rprint("\n[cyan]Logout berhasil. Kembali ke menu utama...[/cyan]")
            time.sleep(1)
            break # Keluar dari loop user, kembali ke main.py
        else:
            rprint("\n[bold red]ERROR: Pilihan tidak valid.[/bold red]")
            time.sleep(1)