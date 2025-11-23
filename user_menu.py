import data_manager
import utils
import time
import os
import webbrowser
import urllib.parse

from rich.console import Console
from rich.table import Table
from rich import print as rprint
from rich.panel import Panel
from rich.text import Text

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    import qrcode
    LIBRARIES_LOADED = True
except ImportError:
    LIBRARIES_LOADED = False
    # Jika gagal, program tetap jalan tapi fitur PDF/QR akan dinonaktifkan

console = Console()

# --- FITUR 1: CETAK TIKET PDF & BUKA EMAIL (SETELAH BAYAR) ---

def _buka_email_client(user, paket, nama_file_pdf):
    try:
        email_tujuan = user.get('email', '')
        if not email_tujuan:
            rprint("[bold red]ERROR: Tidak dapat menemukan email Anda di data user.[/bold red]")
            return

        subjek = f"Tiket Anda untuk {paket['nama']} (ID: {paket['id_paket']})"
        isi_email = (
            f"Halo {user['username']},\n\n"
            f"Terima kasih telah memesan paket {paket['nama']}!\n\n"
            f"Tiket Anda (dalam format PDF) ada di file '{nama_file_pdf}'.\n"
            "Silakan lampirkan (attach) file tersebut ke email ini untuk menyimpannya, atau cetak saat dibutuhkan.\n\n"
            "Terima kasih,\n"
            "When Yh Travel"
        )
        
        url_email = f"mailto:{email_tujuan}" \
                    f"?subject={urllib.parse.quote(subjek)}" \
                    f"&body={urllib.parse.quote(isi_email)}"

        webbrowser.open(url_email)
        
        rprint(f"\n[italic]Silakan periksa browser atau aplikasi email Anda.[/italic]")
        rprint(f"[bold]Jangan lupa lampirkan file:[/bold] {nama_file_pdf}")
        input("\nTekan Enter untuk melanjutkan...")

    except Exception as e:
        rprint(f"[bold red]Gagal membuka email client: {e}[/bold red]")
        time.sleep(2)

def _generate_ticket_pdf(user, booking_data, paket):
    """
    (FITUR UNIK 1)
    Membuat file PDF tiket yang berisi detail booking dan QR Code.
    """
    
    if not LIBRARIES_LOADED:
        rprint("\n[bold red]ERROR: Library 'reportlab' atau 'qrcode' tidak terinstal.[/bold red]")
        rprint("[italic]Fitur cetak PDF/QR tidak aktif. Silakan jalankan 'pip install reportlab qrcode[pil]'[/italic]")
        time.sleep(3)
        return

    booking_id = booking_data['id_booking']
    nama_file_pdf = f"tiket_{booking_id}.pdf"
    nama_file_qr = f"temp_qr_{booking_id}.png"
    
    rprint(f"\n[bold yellow]Membuat tiket {nama_file_pdf}...[/bold yellow]")
    
    try:
        #1. Buat QR Code
        qr_data = f"Booking ID: {booking_id}\nUser: {user['username']}\nPaket: {paket['nama']}"
        img_qr = qrcode.make(qr_data)
        img_qr.save(nama_file_qr)

        #2. Buat Halaman PDF
        c = canvas.Canvas(nama_file_pdf, pagesize=A4)
        width, height = A4
        
        #3. Tulis Teks ke PDF
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(width / 2.0, height - (30*mm), "E-TIKET - WHEN YH TRAVEL")
        c.line(30*mm, height - (35*mm), width - (30*mm), height - (35*mm))

        c.setFont("Helvetica", 12)
        c.drawString(30*mm, height - (45*mm), f"Booking ID  : {booking_id}")
        c.drawString(30*mm, height - (50*mm), f"Nama User   : {user['username']}")
        
        c.setFont("Helvetica-Bold", 14)
        c.drawString(30*mm, height - (60*mm), f"Paket: {paket['nama']}")
        c.setFont("Helvetica", 12)
        c.drawString(30*mm, height - (65*mm), f"Jumlah      : {booking_data['jumlah_tiket']} tiket")
        c.drawString(30*mm, height - (70*mm), f"Total Bayar : Rp {booking_data['total_bayar']:,}")

        #4. Masukkan Gambar QR ke PDF
        c.drawImage(nama_file_qr, width - (70*mm), height - (70*mm), width=150, height=150)
        
        c.showPage()
        c.save()

        #5. Hapus file QR sementara
        os.remove(nama_file_qr)
        
        rprint(f"[bold green]SUKSES! Tiket telah disimpan sebagai '{nama_file_pdf}'[/bold green]")
        
        #6. Panggil Fitur Email
        rprint("[bold yellow]Membuka email client Anda...[/bold yellow]")
        time.sleep(1)
        _buka_email_client(user, paket, nama_file_pdf)

    except Exception as e:
        rprint(f"\n[bold red]ERROR: Gagal membuat tiket PDF.[/bold red]")
        rprint(f"[italic]Detail: {e}[/italic]")
        time.sleep(3)
        if os.path.exists(nama_file_qr):
            os.remove(nama_file_qr)

