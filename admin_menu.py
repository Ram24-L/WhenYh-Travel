# admin_menu.py (Tema Biru & Putih)

import data_manager
import utils
import time

from rich.console import Console
from rich.table import Table
from rich import print as rprint
from rich.panel import Panel
from rich.text import Text

console = Console()


# ============================================================
# LIHAT SEMUA PAKET
# ============================================================

def _lihat_semua_paket(tunggu=True):
    utils.bersihkan_layar()
    rprint("[bold blue]--- DAFTAR SEMUA PAKET ---[/bold blue]")

    paket_list = data_manager.dapatkan_semua_paket()

    if not paket_list:
        rprint("[italic white]Belum ada data paket travel.[/italic white]")
        time.sleep(2)
        return False

    table = Table(
        title="Paket Travel Tersedia",
        show_header=True,
        header_style="bold white"
    )

    table.add_column("ID Paket", style="white", width=10)
    table.add_column("Nama Paket", style="white", min_width=20)
    table.add_column("Harga (Rp)", style="white", justify="right")
    table.add_column("Sisa Kuota", style="white", justify="right")

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


# ============================================================
# TAMBAH PAKET
# ============================================================

def _tambah_paket_baru():
    utils.bersihkan_layar()
    rprint("[bold blue]--- TAMBAH PAKET BARU ---[/bold blue]")
    rprint("[italic white]Ketik 'batal' untuk membatalkan.[/italic white]")

    nama = input("\nNama Paket: ").strip()
    if nama.lower() == "batal":
        rprint("[italic white]Dibatalkan.[/italic white]")
        time.sleep(1)
        return

    while True:
        harga_str = input("Harga: ").strip()
        if harga_str.lower() == "batal":
            rprint("[italic white]Dibatalkan.[/italic white]")
            time.sleep(1)
            return
        try:
            harga = int(harga_str)
            break
        except:
            rprint("[bold blue]Harga harus angka.[/bold blue]")

    while True:
        kuota_str = input("Kuota: ").strip()
        if kuota_str.lower() == "batal":
            rprint("[italic white]Dibatalkan.[/italic white]")
            time.sleep(1)
            return
        try:
            kuota = int(kuota_str)
            break
        except:
            rprint("[bold blue]Kuota harus angka.[/bold blue]")

    # Input rundown
    rundown = []
    rprint("\n[italic white]Masukkan Rundown (ketik 'selesai'):[/italic white]")
    i = 1
    while True:
        item = input(f"  Item {i}: ").strip()

        if item.lower() == "batal":
            rprint("[italic white]Dibatalkan.[/italic white]")
            return

        if item.lower() == "selesai":
            if i == 1:
                rprint("[italic white]Minimal 1 rundown.[/italic white]")
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
    rprint(f"[bold white]Paket '{nama}' berhasil ditambahkan![/bold white]")
    time.sleep(2)


# ============================================================
# EDIT PAKET
# ============================================================

def _edit_paket():
    utils.bersihkan_layar()
    rprint("[bold blue]--- EDIT PAKET ---[/bold blue]")

    if not _lihat_semua_paket(tunggu=False):
        return

    id_paket = input("\nID Paket (atau 'batal'): ").strip()
    if id_paket.lower() == "batal":
        return

    paket_lama = data_manager.dapatkan_paket_by_id(id_paket)
    if not paket_lama:
        rprint("[bold blue]ID Paket tidak ditemukan.[/bold blue]")
        time.sleep(2)
        return

    rprint(f"[bold white]Mengedit: {paket_lama['nama']}[/bold white]")

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
            rprint("[bold blue]Harga harus angka.[/bold blue]")

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
            rprint("[bold blue]Kuota harus angka.[/bold blue]")

    data_update = {
        "nama": nama_baru if nama_baru else paket_lama["nama"],
        "harga": harga_baru,
        "kuota": kuota_baru,
        "rundown": paket_lama["rundown"]
    }

    data_manager.update_paket(id_paket, data_update)
    rprint(f"[bold white]Paket '{data_update['nama']}' berhasil diperbarui.[/bold white]")
    time.sleep(2)


# ============================================================
# HAPUS PAKET
# ============================================================

