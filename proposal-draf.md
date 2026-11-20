# Draf Proposal Proyek: Pemanfaatan Tree-Sitter untuk Web Enterprise

**Nama Mahasiswa:** M. Afzal Riyal Fauzi  
**Kelas / NIM:** 2A - D4 Teknik Informatika / 021  
**Mata Kuliah:** Programming Language Pragmatics (PLP)  

---

### 1. Judul Proyek
**ArchGuard:** Linter Statis Berbasis Tree-Sitter untuk Penegakan Arsitektur Berlapis (*Layered Architecture*) dan Pencegahan Raw SQL Unescaped pada REST API Enterprise (Node.js/TypeScript & Express).

---

### 2. Masalah
Pada pengembangan aplikasi web skala *enterprise*, tim *software engineering* yang terdiri dari puluhan *developer* sering kali melanggar arsitektur *clean/layered architecture*. Kasus pelanggaran paling umum adalah lapisan **Controller** yang langsung mengimpor atau memanggil lapisan database/data-access (**Repository/DAO**) tanpa melalui lapisan **Service/Use-Case**. Pelanggaran ini merusak prinsip pemisahan tanggung jawab (*separation of concerns*), mempersulit *unit testing*, serta memicu kebocoran logika bisnis. Selain itu, *developer* sering mengeksekusi *raw SQL query* menggunakan konkatenasi string di controller/service (`db.query("SELECT ... WHERE id = " + req.id)`), yang membuka celah fatal **SQL Injection (SQLi)**. Masalah ini dialami oleh Tech Lead, Software Architect, dan Code Reviewer saat memeriksa ratusan *pull request* setiap minggu.

---

### 3. Kenapa Tidak Cukup dengan AI Saja?
AI coding agent bersifat non-deterministik (*probabilistic*)—hasil review-nya dapat berbeda pada setiap eksekusi untuk kode yang sama, berpotensi mengalami halusinasi (*false negative/positive*), dan memerlukan biaya komputasi token yang mahal jika harus menganalisis jutaan baris kode secara terus-menerus. Sebaliknya, tool berbasis Tree-sitter bersifat **100% deterministik**, mengeksekusi ribuan file per detik dengan biaya token nol ($0), serta dapat diintegrasikan secara instan ke dalam pipeline **CI/CD (GitHub Actions/GitLab CI)** sebagai *quality gate* otomatis sebelum kode di-*merge*. Tool ini juga dapat dijadikan server MCP (*Model Context Protocol*) untuk memandu AI agent agar selalu mematuhi aturan arsitektur.

---

### 4. Bahasa, Framework, dan Grammar Target
- **Bahasa & Framework Target:** TypeScript / JavaScript dengan framework backend web enterprise **Express.js** dan **NestJS**.
- **Pustaka Grammar Tree-sitter:** `tree-sitter-typescript` (dan `tree-sitter-javascript`) yang tersedia resmi di PyPI / NPM.

---

### 5. Contoh Kode Target

#### A. Kode Pelanggaran yang HARUS Terdeteksi:
```typescript
// CONTROLLER: users.controller.ts
import { UserRepository } from '../repositories/user.repository'; // PELANGGARAN 1: Controller import Repository langsung!

export class UserController {
  async getUser(req: Request, res: Response) {
    const userId = req.params.id;
    // PELANGGARAN 2: Pemanggilan raw query berbahaya dengan konkatenasi string!
    const user = await db.query("SELECT * FROM users WHERE id = " + userId);
    return res.json(user);
  }
}
```

#### B. Kode Sah yang TIDAK Boleh Terdeteksi (*False Positive Prevention*):
```typescript
// CONTROLLER: users.controller.ts (Sesuai Standar Enterprise)
import { UserService } from '../services/user.service'; // BENAR: Mengakses Service layer

export class UserController {
  constructor(private userService: UserService) {}

  async getUser(req: Request, res: Response) {
    const userId = req.params.id;
    // BENAR: Menggunakan Service dan parameterisasi query
    const user = await this.userService.findById(userId);
    return res.json(user);
  }
}
```

---

### 6. Rancangan Query Tree-Sitter (S-Expression)
Query untuk mendeteksi controller yang mengimpor modul repository secara ilegal:
```scheme
(import_statement
  source: (string) @import_path
  (#match? @import_path "repository|repositories|dao")
  (#match? @_current_file_path "controller"))
```

Query untuk mendeteksi pemanggilan *raw SQL* berbasis konkatenasi string biner (`+`):
```scheme
(call_expression
  function: (member_expression
    property: (property_identifier) @fn_name
    (#match? @fn_name "^(query|raw|execute)$"))
  arguments: (arguments
    (binary_expression
      operator: "+"
      left: (string)) @sql_injection_risk))
```

---

### 7. Bentuk Output
- **Laporan Terminal Interaktif:** Ringkasan berwarna dengan nomor baris, cuplikan kode, dan rekomendasi perbaikan.
- **File Laporan JSON:** Untuk integrasi otomasi CI/CD quality gate.
- **Exit Code Non-Zero (1):** Menggagalkan build pipeline jika terdeteksi pelanggaran tingkat `CRITICAL` (misalnya SQL Injection).

---

### 8. Cara Evaluasi
- **Repositori Uji:** Diuji pada proyek backend open-source nyata (misalnya template arsitektur NestJS/Express di GitHub) serta *test suite* sintetis berisi minimal 30 variasi kode (15 melanggar, 15 valid).
- **Metrik Keberhasilan:** Mengukur *Precision* dan *Recall* (target: 0 *false positive* pada kode sah dan 100% deteksi pada kode rentan).

---

### 9. Rencana Kerja Per Minggu dan Risiko

| Minggu | Agenda Kerja | Output Utama |
| :--- | :--- | :--- |
| **Minggu 1** | Studi AST TypeScript/Express, menyusun aturan linter, dan menyiapkan *test dataset*. | File query `.scm` awal dan skenario uji. |
| **Minggu 2** | Implementasi engine Tree-sitter Python untuk mendeteksi *illegal layer imports*. | CLI validator arsitektur controller. |
| **Minggu 3** | Implementasi deteksi konkatenasi string SQL Injection pada method query. | Modul audit keamanan database. |
| **Minggu 4** | Integrasi reporter CLI, format output JSON, dan pengujian pada repositori nyata. | CLI ArchGuard siap pakai & laporan benchmarking. |
| **Minggu 5** | Penyusunan dokumentasi akhir, video demo, dan integrasi GitHub Action CI. | Repositori final & laporan proyek lengkap. |

**Antisipasi Risiko:** Penamaan path repository yang beragam (misalnya `UserDB` alih-alih `UserRepository`) akan diatasi dengan konfigurasi pola regex yang dapat disesuaikan pada file `archguard.config.json`.