# test
# --- FITUR 2: SIMULASI PENDING PAYMENT (SAAT BELI) ---

def _handle_pembayaran_simulasi(user, paket, jumlah_tiket, total_bayar):
    """
    (FITUR UNIK 3)
    Mensimulasikan alur payment gateway dengan 'pending state'.
    Mengembalikan True jika sukses, False jika dibatalkan.
    """
    utils.bersihkan_layar()
    rprint("--- [bold yellow]SIMULASI PAYMENT GATEWAY[/bold yellow] ---")
    rprint(f"Paket       : [green]{paket['nama']}[/green]")
    rprint(f"Total Tagihan : [blue]Rp {total_bayar:,}[/blue]")
    
    rprint("\nSilakan pilih metode pembayaran:")
    rprint("[1] Virtual Account (Simulasi)")
    rprint("[2] QRIS (Simulasi Cetak di Terminal)")
    rprint("[3] Batal")
    
    pilihan = input("Pilihan: ").strip()

    if pilihan == '1':
        # --- SIMULASI VIRTUAL ACCOUNT ---
        utils.bersihkan_layar()
        va_number = f"8808{user['username'].encode().hex()[:8]}"
        rprint(f"Silakan transfer ke [bold]Virtual Account: {va_number}[/bold]")
        rprint(f"Sebesar [bold blue]Rp {total_bayar:,}[/bold blue]")
        rprint("\n[italic]Aplikasi akan menunggu pembayaran Anda...[/italic]")
        
        konfirmasi_bayar = input("Ketik 'bayar' untuk mensimulasikan pembayaran lunas: ").strip().lower()
        
        if konfirmasi_bayar == 'bayar':
            return True # Pembayaran sukses
        else:
            return False # Pembayaran dibatalkan

    elif pilihan == '2':
        # --- SIMULASI QRIS (CETAK KE TERMINAL) ---
        if not LIBRARIES_LOADED:
            rprint("\n[bold red]ERROR: Library 'qrcode' tidak terinstal.[/bold red]")
            rprint("[italic]Fitur QRIS tidak aktif. Silakan jalankan 'pip install qrcode[pil]'[/italic]")
            time.sleep(3)
            return False
            
        utils.bersihkan_layar()
        rprint("Silakan pindai [bold]QRIS[/bold] di bawah ini menggunakan aplikasi Anda.")
        rprint(f"Tagihan: [bold blue]Rp {total_bayar:,}[/bold blue]")
        
        try:
            qris_data = f"QRIS.WHENYH.IDR_{total_bayar}.BOOKING_{paket['id_paket']}"
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(qris_data)
            qr.make(fit=True)
            
            rprint("\n")
            qr.print_tty() # Mencetak QR code ke terminal
            rprint("\n")
            
        except Exception as e:
            rprint(f"[bold red]Gagal membuat QR Code di terminal: {e}[/bold red]")
            time.sleep(2)
            return False

        rprint("[italic]Aplikasi akan menunggu pembayaran Anda...[/italic]")
        konfirmasi_bayar = input("Ketik 'bayar' untuk mensimulasikan pembayaran lunas: ").strip().lower()
        
        if konfirmasi_bayar == 'bayar':
            return True # Pembayaran sukses
        else:
            return False # Pembayaran dibatalkan

    else:
        # Pilihan [3] Batal
        return False

# =====================================================================
# --- FUNGSI MENU UTAMA USER ---
# =====================================================================

