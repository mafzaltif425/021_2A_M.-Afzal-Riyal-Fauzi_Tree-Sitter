# Laporan Praktikum & Penugasan Tree-Sitter (PLP)

**Nama Mahasiswa:** M. Afzal Riyal Fauzi  
**Kelas:** 2A - D4 Teknik Informatika  
**NIM:** 3 Digit Terakhir: 021  
**Mata Kuliah:** Programming Language Pragmatics (PLP)  
**Topik:** Pengenalan Syntax Tree, Tree-Sitter Runtime, Query Matching, DSL Grammar, dan Static Analyzer  

---

## 1. Penjelasan Singkat Tiap Tugas

### Tugas 1 — Membaca Pohon Sintaks (Mental Model "Kode Adalah Pohon")
Pada tugas ini, dilakukan pemahaman representasi pohon Concrete Syntax Tree (CST) dari tiga potongan kode Python: definisi fungsi, percabangan `if/else`, dan kelas dengan sebuah method. Sebelum dijalankan, bentuk pohon diprediksi secara teoretis kemudian diverifikasi terhadap output aktual `tree.root_node`. Selain itu, dianalisis perbedaan fundamental antara node bernama (`named_children`) dan node anonim (seperti keyword `def`, tanda `:`, kurung `()`, dan operator) yang tersimpan di `node.children`. Kemampuan error recovery Tree-sitter juga diuji dengan sengaja merusak sintaks (menghapus tanda titik dua `:` dan kurung tutup `)`), di mana parser tetap menghasilkan CST dengan menyisipkan node `ERROR`.

### Tugas 2 — Penjelajah Node Rekursif & TreeCursor
Membuat script `jelajah.py` untuk menelusuri pohon sintaks secara hierarkis (preorder DFS) dengan visualisasi indentasi berjenjang, tipe node, posisi `[baris:kolom]`, serta label field (misalnya `left:`, `right:`, `name:`). Pengambilan field dilakukan melalui pemetaan indeks child penuh `node.children` dengan fungsi `node.field_name_for_child(i)` agar field tidak hilang. Program diuji pada ekspresi sederhana `kecil.py` dan berkas kode nyata `sampel_nyata.py` (122 baris). Sebagai fitur pengayaan, diimplementasikan traversal non-rekursif berbasis `TreeCursor` (`cursor.goto_first_child()`, `goto_next_sibling()`, `goto_parent()`). Kedua metode diverifikasi menghasilkan representasi pohon 100% identik.

### Tugas 3 — Query & Pattern Matching Deklaratif
Menulis query deklaratif berformat S-expression (`.scm`) untuk mengekstrak informasi struktural kode menggunakan `Query` dan `QueryCursor`:
1. `q_fungsi_params.scm`: Mengekstrak nama fungsi dan menghitung jumlah parameternya melalui `named_child_count` pada node parameters.
2. `q_print.scm`: Menangkap pemanggilan fungsi `print(...)` dengan predikat `(#eq? @fn "print")`.
3. `q_import.scm`: Mengambil semua nama modul dari pernyataan `import ...` maupun `from ... import ...`.
4. `q_docstring.scm` (Pengayaan): Mengekstrak string literal yang berada tepat di awal blok fungsi sebagai docstring.
Seluruh hasil pencarian query dicocokkan dengan verifikasi manual ground truth pada file `contoh_t3.py` dengan tingkat akurasi 100%.

### Tugas 4 & 5 — Grammar DSL Filter & Syntax Highlighting
Merancang grammar Tree-sitter untuk DSL filter pencarian data di dashboard admin enterprise:
- Mendukung tipe data literal: string (`"[^"]*"`), number (`\d+(\.\d+)?`), dan boolean (`true`/`false`).
- Operator perbandingan: `=`, `!=`, `>`, `<`, `>=`, `<=`.
- Logika bertingkat dengan prioritas operator (`prec.left`): `not` (prioritas 3) > `and` (prioritas 2) > `or` (prioritas 1), serta pengelompokan tanda kurung `()`.
- Menambahkan node `in_expression` untuk penyaringan daftar nilai (contoh: `status in ("open", "pending")`) dan `contains_expression` untuk pencarian parsial teks (contoh: `title contains "invoice"`).
- Menyusun corpus uji `test/corpus/dasar.txt` yang memuat 7 kasus uji komprehensif.
- Mengonfigurasi `tree-sitter.json` dan `queries/highlights.scm` untuk pewarnaan syntax highlighting (keyword, operator, konstanta, properti, bracket, delimiter).
- Pengayaan: Membangun konverter AST ke klausa SQL `WHERE` terparameterisasi (`?`) untuk mencegah SQL Injection di backend.

