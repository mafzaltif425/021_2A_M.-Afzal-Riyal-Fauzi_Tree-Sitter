# File Uji: Kode Bersih Standar (Fungsi ringkas dan sintaks valid)

def kalikan(a, b):
    return a * b

def bagikan(a, b):
    if b == 0:
        raise ValueError("Pembagi tidak boleh nol")
    return a / b
