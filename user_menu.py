import data_manager
import utils
import time
import os
import datetime

from rich.console import Console
from rich.table import Table
from rich import print as rprint
from rich.panel import Panel
from rich.text import Text

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.lib.colors import Color
    from reportlab.lib.utils import ImageReader
    import qrcode
    LIBRARIES_LOADED = True
except ImportError:
    LIBRARIES_LOADED = False

console = Console()

def _generate_ticket_pdf(user, booking_data, paket):
    if not LIBRARIES_LOADED:
        rprint("\n[bold red]ERROR: Library 'reportlab', 'Pillow' atau 'qrcode' tidak terinstal.[/bold red]")
        console.input("Tekan [bold]Enter[/bold] untuk lanjut...")
        return

    today_str = datetime.date.today().strftime("%Y-%m-%d")
    base_folder = "tiket_output"
    target_folder = os.path.join(base_folder, today_str)
    logo_path = os.path.join("data", "logo.jpg")

    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    booking_id = booking_data['id_booking']
    nama_file = f"Tiket_{booking_id}.pdf"
    file_path = os.path.join(target_folder, nama_file)
    temp_qr_path = f"temp_qr_{booking_id}.png"

    rprint(f"\n[bold yellow]Sedang mendesain tiket konsep baru...[/bold yellow]")

    try:
        brand_navy = Color(0.05, 0.15, 0.35)
        text_dark = Color(0.2, 0.2, 0.2)

        qr_content = f"BOOKING:{booking_id}|USER:{user['username']}|PAKET:{paket['id_paket']}"
        qr = qrcode.make(qr_content)
        qr.save(temp_qr_path)

        c = canvas.Canvas(file_path, pagesize=A4)
        width, height = A4
        
        logo_width = 60*mm
        logo_height = 20*mm
        logo_x = (width - logo_width) / 2
        logo_y = height - logo_height - 10*mm

        if os.path.exists(logo_path):
            try:
                logo_img = ImageReader(logo_path)
                c.drawImage(logo_img, logo_x, logo_y, width=logo_width, height=logo_height, mask='auto')
            except Exception as e:
                 rprint(f"[yellow]Warning: Gagal memuat logo.png: {e}[/yellow]")

        subtitle_y = logo_y - 10*mm
        c.setFillColor(text_dark)
        c.setFont("Helvetica", 12)
        c.drawCentredString(width / 2, subtitle_y, "E-Ticket Resmi & Bukti Perjalanan")

        main_line_y = subtitle_y - 8*mm
        c.setStrokeColor(brand_navy)
        c.setLineWidth(2)
        c.line(20*mm, main_line_y, width - 20*mm, main_line_y)
        c.setLineWidth(1)


        y_pos = main_line_y - 15*mm
        
        c.setFillColor(text_dark)

        c.setFillColor(brand_navy)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(20*mm, y_pos, "DETAIL PEMESAN:")
        
        c.setFillColor(text_dark)
        c.setFont("Helvetica", 11)
        c.drawString(20*mm, y_pos - 8*mm,  f"Booking ID     :  {booking_id}")
        c.drawString(20*mm, y_pos - 16*mm, f"Nama User      :  {user['username'].upper()}")
        c.drawString(20*mm, y_pos - 24*mm, f"Email          :  {user.get('email', '-')}")
        c.drawString(20*mm, y_pos - 32*mm, f"Tanggal Cetak  :  {today_str}")

        c.setFillColor(brand_navy)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(110*mm, y_pos, "DETAIL PAKET:")
        
        c.setFillColor(text_dark)
        c.setFont("Helvetica", 11)
        c.drawString(110*mm, y_pos - 8*mm,  f"Paket        :  {paket['nama']}")
        c.drawString(110*mm, y_pos - 16*mm, f"Jumlah Tiket :  {booking_data['jumlah_tiket']} Pax")
        
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(brand_navy)
        c.drawString(110*mm, y_pos - 24*mm, f"Total Bayar  :  Rp {booking_data['total_bayar']:,}")

        y_rundown_start = y_pos - 55*mm

        c.setFillColor(brand_navy)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(20*mm, y_rundown_start, "RUNDOWN PERJALANAN:")
        
        qr_x_pos = 130*mm
        qr_size = 45*mm
        qr_y_pos = y_rundown_start - qr_size + 10*mm
        
        c.drawImage(temp_qr_path, qr_x_pos, qr_y_pos- 3*mm, width=qr_size, height=qr_size)
        
        c.setFillColor(text_dark)
        c.setFont("Helvetica", 9)
        c.drawCentredString(qr_x_pos + (qr_size/2), qr_y_pos - 5*mm, "Scan untuk Validasi Petugas")

        y_list = y_rundown_start - 10*mm
        c.setFillColor(text_dark)
        c.setFont("Helvetica", 11)
        
        if paket['rundown']:
            for i, item in enumerate(paket['rundown'], 1):
                text = f"{i}. {item}"
                if len(text) > 60: text = text[:60] + "..."
                
                c.drawString(25*mm, y_list, text)
                y_list -= 8*mm 
                
                if y_list < 20*mm:
                    c.showPage()
                    y_list = height - 30*mm
                    c.setFont("Helvetica", 11)
        else:
            c.drawString(25*mm, y_list, "Informasi rundown tidak tersedia.")

        c.setFont("Helvetica-Oblique", 8)
        c.setFillColor(colors.grey)
        c.drawCentredString(width/2, 15*mm, "Dokumen ini diterbitkan secara elektronik oleh sistem When Yh Travel dan sah tanpa tanda tangan basah.")

        c.save()

        if os.path.exists(temp_qr_path):
            os.remove(temp_qr_path)

        email_user = user.get('email', '[Email tidak terdaftar]')
        
        rprint(Panel(f"""
[bold green]PEMBAYARAN SUKSES & TIKET TERCETAK![/bold green]

Terima kasih, [bold]{user['username']}[/bold].
E-Ticket Anda telah berhasil diterbitkan dengan konsep baru.

[bold yellow]INFO:[/bold yellow]
File tiket juga akan dikirimkan ke email: [cyan u]{email_user}[/cyan u]
Silakan cek Inbox/Spam Anda.
        """, title="Transaksi Berhasil", border_style="green"))

        console.input("\nTekan [bold]Enter[/bold] untuk kembali ke menu utama...")

    except Exception as e:
        rprint(f"\n[bold red]ERROR: Gagal mendesain tiket PDF.[/bold red]")
        rprint(f"[italic]Detail error: {e}[/italic]")
        console.input("\nTekan [bold]Enter[/bold] untuk lanjut...")
        if os.path.exists(temp_qr_path):
            os.remove(temp_qr_path)

