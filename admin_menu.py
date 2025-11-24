import data_manager
import utils
import time
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from rich.panel import Panel
from rich.text import Text

console = Console()


def _lihat_semua_paket(tunggu=True):
    utils.bersihkan_layar()
    rprint("--- [bold yellow]DAFTAR SEMUA PAKET[/bold yellow] ---")
    paket_list = data_manager.dapatkan_semua_paket()
    if not paket_list:
        rprint("[italic red]Belum ada data paket travel.[/italic red]")
        time.sleep(2)
        return False
    table = Table(
        title="Paket Travel Tersedia",
        show_header=True,
        header_style="bold magenta"
    )
    table.add_column("ID Paket", style="cyan", width=10)
    table.add_column("Nama Paket", style="green", min_width=20)
    table.add_column("Harga (Rp)", style="blue", justify="right")
    table.add_column("Sisa Kuota", justify="right")

    for paket in paket_list:
        table.add_row(
            paket["id_paket"],
            paket["nama"],
            f"{paket['harga']:,}",
            str(paket["kuota"])
        )

    console.print(table)

    if tunggu:
        input("\nTekan Enter untuk kembali...")

    return True


def _tambah_paket_baru():
    utils.bersihkan_layar()
    rprint("--- [bold yellow]TAMBAH PAKET BARU[/bold yellow] ---")
    rprint("[italic]Ketik 'batal' untuk membatalkan.[/italic]")

    nama = input("\nNama Paket: ").strip()
    if nama.lower() == "batal":
        rprint("[italic red]Dibatalkan.[/italic red]")
        time.sleep(1)
        return

    while True:
        harga_str = input("Harga: ").strip()
        if harga_str.lower() == "batal":
            rprint("[italic red]Dibatalkan.[/italic red]")
            time.sleep(1)
            return
        try:
            harga = int(harga_str)
            break
        except:
            rprint("[red]Harga harus angka.[/red]")

    while True:
        kuota_str = input("Kuota: ").strip()
        if kuota_str.lower() == "batal":
            rprint("[italic red]Dibatalkan.[/italic red]")
            time.sleep(1)
            return
        try:
            kuota = int(kuota_str)
            break
        except:
            rprint("[red]Kuota harus angka.[/red]")

    rundown = []
    rprint("\n[italic]Masukkan Rundown (ketik 'selesai'):[/italic]")
    i = 1
    while True:
        item = input(f"  Item {i}: ").strip()

        if item.lower() == "batal":
            rprint("[italic red]Dibatalkan.[/italic red]")
            return

        if item.lower() == "selesai":
            if i == 1:
                rprint("[red]Minimal 1 rundown.[/red]")
                return
            break

        rundown.append(item)
        i += 1

    paket_baru = {
        "nama": nama,
        "harga": harga,
        "kuota": kuota,
        "rundown": rundown
    }

    data_manager.simpan_paket_baru(paket_baru)
    rprint(f"[green]Paket '{nama}' berhasil ditambahkan![/green]")
    time.sleep(2)


def _edit_paket():
    utils.bersihkan_layar()
    rprint("--- [bold yellow]EDIT PAKET[/bold yellow] ---")

    if not _lihat_semua_paket(tunggu=False):
        return

    id_paket = input("\nID Paket (atau 'batal'): ").strip()
    if id_paket.lower() == "batal":
        return

    paket_lama = data_manager.dapatkan_paket_by_id(id_paket)
    if not paket_lama:
        rprint("[red]ID Paket tidak ditemukan.[/red]")
        time.sleep(2)
        return

    rprint(f"[green]Mengedit: {paket_lama['nama']}[/green]")

    nama_baru = input(f"Nama [{paket_lama['nama']}]: ").strip()
    if nama_baru.lower() == "batal":
        return

    while True:
        harga_str = input(f"Harga [{paket_lama['harga']}]: ").strip()
        if harga_str.lower() == "batal":
            return
        if harga_str == "":
            harga_baru = paket_lama["harga"]
            break
        try:
            harga_baru = int(harga_str)
            break
        except:
            rprint("[red]Harga harus angka.[/red]")

    while True:
        kuota_str = input(f"Kuota [{paket_lama['kuota']}]: ").strip()
        if kuota_str.lower() == "batal":
            return
        if kuota_str == "":
            kuota_baru = paket_lama["kuota"]
            break
        try:
            kuota_baru = int(kuota_str)
            break
        except:
            rprint("[red]Kuota harus angka.[/red]")

    data_update = {
        "nama": nama_baru if nama_baru else paket_lama["nama"],
        "harga": harga_baru,
        "kuota": kuota_baru,
        "rundown": paket_lama["rundown"]
    }

    data_manager.update_paket(id_paket, data_update)
    rprint(f"[green]Paket '{data_update['nama']}' berhasil diperbarui.[/green]")
    time.sleep(2)


