# data_manager.py
# Penanggung Jawab: Person A

import json
import os
import uuid  # Kita akan pakai UUID untuk ID unik (lebih mudah dari sekuensial)
import utils # Diperlukan untuk membuat admin default saat inisialisasi

# --- KONFIGURASI FILE PATH ---
# Pastikan ada folder 'data/' di proyek Anda
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
PACKAGES_FILE = os.path.join(DATA_DIR, "packages.json")
BOOKINGS_FILE = os.path.join(DATA_DIR, "bookings.json")
RATINGS_FILE = os.path.join(DATA_DIR, "ratings.json")

# Daftar semua file untuk inisialisasi
DATA_FILES = [USERS_FILE, PACKAGES_FILE, BOOKINGS_FILE, RATINGS_FILE]

# --- HELPER INTERNAL (PRIBADI) ---
# Fungsi-fungsi ini sebaiknya tidak dipanggil dari file lain

def _baca_data(filepath):
    """
    Fungsi helper internal untuk MEMBACA file JSON.
    Mengembalikan list kosong jika file tidak ada atau error.
    """
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        # Jika file tidak ada atau kosong/rusak, kembalikan list kosong
        return []

def _tulis_data(filepath, data):
    """
    Fungsi helper internal untuk MENULIS (overwrite) file JSON.
    """
    # Pastikan direktori 'data/' ada
    os.makedirs(DATA_DIR, exist_ok=True)
    
    with open(filepath, 'w') as f:
        # indent=2 membuat file JSON rapi dan mudah dibaca (bagus untuk debug)
        json.dump(data, f, indent=2)

def _generate_id(prefix=''):
    """
    Fungsi helper untuk membuat ID unik (contoh: P-a4b1c2d3)
    """
    # Menghasilkan ID 8 karakter unik, misal 'a4b1c2d3'
    id_unik = str(uuid.uuid4())[:8]
    if prefix:
        return f"{prefix}-{id_unik}"
    return id_unik

# --- FUNGSI UTAMA (UNTUK main.py) ---
# Ini adalah fungsi yang menyebabkan error Anda
# Sekarang kita buat fungsi itu

def inisialisasi_data_files():
    """
    (DIPANGGIL OLEH MAIN.PY)
    Memastikan folder 'data' dan semua file .json yang diperlukan ada.
    Juga membuat admin default jika file user belum ada.
    """
    # 1. Buat folder 'data' jika belum ada
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # 2. Cek file user dan buat admin default
    if not os.path.exists(USERS_FILE):
        print("Membuat admin default...")
        admin_pass = "admin" # Password default
        admin_hash = utils.hash_password(admin_pass)
        admin_user = {
            "username": "admin",
            "password_hash": admin_hash,
            "role": "admin"
        }
        _tulis_data(USERS_FILE, [admin_user]) # Simpan sebagai list
        print(f"Admin default dibuat -> User: admin, Pass: {admin_pass}")
        
    # 3. Buat file data lain jika belum ada (dengan list kosong)
    for filepath in [PACKAGES_FILE, BOOKINGS_FILE, RATINGS_FILE]:
        if not os.path.exists(filepath):
            _tulis_data(filepath, [])

# --- FUNGSI UNTUK MANAJEMEN USER (Kontrak untuk main.py) ---

def dapatkan_user_by_username(username):
    """
    Mencari user berdasarkan username di users.json.
    Mengembalikan data user (dict) jika ketemu, atau None jika tidak.
    """
    users = _baca_data(USERS_FILE)
    for user in users:
        if user['username'] == username:
            return user
    return None

def simpan_user_baru(user_data):
    """
    Menyimpan data user baru ke users.json.
    """
    users = _baca_data(USERS_FILE)
    users.append(user_data)
    _tulis_data(USERS_FILE, users)
    

# --- FUNGSI PAKET (Kontrak untuk admin_menu.py & user_menu.py) ---

def dapatkan_semua_paket():
    """
    Mengembalikan semua data paket dari packages.json.
    """
    return _baca_data(PACKAGES_FILE)