def _handle_pembayaran_simulasi(user, paket, jumlah_tiket, total_bayar):
    utils.bersihkan_layar()
    rprint("--- [bold yellow]SIMULASI PAYMENT GATEWAY[/bold yellow] ---")
    rprint(f"Paket         : [green]{paket['nama']}[/green]")
    rprint(f"Total Tagihan : [blue]Rp {total_bayar:,}[/blue]")

    while True:
        rprint("\nSilakan pilih metode pembayaran:")
        rprint("[1] Virtual Account (Simulasi)")
        rprint("[2] Batal")

        pilihan = console.input("Pilihan ([bold]1[/bold]/[bold]2[/bold]): ").strip()

        if pilihan == '1':
            utils.bersihkan_layar()
            va_number = f"8808{user['username'].encode().hex()[:8]}"
            
            rprint(Panel(f"""
[bold]Bank Transfer (Virtual Account)[/bold]
Nomor VA : [cyan]{va_number}[/cyan]
Total    : [blue]Rp {total_bayar:,}[/blue]

[italic]Silakan lakukan transfer ke nomor di atas...[/italic]
            """, title="Payment Info", border_style="blue"))
            
            while True:
                konfirmasi = console.input("\nKetik '[bold green]bayar[/bold green]' untuk menyelesaikan: ").strip().lower()
                if konfirmasi == 'bayar':
                    return True
                elif konfirmasi == 'batal':
                     rprint("[yellow]Pembayaran dibatalkan user.[/yellow]")
                     return False
                else:
                     rprint("[red]Perintah tidak dikenal. Ketik 'bayar' atau 'batal'.[/red]")

        elif pilihan == '2':
            rprint("\n[yellow]Pembayaran dibatalkan.[/yellow]")
            time.sleep(1)
            return False
        else:
            rprint("[bold red]Pilihan tidak valid! Masukkan angka 1 atau 2.[/bold red]")

