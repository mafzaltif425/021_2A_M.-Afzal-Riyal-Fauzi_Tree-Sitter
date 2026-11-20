# CLI Analisis Kode Otomatis: `cek.py` (Tugas 6)

Tool analisis kode statis berbasis **Tree-sitter** untuk mendeteksi utang teknis (technical debt), fungsi yang terlalu panjang (complex/long functions), dan syntax error pada basis kode Python (serta JavaScript sebagai fitur pengayaan).

---

## 1. Fitur Utama

1. **Pendeteksi Komentar TODO / FIXME**
   - Menggunakan query deklaratif Tree-sitter `((comment) @c (#match? @c "TODO|FIXME"))`.
   - Melaporkan path file, nomor baris, dan teks komentar.
2. **Pendeteksi Fungsi Panjang (> 30 baris)**
   - Menggunakan pattern matching `(function_definition name: (identifier) @nama) @fungsi`.
   - Menghitung rentang baris `end_point[0] - start_point[0] + 1` dari body fungsi.
   - Melaporkan nama fungsi beserta total barisnya jika melebihi 30 baris.
3. **Pendeteksi File dengan Syntax Error**
   - Memeriksa flag `tree.root_node.has_error`.
   - Melakukan traversal rekursif (DFS) untuk menemukan node pertama yang bertipe `ERROR` atau `MISSING`.
   - Melaporkan posisi baris dan kolom persis di mana kesalahan sintaks terjadi.
4. **[Pengayaan] Dukungan File JavaScript (`.js`)**
   - Mendukung analisis file JavaScript secara otomatis menggunakan `tree-sitter-javascript`.
   - Menganalisis deklarasi fungsi, method objek/kelas, arrow functions, dan komentar TODO/FIXME di ekosistem web modern.
5. **Keandalan & Filter Direktori**
   - Mengabaikan direktori dependencies/internal (`.git`, `node_modules`, `venv`, `.venv`, `__pycache__`).
   - Penanganan encoding aman dengan `errors="replace"` agar tidak crash pada file non-UTF-8.

---

## 2. Instalasi Dependensi

Pastikan Python 3.10+ sudah terpasang. Jalankan perintah instalasi pustaka:

```bash
# Menggunakan pip standar:
pip install tree-sitter tree-sitter-python tree-sitter-javascript

# Atau menggunakan uv (ultra-fast Python package manager):
uv pip install tree-sitter tree-sitter-python tree-sitter-javascript
```

---

## 3. Cara Menjalankan

Jalankan perintah berikut di terminal:

```bash
python cek.py <path_folder_target>
```

Contoh pengujian pada folder uji bawaan:
```bash
python cek.py uji
```

---

## 4. Contoh Output Eksekusi

### A. Pengujian pada Folder Uji Sintetis (`cek/uji`)
```text
===========================================================================
MEMULAI ANALISIS KODE MENGGUNAKAN CEK.PY
Target Direktori : C:\...\cek\uji
===========================================================================
[SYNTAX ERROR] cek\uji\file_error.py:3:0: syntax error terdeteksi pada node 'ERROR' (teks: "def hitung_pajak(penghasilan)\n    # Sintaks rusak: lupa titik dua ':' pada def\n    tarif = 0.05\n    return penghasilan * tarif")
[FUNGSI PANJANG] cek\uji\file_panjang.py:3: fungsi 'generate_laporan_bulanan' memiliki 45 baris (> 30 baris)
[TODO/FIXME] cek\uji\file_todo.py:4: # TODO: Implementasikan validasi skema data sebelum disimpan
[TODO/FIXME] cek\uji\file_todo.py:7: # FIXME: Perbaiki potensi pembagian dengan nol pada rumus berikut
[TODO/FIXME] cek\uji\file_todo.py:11: # TODO: Tambahkan integrasi webhook notifikasi Discord
[JS TODO/FIXME] cek\uji\sample.js:3: // TODO: Tambahkan caching token JWT di Redis
[JS TODO/FIXME] cek\uji\sample.js:8: // FIXME: Hindari plain text comparison
===========================================================================
Pemeriksaan selesai. Total file dianalisis: 4 Python (.py), 1 JavaScript (.js)
===========================================================================
```

### B. Pengujian pada Repositori Nyata (Bottle Web Framework)
Perintah:
```bash
python cek.py repo_nyata
```

Hasil cuplikan temuan:
```text
[TODO/FIXME] repo_nyata\bottle.py:1002: # TODO: Handle these explicitly in handle() or make them iterable.
[TODO/FIXME] repo_nyata\bottle.py:2837: # HTTP Utilities and MISC (TODO) ###############################################
[TODO/FIXME] repo_nyata\bottle.py:2004: #: Not a plugin, but part of the plugin API. TODO: Find a better place.
[FUNGSI PANJANG] repo_nyata\bottle.py:329: fungsi 'add' memiliki 75 baris (> 30 baris)
[FUNGSI PANJANG] repo_nyata\bottle.py:2725: fungsi 'static_file' memiliki 110 baris (> 30 baris)
[TODO/FIXME] repo_nyata\test\test_html_helper.py:8: # TODO: Move more of the low level http stuff here.
[FUNGSI PANJANG] repo_nyata\test\test_sendfile.py:118: fungsi 'test_etag' memiliki 35 baris (> 30 baris)
Total file dianalisis: 30 Python (.py), 0 JavaScript (.js)
```

---

## 5. Verifikasi Manual Ground Truth pada 2 File Acak

Untuk membuktikan keandalan dan akurasi analisis AST Tree-sitter, dilakukan pencocokan manual pada 2 file acak dari repositori open-source `bottle`:

1. **Berkas 1:** `repo_nyata/test/test_html_helper.py`
   - **Hasil Tool:** Mendeteksi komentar TODO pada baris ke-8: `# TODO: Move more of the low level http stuff here.`
   - **Pemeriksaan Manual:** Pada baris ke-8 kelas `TestHttpUtils`, memang tertulis tepat baris komentar tersebut.
   - **Status:** **VALID (100% Cocok)**.

2. **Berkas 2:** `repo_nyata/test/test_sendfile.py`
   - **Hasil Tool:** Mendeteksi fungsi `test_etag` pada baris ke-118 dengan panjang 35 baris.
   - **Pemeriksaan Manual:** Fungsi dimulai dari deklarasi `def test_etag(self):` di baris 118 dan berakhir pada baris 152 sebelum method `test_etag_overrides_ims`. Rentang total: $152 - 118 + 1 = 35$ baris.
   - **Status:** **VALID (100% Cocok)**.
