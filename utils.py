# utils.py
# Penanggung Jawab: Person A

import os         # Diperlukan untuk membersihkan layar terminal
import hashlib    # Diperlukan untuk hashing password
import time       # (Opsional) bisa digunakan untuk ID unik atau 'sleep'

def bersihkan_layar():
    """
    Membersihkan layar terminal.
    'nt' adalah untuk Windows, selain itu (Mac/Linux) menggunakan 'clear'.
    """
    os.system('cls' if os.name == 'nt' else 'clear')

def hash_password(password):
    """
    Meng-hash password menggunakan algoritma SHA-256.
    
    Argumen:
        password (str): Password dalam bentuk teks biasa (plain text).
        
    Mengembalikan:
        str: Password yang sudah di-hash dalam format hexadecimal.
    """
    # .encode() mengubah string menjadi bytes, yang diperlukan oleh hashlib
    # .hexdigest() mengubah hash biner menjadi string heksadesimal yang aman disimpan
    return hashlib.sha256(password.encode()).hexdigest()

def cek_password(plain_password, hashed_password):
    """
    Memverifikasi apakah plain_password cocok dengan hashed_password.
    
    Argumen:
        plain_password (str): Password yang diinput oleh user saat login.
        hashed_password (str): Password yang tersimpan di database (JSON).
        
    Mengembalikan:
        bool: True jika cocok, False jika tidak.
    """
    # Kita TIDAK PERNAH men-decrypt hash.
    # Kita HASH input baru (plain_password) dan membandingkan hasilnya 
    # dengan hash yang ada di database.
    return hash_password(plain_password) == hashed_password

# --- Catatan Desain (Sengaja Dihilangkan) ---
#
# Q: Kenapa tidak ada fungsi 'generate_id_unik()' di sini?
# A: Karena untuk membuat ID unik yang berurutan (misal "P005" setelah "P004"),
#    kita perlu MEMBACA file data (misal packages.json) untuk melihat ID terakhir.
#
#    Membaca file data adalah tugas DATA_MANAGER.PY.
#
#    Jika kita letakkan di sini, 'utils.py' jadi bergantung pada 'data_manager.py',
#    atau 'utils.py' melanggar aturan dengan membaca file JSON secara langsung.
#    Ini melanggar prinsip "Separation of Concerns".
#
#    Maka, logika pembuatan ID akan ada di dalam 'data_manager.py'
#    (misal di dalam fungsi 'simpan_paket_baru()').
#