def _lihat_semua_paket(tunggu=True):
    current_keyword = ""
    current_sort = '1'

    while True:
        utils.bersihkan_layar()
        paket_list = data_manager.dapatkan_semua_paket()

        if current_keyword:
            paket_list = [p for p in paket_list if current_keyword in p['nama'].lower()]

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

        if not paket_list:
             rprint("[red]Tidak ada paket yang sesuai.[/red]")
        else:
            for p in paket_list:
                if p['kuota'] > 0:
                    table.add_row(p['id_paket'], p['nama'], f"{p['harga']:,}", str(p['kuota']))
            console.print(table)

        if not tunggu:
            return True

        rprint("\n[bold cyan]Opsi:[/bold cyan]")
        rprint("[1] Cari Nama  [3] Reset")
        rprint("[2] Sorting    [0] Kembali")

        aksi = input("Pilihan: ").strip()

        if aksi == '1':
            current_keyword = input("Masukkan kata kunci: ").strip().lower()
        elif aksi == '2':
            rprint("\n[1] Termurah  [2] Termahal  [3] Nama A-Z  [4] Kuota Sedikit")
            pilih = input(">> ").strip()
            if pilih in ['1', '2', '3', '4']: current_sort = pilih
        elif aksi == '3':
            current_keyword = ""
            current_sort = '1'
            time.sleep(0.5)
        elif aksi == '0':
            break

    return True

def _lihat_detail_paket():
    utils.bersihkan_layar()
    rprint("--- [bold yellow]DETAIL, RUNDOWN & ULASAN[/bold yellow] ---")

    if not _lihat_semua_paket(tunggu=False):
        return

    id_paket = input("\nMasukkan ID Paket: ").strip()
    paket = data_manager.dapatkan_paket_by_id(id_paket)

    if not paket:
        rprint(f"\n[bold red]ERROR: ID Paket '{id_paket}' tidak ditemukan.[/bold red]")
        time.sleep(2)
        return

    utils.bersihkan_layar()
    list_rating = data_manager.dapatkan_rating_by_paket(id_paket)
    
    panel_content = Text()
    panel_content.append(f"ID Paket: {paket['id_paket']}\n", style="cyan")
    panel_content.append(f"Harga   : Rp {paket['harga']:,}\n", style="blue")
    
    panel_content.append("Rating  : ", style="bold")
    if list_rating:
        rata_rata = sum(r['skor'] for r in list_rating) / len(list_rating)
        bintang = "★" * int(rata_rata) + "☆" * (5 - int(rata_rata))
        panel_content.append(f"{bintang}", style="yellow")
        panel_content.append(f" ({rata_rata:.1f}/5.0)\n")
    else:
        panel_content.append("Belum ada ulasan.\n", style="italic dim")

    panel_content.append(f"Sisa Kuota: {paket['kuota']} orang\n\n", style="bold")
    
    panel_content.append("--- RUNDOWN PERJALANAN ---\n", style="bold yellow")
    if paket['rundown']:
        for i, item in enumerate(paket['rundown'], 1):
            panel_content.append(f"  {i}. {item}\n")
    else:
        panel_content.append("[italic]Rundown tidak tersedia.[/italic]\n")

    if list_rating:
        panel_content.append("\n--- APA KATA MEREKA? ---\n", style="bold cyan")
        for r in list_rating[-3:]: 
            user_sensor = r['username_user'][:3] + "***"
            panel_content.append(f"👤 {user_sensor} : ")
            panel_content.append(f"{r['skor']}★\n", style="yellow")
            panel_content.append(f"   \"{r['komentar']}\"\n\n", style="italic")

    console.print(Panel(panel_content, title=f"[bold green]{paket['nama']}[/bold green]", border_style="yellow"))
    input("\nTekan Enter untuk kembali...")

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

    while True:
        try:
            jumlah = int(input(f"Jumlah tiket (maks {paket['kuota']}): "))
            if 1 <= jumlah <= paket['kuota']: break
            rprint("[red]Jumlah tidak valid.[/red]")
        except:
            rprint("[red]Masukkan angka.[/red]")

    total = paket['harga'] * jumlah

    utils.bersihkan_layar()
    rprint(Panel(f"""
[bold]Konfirmasi Pesanan[/bold]
Paket  : {paket['nama']}
Jumlah : {jumlah} Pax
Harga  : Rp {total:,}
    """, style="green"))

    while True:
        konfirmasi = console.input("\nLanjut pembayaran? ([bold green]y[/bold green]/[bold red]n[/bold red]): ").strip().lower()
        if konfirmasi == 'y': break 
        elif konfirmasi == 'n':
            rprint("\n[yellow]Transaksi dibatalkan.[/yellow]")
            time.sleep(1); return
        else: rprint("[red]Ketik 'y' atau 'n'.[/red]")

    sukses = _handle_pembayaran_simulasi(user, paket, jumlah, total)

    if not sukses:
        return

    booking_data = {
        "username_user": user['username'],
        "id_paket": id_paket,
        "jumlah_tiket": jumlah,
        "total_bayar": total
    }
    booking_saved = data_manager.simpan_booking_baru(booking_data)
    
    data_manager.update_paket(id_paket, {"kuota": paket['kuota'] - jumlah})

    rprint(f"\n[bold green]MEMPROSES TIKET...[/bold green]")
    _generate_ticket_pdf(user, booking_saved, paket)

