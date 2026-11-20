"""
Modul Layanan Pemrosesan Pesanan Enterprise (E-Commerce Order Service)
Digunakan sebagai contoh kode nyata Python dengan panjang >= 100 baris.
"""

import os
import sys
import json
import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger("OrderService")

@dataclass
class ItemPesanan:
    id_produk: str
    nama_produk: str
    harga: float
    kuantitas: int

    @property
    def total_harga(self) -> float:
        return self.harga * self.kuantitas

@dataclass
class Pesanan:
    id_pesanan: str
    id_pelanggan: str
    items: List[ItemPesanan] = field(default_factory=list)
    status: str = "PENDING"
    tanggal_dibuat: datetime = field(default_factory=datetime.utcnow)
    diskon_persen: float = 0.0

    def hitung_subtotal(self) -> float:
        total = 0.0
        for item in self.items:
            total += item.total_harga
        return total

    def hitung_total_akhir(self) -> float:
        subtotal = self.hitung_subtotal()
        diskon = subtotal * (self.diskon_persen / 100.0)
        return subtotal - diskon

class ManajerInventaris:
    def __init__(self, stok_awal: Optional[Dict[str, int]] = None):
        self.stok = stok_awal or {}

    def cek_ketersediaan(self, id_produk: str, kuantitas: int) -> bool:
        stok_tersedia = self.stok.get(id_produk, 0)
        if stok_tersedia >= kuantitas:
            return True
        return False

    def kurangi_stok(self, id_produk: str, kuantitas: int) -> None:
        if not self.cek_ketersediaan(id_produk, kuantitas):
            raise ValueError(f"Stok produk {id_produk} tidak mencukupi.")
        self.stok[id_produk] -= kuantitas

class PemrosesPembayaran:
    def __init__(self, gateway_url: str):
        self.gateway_url = gateway_url

    def proses(self, id_pesanan: str, jumlah: float) -> bool:
        # TODO: Hubungkan dengan payment gateway eksternal
        if jumlah <= 0:
            print("Gagal: Jumlah pembayaran tidak valid")
            return False
        print(f"Berhasil: Pembayaran pesanan {id_pesanan} sejumlah Rp{jumlah:,.2f} diproses")
        return True

class LayananPesanan:
    def __init__(self, inventaris: ManajerInventaris, pembayaran: PemrosesPembayaran):
        self.inventaris = inventaris
        self.pembayaran = pembayaran
        self.daftar_pesanan: Dict[str, Pesanan] = {}

    def buat_pesanan(self, id_pesanan: str, id_pelanggan: str, item_list: List[ItemPesanan]) -> Pesanan:
        for it in item_list:
            if not self.inventaris.cek_ketersediaan(it.id_produk, it.kuantitas):
                raise RuntimeError(f"Gagal membuat pesanan: Stok produk {it.nama_produk} habis")

        pesanan = Pesanan(id_pesanan=id_pesanan, id_pelanggan=id_pelanggan, items=item_list)
        self.daftar_pesanan[id_pesanan] = pesanan
        logger.info(f"Pesanan {id_pesanan} dibuat.")
        return pesanan

    def konfirmasi_dan_bayar(self, id_pesanan: str) -> bool:
        pesanan = self.daftar_pesanan.get(id_pesanan)
        if not pesanan:
            logger.error("Pesanan tidak ditemukan.")
            return False

        total_tagihan = pesanan.hitung_total_akhir()
        sukses_bayar = self.pembayaran.proses(id_pesanan, total_tagihan)
        if sukses_bayar:
            for item in pesanan.items:
                self.inventaris.kurangi_stok(item.id_produk, item.kuantitas)
            pesanan.status = "PAID"
            print(f"Pesanan {id_pesanan} resmi lunas.")
            return True
        else:
            pesanan.status = "FAILED"
            return False

def demo():
    inv = ManajerInventaris({"PROD-001": 50, "PROD-002": 10})
    pay = PemrosesPembayaran("https://api.payment.local/v1")
    layanan = LayananPesanan(inv, pay)

    items = [
        ItemPesanan("PROD-001", "Laptop Gaming", 15000000.0, 1),
        ItemPesanan("PROD-002", "Mouse Wireless", 250000.0, 2)
    ]
    p = layanan.buat_pesanan("ORD-1001", "CUST-007", items)
    print("Total sebelum diskon:", p.hitung_subtotal())
    layanan.konfirmasi_dan_bayar("ORD-1001")

if __name__ == "__main__":
    demo()
