# File Uji: Fungsi Panjang (> 30 baris)

def generate_laporan_bulanan(transaksi, tahun, bulan):
    """
    Fungsi ini sengaja dibuat memiliki panjang lebih dari 30 baris
    untuk memicu deteksi 'Fitur 2: fungsi yang lebih dari 30 baris'.
    """
    laporan = {}
    total_debit = 0.0
    total_kredit = 0.0
    kategori_summary = {}

    print(f"Memulai pembuatan laporan {bulan}/{tahun}...")
    
    for tx in transaksi:
        tipe = tx.get("tipe")
        nominal = tx.get("nominal", 0.0)
        kategori = tx.get("kategori", "Umum")

        if tipe == "DEBIT":
            total_debit += nominal
        elif tipe == "KREDIT":
            total_kredit += nominal
        else:
            print(f"Warning: Tipe transaksi {tipe} tidak dikenal")

        if kategori not in kategori_summary:
            kategori_summary[kategori] = 0.0
        kategori_summary[kategori] += nominal

    saldo_akhir = total_kredit - total_debit
    laporan["periode"] = f"{bulan}-{tahun}"
    laporan["total_debit"] = total_debit
    laporan["total_kredit"] = total_kredit
    laporan["saldo_akhir"] = saldo_akhir
    laporan["kategori"] = kategori_summary

    print("Perhitungan debit dan kredit selesai.")
    print("Menghitung rasio keuangan bulanan...")
    
    if total_debit > 0:
        laporan["rasio_efisiensi"] = total_kredit / total_debit
    else:
        laporan["rasio_efisiensi"] = 1.0

    print("Laporan bulanan siap diekspor.")
    return laporan
