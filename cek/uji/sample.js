// File Uji JavaScript [Pengayaan]

// TODO: Tambahkan caching token JWT di Redis
function otentikasiPengguna(username, password) {
  if (!username || !password) {
    return false;
  }
  // FIXME: Hindari plain text comparison
  return username === "admin" && password === "secret";
}

function prosesBatchTransaksi(daftarTransaksi) {
  let hasil = [];
  console.log("Memulai pemrosesan batch...");
  for (let i = 0; i < daftarTransaksi.length; i++) {
    let tx = daftarTransaksi[i];
    if (tx.status === "ACTIVE") {
      hasil.push(tx);
    }
  }
  return hasil;
}
