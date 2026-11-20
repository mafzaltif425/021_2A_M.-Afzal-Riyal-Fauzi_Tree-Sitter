import sys
import os
from pathlib import Path
import tree_sitter_python as tspython
import tree_sitter_javascript as tsjavascript
from tree_sitter import Language, Parser, Query, QueryCursor

# Inisialisasi Parser Python
PY_LANG = Language(tspython.language())
parser_py = Parser(PY_LANG)
Q_TODO_PY = Query(PY_LANG, '((comment) @c (#match? @c "TODO|FIXME"))')
Q_FN_PY = Query(PY_LANG, '(function_definition name: (identifier) @nama) @fungsi')

# Inisialisasi Parser JavaScript [Pengayaan]
JS_LANG = Language(tsjavascript.language())
parser_js = Parser(JS_LANG)
Q_TODO_JS = Query(JS_LANG, '((comment) @c (#match? @c "TODO|FIXME"))')
Q_FN_JS = Query(JS_LANG, """
[
  (function_declaration name: (identifier) @nama)
  (method_definition name: (property_identifier) @nama)
  (variable_declarator name: (identifier) @nama value: [(arrow_function) (function_expression)])
] @fungsi
""")

IGNORABLE_DIRS = {"venv", ".venv", ".git", "node_modules", "__pycache__", ".idea", ".vscode"}

def cari_node_error_pertama(node):
    """
    Menelusuri pohon secara rekursif (DFS) untuk menemukan node pertama
    yang bertipe ERROR atau berstatus MISSING.
    """
    if node.is_error or node.is_missing or node.type in ("ERROR", "MISSING"):
        return node
    for child in node.children:
        err = cari_node_error_pertama(child)
        if err:
            return err
    return None

def cek_file_python(path: Path):
    try:
        content = path.read_bytes()
    except Exception as e:
        print(f"[-] Gagal membaca file {path}: {e}")
        return

    tree = parser_py.parse(content)
    root = tree.root_node

    # --- Fitur 1: Komentar TODO / FIXME ---
    todo_captures = QueryCursor(Q_TODO_PY).captures(root).get("c", [])
    for node in todo_captures:
        baris = node.start_point[0] + 1
        teks = node.text.decode(errors="replace").strip()
        print(f"[TODO/FIXME] {path}:{baris}: {teks}")

    # --- Fitur 2: Fungsi dengan panjang lebih dari 30 baris ---
    # Menggunakan matches agar pasangan @nama dan @fungsi terikat dengan benar
    for _, cap in QueryCursor(Q_FN_PY).matches(root):
        fn_node = cap.get("fungsi", [None])[0]
        nama_node = cap.get("nama", [None])[0]
        if fn_node and nama_node:
            panjang_baris = fn_node.end_point[0] - fn_node.start_point[0] + 1
            if panjang_baris > 30:
                baris_mulai = fn_node.start_point[0] + 1
                nama_fn = nama_node.text.decode(errors="replace")
                print(f"[FUNGSI PANJANG] {path}:{baris_mulai}: fungsi '{nama_fn}' memiliki {panjang_baris} baris (> 30 baris)")

    # --- Fitur 3: File yang pohonnya mengandung Syntax Error ---
    if root.has_error:
        err_node = cari_node_error_pertama(root)
        if err_node:
            baris_err = err_node.start_point[0] + 1
            kolom_err = err_node.start_point[1]
            teks_err = repr(err_node.text.decode(errors="replace").strip())
            print(f"[SYNTAX ERROR] {path}:{baris_err}:{kolom_err}: syntax error terdeteksi pada node '{err_node.type}' (teks: {teks_err})")
        else:
            print(f"[SYNTAX ERROR] {path}: root_node.has_error bernilai True")

def cek_file_javascript(path: Path):
    """[Pengayaan] Analisis file JavaScript dengan tree-sitter-javascript"""
    try:
        content = path.read_bytes()
    except Exception as e:
        print(f"[-] Gagal membaca file {path}: {e}")
        return

    tree = parser_js.parse(content)
    root = tree.root_node

    # 1. Komentar TODO / FIXME
    todo_captures = QueryCursor(Q_TODO_JS).captures(root).get("c", [])
    for node in todo_captures:
        baris = node.start_point[0] + 1
        teks = node.text.decode(errors="replace").strip()
        print(f"[JS TODO/FIXME] {path}:{baris}: {teks}")

    # 2. Fungsi > 30 baris
    for _, cap in QueryCursor(Q_FN_JS).matches(root):
        fn_node = cap.get("fungsi", [None])[0]
        nama_node = cap.get("nama", [None])[0]
        if fn_node and nama_node:
            panjang_baris = fn_node.end_point[0] - fn_node.start_point[0] + 1
            if panjang_baris > 30:
                baris_mulai = fn_node.start_point[0] + 1
                nama_fn = nama_node.text.decode(errors="replace")
                print(f"[JS FUNGSI PANJANG] {path}:{baris_mulai}: fungsi '{nama_fn}' memiliki {panjang_baris} baris (> 30 baris)")

    # 3. Syntax error
    if root.has_error:
        err_node = cari_node_error_pertama(root)
        if err_node:
            baris_err = err_node.start_point[0] + 1
            teks_err = repr(err_node.text.decode(errors="replace").strip())
            print(f"[JS SYNTAX ERROR] {path}:{baris_err}: syntax error pada node '{err_node.type}' ({teks_err})")

def scan_directory(target_folder: str):
    root_path = Path(target_folder)
    if not root_path.exists():
        print(f"Error: Folder '{target_folder}' tidak ditemukan.")
        sys.exit(1)

    print("=" * 75)
    print(f"MEMULAI ANALISIS KODE MENGGUNAKAN CEK.PY")
    print(f"Target Direktori : {root_path.resolve()}")
    print("=" * 75)

    total_py = 0
    total_js = 0

    for path in root_path.rglob("*"):
        # Abaikan direktori terlarang/dependencies
        if any(ignored in path.parts for ignored in IGNORABLE_DIRS):
            continue

        if path.is_file():
            if path.suffix == ".py":
                total_py += 1
                cek_file_python(path)
            elif path.suffix == ".js":
                total_js += 1
                cek_file_javascript(path)

    print("=" * 75)
    print(f"Pemeriksaan selesai. Total file dianalisis: {total_py} Python (.py), {total_js} JavaScript (.js)")
    print("=" * 75)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Penggunaan: python cek.py <folder_target>")
        sys.exit(1)
    scan_directory(sys.argv[1])