### Tugas 6 — Mini Proyek: CLI Linter `cek.py`
Membangun tool CLI mandiri `cek.py <folder>` yang menginspeksi seluruh file Python (dan JavaScript pada fitur pengayaan) dalam suatu direktori:
- **Fitur 1:** Mendeteksi komentar `TODO` dan `FIXME` menggunakan query `#match?`.
- **Fitur 2:** Mendeteksi fungsi yang panjang body-nya melebihi 30 baris dengan menghitung delta `start_point` dan `end_point`.
- **Fitur 3:** Mendeteksi berkas yang memiliki syntax error (`root_node.has_error`) serta melaporkan lokasi baris dan jenis node error pertama via traversal rekursif.
- Dijalankan dan divalidasi pada repositori open-source nyata `bottle` (30 berkas Python), di mana 2 berkas acak diverifikasi silang secara manual dengan hasil 100% valid.

---

## 2. Tangkapan Layar Tekstual (Textual Execution Logs)

### A. Eksekusi Tugas 1 (`t1.py`)
```text
======================================================================
TUGAS 1: MEMBACA POHON SINTAKS (TREE-SITTER)
======================================================================

--- Potongan 1. Fungsi ---
Kode Sumber:
def hitung_diskon(harga, persen):
    return harga * (1 - persen / 100)

[Pohon Sebenarnya (tree.root_node)]:
(module (function_definition name: (identifier) parameters: (parameters (identifier) (identifier)) body: (block (return_statement (binary_operator left: (identifier) right: (parenthesized_expression (binary_operator left: (integer) right: (binary_operator left: (identifier) right: (integer)))))))))

--- Pemeriksaan Node Bernama vs Anonim ---
  [0] type: def                    status: ANONIM   text: 'def'
  [1] type: identifier             status: BERNAMA  text: 'hitung_diskon' [field: name]
  [2] type: parameters             status: BERNAMA  text: '(harga, persen)' [field: parameters]
  [3] type: :                      status: ANONIM   text: ':'
  [4] type: block                  status: BERNAMA  text: 'return harga * (1 - persen / 100)' [field: body]

--- Pengujian Error Recovery (Sintaks Rusak) ---
Kasus A: Hilang tanda ':' pada def sapa(nama)
Pohon: (module (ERROR (identifier) (parameters (identifier)) (identifier)))
Has Error: True
```

### B. Eksekusi Tugas 2 (`jelajah.py`)
```text
> python tugas1-3/jelajah.py tugas1-3/kecil.py
module [1:0]
  expression_statement [1:0]
    assignment [1:0]
      left: identifier [1:0]
      right: integer [1:4]

> python tugas1-3/jelajah.py tugas1-3/sampel_nyata.py --compare
Total node rekursif: 763
Total node TreeCursor: 763
Apakah hasil Rekursif dan TreeCursor IDENTIK? -> True
Perbandingan Sukses: Output kedua metode 100% cocok.
```

### C. Eksekusi Tugas 3 (`q.py --all`)
```text
======================================================================
PENGUJIAN LENGKAP SEMUA QUERY TUGAS 3 TERHADAP FILE UJI
Target File: tugas1-3/contoh_t3.py
======================================================================
=== Menjalankan 'q_fungsi_params.scm' ===
No. Baris    Nama Fungsi               Jumlah Parameter  
Baris 15     tanpa_param               0 parameter
Baris 20     hitung_luas               2 parameter
Baris 26     kalkulasi_volume          3 parameter
Baris 32     cetak_pesan               1 parameter

=== Menjalankan 'q_print.scm' ===
Baris 23     print(f"Luas: {luas}")
Baris 29     print(f"Volume: {volume}")
Baris 33     print("LOG:", pesan)

=== Menjalankan 'q_import.scm' ===
Baris 10     math
Baris 11     sys
Baris 12     datetime
Baris 13     os

=== Menjalankan 'q_docstring.scm' ===
Baris 15     tanpa_param          """Fungsi tanpa parameter sama sekali."""
Baris 20     hitung_luas          """Menghitung luas persegi panjang dengan dua...
======================================================================
VERIFIKASI GROUND TRUTH: Cocok 100% dengan hitungan manual.
```

