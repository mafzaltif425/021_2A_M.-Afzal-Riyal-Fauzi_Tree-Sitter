"""
File uji terstruktur untuk Tugas 3 Tree-Sitter
Berisi target pengujian dengan jumlah yang diketahui secara pasti:
- 4 Definisi Fungsi (parameter: 0, 2, 3, 1)
- 3 Pemanggilan print(...)
- 4 Import (2 import biasa, 2 import from)
- 2 Fungsi yang memiliki docstring pada baris pertama body
"""

import math
import sys
from datetime import datetime
from os import path

def tanpa_param():
    """Fungsi tanpa parameter sama sekali."""
    x = 10
    return x

def hitung_luas(panjang, lebar):
    """Menghitung luas persegi panjang dengan dua parameter."""
    luas = panjang * lebar
    print(f"Luas: {luas}")
    return luas

def kalkulasi_volume(panjang, lebar, tinggi):
    # Catatan: Fungsi ini tidak memiliki docstring
    volume = panjang * lebar * tinggi
    print(f"Volume: {volume}")
    return volume

def cetak_pesan(pesan):
    print("LOG:", pesan)

if __name__ == "__main__":
    p = tanpa_param()
    hitung_luas(5, 4)
    kalkulasi_volume(2, 3, 4)
    cetak_pesan("Pengujian Selesai")