def _hapus_paket():
    utils.bersihkan_layar()
    rprint("[bold blue]--- HAPUS PAKET ---[/bold blue]")

    if not _lihat_semua_paket(tunggu=False):
        return

    id_paket = input("\nID Paket (atau 'batal'): ").strip()
    if id_paket.lower() == "batal":
        return

    paket = data_manager.dapatkan_paket_by_id(id_paket)
    if not paket:
        rprint("[bold blue]ID Paket tidak ditemukan.[/bold blue]")
        return

    rprint(f"[bold white]Menghapus: {paket['nama']}[/bold white]")
    confirm = input("Yakin? (y/n): ").strip().lower()

    if confirm == "y":
        data_manager.hapus_paket_by_id(id_paket)
        rprint("[bold white]Paket berhasil dihapus.[/bold white]")
    else:
        rprint("[italic white]Dibatalkan.[/italic white]")

    time.sleep(2)


# ============================================================
# LIHAT BOOKING
# ============================================================

def _lihat_semua_booking():
    utils.bersihkan_layar()
    rprint("[bold blue]--- DATA BOOKING USER ---[/bold blue]")

    bookings = data_manager.dapatkan_semua_booking()
    if not bookings:
        rprint("[italic white]Belum ada booking.[/italic white]")
        time.sleep(2)
        return

    table = Table(
        title="Data Booking User",
        show_header=True,
        header_style="bold white"
    )

    table.add_column("ID Booking", style="white", width=10)
    table.add_column("Username User", style="white")
    table.add_column("ID Paket", style="white")
    table.add_column("Jumlah", style="white", justify="right")
    table.add_column("Total Bayar", style="white", justify="right")

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


# ============================================================
# LIHAT DETAIL PAKET
# ============================================================

def _admin_lihat_detail_paket():
    utils.bersihkan_layar()
    rprint("[bold blue]--- DETAIL PAKET ---[/bold blue]")

    if not _lihat_semua_paket(tunggu=False):
        return

    id_paket = input("\nID Paket (atau 'batal'): ").strip()
    if id_paket.lower() == "batal":
        return

    paket = data_manager.dapatkan_paket_by_id(id_paket)
    if not paket:
        rprint("[bold blue]ID Paket tidak ditemukan.[/bold blue]")
        time.sleep(2)
        return

    rundown_text = Text()
    for i, item in enumerate(paket["rundown"], 1):
        rundown_text.append(f"{i}. {item}\n")

    panel_text = Text()
    panel_text.append(f"ID Paket: {paket['id_paket']}\n", style="white")
    panel_text.append(f"Harga: Rp {paket['harga']:,}\n", style="white")
    panel_text.append(f"Kuota: {paket['kuota']}\n\n", style="white")
    panel_text.append("--- RUNDOWN ---\n", style="white")
    panel_text.append(rundown_text)

    console.print(Panel(panel_text, title=f"[bold white]{paket['nama']}[/bold white]", border_style="blue"))

    input("\nTekan Enter...")


# ============================================================
# MENU UTAMA ADMIN
# ============================================================

def start(admin_user):
    utils.bersihkan_layar()
    rprint(f"[bold white]Selamat datang, {admin_user['username']}![/bold white]")
    time.sleep(1)

    while True:
        utils.bersihkan_layar()
        rprint("[bold blue]--- MENU ADMIN ---[/bold blue]")
        rprint("[white][1] Manajemen Paket (CRUD)[/white]")
        rprint("[white][2] Lihat Data Booking[/white]")
        rprint("[white][3] Logout[/white]")

        pilih = input("Pilih (1-3): ").strip()

        if pilih == "1":
            _tampilkan_menu_paket()
        elif pilih == "2":
            _lihat_semua_booking()
        elif pilih == "3":
            rprint("[bold white]Logout berhasil.[/bold white]")
            time.sleep(1)
            break
        else:
            rprint("[bold blue]Pilihan tidak valid.[/bold blue]")
            time.sleep(1)


# Submenu CRUD Paket
def _tampilkan_menu_paket():
    while True:
        utils.bersihkan_layar()
        rprint("[bold blue]--- MANAJEMEN PAKET ---[/bold blue]")
        rprint("[white][1] Tambah Paket[/white]")
        rprint("[white][2] Edit Paket[/white]")
        rprint("[white][3] Hapus Paket[/white]")
        rprint("[white][4] Lihat Detail Paket[/white]")
        rprint("[white][5] Kembali[/white]")

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
            rprint("[bold blue]Pilihan tidak valid.[/bold blue]")
            time.sleep(1)
