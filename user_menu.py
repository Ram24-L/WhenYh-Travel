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

# Hanya import library PDF (tanpa QR Code)
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    LIBRARIES_LOADED = True
except ImportError:
    LIBRARIES_LOADED = False

console = Console()

# =====================================================================
# --- FITUR 1: CETAK TIKET PDF & BUKA EMAIL (SETELAH BAYAR)
# =====================================================================

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
            f"Tiket Anda (format PDF) ada di file '{nama_file_pdf}'.\n"
            "Silakan lampirkan file tersebut saat menyimpan.\n\n"
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
    Membuat file PDF tiket TANPA QR CODE.
    """

    if not LIBRARIES_LOADED:
        rprint("\n[bold red]ERROR: Library 'reportlab' tidak terinstal.[/bold red]")
        rprint("[italic]Fitur cetak PDF tidak aktif.[/italic]")
        time.sleep(3)
        return

    booking_id = booking_data['id_booking']
    nama_file_pdf = f"tiket_{booking_id}.pdf"

    rprint(f"\n[bold yellow]Membuat tiket {nama_file_pdf}...[/bold yellow]")

    try:
        c = canvas.Canvas(nama_file_pdf, pagesize=A4)
        width, height = A4
        
        # Judul
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(width / 2.0, height - (30*mm), "E-TIKET - WHEN YH TRAVEL")
        c.line(30*mm, height - (35*mm), width - (30*mm), height - (35*mm))

        # Isi Data
        c.setFont("Helvetica", 12)
        c.drawString(30*mm, height - (45*mm), f"Booking ID  : {booking_id}")
        c.drawString(30*mm, height - (50*mm), f"Nama User   : {user['username']}")

        c.setFont("Helvetica-Bold", 14)
        c.drawString(30*mm, height - (60*mm), f"Paket: {paket['nama']}")
        
        c.setFont("Helvetica", 12)
        c.drawString(30*mm, height - (65*mm), f"Jumlah      : {booking_data['jumlah_tiket']} tiket")
        c.drawString(30*mm, height - (70*mm), f"Total Bayar : Rp {booking_data['total_bayar']:,}")

        c.showPage()
        c.save()

        rprint(f"[bold green]SUKSES! Tiket disimpan sebagai '{nama_file_pdf}'[/bold green]")

        # Buka email
        rprint("[bold yellow]Membuka email client...[/bold yellow]")
        time.sleep(1)
        _buka_email_client(user, paket, nama_file_pdf)

    except Exception as e:
        rprint(f"\n[bold red]ERROR: Gagal membuat tiket PDF.[/bold red]")
        rprint(f"[italic]Detail: {e}[/italic]")
        time.sleep(3)


# =====================================================================
# --- FITUR 2: SIMULASI PEMBAYARAN (TANPA QRIS)
# =====================================================================

def _handle_pembayaran_simulasi(user, paket, jumlah_tiket, total_bayar):

    utils.bersihkan_layar()
    rprint("--- [bold yellow]SIMULASI PAYMENT GATEWAY[/bold yellow] ---")
    rprint(f"Paket         : [green]{paket['nama']}[/green]")
    rprint(f"Total Tagihan : [blue]Rp {total_bayar:,}[/blue]")

    rprint("\nSilakan pilih metode pembayaran:")
    rprint("[1] Virtual Account (Simulasi)")
    rprint("[2] Batal")

    pilihan = input("Pilihan: ").strip()

    if pilihan == '1':
        utils.bersihkan_layar()
        va_number = f"8808{user['username'].encode().hex()[:8]}"
        rprint(f"Virtual Account: [bold]{va_number}[/bold]")
        rprint(f"Total: [blue]Rp {total_bayar:,}[/blue]")
        rprint("\n[italic]Tunggu pembayaran Anda...[/italic]")

        konfirmasi_bayar = input("Ketik 'bayar' jika sudah membayar: ").strip().lower()
        return konfirmasi_bayar == "bayar"

    return False  # Jika batal


# =====================================================================
# --- MENU USER: LIHAT PAKET, SEARCH, SORT
# =====================================================================

def _lihat_semua_paket(tunggu=True):
    """
    Dashboard interaktif untuk search & sort.
    """

    current_keyword = ""
    current_sort = '1'

    while True:
        utils.bersihkan_layar()

        paket_list = data_manager.dapatkan_semua_paket()

        # FILTER
        if current_keyword:
            paket_list = [p for p in paket_list if current_keyword in p['nama'].lower()]

        # SORTING
        if current_sort == '2':   
            paket_list = sorted(paket_list, key=lambda p: p['harga'], reverse=True)
            sort_label = "Harga (Termahal)"
        elif current_sort == '3':
            paket_list = sorted(paket_list, key=lambda p: p['nama'])
            sort_label = "Nama (A-Z)"
        elif current_sort == '4':
            paket_list = sorted(paket_list, key=lambda p: p['kuota'])
            sort_label = "Kuota (Sedikit)"
        else:
            paket_list = sorted(paket_list, key=lambda p: p['harga'])
            sort_label = "Harga (Termurah)"

        rprint("--- [bold yellow]EKSPLORASI PAKET TRAVEL[/bold yellow] ---")
        status_text = f"[dim]Filter: '{current_keyword or 'Semua'}' | Urutkan: {sort_label}[/dim]"
        rprint(Panel(status_text, expand=False))

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan", width=8)
        table.add_column("Nama Paket", style="green")
        table.add_column("Harga (Rp)", style="blue")
        table.add_column("Kuota", justify="right")

        for p in paket_list:
            if p['kuota'] > 0:
                table.add_row(p['id_paket'], p['nama'], f"{p['harga']:,}", str(p['kuota']))

        console.print(table)

        if not tunggu:
            return True

        # Menu eksplorasi
        rprint("\n[bold cyan]Opsi:[/bold cyan]")
        rprint("[1] Cari Nama  [3] Reset")
        rprint("[2] Sorting    [0] Kembali")

        aksi = input("Pilihan: ").strip()

        if aksi == '1':
            current_keyword = input("Masukkan kata kunci: ").strip().lower()

        elif aksi == '2':
            rprint("\n[1] Termurah  [2] Termahal  [3] Nama A-Z  [4] Kuota Sedikit")
            pilih = input(">> ").strip()
            if pilih in ['1', '2', '3', '4']:
                current_sort = pilih

        elif aksi == '3':
            current_keyword = ""
            current_sort = '1'
            time.sleep(1)

        elif aksi == '0':
            break

    return True


# =====================================================================
# --- DETAIL PAKET
# =====================================================================

def _lihat_detail_paket():
    utils.bersihkan_layar()
    rprint("--- [bold yellow]DETAIL PAKET[/bold yellow] ---")

    if not _lihat_semua_paket(tunggu=False):
        return

    id_paket = input("\nMasukkan ID Paket: ").strip()
    paket = data_manager.dapatkan_paket_by_id(id_paket)

    if not paket:
        rprint("[red]ID paket tidak ditemukan.[/red]")
        time.sleep(2)
        return

    utils.bersihkan_layar()
    rundown_text = Text()

    if paket['rundown']:
        for i, item in enumerate(paket['rundown'], 1):
            rundown_text.append(f"{i}. {item}\n")
    else:
        rundown_text.append("[italic]Rundown tidak tersedia.[/italic]")

    panel_content = Text()
    panel_content.append(f"ID Paket: {paket['id_paket']}\n", style="cyan")
    panel_content.append(f"Harga: Rp {paket['harga']:,}\n", style="blue")
    panel_content.append(f"Kuota: {paket['kuota']}\n\n", style="bold")
    panel_content.append("--- RUNDOWN ---\n", style="yellow")
    panel_content.append(rundown_text)

    console.print(Panel(panel_content, title=paket['nama'], border_style="yellow"))
    input("\nTekan Enter...")


# =====================================================================
# --- BELI TIKET
# =====================================================================

def _beli_tiket(user):

    utils.bersihkan_layar()
    rprint("--- [bold yellow]BELI TIKET[/bold yellow] ---")

    if not _lihat_semua_paket(tunggu=False):
        return

    id_paket = input("\nMasukkan ID Paket: ").strip()
    paket = data_manager.dapatkan_paket_by_id(id_paket)

    if not paket:
        rprint("[red]ID Paket tidak ditemukan.[/red]")
        time.sleep(2)
        return

    if paket['kuota'] == 0:
        rprint("[red]Kuota habis.[/red]")
        time.sleep(2)
        return

    # Jumlah tiket
    while True:
        try:
            jumlah = int(input(f"Jumlah tiket (maks {paket['kuota']}): "))
            if 1 <= jumlah <= paket['kuota']:
                break
            rprint("[red]Jumlah tidak valid.[/red]")
        except:
            rprint("[red]Masukkan angka.[/red]")

    total = paket['harga'] * jumlah

    utils.bersihkan_layar()
    rprint("--- [bold yellow]KONFIRMASI[/bold yellow] ---")
    rprint(f"Paket: {paket['nama']}")
    rprint(f"Jumlah: {jumlah}")
    rprint(f"Total Bayar: Rp {total:,}")

    if input("Lanjut beli? (y/n): ").strip().lower() != 'y':
        return

    # Proses pembayaran
    sukses = _handle_pembayaran_simulasi(user, paket, jumlah, total)

    if not sukses:
        rprint("[red]Pembayaran gagal/batal.[/red]")
        time.sleep(2)
        return

    # Simpan booking
    booking_data = {
        "username_user": user['username'],
        "id_paket": id_paket,
        "jumlah_tiket": jumlah,
        "total_bayar": total
    }

    booking_saved = data_manager.simpan_booking_baru(booking_data)

    # Update kuota
    data_manager.update_paket(id_paket, {"kuota": paket['kuota'] - jumlah})

    rprint(f"[green]Pembayaran berhasil! ID Booking: {booking_saved['id_booking']}[/green]")

    # Cetak PDF
    _generate_ticket_pdf(user, booking_saved, paket)


# =====================================================================
# --- HISTORI & RATING
# =====================================================================

def _lihat_histori(user, tunggu=True):

    if tunggu:
        utils.bersihkan_layar()
        rprint("--- [bold yellow]HISTORI PEMBELIAN[/bold yellow] ---")

    bookings = data_manager.dapatkan_booking_by_user(user['username'])

    if not bookings:
        rprint("[italic]Belum ada booking.[/italic]")
        if tunggu:
            time.sleep(2)
        return

    table = Table(title=f"Histori Booking - {user['username']}")
    table.add_column("ID Booking", style="cyan")
    table.add_column("ID Paket")
    table.add_column("Nama Paket", style="green")
    table.add_column("Jumlah", justify="right")
    table.add_column("Total", justify="right", style="blue")

    for b in bookings:
        paket = data_manager.dapatkan_paket_by_id(b['id_paket'])
        table.add_row(
            b['id_booking'],
            b['id_paket'],
            paket['nama'] if paket else "[Hapus]",
            str(b['jumlah_tiket']),
            f"{b['total_bayar']:,}"
        )

    console.print(table)
    if tunggu:
        input("\nEnter untuk kembali...")

def _beri_rating(user):

    utils.bersihkan_layar()
    rprint("--- [bold yellow]BERI RATING[/bold yellow] ---")

    bookings = data_manager.dapatkan_booking_by_user(user['username'])
    
    if not bookings:
        rprint("[red]Belum ada booking untuk dirating.[/red]")
        time.sleep(2)
        return

    _lihat_histori(user, tunggu=False)

    id_paket = input("\nID Paket yang ingin dirating: ").strip()

    if id_paket not in {b['id_paket'] for b in bookings}:
        rprint("[red]Anda belum membeli paket ini.[/red]")
        time.sleep(2)
        return

    paket = data_manager.dapatkan_paket_by_id(id_paket)
    if not paket:
        rprint("[red]Paket tidak ditemukan.[/red]")
        time.sleep(2)
        return

    while True:
        try:
            skor = int(input("Skor (1–5): "))
            if 1 <= skor <= 5:
                break
        except:
            pass
        rprint("[red]Masukkan skor valid.[/red]")

    komentar = input("Komentar (opsional): ").strip()

    data_manager.simpan_rating_baru({
        "username_user": user['username'],
        "id_paket": id_paket,
        "skor": skor,
        "komentar": komentar
    })

    rprint("[green]Terima kasih atas rating Anda![/green]")
    time.sleep(2)

def _tampilkan_menu_riwayat(user):

    while True:
        utils.bersihkan_layar()
        rprint("--- [bold yellow]RIWAYAT SAYA[/bold yellow] ---")
        rprint("[1] Lihat Histori")
        rprint("[2] Beri Rating")
        rprint("[3] Kembali")

        pilih = input("Pilih (1–3): ").strip()

        if pilih == '1':
            _lihat_histori(user)
        elif pilih == '2':
            _beri_rating(user)
        elif pilih == '3':
            break
        else:
            rprint("[red]Pilihan tidak valid[/red]")
            time.sleep(1)

# =====================================================================
# --- ENTRY POINT
# =====================================================================

def start(user):

    utils.bersihkan_layar()

    jumlah_booking = len(data_manager.dapatkan_booking_by_user(user['username']))
    
    rprint(f"[green]Selamat datang, {user['username']}![/green]")
    rprint(f"Anda memiliki {jumlah_booking} riwayat booking.")
    time.sleep(2)

    while True:
        utils.bersihkan_layar()
        rprint("\n--- [bold yellow]MENU UTAMA USER[/bold yellow] ---")
        rprint("[1] Lihat Semua Paket")
        rprint("[2] Lihat Detail Paket")
        rprint("[3] Beli Tiket")
        rprint("[4] Riwayat Saya")
        rprint("[5] Logout")

        pilih = input("Pilih (1–5): ").strip()

        if pilih == '1':
            _lihat_semua_paket()
        elif pilih == '2':
            _lihat_detail_paket()
        elif pilih == '3':
            _beli_tiket(user)
        elif pilih == '4':
            _tampilkan_menu_riwayat(user)
        elif pilih == '5':
            rprint("[cyan]Logout berhasil.[/cyan]")
            time.sleep(1)
            break
        else:
            rprint("[red]Pilihan tidak valid[/red]")
            time.sleep(1)