def _lihat_histori(user, tunggu=True):
    if tunggu:
        utils.bersihkan_layar()
        rprint("--- [bold yellow]HISTORI PEMBELIAN[/bold yellow] ---")

    bookings = data_manager.dapatkan_booking_by_user(user['username'])

    if not bookings:
        rprint("[italic]Belum ada booking.[/italic]")
        if tunggu: time.sleep(2)
        return

    table = Table(title=f"Histori Booking - {user['username']}")
    table.add_column("ID Booking", style="cyan")
    table.add_column("Paket", style="green")
    table.add_column("Jml", justify="right")
    table.add_column("Total", justify="right", style="blue")

    for b in bookings:
        paket = data_manager.dapatkan_paket_by_id(b['id_paket'])
        nama_paket = paket['nama'] if paket else "[Hapus]"
        table.add_row(b['id_booking'], nama_paket, str(b['jumlah_tiket']), f"{b['total_bayar']:,}")

    console.print(table)
    if tunggu: input("\nEnter untuk kembali...")

def _beri_rating(user):
    utils.bersihkan_layar()
    rprint("--- [bold yellow]BERI RATING[/bold yellow] ---")

    bookings = data_manager.dapatkan_booking_by_user(user['username'])
    if not bookings:
        rprint("[red]Belum ada booking untuk dirating.[/red]")
        time.sleep(2); return

    _lihat_histori(user, tunggu=False)
    id_paket = input("\nID Paket yang ingin dirating: ").strip()

    paket_ids_user = [b['id_paket'] for b in bookings]
    
    if id_paket not in paket_ids_user:
        rprint("[red]Anda belum membeli paket ini atau ID salah.[/red]")
        time.sleep(2); return

    paket = data_manager.dapatkan_paket_by_id(id_paket)
    
    while True:
        try:
            skor = int(input(f"Skor untuk {paket['nama']} (1-5): "))
            if 1 <= skor <= 5: break
        except: pass
        rprint("[red]1 sampai 5.[/red]")

    komentar = input("Komentar: ").strip()
    data_manager.simpan_rating_baru({
        "username_user": user['username'],
        "id_paket": id_paket,
        "skor": skor,
        "komentar": komentar
    })
    rprint("[green]Rating terkirim![/green]"); time.sleep(2)

def _tampilkan_menu_riwayat(user):
    while True:
        utils.bersihkan_layar()
        rprint("--- [bold yellow]RIWAYAT SAYA[/bold yellow] ---")
        rprint("[1] Lihat Histori")
        rprint("[2] Beri Rating")
        rprint("[3] Kembali")
        p = input("Pilih: ").strip()
        if p == '1': _lihat_histori(user)
        elif p == '2': _beri_rating(user)
        elif p == '3': break

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

        p = input("Pilih: ").strip()
        if p == '1': _lihat_semua_paket()
        elif p == '2': _lihat_detail_paket()
        elif p == '3': _beli_tiket(user)
        elif p == '4': _tampilkan_menu_riwayat(user)
        elif p == '5': 
            rprint("[cyan]Logout berhasil.[/cyan]")
            time.sleep(1); break
        else:
            rprint("[red]Pilihan salah[/red]"); time.sleep(1)