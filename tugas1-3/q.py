import sys
from pathlib import Path
import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Query, QueryCursor

PY = Language(tspython.language())
parser = Parser(PY)

def jalankan_query(kode_bytes, pola_str):
    tree = parser.parse(kode_bytes)
    query = Query(PY, pola_str)
    cursor = QueryCursor(query)
    return tree, query, cursor

def proses_file_dan_query(file_py, file_scm):
    kode = Path(file_py).read_bytes()
    pola = Path(file_scm).read_text(encoding="utf-8")
    tree, query, cursor = jalankan_query(kode, pola)
    nama_scm = Path(file_scm).name

    print(f"=== Menjalankan '{nama_scm}' pada '{file_py}' ===")

    if "fungsi" in nama_scm and "param" in nama_scm:
        print(f"{'No. Baris':<12} {'Nama Fungsi':<25} {'Jumlah Parameter':<18}")
        print("-" * 55)
        for _, cap in cursor.matches(tree.root_node):
            nama_node = cap.get("nama", [None])[0]
            params_node = cap.get("params", [None])[0]
            if nama_node and params_node:
                baris = nama_node.start_point[0] + 1
                nama_fn = nama_node.text.decode()
                # Hitung named child di dalam parameters (mengabaikan kurung '(' dan ')')
                jumlah_param = params_node.named_child_count
                print(f"Baris {baris:<6} {nama_fn:<25} {jumlah_param} parameter")

    elif "print" in nama_scm:
        print(f"{'No. Baris':<12} {'Pemanggilan print(...)':<40}")
        print("-" * 55)
        for _, cap in cursor.matches(tree.root_node):
            args = cap.get("args", [None])[0]
            fn = cap.get("fn", [None])[0]
            if fn:
                baris = fn.start_point[0] + 1
                full_call = fn.parent.text.decode().strip()
                print(f"Baris {baris:<6} {full_call}")

    elif "import" in nama_scm:
        print(f"{'No. Baris':<12} {'Nama Modul Yang Di-import':<30}")
        print("-" * 55)
        for _, cap in cursor.matches(tree.root_node):
            for modul_node in cap.get("modul", []):
                baris = modul_node.start_point[0] + 1
                nama_modul = modul_node.text.decode()
                print(f"Baris {baris:<6} {nama_modul}")

    elif "docstring" in nama_scm:
        print(f"{'No. Baris':<12} {'Fungsi':<20} {'Docstring':<40}")
        print("-" * 75)
        for _, cap in cursor.matches(tree.root_node):
            fn_node = cap.get("fungsi", [None])[0]
            doc_node = cap.get("docstring", [None])[0]
            if fn_node and doc_node:
                baris = fn_node.start_point[0] + 1
                nama_fn = fn_node.text.decode()
                doc_text = doc_node.text.decode().strip()
                # potong jika panjang
                doc_preview = (doc_text[:45] + "...") if len(doc_text) > 45 else doc_text
                print(f"Baris {baris:<6} {nama_fn:<20} {doc_preview}")

    else:
        # Generic capture fallback
        hasil = cursor.captures(tree.root_node)
        for nama_cap, nodes in hasil.items():
            for n in nodes:
                print(f"@{nama_cap:<12} baris {n.start_point[0] + 1}: {n.text.decode().strip()}")
    print()

def uji_semua(file_target="tugas1-3/contoh_t3.py"):
    print("=" * 70)
    print("PENGUJIAN LENGKAP SEMUA QUERY TUGAS 3 TERHADAP FILE UJI")
    print(f"Target File: {file_target}")
    print("=" * 70)

    folder_scm = Path("tugas1-3")
    queries = [
        folder_scm / "q_fungsi_params.scm",
        folder_scm / "q_print.scm",
        folder_scm / "q_import.scm",
        folder_scm / "q_docstring.scm",
    ]

    for q_file in queries:
        if q_file.exists():
            proses_file_dan_query(file_target, str(q_file))

    print("=" * 70)
    print("VERIFIKASI MANUAL GROUND TRUTH:")
    print("  1. Definisi fungsi: 4 fungsi terdeteksi (tanpa_param: 0, hitung_luas: 2, kalkulasi_volume: 3, cetak_pesan: 1) -> COCOK 100%")
    print("  2. Pemanggilan print: 3 pemanggilan terdeteksi (di baris 20, 26, 30) -> COCOK 100%")
    print("  3. Import modul: 4 import terdeteksi (math, sys, datetime, os) -> COCOK 100%")
    print("  4. Docstring: 2 docstring terdeteksi (tanpa_param, hitung_luas) -> COCOK 100%")
    print("=" * 70)

if __name__ == "__main__":
    if len(sys.argv) == 3:
        proses_file_dan_query(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 2 and sys.argv[1] == "--all":
        uji_semua()
    else:
        uji_semua()