def _lihat_semua_paket(tunggu=True):
    """
    Menampilkan paket dengan konsep INTERACTIVE DASHBOARD.
    User bisa search & sort berulang kali tanpa keluar menu.
    """
    
    # --- STATE AWAL (Default) ---
    current_keyword = ""       # Tidak ada filter nama
    current_sort = '1'         # Default: Harga Termurah
    
    while True:
        utils.bersihkan_layar()
        
        # 1. Ambil Data Mentah
        paket_list = data_manager.dapatkan_semua_paket()
        
        # 2. Terapkan LOGIKA FILTER (Search)
        if current_keyword:
            paket_list = [p for p in paket_list if current_keyword in p['nama'].lower()]

        # 3. Terapkan LOGIKA SORTING
        if current_sort == '2':   # Harga Termahal
            paket_list = sorted(paket_list, key=lambda p: p['harga'], reverse=True)
            sort_label = "Harga (Termahal)"
        elif current_sort == '3': # Nama A-Z
            paket_list = sorted(paket_list, key=lambda p: p['nama'])
            sort_label = "Nama (A-Z)"
        elif current_sort == '4': # Kuota Sedikit
            paket_list = sorted(paket_list, key=lambda p: p['kuota'])
            sort_label = "Sisa Kuota (Sedikit)"
        else:                     # Default: Harga Termurah
            paket_list = sorted(paket_list, key=lambda p: p['harga'])
            sort_label = "Harga (Termurah)"

        # 4. Tampilkan HEADER & STATUS
        rprint("--- [bold yellow]EKSPLORASI PAKET TRAVEL[/bold yellow] ---")
        
        # Tampilkan status filter aktif agar user tidak bingung
        status_text = f"[dim]Filter: '{current_keyword if current_keyword else 'Semua'}' | Urutkan: {sort_label}[/dim]"
        rprint(Panel(status_text, style="white",expand=False))

        # 5. Tampilkan TABEL
        if not paket_list:
            rprint("\n[bold red]Tidak ada paket yang cocok dengan pencarian Anda.[/bold red]")
        else:
            table = Table(show_header=True, header_style="bold magenta", expand=False)
            table.add_column("ID", style="cyan", width=8)
            table.add_column("Nama Paket", style="green")
            table.add_column("Harga (Rp)", style="blue", justify="right")
            table.add_column("Kuota", justify="right")
            
            for paket in paket_list:
                if paket['kuota'] > 0:
                    table.add_row(
                        paket['id_paket'],
                        paket['nama'],
                        f"{paket['harga']:,}",
                        str(paket['kuota'])
                    )
            console.print(table)

        # 6. Jika mode 'tunggu=False' (dipakai utk pilih paket saat beli), 
        #    kita langsung keluar loop agar user bisa input ID di menu sebelumnya.
        if not tunggu:
            return True

        # 7. MENU INTERAKTIF (Hanya muncul jika mode eksplorasi)
        rprint("\n[bold cyan]Opsi Eksplorasi:[/bold cyan]")
        rprint("[1] 🔍 Cari Nama (Filter)   [3] 🔄 Reset Filter")
        rprint("[2] 🔃 Ganti Urutan (Sort)  [0] 🚪 Kembali ke Menu Utama")
        
        aksi = input("Pilihan: ").strip()

        if aksi == '1':
            # Update State Keyword
            rprint("\nMasukkan kata kunci pencarian:")
            current_keyword = input(">> ").strip().lower()
            # Loop akan mengulang dan tabel akan ter-refresh otomatis!
            
        elif aksi == '2':
            # Update State Sort
            rprint("\n[1] Harga Termurah  [2] Harga Termahal")
            rprint("[3] Nama (A-Z)      [4] Kuota Sedikit")
            pilihan_sort = input(">> ").strip()
            if pilihan_sort in ['1', '2', '3', '4']:
                current_sort = pilihan_sort
            
        elif aksi == '3':
            # Reset semua state ke default
            current_keyword = ""
            current_sort = '1'
            rprint("[italic]Filter di-reset...[/italic]")
            time.sleep(1)
            
        elif aksi == '0':
            break # Keluar dari fungsi, kembali ke menu utama user
            
        else:
            rprint("[red]Pilihan tidak valid[/red]")
            time.sleep(0.5)

    return True