### D. Eksekusi Tugas 4 Pengayaan (`filter_to_sql.py`)
```text
Input DSL:
status = "open" and (priority > 2 or owner = "budi") and category in ("bug", "incident") and not archived = true and description contains "timeout"

Hasil SQL WHERE Clause:
WHERE status = ? AND ((priority > ? OR owner = ?)) AND category IN (?, ?) AND NOT (archived = ?) AND description LIKE ?

Parameter Query (?):
["open", 2, "budi", "bug", "incident", true, "%timeout%"]
```

### E. Eksekusi Tugas 6 (`cek.py` pada repositori `bottle`)
```text
> python cek/cek.py cek/repo_nyata
[TODO/FIXME] repo_nyata\bottle.py:1002: # TODO: Handle these explicitly in handle() or make them iterable.
[TODO/FIXME] repo_nyata\bottle.py:2837: # HTTP Utilities and MISC (TODO) ###############################################
[TODO/FIXME] repo_nyata\bottle.py:2004: #: Not a plugin, but part of the plugin API. TODO: Find a better place.
[FUNGSI PANJANG] repo_nyata\bottle.py:329: fungsi 'add' memiliki 75 baris (> 30 baris)
[FUNGSI PANJANG] repo_nyata\bottle.py:2725: fungsi 'static_file' memiliki 110 baris (> 30 baris)
[TODO/FIXME] repo_nyata\test\test_html_helper.py:8: # TODO: Move more of the low level http stuff here.
[FUNGSI PANJANG] repo_nyata\test\test_sendfile.py:118: fungsi 'test_etag' memiliki 35 baris (> 30 baris)
Pemeriksaan selesai. Total file dianalisis: 30 Python (.py), 0 JavaScript (.js)
```

---

## 3. Kendala dan Cara Mengatasinya

1. **Perubahan API py-tree-sitter Versi 0.22+ ke 0.25+:**
   - *Kendala:* Dokumentasi lama di internet menggunakan `parser.set_language()` dan `Language.build_library()`. Pada versi library terbaru (`tree-sitter==0.26.1`), pemanggilan tersebut menghasilkan error karena konstruktor parser kini menerima instance language secara langsung: `Parser(Language(tspython.language()))`.
   - *Solusi:* Membaca spesifikasi pustaka modern dan menggunakan inisialisasi gaya 0.25+ serta `QueryCursor(query).matches(node)` dan `.captures(node)`.

2. **Hilangnya Label Field pada Traversal `jelajah.py`:**
   - *Kendala:* Ketika menelusuri `node.named_children`, memanggil `node.field_name_for_child(i)` menghasilkan nilai `None` untuk seluruh anak.
   - *Solusi:* Berdasarkan arsitektur Tree-sitter, indeks anak untuk pencarian nama field harus merujuk pada urutan di `node.children` (semua token termasuk token anonim), bukan pada array `named_children`. Solusinya adalah melakukan iterasi pada `node.children` dengan filter `child.is_named` sehingga indeks `i` tetap akurat.

3. **Sinkronisasi Kedalaman Traversal pada `TreeCursor`:**
   - *Kendala:* Pada pengayaan Tugas 2, ketika kursor berpindah ke token anonim (seperti tanda kurung), kedalaman pohon bertambah padahal node anonim tidak dicetak. Akibatnya indentasi versi cursor tidak sejajar dengan versi rekursif.
   - *Solusi:* Menyesuaikan penghitung kedalaman hanya bertambah (`+1`) atau berkurang (`-1`) jika node saat ini atau parent yang ditinggalkan adalah node bernama (`is_named == True`).

4. **Karakter Non-UTF-8 pada File Repositori Nyata di Tugas 6:**
   - *Kendala:* Saat membaca repositori eksternal, beberapa file lama memiliki encoding Latin-1 atau karakter non-standar yang memicu `UnicodeDecodeError`.
   - *Solusi:* Menerapkan parameter `errors="replace"` pada method `node.text.decode(errors="replace")` sehingga script linter tetap berjalan tangguh tanpa mengalami crash.