def _hapus_paket():
    utils.bersihkan_layar()
    rprint("--- [bold yellow]HAPUS PAKET[/bold yellow] ---")

    if not _lihat_semua_paket(tunggu=False):
        return

    id_paket = input("\nID Paket (atau 'batal'): ").strip()
    if id_paket.lower() == "batal":
        return

    paket = data_manager.dapatkan_paket_by_id(id_paket)
    if not paket:
        rprint("[red]ID Paket tidak ditemukan.[/red]")
        return

    rprint(f"[red]Menghapus: {paket['nama']}[/red]")
    confirm = input("Yakin? (y/n): ").strip().lower()

    if confirm == "y":
        data_manager.hapus_paket_by_id(id_paket)
        rprint("[green]Paket berhasil dihapus.[/green]")
    else:
        rprint("[italic red]Dibatalkan.[/italic red]")

    time.sleep(2)


def _lihat_semua_booking():
    utils.bersihkan_layar()
    rprint("--- [bold yellow]DATA BOOKING USER[/bold yellow] ---")

    bookings = data_manager.dapatkan_semua_booking()
    if not bookings:
        rprint("[italic red]Belum ada booking.[/italic red]")
        time.sleep(2)
        return

    table = Table(
        title="Data Booking User",
        show_header=True,
        header_style="bold magenta"
    )

    table.add_column("ID Booking", style="cyan", width=10)
    table.add_column("Username User", style="green")
    table.add_column("ID Paket", style="blue")
    table.add_column("Jumlah", justify="right")
    table.add_column("Total Bayar", style="blue", justify="right")

    for b in bookings:
        table.add_row(
            b["id_booking"],
            b["username_user"],
            b["id_paket"],
            str(b["jumlah_tiket"]),
            f"{b['total_bayar']:,}"
        )

    console.print(table)
    input("\nTekan Enter untuk kembali...")


def _admin_lihat_detail_paket():
    utils.bersihkan_layar()
    rprint("--- [bold yellow]DETAIL PAKET[/bold yellow] ---")

    if not _lihat_semua_paket(tunggu=False):
        return

    id_paket = input("\nID Paket (atau 'batal'): ").strip()
    if id_paket.lower() == "batal":
        return

    paket = data_manager.dapatkan_paket_by_id(id_paket)
    if not paket:
        rprint("[red]ID Paket tidak ditemukan.[/red]")
        time.sleep(2)
        return

    rundown_text = Text()
    for i, item in enumerate(paket["rundown"], 1):
        rundown_text.append(f"{i}. {item}\n")

    panel_text = Text()
    panel_text.append(f"ID Paket: {paket['id_paket']}\n", style="cyan")
    panel_text.append(f"Harga: Rp {paket['harga']:,}\n", style="blue")
    panel_text.append(f"Kuota: {paket['kuota']}\n\n")
    panel_text.append("--- RUNDOWN ---\n", style="bold yellow")
    panel_text.append(rundown_text)

    console.print(Panel(panel_text, title=f"[bold green]{paket['nama']}[/bold green]", border_style="yellow"))

    input("\nTekan Enter...")


def start(admin_user):
    utils.bersihkan_layar()
    rprint(f"[green]Selamat datang, {admin_user['username']}![/green]")
    time.sleep(1)

    while True:
        utils.bersihkan_layar()
        rprint("--- [bold yellow]MENU ADMIN[/bold yellow] ---")
        rprint("[1] Manajemen Paket (CRUD)")
        rprint("[2] Lihat Data Booking")
        rprint("[3] Logout")

        pilih = input("Pilih (1-3): ").strip()

        if pilih == "1":
            _tampilkan_menu_paket()
        elif pilih == "2":
            _lihat_semua_booking()
        elif pilih == "3":
            rprint("[cyan]Logout berhasil.[/cyan]")
            time.sleep(1)
            break
        else:
            rprint("[red]Pilihan tidak valid.[/red]")
            time.sleep(1)


def _tampilkan_menu_paket():
    while True:
        utils.bersihkan_layar()
        rprint("--- [bold yellow]MANAJEMEN PAKET[/bold yellow] ---")
        rprint("[1] Tambah Paket")
        rprint("[2] Edit Paket")
        rprint("[3] Hapus Paket")
        rprint("[4] Lihat Detail Paket")
        rprint("[5] Kembali")

        pilih = input("Pilih (1–5): ").strip()

        if pilih == "1":
            _tambah_paket_baru()
        elif pilih == "2":
            _edit_paket()
        elif pilih == "3":
            _hapus_paket()
        elif pilih == "4":
            _admin_lihat_detail_paket()
        elif pilih == "5":
            break
        else:
            rprint("[red]Pilihan tidak valid.[/red]")
            time.sleep(1)