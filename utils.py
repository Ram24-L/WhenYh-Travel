
import os        
import hashlib    
import time      

def bersihkan_layar():
    #Bersihkan Layar
    os.system('cls' if os.name == 'nt' else 'clear')

def hash_password(password):
    #Hash SHA-256
    # .encode() mengconvert string menjadi bytes yang kmudian akan dihash
    # .hexdigest() mmengconvert hasil hash bytes menjadi string hexadecimal
    return hashlib.sha256(password.encode()).hexdigest()

def cek_password(plain_password, hashed_password):
    return hash_password(plain_password) == hashed_password