def _lihat_detail_paket():
    """
    Menampilkan detail rundown dari satu paket.
    """
    utils.bersihkan_layar()
    rprint("--- [bold yellow]DETAIL & RUNDOWN PAKET[/bold yellow] ---")

    if not _lihat_semua_paket(tunggu=False):
        return

    id_paket = input("\nMasukkan ID Paket yang ingin dilihat detailnya: ").strip()
    paket = data_manager.dapatkan_paket_by_id(id_paket)

    if not paket:
        rprint(f"\n[bold red]ERROR: ID Paket '{id_paket}' tidak ditemukan.[/bold red]")
        time.sleep(2)
        return

    utils.bersihkan_layar()
    
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
    (SUDAH DIPERBARUI DENGAN LOGIKA PAYMENT GATEWAY)
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
                break
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
    
    konfirmasi = input("\nLanjutkan ke pembayaran? (y/n): ").strip().lower()

    if konfirmasi == 'y':
        # 4. (BARU) Panggil Modul Pembayaran Simulasi
        sukses_bayar = _handle_pembayaran_simulasi(user, paket, jumlah_tiket, total_bayar)
        
        if sukses_bayar:
            # 5. Proses Transaksi HANYA JIKA BAYAR SUKSES
            
            # a. Buat data booking
            booking_data = {
                "username_user": user['username'],
                "id_paket": id_paket,
                "jumlah_tiket": jumlah_tiket,
                "total_bayar": total_bayar
            }
            booking_tersimpan = data_manager.simpan_booking_baru(booking_data)

            # b. Kurangi kuota paket
            sisa_kuota = paket['kuota'] - jumlah_tiket
            data_update = {"kuota": sisa_kuota}
            data_manager.update_paket(id_paket, data_update)

            rprint(f"\n[bold green]PEMBAYARAN DITERIMA! (ID Booking: {booking_tersimpan['id_booking']}).[/bold green]")
            
            # c. Cetak tiket PDF & buka email
            _generate_ticket_pdf(user, booking_tersimpan, paket)
        
        else:
            # Jika _handle_pembayaran_simulasi() mengembalikan False
            rprint("\n[bold red]PEMBAYARAN DIBATALKAN / GAGAL.[/bold red]")
            time.sleep(2)
            
    else:
        rprint("\n[italic]Pembelian dibatalkan.[/italic]")
        time.sleep(2)


def _lihat_histori(user, tunggu=True):
    """
    Menampilkan histori pembelian user.
    """
    if tunggu:
        utils.bersihkan_layar()
        rprint("--- [bold yellow]RIWAYAT BOOKING SAYA[/bold yellow] ---")

    bookings = data_manager.dapatkan_booking_by_user(user['username'])
    
    if not bookings:
        rprint("[italic]Anda belum memiliki riwayat booking.[/italic]")
        if tunggu:
            time.sleep(2)
        return False

    table = Table(title=f"Histori Booking - {user['username']}", show_header=True, header_style="bold magenta")
    table.add_column("ID Booking", style="cyan")
    table.add_column("ID Paket", style="cyan")
    table.add_column("Nama Paket", style="green")
    table.add_column("Jml Tiket", justify="right")
    table.add_column("Total Bayar (Rp)", style="blue", justify="right")

    for booking in bookings:
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
    (SUDAH DIPERBAIKI - 'Flashing' bug)
    """
    utils.bersihkan_layar()
    rprint("--- [bold yellow]BERI RATING & ULASAN[/bold yellow] ---")
    
    # Perbaikan "Flashing" Bug
    if not data_manager.dapatkan_booking_by_user(user['username']):
        rprint(f"\n[bold red][ERROR] Anda belum memiliki riwayat booking untuk diberi rating.[/bold red]")
        time.sleep(2)
        return
        
    # Jika lolos, baru tampilkan histori untuk dipilih
    _lihat_histori(user, tunggu=False)

    bookings = data_manager.dapatkan_booking_by_user(user['username'])
    paket_dibeli_ids = {b['id_paket'] for b in bookings}

    id_paket = input("\nMasukkan ID Paket yang ingin diberi rating: ").strip()

    if id_paket not in paket_dibeli_ids:
        rprint(f"\n[bold red]ERROR: Anda hanya bisa memberi rating untuk paket yang sudah Anda beli.[/bold red]")
        time.sleep(2)
        return

    paket = data_manager.dapatkan_paket_by_id(id_paket)
    if not paket:
        rprint(f"\n[bold red]ERROR: Paket ini (ID: {id_paket}) sepertinya sudah tidak ada.[/bold red]")
        time.sleep(2)
        return

    rprint(f"\nMemberi rating untuk: [bold green]{paket['nama']}[/bold green]")
    
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

    data_rating = {
        "username_user": user['username'],
        "id_paket": id_paket,
        "skor": skor,
        "komentar": komentar
    }
    
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


# =====================================================================
# --- FUNGSI UTAMA (ENTRY POINT) ---
# =====================================================================

def start(user):
    """
    Fungsi utama yang dipanggil oleh main.py saat user login.
    """
    utils.bersihkan_layar()
    
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
            _beli_tiket(user)
        elif pilihan == '4':
            _tampilkan_menu_riwayat(user)
        elif pilihan == '5':
            rprint("\n[cyan]Logout berhasil. Kembali ke menu utama...[/cyan]")
            time.sleep(1)
            break
        else:
            rprint("\n[bold red]ERROR: Pilihan tidak valid.[/bold red]")
            time.sleep(1)