---

## 4. Catatan Penggunaan AI

Sesuai ketentuan, berikut rincian penggunaan AI coding agent pada pengerjaan tugas, meliputi instruksi permintaan, kesalahan/kekurangan AI yang ditemukan, dan bukti verifikasinya:

### 1. Tugas 1 & 2 (Membaca Pohon & Penjelajah Node)
- **Apa yang diminta ke AI:** Meminta kerangka fungsi rekursif untuk mencetak nama field dan tipe node dari `tree.root_node`.
- **Kesalahan/Kekurangan AI:** Kode awal yang dihasilkan AI menggunakan perulangan `for i, child in enumerate(node.named_children): field = node.field_name_for_child(i)`. Ini adalah bug logika karena `field_name_for_child` pada C API Tree-sitter mengharapkan indeks child komprehensif (`node.children`). Akibatnya, semua label field seperti `left:`, `right:`, dan `name:` bernilai `None`.
- **Cara membuktikannya:** Menjalankan script pada `kecil.py` (`x = 1`). Kode AI menghasilkan:
  ```text
  module [1:0]
    expression_statement [1:0]
      assignment [1:0]
        identifier [1:0]
        integer [1:4]
  ```
  Field `left:` dan `right:` hilang. Setelah diperbaiki dengan mengiterasi `node.children`, output menampilkan `left: identifier` dan `right: integer` secara tepat.

### 2. Tugas 3 (Query Deklaratif)
- **Apa yang diminta ke AI:** Meminta query S-expression untuk menghitung jumlah parameter pada fungsi Python.
- **Kesalahan/Kekurangan AI:** AI memberikan query `(function_definition name: (identifier) @nama parameters: (parameters (identifier) @param))` dan menyarankan menggunakan `.captures()`. Pendekatan ini gagal untuk fungsi tanpa parameter (karena pola tidak cocok sama sekali) dan memecah relasi antara fungsi dengan parameternya ketika ada banyak fungsi di satu file.
- **Cara membuktikannya:** Menguji pada fungsi `def tanpa_param(): pass`. Query usulan AI tidak mengembalikan capture apa pun untuk fungsi tersebut. Solusi yang benar adalah menangkap container node `parameters: (parameters) @params` lalu menggunakan method `.matches()` serta menghitung `named_child_count`.

### 3. Tugas 4 & 5 (Grammar DSL Filter)
- **Apa yang diminta ke AI:** Merancang aturan sintaks untuk operator `in` pada `grammar.js`.
- **Kesalahan/Kekurangan AI:** AI awalnya menulis rule `in_expression` tanpa mendefinisikan operator precedence (`prec.left`), sehingga memicu konflik shift/reduce pada parser generator terhadap operator `and` dan `or`.
- **Cara membuktikannya:** Menjalankan analisis ambiguitas pada ekspresi campuran `status in ("a", "b") and priority = 1`. Tanpa prioritas eksplisit, parser ragu apakah mengelompokkan `in` sebelum atau sesudah `and`. Dengan menambahkan `prec.left(2, ...)` yang setingkat dengan `and`, pohon terurai secara konsisten dan deterministik.

### 4. Tugas 6 (Linter `cek.py`)
- **Apa yang diminta ke AI:** Menghitung panjang baris fungsi untuk mendeteksi fungsi lebih dari 30 baris.
- **Kesalahan/Kekurangan AI:** AI menghitung baris dengan rumus `fn_node.end_point[0] - fn_node.start_point[0]`. Rumus ini mengalami *off-by-one error* (kurang 1 baris) karena baris Tree-sitter bersifat 0-indexed inklusif. Selain itu, AI tidak menyaring folder `.git` dan `.venv`, sehingga eksekusi di repositori nyata memindai ribuan file dependency library luar.
- **Cara membuktikannya:** Menguji fungsi 31 baris (baris 10 hingga 40). Rumus AI menghasilkan $40 - 10 = 30$, sehingga fungsi tersebut lolos dari deteksi. Dengan rumus yang benar (`end - start + 1 = 31`), fungsi terdeteksi dengan tepat. Penambahan filter `IGNORABLE_DIRS` juga memangkas waktu pemindaian dari 45 detik menjadi hanya 0,4 detik.
