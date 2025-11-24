
import os        
import hashlib    

def bersihkan_layar():
    os.system('cls' if os.name == 'nt' else 'clear')

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def cek_password(plain_password, hashed_password):
    return hash_password(plain_password) == hashed_password