def dapatkan_paket_by_id(id_paket):
    """
    Mencari satu paket berdasarkan ID-nya.
    """
    paket_list = _baca_data(PACKAGES_FILE)
    for paket in paket_list:
        if paket['id_paket'] == id_paket:
            return paket
    return None

def simpan_paket_baru(data_paket):
    """
    Menyimpan paket baru. Menambahkan ID unik secara otomatis.
    """
    paket_list = _baca_data(PACKAGES_FILE)
    
    # Tambahkan ID unik
    data_paket['id_paket'] = _generate_id(prefix="P") # Contoh: P-1a2b3c4d
    
    paket_list.append(data_paket)
    _tulis_data(PACKAGES_FILE, paket_list)
    print(f"DEBUG (data_manager): Paket {data_paket['id_paket']} disimpan.")

def update_paket(id_paket, data_update):
    """
    Mencari paket berdasarkan ID dan memperbarui datanya.
    data_update adalah dict berisi field yang mau diubah (misal: {'kuota': 10})
    """
    paket_list = _baca_data(PACKAGES_FILE)
    
    # Kita harus cari dan ganti datanya
    paket_ditemukan = False
    for i, paket in enumerate(paket_list):
        if paket['id_paket'] == id_paket:
            # .update() menggabungkan/menimpa field di dict
            paket_list[i].update(data_update)
            paket_ditemukan = True
            break
            
    if paket_ditemukan:
        _tulis_data(PACKAGES_FILE, paket_list)
    else:
        print(f"ERROR (data_manager): Gagal update, paket {id_paket} tidak ditemukan.")

def hapus_paket_by_id(id_paket):
    """
    Menghapus paket berdasarkan ID.
    """
    paket_list = _baca_data(PACKAGES_FILE)
    
    # Buat list baru yang TIDAK mengandung paket dengan ID tersebut
    paket_list_baru = [paket for paket in paket_list if paket['id_paket'] != id_paket]
    
    if len(paket_list_baru) < len(paket_list):
        _tulis_data(PACKAGES_FILE, paket_list_baru)
        print(f"DEBUG (data_manager): Paket {id_paket} dihapus.")
    else:
        print(f"ERROR (data_manager): Gagal hapus, paket {id_paket} tidak ditemukan.")


# --- FUNGSI BOOKING (Kontrak untuk admin_menu.py & user_menu.py) ---

def dapatkan_semua_booking():
    """
    Mengembalikan semua data booking dari bookings.json.
    """
    return _baca_data(BOOKINGS_FILE)

def dapatkan_booking_by_user(username):
    """
    Mengembalikan list booking HANYA untuk user tertentu.
    """
    semua_booking = _baca_data(BOOKINGS_FILE)
    booking_user = [b for b in semua_booking if b['username_user'] == username]
    return booking_user

def simpan_booking_baru(data_booking):
    """
    Menyimpan data booking baru. Menambahkan ID unik.
    Mengembalikan data booking yang telah disimpan (termasuk ID).
    """
    bookings = _baca_data(BOOKINGS_FILE)
    
    # Tambahkan ID unik
    data_booking['id_booking'] = _generate_id(prefix="B") # Contoh: B-5e6f7a8b
    
    bookings.append(data_booking)
    _tulis_data(BOOKINGS_FILE, bookings)
    print(f"DEBUG (data_manager): Booking {data_booking['id_booking']} disimpan.")
    return data_booking # Kembalikan agar user_menu bisa pakai ID-nya


# --- FUNGSI RATING (Kontrak untuk user_menu.py) ---

def simpan_rating_baru(data_rating):
    """
    Menyimpan data rating baru.
    """
    ratings = _baca_data(RATINGS_FILE)
    
    # Tambahkan ID unik
    data_rating['id_rating'] = _generate_id(prefix="R")
    
    ratings.append(data_rating)
    _tulis_data(RATINGS_FILE, ratings)
    print(f"DEBUG (data_manager): Rating {data_rating['id_rating']} disimpan.")