import json
import os
import uuid  

DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
PACKAGES_FILE = os.path.join(DATA_DIR, "packages.json")
BOOKINGS_FILE = os.path.join(DATA_DIR, "bookings.json")
RATINGS_FILE = os.path.join(DATA_DIR, "ratings.json")

DATA_FILES = [USERS_FILE, PACKAGES_FILE, BOOKINGS_FILE, RATINGS_FILE]


def _baca_data(filepath):
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def _tulis_data(filepath, data):
    os.makedirs(DATA_DIR, exist_ok=True)
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def _generate_id(prefix=''):
    id_unik = str(uuid.uuid4())[:8]
    if prefix:
        return f"{prefix}-{id_unik}"
    return id_unik

def inisialisasi_data_files():
    
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(USERS_FILE):
        print("Membuat admin default...")
        admin_pass = "admin" 
        admin_hash = utils.hash_password(admin_pass)
        admin_user = {
            "username": "admin",
            "password_hash": admin_hash,
            "role": "admin",
            "email": "admin@travel.com" # 
        }
        _tulis_data(USERS_FILE, [admin_user]) 
        print(f"Admin default dibuat -> User: admin, Pass: {admin_pass}")
        
    for filepath in [PACKAGES_FILE, BOOKINGS_FILE, RATINGS_FILE]:
        if not os.path.exists(filepath):
            _tulis_data(filepath, [])


def dapatkan_user_by_username(username):

    users = _baca_data(USERS_FILE)
    for user in users:
        if user['username'] == username:
            return user
    return None

def simpan_user_baru(user_data):

    users = _baca_data(USERS_FILE)
    users.append(user_data)
    _tulis_data(USERS_FILE, users)
    



def dapatkan_semua_paket():

    return _baca_data(PACKAGES_FILE)

def dapatkan_paket_by_id(id_paket):

    paket_list = _baca_data(PACKAGES_FILE)
    for paket in paket_list:
        if paket['id_paket'] == id_paket:
            return paket
    return None

def simpan_paket_baru(data_paket):

    paket_list = _baca_data(PACKAGES_FILE)
    
    data_paket['id_paket'] = _generate_id(prefix="P") 
    
    paket_list.append(data_paket)
    _tulis_data(PACKAGES_FILE, paket_list)
    print(f"DEBUG (data_manager): Paket {data_paket['id_paket']} disimpan.")

def update_paket(id_paket, data_update):
    paket_list = _baca_data(PACKAGES_FILE)
    
    paket_ditemukan = False
    for i, paket in enumerate(paket_list):
        if paket['id_paket'] == id_paket:
            paket_list[i].update(data_update)
            paket_ditemukan = True
            break
            
    if paket_ditemukan:
        _tulis_data(PACKAGES_FILE, paket_list)
    else:
        print(f"ERROR (data_manager): Gagal update, paket {id_paket} tidak ditemukan.")

def hapus_paket_by_id(id_paket):
    paket_list = _baca_data(PACKAGES_FILE)

    paket_list_baru = [paket for paket in paket_list if paket['id_paket'] != id_paket]
    
    if len(paket_list_baru) < len(paket_list):
        _tulis_data(PACKAGES_FILE, paket_list_baru)
        print(f"DEBUG (data_manager): Paket {id_paket} dihapus.")
    else:
        print(f"ERROR (data_manager): Gagal hapus, paket {id_paket} tidak ditemukan.")



def dapatkan_semua_booking():

    return _baca_data(BOOKINGS_FILE)

def dapatkan_booking_by_user(username):
    semua_booking = _baca_data(BOOKINGS_FILE)
    booking_user = [b for b in semua_booking if b['username_user'] == username]
    return booking_user

def simpan_booking_baru(data_booking):
    bookings = _baca_data(BOOKINGS_FILE)

    data_booking['id_booking'] = _generate_id(prefix="B") 
    
    bookings.append(data_booking)
    _tulis_data(BOOKINGS_FILE, bookings)
    print(f"DEBUG (data_manager): Booking {data_booking['id_booking']} disimpan.")
    return data_booking 


def simpan_rating_baru(data_rating):

    ratings = _baca_data(RATINGS_FILE)
    
    data_rating['id_rating'] = _generate_id(prefix="R")
    
    ratings.append(data_rating)
    _tulis_data(RATINGS_FILE, ratings)
    print(f"DEBUG (data_manager): Rating {data_rating['id_rating']} disimpan.")



def dapatkan_rating_by_paket(id_paket):

    semua_rating = _baca_data(RATINGS_FILE)

    rating_paket = [r for r in semua_rating if r['id_paket'] == id_paket]
    return rating_paket

def dapatkan_semua_user():
    semua_user = _baca_data(USERS_FILE)
    users_aman = []
    
    for u in semua_user:
        users_aman.append({
            "username": u['username'],
            "role": u['role'],
            "email": u.get('email', "-") 
        })
        
    return users_aman