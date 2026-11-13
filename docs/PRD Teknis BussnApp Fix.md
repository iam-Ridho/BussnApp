# PRD Teknis BussnApp

Nov 7, 2026 · @Demss ARS

## 1. Executive Summary & KPI

BussnApp adalah pemandu kesiapan usaha mandiri untuk UMKM: aplikasi menghitung skor kesiapan 0–100 dari data keuangan nyata yang dicatat pengguna, menunjukkan masalah yang harus diperbaiki lebih dulu, lalu membantu merencanakan pengembangan usaha secara bertahap. Tagline produk: "Know your business before you seek funding."

### 1.1 Masalah yang Diselesaikan

- Pemilik UMKM tahu modal yang diinginkan, tetapi tidak tahu apakah usahanya sudah siap menerima modal itu.
- Pencatatan keuangan berantakan: uang pribadi dan usaha tercampur, keuntungan hanya diperkirakan dari perasaan.
- Aplikasi UMKM yang ada hanya mencatat atau meminjamkan; hampir tidak ada yang mendiagnosis lalu membimbing.

### 1.2 Filosofi Tiga Tahap

| Tahap | Tujuan pengguna | Keluaran utama | Fitur inti |
| --- | --- | --- | --- |
| KNOW | Mengenali kondisi usaha | Laporan otomatis, skor 0–100, confidence level | Scan struk, catat penjualan, impor CSV, Laba Rugi, Arus Kas, Neraca, Diagnosis |
| IMPROVE | Memperbaiki yang lemah | Daftar masalah terurut, Action Plan, jawaban chat berbasis data | Deteksi masalah/anomali, Prioritas, Action Plan, AI Konsultasi |
| GROW | Merencanakan pertumbuhan | Rencana bertahap, rentang modal, PDF siap-bank | Growth Planner, Proyeksi Modal Berentang, Laporan Siap-Bank |

### 1.3 Prinsip Arsitektur: Kode Menghitung, AI Menjelaskan

1. Semua angka (laporan, skor 0–100, 7 indikator, confidence, runway, break-even, deteksi masalah, anomali, duplikat, prioritas) dihitung oleh Rule Engine deterministik di backend. AI tidak ikut menentukan angka apa pun.
2. AI hanya menerima angka hasil hitungan kode dalam bentuk JSON terstruktur (Bab 4), lalu menjelaskan, menyusun langkah, atau menjawab pertanyaan.
3. Setiap keluaran AI yang memuat angka divalidasi otomatis terhadap JSON masukan sebelum sampai ke pengguna; yang gagal diganti template tetap.
4. Lapisan AI bersifat modular (satu antarmuka layanan), sehingga penyedia (OpenAI atau Gemini) dan OCR dapat diganti tanpa mengubah UI maupun aturan skor.

### 1.4 Posisi Produk dan Batas Klaim

BussnApp bukan produk kredit dan bukan penilaian kelayakan kredit. Skor adalah indikator kesiapan usaha yang transparan dan dapat ditelusuri ke data pengguna. Keputusan pembiayaan tetap di tangan lembaga keuangan dan pengguna.

- Boleh dikatakan di UI: "skor kesiapan usaha", "hal yang perlu diperbaiki", "rentang kebutuhan modal".
- Tidak boleh dikatakan: "layak kredit", "pasti disetujui", "jaminan pinjaman", atau rekomendasi lembaga pemberi pinjaman tertentu.
- Setiap layar skor, rentang modal, dan PDF siap-bank memuat catatan: "Skor ini pemandu kesiapan usaha, bukan penilaian kelayakan kredit."
- Tidak ada fitur pengajuan kredit di MVP (Fase 2 pun hanya setelah kajian hukum).

### 1.5 KPI Terukur

| ID | Metrik | Target | Cara pengukuran | PIC |
| --- | --- | --- | --- | --- |
| K1 | Latensi OCR struk | p95 < 3 detik | Dari unggah selesai sampai JSON terstruktur diterima klien. 100 uji, foto ≤ 1,5 MB setelah kompresi di klien, jaringan 4G ≥ 5 Mbps. Dicatat di log `ocr_latency_ms`. | Febri |
| K2 | Latensi API inti | p95 < 1,5 detik | Semua endpoint selain AI dan PDF. Uji beban k6: 50 pengguna simultan, 5 menit, data 10.000 transaksi per usaha. | Rido |
| K3 | Frame rate UI | 60 fps, jank < 1% | Flutter DevTools mode profile pada perangkat acuan (Android, RAM 4 GB, layar 60 Hz) di 5 alur utama. Frame > 16,6 ms dihitung jank. | Said, Arya |
| K4 | Akurasi OCR struk | > 90% akurasi level-field | 150 struk cetak (toko, tanggal, total, item: nama, jumlah, harga). Akurasi = field benar ÷ seluruh field. Syarat tambahan: total harga cocok persis ≥ 95%. Struk buram atau tulisan tangan dilaporkan terpisah, tanpa target. | Febri |
| K5 | Halusinasi angka AI | 0 kasus lolos | Validator numerik memeriksa 100% keluaran AI terhadap JSON masukan. Suite CI 300 skenario harus 0 pelanggaran; audit manual 50 respons per minggu. | Febri |
| K6 | Kepatuhan UU PDP | 10 dari 10 item daftar periksa (Bab 8) | Daftar periksa DoD diverifikasi sebelum rilis; kajian hukum oleh pihak yang berwenang tetap diperlukan sebelum peluncuran publik. | Rido, Febri |
| K7 | Reproduktifitas skor | 100% identik | Golden test: 40 dataset uji, masukan sama harus menghasilkan skor, confidence, dan daftar masalah yang sama persis. | Rido |
| K8 | Stabilitas aplikasi | ≥ 99% sesi bebas crash | Sentry, pada uji internal minimal 100 sesi sebelum rilis. | Febri |
| K9 | Waktu ke diagnosis awal | ≤ 5 menit | Dari buka pertama sampai Diagnosis Awal tampil. Uji usabilitas dengan 5 pelaku UMKM. | Said |

Semua target diukur pada build rilis kandidat di akhir Sprint 3. Target yang gagal menjadi blocker rilis, kecuali Product Manager menyetujui pengecualian tertulis.

## 2. Persona & Alur Kerja

Satu persona (Said) dan satu alur 12 langkah menjadi acuan semua modul: setiap fitur di Bab 3 harus bisa ditunjuk pada langkah tertentu di alur ini.

### 2.1 Persona Utama: Said (nama persona, bukan anggota tim)

- Profil: 20 tahun, pemilik kedai minuman di Samarinda, usaha berjalan 1,5 tahun.
- Kondisi: pencatatan belum rutin; uang pribadi dan usaha masih di rekening yang sama; keuntungan diperkirakan dari perasaan.
- Tujuan: menambah mesin untuk kedainya dan tahu apakah usahanya sudah siap menerima modal.
- Hambatan: malas mencatat satu per satu, belanja sering tanpa struk, tidak paham istilah akuntansi.

### 2.2 Perjalanan Said: Hari 1, Minggu 3, Bulan 3

| Waktu | Yang dilakukan Said | Hasil dari kode (Rule Engine) | Peran AI |
| --- | --- | --- | --- |
| Hari 1 | Mengisi Profil Usaha dan Setup Awal (modal, mesin, stok). | Diagnosis Awal: skor sementara dari 2 indikator (Administrasi, Kemampuan Bayar), label "Rendah: belum ada data transaksi". Tidak masuk riwayat skor bulanan. | Tidak dipanggil; penjelasan memakai template tetap. |
| Minggu 1–2 | Memotret struk belanja bahan, mencatat penjualan cepat, mengisi rekap harian saat sibuk. | Transaksi tersimpan, deteksi duplikat dan anomali berjalan, confidence naik bertahap. | AI membaca struk menjadi data terstruktur. |
| Minggu 3 | Membuka laporan dan Diagnosis. | Laba Rugi dan Arus Kas terbentuk; skor 72 (kategori Cukup Siap) dengan keyakinan Sedang; masalah terdeteksi: margin turun (R01) dan rekening tercampur (R04). | AI menyusun narasi dan Action Plan: "Buka rekening khusus usaha (2 minggu)" dan "Naikkan harga produk A". Said bertanya "Kenapa untung turun?" lalu dijawab dari datanya. |
| Bulan 3 | Menyelesaikan langkah Action Plan, terus mencatat. | Skor naik (data contoh prototipe: 81), keyakinan Tinggi; gerbang kesiapan terpenuhi; rentang kebutuhan modal untuk "tambah mesin" dihitung. | AI menyusun Growth Planner bertahap; Said mengekspor PDF Laporan Siap-Bank. |

### 2.3 Alur Kerja 12 Langkah

Alur berulang: makin banyak data masuk, makin akurat diagnosisnya. Langkah 10 adalah satu-satunya percabangan: belum cukup siap kembali ke langkah 7 (Action Plan), cukup siap lanjut ke langkah 11 (Growth Planner).

**Aturan gerbang langkah 10** (dihitung kode, dipakai sebagai rekomendasi, bukan penghalang):

- Jalur "Ya" (ke langkah 11) jika skor ≥ 75, confidence = Tinggi, dan tidak ada masalah severity Tinggi yang terbuka dari R05 (runway), R06 (di bawah break-even), atau R07 (kemampuan bayar).
- Jalur "Belum" (ke langkah 7) jika salah satu syarat tidak terpenuhi; Action Plan diperbarui dari daftar masalah terbaru.
- Pengguna tetap dapat membuka Growth Planner setelah ≥ 30 hari data; jika gerbang belum terpenuhi, layar menampilkan banner "Belum disarankan: selesaikan dulu langkah perbaikan".
- AI Konsultasi (chat) dapat dibuka kapan saja dari langkah 5 sampai 11.

| No | Langkah | Dikerjakan oleh | PIC | Modul (Bab 3) |
| --- | --- | --- | --- | --- |
| 1 | Daftar dan login (onboarding, persetujuan privasi) | Pengguna | Said (UI), Arya (auth) | A |
| 2 | Profil dan setup awal (modal, aset, utang, stok) | Pengguna | Arya | A |
| 3 | Input data (struk, penjualan, mutasi) | Pengguna, AI (baca struk) | Arya, Febri | B1, B2 |
| 4 | Sistem menghitung laporan dan skor | Kode | Rido | D, E1, E2 |
| 5 | Diagnosis: masalah dan keyakinan | Kode | Rido (hitung), Agam (layar) | E1, E3 |
| 6 | Prioritas: dampak × kemudahan | Kode | Rido, Agam | E3 |
| 7 | Action Plan | AI dari daftar masalah kode | Febri, Said | F |
| 8 | Kerjakan dan catat status langkah | Pengguna | Said, Arya | F |
| 9 | Data bertambah, skor diperbarui tiap bulan | Kode | Rido, Agam | E1 |
| 10 | Cek kesiapan: skor dan tren | Kode | Rido (gerbang), Agam (layar) | E1, E3 |
| 11 | Growth Planner dan proyeksi modal berentang | Kode (rentang), AI (rencana) | Agam, Febri | F |
| 12 | Siap berkembang: ekspor laporan siap-bank PDF | Kode | Agam | D |

### 2.4 Alur Scan Struk: 5 Tahap

Scan struk adalah cara utama memasukkan pengeluaran. Struk hanya membuktikan pengeluaran; penjualan masuk lewat Catat Penjualan Cepat, Rekap Harian, atau Impor Mutasi.

1. **Foto struk.** Pengguna memotret struk dari tombol tengah "Catat". Klien memeriksa ketajaman (peringatan jika buram) dan mengompres gambar menjadi ≤ 1,5 MB sebelum unggah. PIC: Arya.
2. **AI membaca.** Klien memanggil `POST /receipts/scan`; layanan OCR/visi mengembalikan toko, tanggal, daftar item (nama, jumlah, harga satuan, subtotal), total, kategori usulan, dan nilai keyakinan tiap kolom. Target p95 < 3 detik. PIC: Febri.
3. **Pengguna cek.** Layar Konfirmasi menampilkan hasil yang dapat diedit. Kolom dengan keyakinan < 0,80 berwarna kuning; selisih antara jumlah subtotal item dan total > 1% menandai total dan item terkait kuning. PIC: Arya (logika), Said (tampilan).
4. **Disimpan.** Setelah dikonfirmasi, struk disimpan sebagai transaksi pengeluaran bersumber "struk". Rule Engine memeriksa duplikat (toko + tanggal + total sama, atau gambar sangat mirip) dan meminta konfirmasi bila terdeteksi. PIC: Rido.
5. **Dampak.** Item bahan baku menambah stok, harga beli memperbarui HPP produk terkait, laporan dihitung ulang, dan deteksi anomali (lonjakan biaya, kenaikan harga bahan) dijalankan. PIC: Rido.

## 3. Spesifikasi Fitur & Rumus Kode (Modul A–F)

Setiap fitur di bawah memiliki user story, acceptance criteria Given-When-Then (GWT), dan PIC. Modul E dan sebagian D, F menjalankan rumus eksplisit yang dihitung Rule Engine (Rido); AI tidak menghitung angka apa pun.

### 3.0 Konvensi Hitung (berlaku untuk semua modul)

- Mata uang: Rupiah, bilangan bulat (BIGINT), tanpa desimal. Zona waktu mengikuti profil usaha (default Asia/Makassar).
- Tag transaksi: `usaha`, `pribadi`, `belum_ditag`. Transaksi dari catat manual, struk, dan penjualan berstatus `usaha` secara default. Transaksi hasil impor mutasi berstatus `belum_ditag`. Hanya `usaha` yang masuk laporan dan skor; `pribadi` dan `belum_ditag` dikecualikan.
- hari\_data: jumlah hari kalender berbeda yang memiliki minimal satu catatan (transaksi atau rekap). Jendela W30 = 30 hari kalender terakhir; W90 = 90 hari terakhir (atau seluruh data jika lebih pendek).
- Fungsi bantu: clip(x, a, b) membatasi x ke rentang \[a, b\]. lin(x; a, b) = 100 × clip((x − a) ÷ (b − a), 0, 1); berlaku untuk a < b (nilai besar bagus) maupun a > b (nilai kecil bagus).
- Bobot sumber data (untuk confidence): `receipt` 1,0; `bank_import` 1,0; `quick_sale` 0,6; `manual` 0,6; `daily_recap` 0,4.
- Jenis transaksi: `sale` (penjualan), `expense` (pengeluaran), `capital_in` (tambahan modal atau pinjaman cair), `asset_purchase` (pembelian peralatan), `debt_payment` (cicilan utang; bunga tidak dipisah di MVP).

| Kode kategori | Nama | Kelompok | Sifat biaya |
| --- | --- | --- | --- |
| bahan\_baku | Bahan baku | HPP | Variabel |
| kemasan | Kemasan | HPP | Variabel |
| tenaga\_kerja | Gaji dan upah | Operasional | Tetap |
| sewa | Sewa tempat | Operasional | Tetap |
| utilitas | Listrik, air, internet | Operasional | Tetap |
| transport | Transportasi dan pengiriman | Operasional | Variabel |
| pemasaran | Promosi dan pemasaran | Operasional | Variabel |
| perawatan\_alat | Perawatan peralatan | Operasional | Tetap |
| administrasi\_pajak | Administrasi, izin, pajak | Operasional | Tetap |
| lainnya | Lainnya | Operasional | Variabel |

### 3.1 Modul A: Masuk & Profil

| ID | Fitur | User story | Acceptance Criteria (GWT) | PIC |
| --- | --- | --- | --- | --- |
| A-01 | Onboarding | Sebagai pengguna baru, saya ingin pengenalan singkat agar paham manfaat aplikasi. | Given pertama kali membuka aplikasi, When pengguna melihat 3 layar onboarding, Then tombol "Lewati" ada di setiap layar dan layar login tampil setelah layar ke-3 atau setelah "Lewati". | Said |
| A-02 | Login | Sebagai pengguna, saya ingin masuk dengan aman agar data usaha tidak bocor. | Given akun terdaftar (email dan kata sandi minimal 8 karakter), When login benar, Then access token JWT (berlaku 15 menit) dan refresh token (30 hari) tersimpan di secure storage. Given 5 kali salah berturut-turut, When mencoba lagi, Then akun terkunci 15 menit dengan pesan jelas. | Arya, Rido |
| A-03 | Persetujuan privasi UU PDP | Sebagai pengguna, saya ingin tahu dan menyetujui data apa yang diproses dan dikirim ke pihak ketiga. | Given pendaftaran, When pengguna belum mencentang persetujuan 1 (pemrosesan data keuangan), Then pendaftaran tidak bisa dilanjutkan. Given persetujuan 2 (kirim data ringkas ke penyedia AI) tidak dicentang, Then fitur AI nonaktif tetapi laporan dan skor tetap berjalan. Setiap persetujuan tercatat dengan versi teks dan waktu, dan dapat ditarik dari Profil. | Arya, Rido |
| A-04 | Profil Usaha | Sebagai pemilik usaha, saya ingin mengisi profil singkat agar diagnosis sesuai konteks. | Given login pertama, When mengisi jenis usaha, lama berjalan (bulan), jumlah karyawan, status NIB (punya, proses, belum), dan rekening terpisah (ya, tidak), Then profil tersimpan dan Diagnosis Awal dapat dihitung. Semua kolom wajib. | Arya |
| A-05 | Setup Awal Usaha | Sebagai pemilik usaha, saya ingin mencatat kondisi awal sekali saja agar neraca dan kemampuan bayar bisa dihitung. | Given profil terisi, When mengisi saldo kas awal, modal awal, aset (nama, nilai), utang (pemberi, sisa, cicilan bulanan), dan stok awal, Then neraca awal terbentuk. Pilihan "Tidak ada utang" sah. Tombol "Lewati dulu" tersedia, tetapi menandai setup belum lengkap (berdampak ke indikator Administrasi). | Arya |

### 3.2 Modul B1: Input Struk (KNOW)

| ID | Fitur | User story | Acceptance Criteria (GWT) | PIC |
| --- | --- | --- | --- | --- |
| B1-01 | Scan Struk | Sebagai pemilik usaha, saya ingin cukup memotret struk agar pengeluaran tercatat tanpa mengetik. | Given izin kamera aktif, When pengguna memotret struk, Then layar Konfirmasi tampil dengan toko, tanggal, item, total, dan kategori usulan dalam p95 < 3 detik. Given tidak ada jaringan, When foto diambil, Then foto masuk antrean offline dan diproses otomatis saat online. | Arya, Febri |
| B1-02 | Konfirmasi Struk | Sebagai pemilik usaha, saya ingin memeriksa dan memperbaiki hasil baca AI agar analisis tidak rusak oleh salah baca. | Given hasil OCR, When ada kolom dengan keyakinan < 0,80 atau selisih subtotal item dan total > 1%, Then kolom itu berwarna kuning dan tombol Simpan menampilkan jumlah kolom kuning yang belum diperiksa. Semua kolom dapat diedit. Simpan aktif hanya jika total > 0 dan tanggal tidak di masa depan. | Arya, Said |
| B1-03 | Deteksi Struk Duplikat | Sebagai pemilik usaha, saya ingin diperingatkan jika struk sama tercatat dua kali. | Given struk dikonfirmasi, When aturan duplikat keras terpenuhi (3.9), Then dialog menampilkan struk yang mirip dengan tombol "Batalkan" (default) dan "Tetap simpan". When hanya aturan lunak terpenuhi, Then banner muncul dengan default "Simpan". | Rido |

### 3.3 Modul B2: Input Transaksi Lain

| ID | Fitur | User story | Acceptance Criteria (GWT) | PIC |
| --- | --- | --- | --- | --- |
| B2-01 | Catat Penjualan Cepat | Sebagai penjual, saya ingin mencatat penjualan dengan satu tap agar tidak mengganggu pelanggan. | Given tombol Catat, When pengguna mengisi nominal atau memilih produk katalog dan jumlah lalu menekan satu tombol, Then transaksi tampil di daftar seketika (optimistic UI) dan tersinkron di latar. Produk katalog mengurangi stok bahan dan menyimpan HPP saat itu (snapshot). | Arya |
| B2-02 | Rekap Harian | Sebagai penjual yang sibuk, saya ingin mengisi total penjualan sehari agar hari itu tetap tercatat. | Given hari berjalan, When pengguna mengisi satu angka total penjualan, Then tersimpan sebagai `sale` bersumber `daily_recap`. Rekap hanya menambah selisih positif terhadap total penjualan per transaksi hari itu, sehingga tidak terhitung ganda. | Arya, Rido |
| B2-03 | Pengeluaran Manual | Sebagai pembeli di pasar tradisional, saya ingin mencatat belanja tanpa struk. | Given belanja tanpa struk, When memilih salah satu dari 10 kategori, mengisi nominal dan tanggal, Then tersimpan sebagai `expense` bersumber `manual` (bobot 0,6). | Arya |
| B2-04 | Impor Mutasi CSV umum | Sebagai pemilik usaha, saya ingin mengunggah mutasi rekening agar penjualan non-tunai tercatat. | Given file CSV UTF-8 (maks 5 MB, 5.000 baris, kolom tanggal, deskripsi, debit, kredit; pemisah koma atau titik koma), When diunggah, Then pratinjau tampil dengan status tiap baris: cocok, belum tercatat, atau duplikat. Baris belum tercatat berstatus `belum_ditag`. Given kolom wajib tidak ditemukan, Then pesan menyebut kolom yang hilang dan tidak ada data tersimpan. | Arya, Rido |
| B2-05 | Tag Pribadi / Usaha massal | Sebagai pemilik yang uangnya tercampur, saya ingin memisahkan transaksi sekaligus. | Given daftar transaksi, When memilih banyak transaksi (maks 200 per operasi) atau aturan "semua dengan deskripsi X" lalu memberi tag, Then tag berubah dan laporan serta skor dihitung ulang; badge jumlah `belum_ditag` diperbarui. | Arya, Rido |
| B2-06 | Pengingat & Streak | Sebagai pengguna yang malas mencatat, saya ingin pengingat dan penanda konsistensi. | Given belum ada catatan hari ini, When pukul 17:00 waktu usaha (dapat diubah), Then notifikasi lokal muncul; tidak muncul jika sudah mencatat. Streak bertambah 1 untuk setiap hari berurutan dengan minimal satu catatan. | Arya |

### 3.4 Modul C: Pengelolaan Usaha

**HPP per unit produk** = Σ (jumlah bahan i per unit × harga satuan terakhir bahan i) + biaya kemasan per unit. **Margin Rp** = harga jual − HPP unit. **Margin %** = Margin Rp ÷ harga jual. Harga satuan terakhir bahan diperbarui otomatis dari struk yang dipetakan ke bahan itu.

| ID | Fitur | User story | Acceptance Criteria (GWT) | PIC |
| --- | --- | --- | --- | --- |
| C-01 | Katalog Produk dan HPP | Sebagai pemilik usaha, saya ingin tahu produk mana yang benar-benar untung. | Given katalog, When pengguna menambah produk (nama, harga jual) dan resep bahan (bahan, jumlah, satuan), Then HPP unit dan Margin % tampil; produk dengan Margin % < 20% bertanda merah. Given harga bahan berubah dari struk baru, Then HPP dan margin produk terkait dihitung ulang. | Arya, Rido |
| C-02 | Stok Sederhana | Sebagai pemilik usaha, saya ingin tahu kapan bahan hampir habis. | Given bahan dengan stok awal, When struk dikonfirmasi atau produk beresep terjual, Then stok bertambah atau berkurang sesuai jumlah. Given stok ≤ 3 × pemakaian harian rata-rata 14 hari (atau batas yang diisi pengguna), Then satu notifikasi stok tipis dikirim per bahan per hari. | Arya, Rido |

### 3.5 Modul D: Laporan Otomatis

**Rumus laporan** (periode P, hanya tag `usaha`):

- Omzet = Σ `sale`.
- HPP, metode katalog: jika ≥ 60% nilai penjualan terhubung ke produk katalog, HPP = Σ (jumlah terjual × HPP snapshot); penjualan non-katalog dihitung dengan rasio HPP katalog rata-rata. Metode pembelian (jika di bawah 60%): HPP = Σ `expense` kategori `bahan_baku` dan `kemasan` pada P, dan laporan memberi label "HPP estimasi dari pembelian bahan".
- Laba Kotor = Omzet − HPP. Opex = Σ `expense` selain `bahan_baku` dan `kemasan`. Laba Operasional = Laba Kotor − Opex.
- Margin Kotor (GM) = Laba Kotor ÷ Omzet. Margin Bersih (NM) = Laba Operasional ÷ Omzet.
- Arus kas: Kas Masuk = Σ `sale` + Σ `capital_in`; Kas Keluar = Σ `expense` + Σ `asset_purchase` + Σ `debt_payment`; Saldo Kas = saldo kas awal + Σ Kas Masuk − Σ Kas Keluar (sejak awal).
- Neraca: Aset = Saldo Kas + nilai stok (jumlah × harga satuan terakhir) + aset tetap (setup + `asset_purchase`, tanpa penyusutan di MVP). Utang = sisa utang setup − cicilan tercatat (minimum 0). Modal = Aset − Utang.

| ID | Fitur | User story | Acceptance Criteria (GWT) | PIC |
| --- | --- | --- | --- | --- |
| D-01 | Laporan Laba Rugi | Sebagai pemilik tanpa ilmu akuntansi, saya ingin laba rugi tersusun otomatis. | Given data periode, When memilih 7 hari, 30 hari, 90 hari, bulan kalender, atau rentang bebas, Then tampil Omzet, HPP, Laba Kotor, Opex per kategori, Laba Operasional, GM, NM, dan label metode HPP. Angka identik dengan keluaran Rule Engine (diuji golden test). | Agam |
| D-02 | Arus Kas dan Runway | Sebagai pemilik usaha, saya ingin tahu berapa bulan kas bisa bertahan. | Given data, When membuka tab Arus Kas, Then tampil Kas Masuk, Kas Keluar, arus bersih, Saldo Kas, dan Runway (3.7) satu desimal, atau "tak terhingga" jika tidak ada kas keluar. | Agam |
| D-03 | Neraca Sederhana | Sebagai pemilik usaha, saya ingin ringkasan aset, utang, dan modal. | Given setup dan transaksi, When membuka Neraca, Then Aset, Utang, dan Modal tampil per tanggal yang dipilih dan Modal = Aset − Utang. | Agam |
| D-04 | Grafik Tren | Sebagai pemilik usaha, saya ingin melihat arah omzet, biaya, dan margin. | Given data, When memilih 30 hari, 3 bulan, 6 bulan, atau 1 tahun, Then grafik omzet, pengeluaran, dan margin tampil < 1 detik dengan agregasi harian (≤ 90 hari), mingguan (≤ 6 bulan), bulanan (1 tahun) dan tetap 60 fps saat digeser. | Agam |
| D-05 | PDF Laporan Siap-Bank | Sebagai pemilik usaha, saya ingin laporan rapi untuk dibawa ke lembaga keuangan. | Given ≥ 30 hari data, When menekan Ekspor, Then PDF (< 2 MB, dibuat < 5 detik) memuat identitas usaha, periode, Laba Rugi, Arus Kas, Neraca, skor dan confidence level, asumsi metode HPP, tanggal cetak, dan disclaimer "pemandu kesiapan, bukan penilaian kelayakan kredit". Given < 30 hari, Then PDF tetap dibuat dengan label "Data belum cukup (n hari)". | Agam |

### 3.6 Modul E1: Skor Diagnosis (Kode)

Skor akhir adalah rata-rata tertimbang skor 7 indikator (masing-masing 0–100) yang datanya cukup. Indikator yang datanya belum cukup dikeluarkan dari perhitungan, bobotnya dinormalkan ulang, dan hal itu tampil di layar serta menurunkan confidence.

```latex
\text{Skor} = \operatorname{round}\left(\frac{\sum_{i \in \text{ada}} w_i S_i}{\sum_{i \in \text{ada}} w_i}\right)
```

| Indikator | Kode | Bobot w | Data minimum agar dihitung |
| --- | --- | --- | --- |
| Profitabilitas | P | 0,20 | hari\_data ≥ 14 dan Omzet > 0 |
| Arus Kas | C | 0,20 | hari\_data ≥ 14 |
| Pertumbuhan | G | 0,10 | ≥ 60 hari sejak catatan pertama, dan tiap jendela 30 hari punya hari\_data ≥ 10 |
| Efisiensi Biaya | E | 0,15 | hari\_data ≥ 14 dan Omzet > 0 |
| Disiplin Pencatatan | D | 0,15 | ≥ 7 hari sejak catatan pertama |
| Kemampuan Bayar | B | 0,10 | hari\_data ≥ 30 dan setup utang terisi (boleh "tidak ada utang") |
| Administrasi | A | 0,10 | selalu dihitung dari profil |

Bobot berjumlah 1,00. Bobot dan ambang batas adalah rancangan awal dan disimpan di tabel `scoring_config` agar dapat diubah setelah validasi ahli keuangan tanpa merilis ulang aplikasi.

| Skor | Kategori | Warna |
| --- | --- | --- |
| 0–39 | Belum Siap | Merah |
| 40–59 | Perlu Perbaikan | Oranye |
| 60–79 | Cukup Siap | Kuning |
| 80–100 | Siap Berkembang | Hijau |

**Skor sementara.** Jika jumlah indikator yang dihitung (n\_ind) < 4, skor ditandai "sementara", tidak masuk riwayat Skor Tren, dan UI menampilkan jumlah indikator yang dipakai.

**Diagnosis Awal (hari\_data = 0).** Hanya dua indikator dari profil dan setup yang dihitung, lalu dirata-rata:

```latex
S_{A0} = 100 \cdot \frac{30\,\text{NIB} + 25\,\text{Rek} + 15\,\text{Setup}}{70}, \quad S_{B0} = \operatorname{lin}(\text{DAR};\,0{,}7,\,0{,}2), \quad \text{Skor}_0 = \frac{S_{A0} + S_{B0}}{2}
```

NIB = 1 jika status NIB "punya"; Rek = 1 jika rekening usaha terpisah; Setup = 1 jika setup awal lengkap; DAR = total utang ÷ total aset dari setup.

**Confidence Level (K).**

```latex
K = 0{,}40 \cdot \min\left(1, \frac{\text{hari data}}{60}\right) + 0{,}25 \cdot R_{30} + 0{,}20 \cdot V + 0{,}15 \cdot \frac{n_{\text{ind}}}{7}
```

- R30 = hari\_data dalam 30 hari terakhir ÷ min(30, jumlah hari sejak catatan pertama + 1).
- V = Σ (nilai transaksi × bobot sumber) ÷ Σ nilai transaksi, bobot sumber seperti di 3.0.
- Level: K < 0,40 Rendah; 0,40 ≤ K < 0,70 Sedang; K ≥ 0,70 Tinggi.
- Batas keras: hari\_data < 14 maksimum Rendah; hari\_data < 30 maksimum Sedang.
- Label UI memuat level, alasan utama (komponen K terendah), dan jumlah hari, misalnya "Rendah: baru 12 hari data".

**Skor Tren Bulanan.** Pekerjaan terjadwal pada hari terakhir tiap bulan kalender pukul 23:59 waktu usaha menyimpan snapshot (skor, 7 indikator, confidence, daftar masalah) hanya jika skor bukan sementara. Bulan berjalan ditampilkan langsung; selisih terhadap bulan sebelumnya dihitung kode.

| ID | Fitur | User story | Acceptance Criteria (GWT) | PIC |
| --- | --- | --- | --- | --- |
| E1-01 | Diagnosis Awal | Sebagai pengguna baru tanpa data, saya ingin langsung melihat gambaran kondisi usaha. | Given hari\_data = 0 dan setup terisi, When membuka tab Diagnosis, Then skor sementara dari 2 indikator tampil dengan label "Rendah: belum ada data transaksi" dan ajakan mencatat transaksi pertama. Diperbarui otomatis tiap data masuk. | Rido, Agam |
| E1-02 | Business Readiness Score | Sebagai pemilik usaha, saya ingin satu angka kesiapan yang bisa saya telusuri. | Given data cukup, When membuka Diagnosis, Then skor 0–100, kategori, dan skor 7 indikator tampil; mengetuk indikator menampilkan rumus, nilai masukan, dan tanggal data. Masukan sama menghasilkan skor sama persis (golden test). | Rido, Agam |
| E1-03 | Confidence Level | Sebagai pengguna, saya ingin tahu seberapa bisa dipercaya skor saya. | Given skor tampil, When confidence dihitung, Then label level, alasan utama, dan jumlah hari tampil di dekat skor dan di PDF. Given hari\_data < 14, Then level tidak pernah lebih tinggi dari Rendah. | Rido, Agam |
| E1-04 | Skor Tren Bulanan | Sebagai pemilik usaha, saya ingin melihat kemajuan dari bulan ke bulan. | Given ≥ 2 snapshot bulanan, When membuka Skor Tren, Then grafik garis skor per bulan dengan penanda confidence tampil; skor sementara tidak muncul di grafik. | Agam |

### 3.7 Modul E2: 7 Indikator, Runway, dan Break-even (Kode)

Semua indikator memakai data usaha pada W90 kecuali dinyatakan lain. Total yang disebut "per bulan" dinormalkan ke 30 hari dengan faktor 30 ÷ hari\_W. Profitabilitas dan Efisiensi Biaya sama-sama memakai margin sehingga ada tumpang tindih; ini diterima di MVP dan menjadi bahan validasi bobot.

**P. Profitabilitas**

```latex
S_P = 0{,}6 \cdot \operatorname{lin}(NM;\,0,\,0{,}20) + 0{,}4 \cdot \operatorname{lin}(GM;\,0{,}20,\,0{,}60)
```

**C. Arus Kas**

```latex
NCF = \frac{\sum \text{sale} - \sum \text{expense} - \sum \text{debt payment}}{\sum \text{sale}}, \quad S_C = 0{,}5 \cdot \operatorname{lin}(NCF;\,-0{,}10,\,0{,}15) + 0{,}5 \cdot \operatorname{lin}(\text{Runway};\,1,\,6)
```

Jika Runway tak terhingga (tidak ada kas keluar), nilainya diperlakukan 6 bulan.

**G. Pertumbuhan**

```latex
g = \frac{\text{Omzet}_{\text{W30 terbaru}} - \text{Omzet}_{\text{W30 sebelumnya}}}{\text{Omzet}_{\text{W30 sebelumnya}}}, \quad S_G = \operatorname{lin}(g;\,-0{,}10,\,0{,}10)
```

**E. Efisiensi Biaya**

```latex
S_E = 0{,}5 \cdot \operatorname{lin}(\text{OpexRatio};\,0{,}40,\,0{,}15) + 0{,}3 \cdot \operatorname{lin}(\text{HPPRatio};\,0{,}70,\,0{,}35) + 0{,}2 \cdot \left(100 - \min(100,\,25 \cdot A_{\text{tinggi}})\right)
```

OpexRatio = Opex ÷ Omzet; HPPRatio = HPP ÷ Omzet; A\_tinggi = jumlah anomali severity Tinggi dalam 30 hari terakhir yang belum ditandai "wajar" oleh pengguna.

**D. Disiplin Pencatatan**

```latex
S_D = 0{,}6 \cdot \operatorname{lin}(R_{30};\,0{,}30,\,0{,}90) + 0{,}2 \cdot \operatorname{lin}(\text{Streak};\,0,\,14) + 0{,}2 \cdot \operatorname{lin}(\text{RasioKlasifikasi};\,0{,}5,\,1)
```

Streak = jumlah hari berurutan yang berakhir kemarin atau hari ini dengan minimal satu catatan. RasioKlasifikasi = transaksi W30 yang bertag `usaha` atau `pribadi` dan berkategori ÷ semua transaksi W30.

**B. Kemampuan Bayar**

```latex
\text{DSCR} = \frac{(\sum \text{sale} - \sum \text{expense}) \cdot 30 / \text{hari}_{W90}}{\text{CicilanBulanan}}, \quad \text{DAR} = \frac{\text{Utang}}{\text{Aset}}
```

```latex
S_B = 0{,}6 \cdot \operatorname{lin}(\text{DSCR};\,1{,}0,\,2{,}0) + 0{,}4 \cdot \operatorname{lin}(\text{DAR};\,0{,}7,\,0{,}2)
```

CicilanBulanan = jumlah cicilan bulanan utang aktif dari setup. Jika tidak ada utang, komponen DSCR bernilai 100 dan DAR = 0.

**A. Administrasi**

```latex
S_A = 30\,\text{NIB} + 25\,\text{Rek} + 15\,\text{Setup} + 30\left(1 - \operatorname{clip}\left(\frac{\text{Campur} - 0{,}02}{0{,}18}, 0, 1\right)\right)
```

Campur = pengeluaran bertag `pribadi` yang dibayar dari akun usaha ÷ seluruh pengeluaran dari akun usaha (W90).

**Runway**

```latex
\text{Runway (bulan)} = \frac{\text{SaldoKas}}{\text{BurnBulanan}}, \quad \text{BurnBulanan} = 30 \cdot \frac{\sum (\text{expense} + \text{debt payment})_W}{\text{hari}_W}
```

W = min(30 hari, hari sejak catatan pertama + 1). Pembelian aset tidak dihitung karena sekali bayar. BurnBulanan = 0 berarti Runway "tak terhingga".

**Break-even harian**

```latex
\text{BiayaTetapBulanan} = \overline{\sum \text{expense}_{\text{Tetap}}} + \text{CicilanBulanan}, \quad CMR = \frac{\text{Omzet} - \text{HPP} - \sum \text{expense}_{\text{Variabel non-HPP}}}{\text{Omzet}}
```

```latex
\text{BEP}_{\text{harian}} = \frac{\text{BiayaTetapBulanan} / 30}{CMR}, \quad \text{RasioAman} = \frac{\text{Omzet rata-rata harian (W30)}}{\text{BEP}_{\text{harian}}}
```

Garis atas pada Σ expense Tetap berarti rata-rata bulanan. Jika CMR < 0,05, BEP ditampilkan "tidak dapat dihitung: margin kontribusi terlalu tipis" dan masalah R06 tidak dipicu. Untuk usaha dengan katalog, BEP unit = (BiayaTetapBulanan ÷ 30) ÷ rata-rata Margin Rp per unit terjual (W30), ditampilkan sebagai "jual minimal N unit per hari".

| ID | Fitur | User story | Acceptance Criteria (GWT) | PIC |
| --- | --- | --- | --- | --- |
| E2-01 | 7 Indikator Diagnosis | Sebagai pemilik usaha, saya ingin tahu bagian usaha mana yang kuat dan lemah. | Given data cukup, When membuka Diagnosis, Then 7 indikator tampil sebagai skor 0–100 dengan warna kategori. Indikator yang datanya belum cukup tampil abu-abu dengan keterangan syarat data yang kurang (misal "butuh 60 hari"). | Rido, Agam |
| E2-02 | Break-even Analysis | Sebagai pemilik usaha, saya ingin tahu penjualan minimum harian agar tidak rugi. | Given biaya tetap dan margin kontribusi tersedia, When membuka Break-even, Then BEP harian (Rp), BEP unit (jika ada katalog), omzet rata-rata harian, dan RasioAman tampil; RasioAman < 1 diberi tanda peringatan. | Rido, Agam |

### 3.8 Modul E3: Deteksi Masalah dan Prioritas (Kode)

Rule Engine menjalankan 11 aturan masalah setelah setiap penulisan data (ditunda 5 detik agar tidak berulang) dan setiap malam pukul 02:00. Hasilnya disimpan di tabel `problems` dengan status `aktif`, `selesai` (kondisi tidak terpenuhi selama 7 hari berturut-turut), atau `diabaikan` (disembunyikan pengguna 30 hari). Ambang batas disimpan di `rule_config`.

| ID | Masalah | Kondisi pemicu | Severity | Dampak | Kemudahan (1–5) |
| --- | --- | --- | --- | --- | --- |
| R01 | Margin turun | NM akhir − NM awal ≤ −0,04 (poin persentase). Jika data ≥ 90 hari: W30 terbaru dibanding W30 pada hari 61–90. Jika data 21–89 hari: paruh terbaru dibanding paruh pertama (masing-masing hari\_data ≥ 10). | Sedang ≤ −0,04; Tinggi ≤ −0,08 | Rp: selisih NM × Omzet bulanan | 3 |
| R02 | Biaya bahan terkonsentrasi | bahan\_baku ÷ seluruh pengeluaran (W30) | Sedang ≥ 0,70; Tinggi ≥ 0,80 | Rp: 0,05 × pengeluaran bahan baku bulanan (asumsi potensi hemat 5%) | 3 |
| R03 | Uang pribadi tercampur | Campur (3.7) > 0,10 | Sedang > 0,10; Tinggi > 0,25 | Tetap 3 | 4 |
| R04 | Rekening usaha belum terpisah | Profil: rekening terpisah = tidak | Sedang | Tetap 3 | 4 |
| R05 | Runway pendek | Runway < 2 bulan | Sedang < 2; Tinggi < 1 | Tetap 4 (Sedang) atau 5 (Tinggi) | 2 |
| R06 | Di bawah break-even | RasioAman < 1 | Sedang < 1,0; Tinggi < 0,8 | Rp: (BEP harian − omzet rata-rata harian) × 30 × CMR | 2 |
| R07 | Kemampuan bayar rendah | DSCR < 1,25 (hanya jika ada cicilan) | Sedang < 1,25; Tinggi < 1,0 | Tetap 4 | 2 |
| R08 | Disiplin pencatatan rendah | R30 < 0,50 | Sedang < 0,50; Tinggi < 0,30 | Tetap 3 | 5 |
| R09 | NIB belum ada | Status NIB = belum | Sedang | Tetap 2 | 3 |
| R10 | Omzet turun | g ≤ −0,10 | Sedang ≤ −0,10; Tinggi ≤ −0,20 | Rp: ABS(selisih omzet W30) × CMR | 2 |
| R11 | Produk margin rendah | Produk dengan Margin % < 20% yang menyumbang ≥ 30% omzet | Sedang; Tinggi jika Margin % ≤ 0 | Rp: Σ omzet produk × (0,20 − Margin % produk) | 4 |

**Skor Dampak (1–5).** Untuk aturan berdampak Rp, Rasio = dampak Rp per bulan ÷ Omzet bulanan. Rasio ≥ 0,10 menjadi 5; ≥ 0,05 menjadi 4; ≥ 0,02 menjadi 3; ≥ 0,005 menjadi 2; selain itu 1. Aturan berdampak tetap memakai nilai di tabel.

```latex
\text{Prioritas} = \text{Dampak} \times \text{Kemudahan} \quad (1\ \text{sampai}\ 25)
```

Urutan: Prioritas menurun, lalu severity (Tinggi lebih dulu), lalu Dampak menurun, lalu ID menaik. Action Plan mengambil maksimal 5 masalah teratas; target selesai ditetapkan kode: peringkat 1–2 dalam 2 minggu, peringkat 3–5 dalam 4 minggu.

| ID | Fitur | User story | Acceptance Criteria (GWT) | PIC |
| --- | --- | --- | --- | --- |
| E3-01 | Deteksi Masalah | Sebagai pemilik usaha, saya ingin tahu masalah bisnis saya dalam kalimat jelas. | Given data memicu aturan, When Rule Engine selesai, Then kartu masalah tampil dengan judul, angka pemicu (misal "margin turun 8 poin dalam 2 bulan"), severity, dan tombol "Jadikan langkah". Given data tidak memicu aturan apa pun, Then layar menampilkan "Belum ada masalah terdeteksi" bersama label confidence. | Rido, Agam |
| E3-03 | Prioritas Perbaikan | Sebagai pemilik usaha, saya ingin tahu mana yang harus diperbaiki lebih dulu. | Given ≥ 2 masalah aktif, When membuka Prioritas, Then daftar terurut menurut rumus Prioritas dengan skor Dampak dan Kemudahan terlihat; urutan sama untuk masukan sama. | Rido, Agam |

### 3.9 Deteksi Anomali dan Duplikat (Kode)

| ID | Anomali | Kondisi pemicu | Severity |
| --- | --- | --- | --- |
| A01 | Lonjakan pengeluaran kategori | Rasio7 = pengeluaran kategori k selama 7 hari terakhir ÷ rata-rata pengeluaran 7 harian kategori itu pada 4 minggu sebelumnya. Syarat: hari\_data ≥ 21 dan rata-rata > 0. | Sedang ≥ 1,5; Tinggi ≥ 2,0 |
| A02 | Kenaikan harga bahan | Kenaikan = harga satuan item pada struk baru ÷ median harga satuan 3 pembelian terakhir item itu − 1. Syarat: ≥ 2 pembelian sebelumnya. | Sedang ≥ 0,15; Tinggi ≥ 0,30 |

Item dicocokkan antarstruk lewat nama yang dinormalisasi (huruf kecil, angka ukuran dan kata umum dibuang). Cocok jika kemiripan trigram ≥ 0,6 atau item sudah dipetakan manual ke tabel `item_master` pada layar Konfirmasi. Pengguna dapat menandai anomali "wajar" (tidak dihitung di A\_tinggi) atau "salah catat" (membuka transaksi untuk dikoreksi).

**Aturan duplikat struk**

- Keras: kemiripan nama toko ≥ 0,85 dan tanggal sama dan total sama; atau jarak Hamming perceptual hash gambar ≤ 6 bit.
- Lunak: kemiripan nama toko ≥ 0,85 dan total sama dan selisih tanggal ≤ 1 hari.
- Impor mutasi: baris dianggap duplikat jika hash dari (tanggal, nominal, arah debit atau kredit, deskripsi ternormalisasi) sudah ada.

| ID | Fitur | User story | Acceptance Criteria (GWT) | PIC |
| --- | --- | --- | --- | --- |
| E3-02 | Deteksi Anomali | Sebagai pemilik usaha, saya ingin diperingatkan jika biaya atau harga bahan melonjak. | Given struk baru dikonfirmasi, When harga satuan item naik ≥ 15% dari median 3 pembelian terakhir, Then notifikasi dan kartu anomali tampil dengan harga lama, harga baru, dan toko. Given pengeluaran kategori 7 hari naik ≥ 1,5 kali rata-rata, Then kartu anomali kategori tampil. Anomali yang ditandai "wajar" tidak muncul lagi untuk kejadian itu. | Rido, Agam |

### 3.10 Modul F: Fitur AI (IMPROVE dan GROW)

Pembagian tugas: Rule Engine menghasilkan semua angka, rentang, urutan, dan target waktu; AI hanya menyusun kalimat dan langkah dari angka itu (kontrak JSON di Bab 4).

**Proyeksi Modal Berentang (dihitung kode).** Masukan pengguna: tujuan (`tambah_alat`, `buka_cabang`, `tambah_stok`), Investasi\_min, dan Investasi\_maks dalam Rupiah.

```latex
MK_{\min} = 1 \cdot \text{BurnBulanan}, \quad MK_{\max} = 2 \cdot \text{BurnBulanan}
```

```latex
\text{Kebutuhan}_{\min} = 1{,}10 \cdot (\text{Investasi}_{\min} + MK_{\min}), \quad \text{Kebutuhan}_{\max} = 1{,}10 \cdot (\text{Investasi}_{\max} + MK_{\max})
```

```latex
u_{\text{rendah}} = \operatorname{clip}(0{,}5\,g_m;\,0{,}02,\,0{,}15), \quad u_{\text{tinggi}} = \operatorname{clip}(1{,}5\,g_m;\,0{,}05,\,0{,}30), \quad \Delta K_x = \text{Omzet}_{W30} \cdot u_x \cdot CMR
```

```latex
\text{Payback (bulan)} = \left[\frac{\text{Investasi}_{\min}}{\Delta K_{\text{tinggi}}},\ \frac{\text{Investasi}_{\max}}{\Delta K_{\text{rendah}}}\right]
```

- MK = modal kerja (1 sampai 2 bulan pengeluaran) dan 1,10 adalah cadangan 10%.
- g\_m = rata-rata pertumbuhan omzet bulanan (g di 3.7) dari maksimal 3 jendela 30 hari terakhir; u = asumsi kenaikan omzet bulanan setelah investasi.
- Asumsi u, MK, dan cadangan tampil di layar dan dapat diubah pengguna; hasil dihitung ulang oleh kode, bukan AI.
- Jika CMR ≤ 0 atau g\_m < 0, payback ditampilkan "tidak dapat dihitung" atau disertai peringatan tren turun.
- Rentang ini perkiraan berbasis data usaha sendiri, bukan jaminan pembiayaan. Bobot dan asumsi menunggu validasi ahli keuangan atau pendamping UMKM.

**Kartu Action Plan.** Atribut: `problem_id` (satu masalah per kartu), judul, deskripsi langkah, peringkat (dari 3.8), `target_date` (dari target minggu yang ditetapkan kode), status (`belum_mulai`, `dikerjakan`, `selesai`, `dilewati`), dan `terverifikasi_data` (menjadi benar otomatis jika masalah terkait berstatus `selesai` menurut data).

| ID | Fitur | User story | Acceptance Criteria (GWT) | PIC |
| --- | --- | --- | --- | --- |
| F-01 | Analisis Keuangan Naratif | Sebagai pemilik tanpa ilmu akuntansi, saya ingin tahu mengapa angka naik atau turun dalam bahasa sehari-hari. | Given laporan periode, When membuka "Penjelasan", Then narasi ≤ 120 kata tampil dan semua angkanya lolos validator numerik (Bab 4). Given validator gagal atau persetujuan AI tidak diberikan, Then template tetap berbasis angka kode tampil dengan label "penjelasan otomatis sederhana". | Febri, Agam |
| F-02 | AI Konsultasi (chat) | Sebagai pemilik usaha, saya ingin bertanya soal data usaha dan dijawab spesifik. | Given pertanyaan "Kenapa untung bulan ini turun?", When dikirim, Then jawaban memakai ringkasan data usaha (bukan data mentah), menyebut periode dan angka rujukan, dan selesai < 10 detik (p95). Given pertanyaan di luar keuangan usaha atau meminta kepastian kredit, hukum, atau pajak, Then AI menolak sopan dan mengarahkan ke ahli. | Febri, Said, Rido |
| F-03 | Action Plan | Sebagai pemilik usaha, saya ingin langkah perbaikan yang jelas dan bertahap. | Given masalah aktif dari kode, When membuka Action Plan, Then maksimal 5 kartu tampil terurut peringkat, masing-masing dengan target tanggal dan status yang dapat diubah. Given masalah terkait selesai menurut data, Then kartu bertanda "terverifikasi data". | Febri, Said, Rido |
| F-04 | Growth Planner | Sebagai pemilik usaha, saya ingin rencana bertahap untuk tujuan pengembangan saya. | Given ≥ 30 hari data, When memilih tujuan dan mengisi kisaran investasi, Then rencana 3 tahap (persiapan minggu 1–4, eksekusi minggu 5–8, evaluasi minggu 9–12) tampil dengan rentang modal dan asumsi. Given gerbang kesiapan (2.3) belum terpenuhi, Then banner "Belum disarankan: selesaikan dulu langkah perbaikan" tampil di atas rencana. | Agam, Febri |
| F-05 | Proyeksi Modal Berentang | Sebagai pemilik usaha, saya ingin tahu kisaran modal yang dibutuhkan, bukan satu angka palsu. | Given tujuan dan kisaran investasi, When dihitung, Then kebutuhan modal tampil sebagai rentang Rp minimum sampai maksimum beserta asumsi yang dapat diubah dan teks "Rentang ini perkiraan, bukan jaminan pembiayaan". | Rido, Agam |

## 4. Arsitektur AI & Kontrak JSON

AI hanya dipanggil lewat satu lapisan layanan (AI Gateway) dan hanya menerima angka yang sudah dihitung Rule Engine. Bab ini menetapkan kontrak JSON antara kode Rido dan modul AI Febri untuk lima tugas: Struk, Naratif, Action Plan, Konsultasi, dan Growth Planner, beserta guardrails anti-halusinasi.

### 4.1 Alur Panggilan AI

1. **Rule Engine (Rido)** menghitung angka dan membangun objek `facts` lewat builder berversi yang dijaga golden test.
2. **Pra-pemeriksaan (Febri)**: cek persetujuan AI (A-03), batas pemakaian, penghapusan data pribadi (nama pengguna, email, NIB, nomor rekening, dan alamat tidak pernah masuk `facts`), dan batas ukuran masukan 6 KB teks.
3. **AI Gateway** memilih penyedia dari konfigurasi (`AI_PROVIDER` bernilai `openai` atau `gemini`; `OCR_PROVIDER` bernilai `vision` atau `ocr_service`), memanggil dengan prompt berversi, suhu ≤ 0,2, batas keluaran 600 token, dan timeout 8 detik (OCR 6 detik tanpa pengulangan).
4. **Validasi skema**: keluaran diparse dan dicek dengan JSON Schema ketat; jika tidak valid, satu kali perbaikan otomatis.
5. **Validator numerik dan lingkup** (4.4).
6. **Lolos**: respons dikirim ke klien. **Gagal**: template tetap dikirim dan kejadian dicatat di tabel `ai_events`.

Antarmuka penyedia hanya dua metode sehingga model dapat diganti tanpa mengubah UI maupun aturan skor: `extractReceipt(image, hints)` yang mengembalikan JSON struk, dan `generate(task, facts, promptVersion)` yang mengembalikan JSON tugas. Setiap kontrak punya JSON Schema di `contracts/ai/` yang diverifikasi di CI: Rido memvalidasi keluaran builder, Febri memvalidasi masukan dan keluaran gateway.

### 4.2 Amplop dan Aturan Umum

```json
{
  "request_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "task": "narrative",
  "schema_version": "1.0",
  "locale": "id-ID"
}
```

- Nilai uang berupa bilangan bulat Rupiah. Setiap fakta memuat `value` (angka mentah) dan `display` (teks Indonesia siap pakai, misal "Rp18.450.000" atau "11,2%"). AI wajib menyalin `display` apa adanya dan dilarang menghitung selisih, rasio, atau total sendiri; selisih sudah disediakan kode.
- Pengguna dan bisnis tidak diidentifikasi dalam JSON. Tidak ada nama, email, NIB, nomor rekening, atau alamat.
- Perubahan yang merusak kontrak menaikkan `schema_version` dan harus lolos contract test sebelum digabung.
- Galat memakai amplop: `{"status":"error","code":"AI_VALIDATION_FAILED","fallback_used":true,"message":"..."}`. Kode galat: `AI_CONSENT_REQUIRED` (403), `AI_RATE_LIMIT` (429), `AI_TIMEOUT` (504), `AI_SCHEMA_INVALID` (502), `AI_VALIDATION_FAILED` (502), `AI_OUT_OF_SCOPE` (200 dengan `scope` = `out_of_scope`).

### 4.3 Kontrak Lima Tugas AI

**Tugas 1: Baca Struk.** Masukan: gambar JPEG ≤ 1,5 MB dan petunjuk (daftar kategori sah). Keluaran dari AI; setiap kolom membawa `confidence` 0–1; kolom dengan nilai kosong memakai `value: null` dan `confidence: 0`. Kode (bukan AI) kemudian memeriksa jumlah subtotal terhadap total dan format tanggal.

```json
{
  "request_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "merchant": {"value": "Toko Sumber Rejeki", "confidence": 0.93},
  "date": {"value": "2026-11-05", "confidence": 0.88},
  "items": [
    {
      "name": {"value": "Susu UHT 1L", "confidence": 0.90},
      "qty": {"value": 12, "confidence": 0.95},
      "unit_price": {"value": 18500, "confidence": 0.91},
      "subtotal": {"value": 222000, "confidence": 0.90},
      "suggested_category": "bahan_baku",
      "category_confidence": 0.82
    }
  ],
  "total": {"value": 222000, "confidence": 0.96},
  "image_quality": {"readable": true, "blur_score": 0.12},
  "model": {"provider": "openai", "latency_ms": 2100}
}
```

**Tugas 2: Analisis Naratif.** Masukan dari kode: periode, confidence, fakta (termasuk selisih yang sudah dihitung), dan masalah terdeteksi.

```json
{
  "request_id": "0b7e0c52-6f0e-4a54-9a1f-3a3a2d5d8c10",
  "task": "narrative",
  "schema_version": "1.0",
  "locale": "id-ID",
  "period": {"start": "2026-10-01", "end": "2026-10-31", "label": "Oktober 2026"},
  "confidence": {"level": "Tinggi", "hari_data": 74, "display": "Tinggi: 74 hari data"},
  "facts": {
    "omzet": {"value": 18450000, "display": "Rp18.450.000"},
    "omzet_prev": {"value": 19200000, "display": "Rp19.200.000"},
    "omzet_delta": {"value": -3.9, "display": "3,9%"},
    "nm": {"value": 0.112, "display": "11,2%"},
    "nm_prev": {"value": 0.196, "display": "19,6%"},
    "nm_delta": {"value": -8.4, "display": "8,4 poin persentase"}
  },
  "problems": [
    {"rule_id": "R01", "title": "Margin turun", "severity": "Tinggi", "fact_refs": ["nm_prev", "nm", "nm_delta"]}
  ]
}
```

Keluaran AI:

```json
{
  "narrative": "Omzet Oktober Rp18.450.000, turun 3,9% dari bulan lalu (Rp19.200.000). Margin bersih menyusut dari 19,6% menjadi 11,2%, turun 8,4 poin persentase, sehingga laba turun lebih tajam daripada omzet.",
  "highlights": [
    {"text": "Margin bersih turun 8,4 poin persentase", "fact_refs": ["nm_prev", "nm", "nm_delta"]}
  ],
  "caveat": "Keyakinan Tinggi: 74 hari data."
}
```

**Tugas 3: Action Plan.** Masukan: masalah yang sudah diurutkan dan diberi target waktu oleh kode. AI hanya menulis judul, langkah, dan alasan; AI tidak boleh mengubah peringkat, target, atau menambah masalah.

```json
{
  "task": "action_plan",
  "schema_version": "1.0",
  "locale": "id-ID",
  "constraints": {"max_cards": 5, "max_steps_per_card": 3, "max_title_chars": 60},
  "problems": [
    {
      "problem_id": "p_01", "rule_id": "R04", "title": "Rekening usaha belum terpisah",
      "severity": "Sedang", "rank": 1, "target_weeks": 2,
      "facts": {"campur": {"value": 0.18, "display": "18%"}}
    },
    {
      "problem_id": "p_02", "rule_id": "R11", "title": "Produk margin rendah",
      "severity": "Sedang", "rank": 2, "target_weeks": 2,
      "facts": {
        "produk": {"value": "Produk A", "display": "Produk A"},
        "margin_produk": {"value": 0.14, "display": "14%"},
        "target_margin": {"value": 0.20, "display": "20%"}
      }
    }
  ]
}
```

```json
{
  "cards": [
    {
      "problem_id": "p_01",
      "title": "Buka rekening khusus usaha",
      "steps": ["Siapkan KTP dan dokumen usaha lalu pilih bank", "Arahkan penerimaan QRIS ke rekening itu", "Bayar belanja usaha hanya dari rekening itu"],
      "why": "Sebanyak 18% pengeluaran tercatat bercampur dengan keperluan pribadi.",
      "fact_refs": ["campur"]
    },
    {
      "problem_id": "p_02",
      "title": "Naikkan harga Produk A",
      "steps": ["Hitung harga jual agar margin mencapai 20%", "Uji harga baru selama 2 minggu dan catat penjualannya"],
      "why": "Margin Produk A baru 14%, di bawah target 20%.",
      "fact_refs": ["margin_produk", "target_margin"]
    }
  ]
}
```

**Tugas 4: AI Konsultasi.** Masukan: pertanyaan bebas, riwayat maksimal 6 giliran terakhir, dan ringkasan data (bukan data mentah). MVP tidak streaming sehingga seluruh jawaban dapat divalidasi sebelum tampil.

```json
{
  "task": "consult",
  "schema_version": "1.0",
  "locale": "id-ID",
  "question": "Kenapa untung bulan ini turun?",
  "history": [],
  "allowed_scope": ["laporan", "skor", "masalah", "katalog", "stok", "growth_planner"],
  "snapshot": {
    "period": {"start": "2026-10-01", "end": "2026-10-31", "label": "Oktober 2026"},
    "confidence": {"level": "Tinggi", "hari_data": 74, "display": "Tinggi: 74 hari data"},
    "score": {"value": 72, "category": "Cukup Siap", "display": "72"},
    "facts": {
      "nm": {"value": 0.112, "display": "11,2%"},
      "nm_prev": {"value": 0.196, "display": "19,6%"},
      "nm_delta": {"value": -8.4, "display": "8,4 poin persentase"}
    },
    "problems": [{"rule_id": "R01", "title": "Margin turun", "severity": "Tinggi", "fact_refs": ["nm_prev", "nm", "nm_delta"]}]
  }
}
```

```json
{
  "scope": "in_scope",
  "answer": "Untung turun terutama karena margin bersih menyusut dari 19,6% menjadi 11,2%, turun 8,4 poin persentase, pada Oktober 2026.",
  "fact_refs": ["nm_prev", "nm", "nm_delta"],
  "refusal_reason": null
}
```

**Tugas 5: Growth Planner.** Masukan: tujuan, status gerbang, hasil hitung kode (rentang modal, payback, asumsi), dan kerangka tahap dari kode. AI hanya menyusun isi tiap tahap.

```json
{
  "task": "growth_plan",
  "schema_version": "1.0",
  "locale": "id-ID",
  "goal": "tambah_alat",
  "gate": {"met": true, "skor_min": {"value": 75, "display": "75"}},
  "computed": {
    "investasi_min": {"value": 8000000, "display": "Rp8.000.000"},
    "investasi_maks": {"value": 12000000, "display": "Rp12.000.000"},
    "kebutuhan_min": {"value": 26840000, "display": "Rp26.840.000"},
    "kebutuhan_maks": {"value": 49280000, "display": "Rp49.280.000"},
    "payback_min": {"value": 12.1, "display": "12,1 bulan"},
    "payback_maks": {"value": 54.4, "display": "54,4 bulan"},
    "modal_kerja_bulan": {"value": "1 sampai 2", "display": "1 sampai 2 bulan pengeluaran"}
  },
  "stage_template": [
    {"tahap": 1, "minggu": "1-4", "label": "Persiapan"},
    {"tahap": 2, "minggu": "5-8", "label": "Eksekusi"},
    {"tahap": 3, "minggu": "9-12", "label": "Evaluasi"}
  ]
}
```

```json
{
  "ringkasan": "Menambah alat membutuhkan modal Rp26.840.000 sampai Rp49.280.000 dengan perkiraan balik modal 12,1 sampai 54,4 bulan.",
  "stages": [
    {"tahap": 1, "minggu": "1-4", "tujuan": "Menyiapkan dana dan menjaga margin tetap stabil", "aktivitas": ["Bandingkan tiga penawaran alat", "Sisihkan modal kerja 1 sampai 2 bulan pengeluaran"], "indikator_keberhasilan": "Skor tetap di atas 75", "fact_refs": ["modal_kerja_bulan", "gate.skor_min"]},
    {"tahap": 2, "minggu": "5-8", "tujuan": "Membeli dan memasang alat", "aktivitas": ["Catat pembelian alat dengan struk", "Perbarui katalog dan HPP produk baru"], "indikator_keberhasilan": "Pembelian tercatat dan HPP produk diperbarui", "fact_refs": ["investasi_min", "investasi_maks"]},
    {"tahap": 3, "minggu": "9-12", "tujuan": "Mengevaluasi dampak alat", "aktivitas": ["Bandingkan omzet dan margin sebelum dan sesudah alat", "Perbarui rentang balik modal"], "indikator_keberhasilan": "Omzet naik dan margin tidak turun", "fact_refs": ["payback_min", "payback_maks"]}
  ],
  "caveat": "Rentang ini perkiraan, bukan jaminan pembiayaan."
}
```

### 4.4 Guardrails Anti-Halusinasi

| Kode | Guardrail | Mekanisme | Pemilik | Bukti uji |
| --- | --- | --- | --- | --- |
| G1 | Angka hanya dari kode | Semua angka masuk lewat `facts` dengan `display` siap pakai; AI dilarang menghitung. | Rido, Febri | Contract test builder |
| G2 | Validator numerik | Semua angka (termasuk persen dan "juta" atau "ribu") di teks keluaran diekstrak, dinormalkan, lalu dicocokkan dengan himpunan `display` dan `value` dari masukan ditambah angka yang ditulis pengguna di pertanyaannya. Angka di luar himpunan menggagalkan respons. | Febri | Suite CI 300 skenario, 0 pelanggaran (K5) |
| G3 | Skema ketat | JSON Schema; satu kali perbaikan otomatis; kolom tidak dikenal ditolak. | Febri | Uji skema per tugas |
| G4 | Rujukan fakta | Setiap kalimat inti memuat `fact_refs` yang harus ada di masukan. | Febri | Uji referensi |
| G5 | Lingkup dan penolakan | Hanya topik di `allowed_scope`; menolak kepastian kredit, saran hukum, saran pajak, dan permintaan mengabaikan aturan. | Febri | 40 prompt uji penolakan |
| G6 | Anti prompt-injection | Teks struk dan pertanyaan pengguna diperlakukan sebagai data, bukan perintah; AI tidak memiliki alat atau akses basis data; instruksi sistem terpisah. | Febri | 20 struk dan pesan uji berisi perintah tersembunyi |
| G7 | Fallback tetap | Jika G2 atau G3 gagal dua kali, template tetap berbasis `display` ditampilkan dengan label "penjelasan otomatis sederhana". | Febri, Said | Uji UI fallback |
| G8 | Determinisme | Suhu ≤ 0,2; prompt dan model berversi; narasi di-cache per (usaha, periode, versi data). | Febri | Uji regresi prompt |
| G9 | Minimisasi data | Tanpa data pribadi di JSON; hanya agregat dan nama produk atau kategori; gambar struk hanya untuk tugas 1. | Rido, Febri | Daftar periksa UU PDP |

Pelanggaran G2 dicatat sebagai `ai_events` bertipe `numeric_violation` dengan hash prompt (bukan isi pesan). Audit manual 50 respons per minggu menjadi bukti K5.

### 4.5 Penanganan Kegagalan dan Biaya

| Kondisi | Perilaku |
| --- | --- |
| Persetujuan AI tidak diberikan | `AI_CONSENT_REQUIRED`; fitur AI tersembunyi, template tetap dipakai, laporan dan skor tetap berjalan. |
| Timeout atau penyedia gagal | Satu pengulangan untuk tugas teks (tidak untuk OCR); jika tetap gagal, fallback tetap; OCR menawarkan "Ulangi" atau "Isi manual". |
| Skema tidak valid atau validator gagal | Satu perbaikan otomatis, lalu fallback tetap. |
| Batas pemakaian | 30 pesan chat per pengguna per hari dan 100 pindai struk per usaha per hari; melebihi itu `AI_RATE_LIMIT`. |
| Biaya | Narasi dan Action Plan di-cache per versi data; chat hanya menerima ringkasan; model dipilih per tugas lewat konfigurasi; semua panggilan mencatat jumlah token dan biaya di `ai_events`. |

## 5. Database & REST API

PostgreSQL menyimpan data relasional; semua tabel milik usaha memiliki `business_id` dan dilindungi Row-Level Security berdasarkan klaim JWT. Rido memiliki skema dan API; Febri memegang kontrak Swagger (OpenAPI 3).

### 5.1 Skema PostgreSQL

Konvensi: kunci primer `id` bertipe UUID; uang BIGINT (Rupiah); tanggal transaksi DATE; semua tabel punya `created_at` dan `updated_at`; penghapusan data transaksi memakai `deleted_at` (soft delete). Kolom sensitif (`receipts.ocr_json`, `import_rows.description`, `chat_messages.content`) dienkripsi tingkat aplikasi dengan AES-256-GCM sebelum disimpan, kunci dari secret manager; gambar struk disimpan terenkripsi di object storage.

**Akun dan profil**

| Tabel | Kolom penting (PK, FK, tipe) | Catatan |
| --- | --- | --- |
| users | id PK; email UNIQUE; password\_hash (argon2id); deleted\_at | Satu pengguna memiliki satu usaha di MVP. |
| consents | id PK; user\_id FK → users; type (financial\_processing, ai\_processing); version; granted BOOLEAN | Riwayat persetujuan, tidak pernah ditimpa. |
| refresh\_tokens | id PK; user\_id FK → users; token\_hash; expires\_at; revoked\_at | Rotasi token tiap refresh. |
| businesses | id PK; user\_id FK → users UNIQUE; name; jenis\_usaha; lama\_usaha\_bulan INT; jumlah\_karyawan INT; nib\_status (punya, proses, belum); rekening\_terpisah BOOLEAN; modal\_awal BIGINT; setup\_complete BOOLEAN; timezone; data\_version BIGINT | data\_version naik tiap penulisan data, dipakai untuk cache AI dan hitung ulang. |
| accounts | id PK; business\_id FK → businesses; name; kind (kas, rekening, qris); is\_business BOOLEAN; opening\_balance BIGINT | Saldo kas awal = opening\_balance akun usaha. |
| setup\_assets | id PK; business\_id FK; name; value BIGINT | Aset tetap awal. |
| setup\_debts | id PK; business\_id FK; creditor; remaining BIGINT; monthly\_installment BIGINT; active BOOLEAN | Dasar CicilanBulanan dan DAR. |

**Transaksi dan input**

| Tabel | Kolom penting (PK, FK, tipe) | Catatan |
| --- | --- | --- |
| categories | code PK; name; kelompok (hpp, operasional); sifat (tetap, variabel) | 10 baris seed (3.0). |
| transactions | id PK; business\_id FK; account\_id FK → accounts; type (sale, expense, capital\_in, asset\_purchase, debt\_payment); category\_code FK → categories NULL; amount BIGINT CHECK > 0; occurred\_on DATE; tag (usaha, pribadi, belum\_ditag); source (receipt, bank\_import, quick\_sale, manual, daily\_recap); receipt\_id FK NULL; import\_row\_id FK NULL; client\_uuid; deleted\_at | UNIQUE (business\_id, client\_uuid) untuk idempotensi antrean offline. Indeks (business\_id, occurred\_on) dan (business\_id, tag). |
| transaction\_items | id PK; transaction\_id FK; product\_id FK NULL; item\_master\_id FK NULL; name; qty NUMERIC(12,3); unit\_price BIGINT; subtotal BIGINT; hpp\_snapshot BIGINT NULL | Baris penjualan (produk) dan baris struk (bahan). |
| receipts | id PK; business\_id FK; image\_key; image\_phash BIGINT; merchant; merchant\_norm; receipt\_date DATE; total BIGINT; ocr\_json JSONB; status (scanned, confirmed, discarded); duplicate\_of FK → receipts NULL; confirmed\_at; image\_deleted\_at | Gambar dihapus 30 hari setelah konfirmasi. Indeks (business\_id, receipt\_date, total). |
| imports | id PK; business\_id FK; filename; row\_count INT; status (preview, committed) | Satu baris per unggahan CSV. |
| import\_rows | id PK; import\_id FK → imports; row\_hash; occurred\_on; description; direction (debit, kredit); amount BIGINT; match\_status (cocok, belum\_tercatat, duplikat); transaction\_id FK NULL | UNIQUE (import\_id, row\_hash). |
| daily\_recaps | id PK; business\_id FK; recap\_date DATE; total BIGINT; transaction\_id FK | UNIQUE (business\_id, recap\_date). |
| streaks | business\_id PK dan FK; current INT; longest INT; last\_logged\_on DATE | Diperbarui tiap penulisan data. |
| daily\_aggregates | business\_id FK; day DATE; sales BIGINT; expense\_by\_category JSONB; cash\_in BIGINT; cash\_out BIGINT; tx\_count INT; PK (business\_id, day) | Agregat harian agar laporan memenuhi p95 < 1,5 detik. |

**Katalog dan stok**

| Tabel | Kolom penting (PK, FK, tipe) | Catatan |
| --- | --- | --- |
| products | id PK; business\_id FK; name; price BIGINT; kemasan\_cost BIGINT; active BOOLEAN | HPP dan margin dihitung kode, tidak disimpan permanen. |
| item\_master | id PK; business\_id FK; canonical\_name; unit; last\_unit\_price BIGINT; stock\_qty NUMERIC(12,3); min\_stock NUMERIC NULL; category\_code FK | Bahan dan barang dagang. |
| item\_aliases | id PK; item\_master\_id FK; alias\_norm; source (auto, manual) | Dasar pencocokan nama antarstruk (3.9). |
| recipes | id PK; product\_id FK → products; item\_master\_id FK → item\_master; qty\_per\_unit NUMERIC(12,4) | UNIQUE (product\_id, item\_master\_id). |
| price\_history | id PK; item\_master\_id FK; receipt\_id FK; unit\_price BIGINT; occurred\_on DATE | Sumber deteksi anomali A02. |
| stock\_movements | id PK; item\_master\_id FK; delta NUMERIC; reason (opening, purchase, sale, adjust); transaction\_id FK NULL; occurred\_on DATE | Saldo stok = jumlah delta. |

**Hasil Rule Engine, AI, dan audit**

| Tabel | Kolom penting (PK, FK, tipe) | Catatan |
| --- | --- | --- |
| scoring\_config | key PK; value JSONB; version INT | Bobot, ambang batas, dan batas data minimum (3.6, 3.7). |
| rule\_config | rule\_id PK; params JSONB; kemudahan SMALLINT; enabled BOOLEAN | R01 sampai R11 dan A01, A02 (3.8, 3.9). |
| score\_runs | id PK; business\_id FK; data\_version BIGINT; score INT; is\_provisional BOOLEAN; confidence\_k NUMERIC(4,3); confidence\_level; hari\_data INT; n\_ind INT; indicators JSONB | Satu baris per hitung ulang; masukan dan keluaran tiap indikator tersimpan agar dapat ditelusuri. |
| score\_snapshots | id PK; business\_id FK; month DATE; score\_run\_id FK → score\_runs | UNIQUE (business\_id, month); hanya skor non-sementara. |
| problems | id PK; business\_id FK; rule\_id FK → rule\_config; severity; dampak SMALLINT; kemudahan SMALLINT; priority SMALLINT; rank SMALLINT; trigger\_value NUMERIC; facts JSONB; status (aktif, selesai, diabaikan); first\_seen\_at; resolved\_at; snoozed\_until | Dihasilkan Rule Engine. |
| anomalies | id PK; business\_id FK; code (A01, A02); severity; transaction\_id FK NULL; receipt\_id FK NULL; item\_master\_id FK NULL; facts JSONB; status (baru, wajar, salah\_catat) |  |
| action\_cards | id PK; business\_id FK; problem\_id FK → problems; title; steps JSONB; why TEXT; rank SMALLINT; target\_date DATE; status (belum\_mulai, dikerjakan, selesai, dilewati); verified\_by\_data BOOLEAN | Peringkat dan tanggal dari kode, teks dari AI. |
| growth\_plans | id PK; business\_id FK; goal; investasi\_min BIGINT; investasi\_maks BIGINT; assumptions JSONB; computed JSONB; ai\_output JSONB; gate\_met BOOLEAN |  |
| chat\_messages | id PK; business\_id FK; role (user, assistant); content TEXT; scope | Dihapus otomatis setelah 90 hari. |
| ai\_events | id PK; business\_id FK; task; provider; model; prompt\_version; status (ok, fallback, error); error\_code; latency\_ms INT; tokens\_in INT; tokens\_out INT; cost\_micro\_usd BIGINT; prompt\_hash; violations JSONB | Bahan K1, K5, dan kontrol biaya. |
| audit\_logs | id PK; user\_id FK → users; action; entity; entity\_id; ip; created\_at | Akses dan perubahan data sensitif. |

### 5.2 Konvensi REST API

- Dasar URL `/api/v1`, JSON UTF-8, autentikasi `Authorization: Bearer <access token>`. Dokumentasi OpenAPI di `/docs`, dihasilkan dari kontrak yang dijaga Febri.
- Penulisan idempoten lewat `client_uuid` (antrean offline aman diulang). Daftar memakai paginasi kursor `cursor` dan `limit` (maks 100).
- Galat: `{"error": {"code": "...", "message": "...", "fields": {}}}` dengan status 400, 401, 403, 404, 409 (konflik atau duplikat), 422 (validasi), 429 (batas laju), 5xx.
- Batas laju: 120 permintaan per menit per pengguna untuk endpoint non-AI; batas AI di 4.5.
- Setiap penulisan data menaikkan `businesses.data_version` dan memicu hitung ulang Rule Engine (ditunda 5 detik); respons penulisan memuat `meta.data_version`.

### 5.3 Daftar Endpoint Utama

**Akun, profil, dan setup**

| Method | URL | Payload | Response |
| --- | --- | --- | --- |
| POST | /auth/register | email, password, consents\[\] (type, version, granted) | 201: user\_id |
| POST | /auth/login | email, password | 200: access\_token, refresh\_token, expires\_in |
| POST | /auth/refresh | refresh\_token | 200: access\_token, refresh\_token baru |
| POST | /auth/logout | refresh\_token | 204 |
| GET | /me | - | 200: user, business, consents |
| PUT | /me/consents | type, version, granted | 200: consents |
| POST | /me/export | - | 202: job\_id |
| DELETE | /me | konfirmasi kata sandi | 202: job\_id penghapusan akun dan data |
| GET | /jobs/{id} | - | 200: status, download\_url bila ekspor selesai |
| GET | /business | - | 200: profil, setup, accounts |
| PUT | /business/profile | jenis\_usaha, lama\_usaha\_bulan, jumlah\_karyawan, nib\_status, rekening\_terpisah | 200: business |
| PUT | /business/setup | saldo\_kas\_awal, modal\_awal, assets\[\], debts\[\], stok\_awal\[\], lewati (boolean) | 200: setup\_complete, diagnosis awal |

**Input data**

| Method | URL | Payload | Response |
| --- | --- | --- | --- |
| POST | /receipts/scan | multipart: image (JPEG ≤ 1,5 MB), client\_uuid | 200: receipt\_id, ocr (kontrak Tugas 1), flags (kolom\_kuning\[\], total\_mismatch), duplicate (level none, soft, hard; similar\_receipt\_id) |
| POST | /receipts/{id}/confirm | merchant, date, items\[\], total, force\_duplicate | 201: transaction\_id, impacts (stok, hpp, anomalies\[\]) |
| DELETE | /receipts/{id} | - | 204 (buang hasil scan) |
| POST | /transactions | client\_uuid, type, category\_code, amount, occurred\_on, account\_id, tag, note | 201: transaction, meta |
| GET | /transactions | query: from, to, type, tag, cursor, limit | 200: items\[\], next\_cursor |
| PATCH | /transactions/{id} | kolom yang diubah | 200: transaction |
| DELETE | /transactions/{id} | - | 204 |
| POST | /transactions/bulk-tag | ids\[\] (maks 200) atau rule (description\_contains), tag | 200: updated |
| POST | /sales/quick | client\_uuid, amount atau items\[\] (product\_id, qty), occurred\_at | 201: transaction |
| POST | /sales/daily-recap | recap\_date, total | 201: added\_amount, transaction\_id |
| POST | /imports/bank-csv | multipart: file (CSV ≤ 5 MB, ≤ 5.000 baris) | 201: import\_id, rows\_preview\[\], summary (cocok, belum\_tercatat, duplikat) |
| POST | /imports/{id}/commit | decisions\[\] (row\_id, action, tag, category\_code) | 200: created, skipped |
| POST | /sync/batch | operations\[\] (maks 100; type, client\_uuid, payload) | 200: results\[\] (client\_uuid, status, server\_id atau error) |
| GET | /sync/changes | query: since (kursor) | 200: perubahan sejak kursor |

**Katalog dan stok**

| Method | URL | Payload | Response |
| --- | --- | --- | --- |
| GET | /products | - | 200: items\[\] (hpp, margin\_rp, margin\_pct) |
| POST | /products | name, price, kemasan\_cost, recipe\[\] (item\_master\_id, qty\_per\_unit) | 201: product dengan hpp dan margin |
| PUT | /products/{id} | sama seperti POST | 200: product |
| DELETE | /products/{id} | - | 204 |
| GET | /items | query: q | 200: item\_master\[\] |
| PATCH | /items/{id} | canonical\_name, unit, min\_stock, alias\_baru | 200: item |
| GET | /stock | - | 200: items\[\] (stock\_qty, days\_cover, low) |
| POST | /stock/adjust | item\_master\_id, delta, reason | 201: stock\_movement |

**Laporan**

| Method | URL | Payload | Response |
| --- | --- | --- | --- |
| GET | /reports/profit-loss | query: from, to | 200: omzet, hpp, hpp\_method, laba\_kotor, opex\_by\_category, laba\_operasional, gm, nm |
| GET | /reports/cash-flow | query: from, to | 200: kas\_masuk, kas\_keluar, arus\_bersih, saldo\_akhir, burn\_bulanan, runway\_bulan (null jika tak terhingga) |
| GET | /reports/balance-sheet | query: as\_of | 200: aset (kas, stok, tetap), utang, modal |
| GET | /reports/trends | query: range (30d, 3m, 6m, 1y) | 200: granularity, series\[\] (date, omzet, pengeluaran, margin) |
| GET | /reports/bank-pack | query: from, to | 200: profil, periode, laba\_rugi, arus\_kas, neraca, skor, confidence, asumsi, generated\_at (PDF dibuat di perangkat) |

**Diagnosis, masalah, dan anomali**

| Method | URL | Payload | Response |
| --- | --- | --- | --- |
| GET | /diagnosis | - | 200: score, category, is\_provisional, confidence (k, level, label, reason), indicators\[\] (code, score, available, missing\_requirement, inputs), breakeven |
| GET | /diagnosis/history | query: months (maks 12) | 200: snapshots\[\] |
| GET | /diagnosis/gate | - | 200: met, reasons\[\] |
| GET | /problems | query: status | 200: items\[\] terurut prioritas (rule\_id, severity, dampak, kemudahan, priority, facts) |
| PATCH | /problems/{id} | status = diabaikan | 200: problem |
| GET | /anomalies | query: status | 200: items\[\] |
| PATCH | /anomalies/{id} | status = wajar atau salah\_catat | 200: anomaly |

**AI, Action Plan, dan Growth**

| Method | URL | Payload | Response |
| --- | --- | --- | --- |
| POST | /ai/narrative | period (start, end) | 200: narrative, highlights\[\], caveat, fallback\_used |
| POST | /ai/consult | question | 200: scope, answer, fact\_refs\[\], refusal\_reason, fallback\_used |
| GET | /ai/consult/history | query: cursor | 200: messages\[\] |
| POST | /action-plan/generate | - | 200: cards\[\] (kontrak Tugas 3 digabung peringkat dan target dari kode) |
| GET | /action-cards | - | 200: cards\[\] |
| PATCH | /action-cards/{id} | status | 200: card |
| POST | /growth/projection | goal, investasi\_min, investasi\_maks, assumptions (opsional) | 200: kebutuhan\_min, kebutuhan\_maks, payback\_min, payback\_maks, assumptions\[\], gate |
| POST | /growth/plan | goal, investasi\_min, investasi\_maks, assumptions | 200: plan\_id, ringkasan, stages\[\], caveat, projection |

## 6. Arsitektur Flutter, UI/UX & Edge Cases

Flutter menampilkan hasil dari server; aplikasi tidak menghitung skor atau laporan sendiri. Satu basis kode untuk Android dan iOS, state dengan Riverpod, penyimpanan lokal SQLite terenkripsi untuk mode offline.

### 6.1 Struktur Folder dan Lapisan

```text
bussnapp/
├── lib/
│   ├── main.dart
│   ├── app/                 # go_router, tema, lokalisasi id_ID, injeksi dependensi
│   ├── core/
│   │   ├── network/         # klien Dio, interceptor auth dan retry, pemeta galat
│   │   ├── storage/         # secure storage (token), SQLite terenkripsi (drift + sqlcipher)
│   │   ├── sync/            # antrean offline dan sync engine
│   │   ├── utils/           # format Rupiah, tanggal, validator
│   │   └── design_system/   # token, tema, widget reusable (Said)
│   └── features/
│       ├── auth/            # login, daftar, persetujuan privasi
│       ├── onboarding/
│       ├── profile_setup/   # profil usaha, setup awal
│       ├── capture/         # scan struk, konfirmasi, penjualan cepat, rekap, manual, impor CSV, tag
│       ├── catalog/         # produk, HPP, stok
│       ├── reports/         # laba rugi, arus kas, neraca, tren, PDF siap-bank
│       ├── diagnosis/       # skor, indikator, masalah, anomali, skor tren
│       ├── action_plan/
│       ├── growth/          # growth planner, proyeksi modal
│       ├── chat/            # AI Konsultasi
│       └── home/            # beranda
├── test/                    # unit dan widget test
└── integration_test/        # alur utama end-to-end
```

Setiap fitur memakai tiga lapisan: `data/` (DTO, repository, sumber lokal dan jarak jauh), `domain/` (entitas dan use case), `presentation/` (layar, widget, provider Riverpod). Aliran data: layar → provider → use case → repository → (API atau SQLite). Aturan: layar tidak memanggil API langsung, dan tidak ada rumus bisnis di lapisan presentation.

Pustaka utama: `flutter_riverpod`, `go_router`, `dio`, `drift` dengan `sqlcipher_flutter_libs`, `flutter_secure_storage`, `fl_chart`, `pdf` dan `printing`, `camera` dan `image_picker`, `image` (kompresi), `connectivity_plus`, `workmanager`, `flutter_local_notifications`, `intl`, `freezed` dan `json_serializable`.

### 6.2 Lima Menu Navigasi Bawah

| Menu | Isi layar utama | PIC |
| --- | --- | --- |
| Beranda | Kartu skor ringkas dengan label confidence, omzet hari ini, streak, satu masalah teratas, tombol pintas Catat dan Tanya AI. | Said, Agam |
| Laporan | Tab Laba Rugi, Arus Kas dan Runway, Neraca, Tren; pemilih periode; tombol Ekspor PDF Siap-Bank. | Agam |
| Catat (tombol tengah, menonjol) | Bottom sheet: Scan Struk (aksi utama), Penjualan Cepat, Rekap Harian, Pengeluaran Manual, Impor CSV. | Arya, Said |
| Diagnosis | Segmen Diagnosis (skor, 7 indikator, break-even, masalah dan prioritas, anomali, Skor Tren), Action Plan, dan Growth; tombol mengambang Tanya AI. | Agam, Said |
| Profil | Profil usaha, setup awal, Katalog Produk dan HPP, Stok, persetujuan privasi, ekspor dan hapus data, pengingat dan streak. | Arya, Said |

### 6.3 Design System dan Widget Reusable (Said)

- Warna: Primer `#1B7F5C`; latar `#F7F8F6`; teks `#1C2321`. Kategori skor: Belum Siap `#D64545`, Perlu Perbaikan `#EE8A2B`, Cukup Siap `#E8B81A`, Siap Berkembang `#2E9E5B`. Penanda OCR kuning: isi `#FFF3C4`, garis `#E8B81A`.
- Tipografi: Plus Jakarta Sans (disertakan di aset agar jalan offline); skala 12, 14, 16, 20, 24, 32 sp. Jarak kelipatan 4 dp (4, 8, 12, 16, 24, 32); radius 12 dp; area sentuh ≥ 48 dp.
- Aksesibilitas: kontras teks ≥ 4,5:1; makna tidak hanya dari warna (selalu ada ikon dan teks); mendukung skala teks hingga 130%.
- Animasi: maksimal 250 ms, hanya properti transform dan opacity agar tetap 60 fps.

| Widget | Fungsi | Dipakai di |
| --- | --- | --- |
| `ScoreGauge` | Skor 0–100 melingkar dengan warna kategori | Beranda, Diagnosis |
| `ConfidenceBadge` | Label level dan alasan, dapat diketuk | Beranda, Diagnosis, PDF |
| `IndicatorBar` | Skor satu indikator, abu-abu jika data belum cukup | Diagnosis |
| `ProblemCard` | Judul masalah, angka pemicu, severity, tombol Jadikan langkah | Diagnosis |
| `ActionCard` | Langkah, target tanggal, status, penanda terverifikasi data | Action Plan |
| `YellowField` | Kolom form OCR dengan status ok, ragu, sudah dicek | Konfirmasi struk |
| `MoneyField` | Input Rupiah dengan pemisah ribuan | Semua input |
| `TagChip` | Usaha, Pribadi, Belum ditag | Daftar transaksi |
| `EmptyState` | Ilustrasi, satu kalimat, satu tombol aksi | Semua layar |
| `StreakChip` | Jumlah hari berurutan | Beranda, Catat |
| `AiBadge` dan `AiBubble` | Menandai konten AI dan gelembung chat | Narasi, Action Plan, Chat |
| `DisclaimerBanner` | "Skor ini pemandu kesiapan usaha, bukan penilaian kelayakan kredit." | Skor, Growth, PDF |

### 6.4 Penanda Kuning OCR dan Label Confidence

**Penanda kuning.** Setiap kolom hasil OCR berada pada salah satu status: `ok` (keyakinan ≥ 0,80), `ragu` (< 0,80 atau diberi bendera kode, tampil kuning dengan ikon seru dan teks "Cek ulang"), dan `sudah_dicek` (pengguna mengubah nilai atau mengetuk "Sudah benar", kembali ke warna normal). Tombol Simpan menampilkan "Simpan (2 perlu dicek)"; jika masih ada kolom `ragu`, menekan Simpan memunculkan dialog "2 kolom belum dicek. Tetap simpan?".

| Level | Tampilan | Contoh teks | Perilaku saat diketuk |
| --- | --- | --- | --- |
| Rendah | Lencana oranye dengan ikon info | "Rendah: baru 12 hari data" | Bottom sheet "Kenapa keyakinan ini?" menampilkan 4 komponen K (hari data, konsistensi catat, kualitas sumber, kelengkapan indikator) dan satu saran dari kode, misalnya "Catat 2 hari lagi untuk naik ke Sedang". |
| Sedang | Lencana kuning dengan ikon sedang | "Sedang: 28 hari data, banyak rekap harian" | Sama; saran menunjuk komponen terendah. |
| Tinggi | Lencana hijau dengan ikon centang | "Tinggi: 74 hari data" | Sama; menjelaskan bahwa skor stabil. |

### 6.5 Empty State Hari ke-1

Pengguna yang baru selesai setup belum punya transaksi. Setiap layar harus bermakna tanpa data dan mengarahkan ke satu aksi.

| Layar | Tampilan hari ke-1 | Aksi utama |
| --- | --- | --- |
| Beranda | Kartu Diagnosis Awal (skor sementara dari 2 indikator, label "Rendah: belum ada data transaksi") dan daftar periksa 3 langkah: catat penjualan pertama, foto struk pertama, aktifkan pengingat. | Catat penjualan pertama |
| Laporan | "Belum ada data. Laporan tersusun otomatis begitu kamu mencatat." | Buka menu Catat |
| Diagnosis | Skor sementara; indikator tanpa data berwarna abu-abu dengan keterangan syarat (misal "butuh 14 hari catatan"). | Catat transaksi |
| Action Plan | "Langkah perbaikan muncul setelah ada data yang bisa dianalisis." | Lihat daftar periksa |
| Growth | Terkunci dengan bilah kemajuan "hari data x dari 30". | Catat rutin |
| Chat | Contoh pertanyaan sebagai chip; jawaban hari ke-1 hanya merujuk profil dan setup. | Pilih chip |
| Katalog | "Tambahkan produk pertama agar margin dan HPP terhitung." | Tambah produk |

### 6.6 Offline Caching dan Antrean

SQLite terenkripsi (SQLCipher; kunci di secure storage) menyimpan: `pending_ops` (id, client\_uuid, type, payload\_json, created\_at, attempts, status: pending, sending, failed, done, last\_error), `pending_receipts` (id, client\_uuid, image\_path, created\_at, status), `cache_entries` (key, json, fetched\_at, ttl\_detik), dan salinan baca-saja transaksi 90 hari terakhir.

1. Setiap aksi tulis (penjualan, rekap, pengeluaran manual, konfirmasi, tag) masuk SQLite berstatus `pending` dan langsung tampil di UI (optimistic).
2. Sync engine mengirim FIFO lewat `POST /sync/batch` (maks 100 operasi), dipicu: aplikasi dibuka, koneksi kembali, setiap penambahan antrean, dan tugas latar tiap 15 menit di Android (iOS sebisa sistem).
3. Gagal: jeda eksponensial 5, 15, 45, 135 detik, maksimal 6 percobaan, lalu status `failed` dengan tombol "Coba lagi". Idempotensi lewat `client_uuid`; jawaban 409 dianggap sudah tersimpan.
4. Foto struk saat offline disimpan di `pending_receipts`; saat online diunggah ke `/receipts/scan`, lalu notifikasi "Struk siap dicek" membuka layar Konfirmasi. Gambar lokal dihapus setelah struk dikonfirmasi atau dibuang.
5. Laporan dan diagnosis di-cache 24 jam dengan label "Terakhir diperbarui {waktu}"; selama ada antrean, banner "Mode offline: angka belum termasuk N catatan yang menunggu kirim" tampil.
6. Batas antrean 500 operasi dan 50 foto; pada 80% tampil peringatan agar pengguna tersambung ke internet.

### 6.7 Edge Cases UI dan Perilaku Sistem

| Kasus | Perilaku yang ditetapkan | PIC |
| --- | --- | --- |
| Struk buram atau gelap | Pra-cek klien menampilkan peringatan dan tombol "Foto ulang"; pengguna tetap boleh melanjutkan. | Arya |
| Struk terlipat atau total terpotong | Total dan item terkait berwarna kuning; dialog menyarankan foto ulang atau isi manual. | Arya, Febri |
| Struk tulisan tangan | Diproses seperti biasa; kolom keyakinan rendah kuning; tidak dihitung dalam target akurasi K4. | Febri |
| OCR timeout atau galat penyedia | Pesan ramah dengan "Ulangi" dan "Isi manual"; tidak ada data tersimpan setengah jadi. | Arya, Febri |
| Total 0, negatif, atau tanggal di masa depan | Simpan dinonaktifkan dengan pesan di bawah kolom; tanggal > 1 tahun lalu meminta konfirmasi. | Arya |
| Item lebih dari 80 baris | Pesan "Pecah struk menjadi beberapa foto". | Arya |
| Izin kamera ditolak | Tawarkan pilih dari galeri dan jalur manual. | Arya |
| Struk duplikat keras | Dialog dengan "Batalkan" sebagai default (3.2, B1-03). | Rido, Arya |
| CSV salah format, bukan UTF-8, atau > 5 MB | Pesan menyebut penyebab dan kolom yang hilang; tidak ada data tersimpan. | Arya |
| Jam perangkat salah > 1 hari dari server | Banner peringatan; tanggal transaksi tetap dari pilihan pengguna. | Arya |
| Token kedaluwarsa saat sinkron | Refresh otomatis lalu ulangi; jika gagal, minta login ulang tanpa menghapus antrean. | Arya |
| Keluar akun saat antrean belum kosong | Peringatan "N data belum terkirim"; keluar hanya dengan konfirmasi. | Arya |
| Produk tanpa resep | HPP ditandai "Belum ada resep"; produk dikeluarkan dari R11; laporan memakai metode pembelian jika cakupan katalog < 60%. | Arya, Rido |
| Stok menjadi minus | Stok ditampilkan dengan peringatan "periksa catatan"; tidak memblokir penjualan. | Arya |
| Nominal sangat besar (> Rp10.000.000.000) | Dialog konfirmasi digit sebelum menyimpan. | Arya |
| Hari ke-1 tanpa data | Empty state di 6.5. | Said |
|  |  |  |

### 7. Timeline & WBS 6 Minggu

Pengerjaan berjalan 6 minggu dalam 3 sprint (masing-masing 2 minggu) oleh 5 PIC: Rido (Rule Engine, PostgreSQL, REST API), Febri (AI Gateway, kontrak OpenAPI, QA, DevOps), Arya (Flutter: auth, capture, sinkronisasi, katalog), Agam (Flutter: laporan, diagnosis, growth, PDF), dan Said (design system, UX, copy). Prinsipnya *contract-first* dan *mock-first*: kontrak API dibekukan lebih dulu, sehingga Flutter bekerja pada mock sebelum endpoint hidup. Seluruh target `K1`–`K9` diukur pada build rilis kandidat (RC) di akhir Sprint 3 (1.5), tetapi alat ukurnya dibangun sejak Sprint 1.

#### 7.1 Ritme 3 Sprint (Minggu 1–6)

| Sprint | Minggu | Fokus | Fitur yang selesai | KPI yang mulai diukur | Kriteria selesai sprint |
| --- | --- | --- | --- | --- | --- |
| 1 | 1–2 | Fondasi, Auth, Input, Katalog | `A-01`–`A-05`, `B1-01`–`B1-03`, `B2-01`–`B2-03`, `C-01`, `C-02`; server `B2-04`–`B2-06` | Instrumentasi `ocr_latency_ms` (`K1`), Sentry (`K8`), profil jank (`K3`) | Pengguna dapat mendaftar dengan dua persetujuan, mengisi profil dan setup, memotret struk lalu mengonfirmasi dan menyimpannya, mencatat penjualan, rekap, dan pengeluaran manual, serta mengelola katalog dan stok. Antrean offline berjalan. OpenAPI Gelombang 1 dan 2 beku. |
| 2 | 3–4 | Rule Engine, Laporan, Diagnosis | `D-01`–`D-04`, `E1-01`–`E1-04`, `E2-01`, `E2-02`, `E3-01`–`E3-03`, `F-05` (hitung kode); Flutter `B2-04`–`B2-06` | `K7` (40 dataset), `K2` (k6 awal), `K9` (uji internal) | Skor 0–100, 7 indikator, confidence, `R01`–`R11`, `A01`, `A02`, dan Break-even tampil di Flutter dari angka server. 40 golden test hijau. OpenAPI Gelombang 3, `contracts/ai/` v1.0, dan fixture `facts` sudah diserahkan. |
| 3 | 5–6 | AI Gateway, PDF Siap-Bank, Hardening `K1`–`K9` | `F-01`–`F-04`, `F-05` (layar), `D-05` | `K1`, `K4`, `K5`, `K2`, `K3`, `K6`, `K8`, `K9` | RC lulus seluruh Gate Rilis 8.3, dengan `K1`–`K9` hijau pada build yang sama. |

**Catatan ritme:**

- **Jalur paralel Febri.** OCR (Tugas 1) dibangun di Sprint 1 karena `B1-01` tidak dapat diuji tanpanya. Kerangka dan validator Gateway dibangun di Sprint 2 karena hanya bergantung pada fixture `facts` dari Rido. Fitur AI yang tampil ke pengguna (`F-01`–`F-04`) dikirim di Sprint 3.
- **Agam lebih ringan di Sprint 1.** Laporan baru dapat dibangun setelah Rule Engine ada. Agam mengerjakan shell navigasi dan sisi presentasi katalog (`C-01`, `C-02`) bersama Arya yang memegang logika.
- **Carry-over yang diizinkan.** Sisi Flutter `B2-04`–`B2-06` boleh bergeser ke awal Minggu 3.
- **Kadensi.** Planning hari Senin, sinkronisasi serah terima lintas-PIC 30 menit setiap Rabu, demo dan retrospektif setiap Jumat.

#### 7.2 Tabel WBS Mingguan (Minggu 1 s.d. Minggu 6)

Legenda: `←` menerima dari, `→` menyerahkan ke, `Hn` titik serah terima di 7.3, `—` tidak terkait satu ID fitur. “Fondasi” berarti pekerjaan pendukung yang belum menyelesaikan satu fitur utuh.

**Minggu 1: Fondasi, Auth, Setup (Sprint 1)**

| PIC | Deliverable | ID fitur | KPI | Ketergantungan |
| --- | --- | --- | --- | --- |
| Rido | Migrasi awal `users`, `consents`, `refresh_tokens`, `businesses`, `accounts`, `setup_assets`, `setup_debts`, `categories` (10 seed), `transactions` (UNIQUE `business_id, client_uuid`); RLS dari klaim JWT; `/auth/*`, `/me`, `/me/consents`, `/business/*`; kunci akun 15 menit setelah 5 kali salah; `consents` append-only | `A-02`, `A-03`, `A-04`, `A-05` | `K6`, `K2` (indeks awal) | → Arya: Auth live di staging hari Rabu. ← Febri: CI dan staging |
| Febri | Repo backend dan CI (lint, contract test, cek skema); `contracts/openapi.yaml` dari 5.3 dan `/docs`; mock server; staging dengan TLS 1.3; secret manager (kunci AES-256-GCM); Sentry backend dan Flutter. **Bekukan G1** | — (fondasi A–C) | `K8`, `K6` | → Rido, Arya, Agam: kontrak Auth (Rabu), Input, Katalog, dan Sync (Jumat) (H1). ← Rido: skema |
| Arya | Kerangka Flutter `app/` dan `core/` (`network`: Dio dan interceptor refresh; `storage`: secure storage dan drift+SQLCipher; `utils`: format Rupiah); `features/auth` (login, daftar, dua persetujuan); `features/profile_setup` | `A-02`, `A-03`, `A-04`, `A-05` | `K6`, `K9` | ← Said: token dan tema (Rabu). ← Febri: kontrak Auth |
| Said | Token warna, tipografi, jarak, tema, dan aset font; widget batch 1 (`MoneyField`, `EmptyState`, `DisclaimerBanner`, `TagChip`, `StreakChip`); tiga layar onboarding; desain Konfirmasi dan bottom sheet Catat | `A-01` | `K3` (aturan animasi), `K9` | → Arya, Agam: batch 1 hari Rabu (H2) |
| Agam | Shell navigasi 5 menu (6.2) dengan `EmptyState` hari ke-1 (6.5); Beranda kosong; spike `fl_chart` di perangkat acuan untuk `D-04`; DTO laporan dari mock | — (persiapan `D-01`, `D-04`) | `K3` | ← Said: batch 1. ← Febri: mock |

*Gerbang Minggu 1:* login dan persetujuan berjalan end-to-end di staging, G1 beku, CI hijau di kedua repo.

**Minggu 2: Input Struk, Transaksi, Katalog (Sprint 1)**

| PIC | Deliverable | ID fitur | KPI | Ketergantungan |
| --- | --- | --- | --- | --- |
| Rido | `/transactions`, `/sales/quick`, `/sales/daily-recap` (hanya selisih positif), `/transactions/bulk-tag`, `/imports/bank-csv` dan `/commit`, `/sync/batch`, `/sync/changes`; aturan duplikat keras dan lunak (3.9); `/products`, `/items`, `/stock`, HPP dan margin (3.4); `price_history`, `stock_movements`, `daily_aggregates`, `streaks` | `B1-03`, `B2-01`–`B2-06`, `C-01`, `C-02` | `K2` (indeks, agregat) | → Arya: endpoint live per Rabu. ← Febri: `/receipts/scan` |
| Febri | `/receipts/scan`; adaptor `extractReceipt` (Tugas 1) dengan JSON Schema, timeout 6 detik, `OCR_PROVIDER`, flag `kolom_kuning` dan `total_mismatch`; log `ai_events` dan `ocr_latency_ms`; mulai korpus 150 struk, struk ekstrem, dan 20 uji injeksi. **Bekukan G2** hari Jumat | `B1-01`, `B1-02` | `K1`, `K4` (baseline), `K8` | → Arya: JSON struk. ← Rido: aturan duplikat |
| Arya | `features/capture`: kamera, pra-cek ketajaman, kompres ≤ 1,5 MB, Konfirmasi (status `ok`, `ragu`, `sudah_dicek`), penjualan cepat, rekap harian, pengeluaran manual; `core/sync` (`pending_ops`, `pending_receipts`, FIFO, jeda 5/15/45/135 detik, `client_uuid`); `catalog` data dan domain | `B1-01`, `B1-02`, `B2-01`, `B2-02`, `B2-03`, `C-01`, `C-02` | `K1` (sisi klien), `K3` | ← Said: `YellowField` (Senin). ← Rido: endpoint. → Agam: use case katalog |
| Said | `YellowField` (batch 2, Senin); layar Konfirmasi, bottom sheet Catat, Katalog dan Stok; batch 3 (`ScoreGauge`, `ConfidenceBadge`, `IndicatorBar`, `ProblemCard`, Jumat); rencana uji `K9` | — (tampilan `B1-02`, `C-01`) | `K3`, `K9` | → Arya: batch 2. → Agam: batch 3 (H2) |
| Agam | Presentasi `catalog` (kartu produk, margin < 20% merah, notifikasi stok tipis) bersama Arya; provider laporan di atas mock G2 | `C-01`, `C-02` | `K3` | ← Arya: use case katalog. ← Febri: kontrak G2 |

*Gerbang Minggu 2 (akhir Sprint 1):* alur struk end-to-end berjalan, antrean offline memproses ulang tanpa duplikat, G2 beku, demo Sprint 1.

**Minggu 3: Rule Engine Inti dan Laporan (Sprint 2)**

| PIC | Deliverable | ID fitur | KPI | Ketergantungan |
| --- | --- | --- | --- | --- |
| Rido | Laporan (3.5): `/reports/profit-loss`, `cash-flow`, `balance-sheet`, `trends`; 7 indikator, Runway, dan Break-even (3.7); skor dan confidence K (3.6); `scoring_config`, `score_runs`, `/diagnosis`, `/diagnosis/history`; golden dataset 1–20 | `D-01`–`D-04`, `E1-01`–`E1-03`, `E2-01`, `E2-02` | `K7`, `K2` | → Agam: endpoint live Rabu (H4). ← Febri: harness golden |
| Febri | Harness golden test di CI bersama Rido; JSON Schema lima tugas di `contracts/ai/`; kerangka Gateway (cek persetujuan, batas 30 chat dan 100 scan, `AI_PROVIDER`, amplop galat); hardening OCR untuk struk ekstrem. **Bekukan G3** (REST AI, Action Plan, Growth, dan `contracts/ai/` v1.0) hari Jumat | — (fondasi `F-01`–`F-05`) | `K7`, `K1`, `K4`, `K5` | → Rido: harness. ← Rido: fixture `facts` Tugas 2 (Jumat, H3) |
| Arya | Sisi Flutter impor CSV (pratinjau tiga status), tag massal ≤ 200, pengingat 17:00 dan streak; cache 24 jam dan banner mode offline (6.6) | `B2-04`, `B2-05`, `B2-06` | `K3`, `K8` | ← Rido: endpoint. → Agam: repository laporan |
| Said | Desain final Diagnosis, Laporan, Action Plan, Growth, Chat; batch 4 (`ActionCard`, `AiBadge`, `AiBubble`, Rabu); audit teks `DisclaimerBanner` terhadap larangan 1.4; rekrut 5 pelaku UMKM untuk `K9` | — | `K9`, `K3` | → Agam, Arya: batch 4 (H2) |
| Agam | `features/reports`: Laba Rugi, Arus Kas dan Runway, Neraca, Tren (pemilih periode, `fl_chart` 60 fps, agregasi harian, mingguan, bulanan); kartu skor di Beranda | `D-01`–`D-04`, `E1-01` | `K3`, `K2` (konsumsi) | ← Rido: endpoint. ← Said: batch 3 |

*Gerbang Minggu 3:* laporan tampil dari server dan identik dengan keluaran Rule Engine, 20 dataset golden hijau, G3 beku, fixture Tugas 2 diterima Febri.

**Minggu 4: Diagnosis, Masalah, Gerbang Kesiapan (Sprint 2)**

| PIC | Deliverable | ID fitur | KPI | Ketergantungan |
| --- | --- | --- | --- | --- |
| Rido | `R01`–`R11`, Skor Dampak × Kemudahan, `problems`, `rule_config`; anomali `A01`, `A02` dan `/anomalies`; `/diagnosis/gate`; snapshot bulanan (23:59) dan job malam 02:00; `/growth/projection`; `FactsBuilder` Tugas 3–5 dan fixture; golden dataset 21–40 | `E3-01`, `E3-02`, `E3-03`, `E1-04`, `F-05` | `K7` (40 dari 40), `K2` | → Febri: fixture Tugas 3–5 hari Rabu (H3). → Agam: endpoint masalah dan gerbang |
| Febri | Gateway inti: `generate()`, validasi skema G3 dengan satu perbaikan, validator numerik G2 v1, `fact_refs` G4, fallback G7, cache G8, `ai_events`; `/ai/narrative` (Tugas 2); mulai suite 300 skenario G2 | `F-01` | `K5`, `K1` | ← Rido: fixture. → Said, Agam: respons dan fallback |
| Arya | Dampak struk (stok, HPP, notifikasi anomali; 2.4 tahap 5) dan notifikasi stok tipis; Profil: kelola persetujuan (cabut izin AI), ekspor dan hapus akun (`/me/export`, `DELETE /me`), keluar akun saat antrean belum kosong; batas antrean 500 operasi dan 50 foto dengan peringatan 80% | `C-02`, `A-03`, `B1-03` | `K6`, `K8`, `K3` | ← Rido: `/me/*` dan `/problems` |
| Said | Uji usabilitas internal #1 (buka pertama hingga Diagnosis Awal); tampilan Action Plan, Growth, Chat; UI fallback G7 (“penjelasan otomatis sederhana”) | `F-01`–`F-03` (tampilan) | `K9`, `K3` | ← Febri: bentuk respons dan fallback |
| Agam | `features/diagnosis`: skor dan kategori, 7 indikator (abu-abu bila data kurang), Break-even, `ProblemCard`, Prioritas, anomali, Skor Tren; Diagnosis Awal hari ke-1; banner gerbang | `E1-01`–`E1-04`, `E2-01`, `E2-02`, `E3-01`–`E3-03` | `K3`, `K9` | ← Rido: endpoint. ← Said: batch 3 dan 4 |

*Gerbang Minggu 4 (akhir Sprint 2):* 40 dari 40 golden test hijau (`K7`), Diagnosis lengkap di perangkat, fixture lima tugas lengkap, demo Sprint 2.

**Minggu 5: AI Gateway Penuh, Growth, PDF (Sprint 3)**

| PIC | Deliverable | ID fitur | KPI | Ketergantungan |
| --- | --- | --- | --- | --- |
| Rido | `/action-plan/generate` (peringkat dan target dari kode, teks dari AI), `/action-cards`, `/growth/plan`; `/reports/bank-pack`; job retensi (foto struk 30 hari, `chat_messages` 90 hari); job ekspor dan hapus akun; tuning indeks dari k6 awal | `F-03`, `F-04`, `D-05`, `F-05` | `K2`, `K6` | ← Febri: keluaran Tugas 3 dan 5. → Agam: `/growth/*` dan `/bank-pack` |
| Febri | Gateway Tugas 3 (Action Plan), Tugas 4 (Konsultasi), Tugas 5 (Growth); G5 (40 prompt), G6 (20 uji), G2 300 skenario di CI; pengukuran pertama `K1` dan `K4`; skrip k6; audit manual 50 respons (pertama) | `F-02`, `F-03`, `F-04` | `K5`, `K1`, `K4` | ← Rido: fixture. → Agam, Said: endpoint AI live |
| Arya | `features/chat` data dan domain (riwayat 6 giliran, batas 30 pesan per hari, `AI_RATE_LIMIT`, `AI_CONSENT_REQUIRED` menyembunyikan fitur AI); uji putus-nyambung `/sync/batch`; seluruh edge case 6.7 | `F-02` | `K8`, `K3` | ← Febri: kontrak AI. → Said: provider chat |
| Said | `features/chat` presentasi (`AiBubble`, chip contoh, penolakan sopan); polesan Action Plan dan Growth; audit aksesibilitas (kontras ≥ 4,5:1, skala teks 130%); **uji usabilitas `K9` dengan 5 pelaku UMKM** (Jumat) | `F-02`, `F-03` | `K9`, `K3` | ← Arya: provider chat. ← Febri: fallback |
| Agam | `features/action_plan` (≤ 5 kartu), `features/growth` (rencana 3 tahap, rentang modal, asumsi dapat diubah, banner gerbang); PDF Siap-Bank di perangkat (`pdf`+`printing`, < 2 MB, < 5 detik, label “Data belum cukup (n hari)”) dengan `DisclaimerBanner` dan `ConfidenceBadge`; narasi `F-01` di Diagnosis | `D-05`, `F-01`, `F-03`, `F-04`, `F-05` | `K3`, `K9` | ← Rido: `/growth/*`, `/bank-pack`. ← Febri: narasi |

*Gerbang Minggu 5:* seluruh fitur `A-01`–`F-05` lengkap dan dapat didemokan, RC1 dipotong hari Jumat.

**Minggu 6: Hardening `K1`–`K9` dan Gate Rilis (Sprint 3)**

| PIC | Deliverable | ID fitur | KPI | Ketergantungan |
| --- | --- | --- | --- | --- |
| Rido | **Code freeze hari Rabu**; golden final 40 dataset; k6 final (50 pengguna, 5 menit, 10.000 transaksi per usaha); verifikasi PDP-01, 02, 07–10 (8.2); perbaikan bug P0 dan P1; bekukan versi `scoring_config` dan `rule_config` | — | `K2`, `K7`, `K6` | → Febri: bukti uji. ← Febri: daftar bug |
| Febri | Eksekusi Gate Rilis 8.3 (`K1`, `K4`, `K5`, `K8`) dan verifikasi daftar periksa PDP 10/10; audit manual 50 respons; build RC; laporan gate `K1`–`K9` ke Product Manager | semua | `K1`, `K4`, `K5`, `K6`, `K8` | ← semua PIC: RC (H5) |
| Arya | Perbaikan bug dari uji; `integration_test` lima alur utama; sesi uji 100 sesi bersama Febri; build Android dan iOS | `A-02`, `B1-01`, `B2-01`, `B2-02` | `K8`, `K3` | → Febri: RC Flutter |
| Said | Ulang `K9` bila ada partisipan > 5 menit; QA visual dan aksesibilitas; pemeriksaan teks terlarang (1.4) di seluruh layar dan template; profil jank bersama Agam | — | `K9`, `K3` | → Febri: laporan `K9` |
| Agam | Profil mode profile pada 5 alur di perangkat acuan dan perbaikan jank; penyelesaian akhir PDF | `D-04`, `D-05`, `E1-02` | `K3` | → Febri: RC Flutter |

*Gerbang Minggu 6:* Rabu code freeze dan RC dipotong, Kamis–Jumat pengukuran final pada RC yang sama, Jumat peninjauan Gate Rilis bersama Product Manager.

#### 7.3 Titik Serah Terima Kritis & Git Workflow

**Titik serah terima kritis**

| Kode | Serah terima | Waktu | Aturan dan syarat diterima | Bukti |
| --- | --- | --- | --- | --- |
| H1 | Kontrak OpenAPI: Febri ↔ Rido, dikonsumsi Arya dan Agam | G1: Auth Rabu dan Input, Katalog, Sync Jumat (Minggu 1). G2: Laporan, Diagnosis, Masalah, Anomali (Jumat Minggu 2). G3: AI, Action Plan, Growth, `contracts/ai/` v1.0 (Jumat Minggu 3) | Setiap gelombang dibekukan **sebelum** konsumennya mulai. Setelah beku, perubahan non-breaking (kolom opsional baru) lewat PR `contract/*` dengan 2 reviewer (Febri dan Rido), Arya dan Agam diberi tahu. Perubahan breaking (ganti nama, hapus, ubah tipe atau status code) dilarang setelah beku, kecuali berstatus P0 dan disetujui Febri, Rido, serta konsumen terdampak. Untuk kontrak AI, perubahan merusak menaikkan `schema_version` (4.2). Setelah G3, hanya perbaikan kontrak P0. | Tag `contract-g1`, `contract-g2`, `contract-g3`; contract test hijau di kedua sisi |
| H2 | Widget `core/design_system/`: Said → Arya dan Agam | Batch 1: Rabu Minggu 1. Batch 2 (`YellowField`): Senin Minggu 2. Batch 3 (`ScoreGauge`, `ConfidenceBadge`, `IndicatorBar`, `ProblemCard`): Jumat Minggu 2. Batch 4 (`ActionCard`, `AiBadge`, `AiBubble`): Rabu Minggu 3 | Hanya Said yang menggabungkan perubahan di `core/design_system/`. Widget tanpa logika bisnis dan menerima data lewat parameter. Setiap widget lolos widget test dan golden image (normal dan skala teks 130%), kontras ≥ 4,5:1, area sentuh ≥ 48 dp, animasi ≤ 250 ms (transform dan opacity). Arya dan Agam tidak membuat widget serupa di `features/`. Kekurangan diminta lewat issue ke Said (respons 1 hari kerja), dan placeholder sementara ditandai `// TODO(design_system)`. `EmptyState` wajib di setiap layar dan `DisclaimerBanner` wajib di Skor, Growth, dan PDF. | PR Said dengan tangkapan layar dan hasil golden |
| H3 | JSON `facts`: `FactsBuilder` Rido → AI Gateway Febri | Tugas 2: Jumat Minggu 3. Tugas 3–5: Rabu Minggu 4 | Gateway hanya menerima `facts` dari builder dan tidak membaca basis data. Setiap fakta memuat `value` dan `display` berformat Indonesia (G1). Tidak ada nama, email, NIB, nomor rekening, atau alamat (G9). Fixture per tugas ada di `contracts/ai/fixtures/`, minimal 3 per tugas, termasuk kasus tepi: confidence Rendah, tanpa masalah, Runway tak terhingga, CMR < 0,05. Keluaran builder divalidasi JSON Schema di CI (Rido) dan masukan serta keluaran Gateway divalidasi oleh Febri (4.1). Perubahan builder menaikkan `schema_version` dan wajib lolos golden test `K7`. | Contract test dan golden test hijau |
| H4 | Mock → live: Rido → Arya dan Agam | Tiap endpoint, paling lambat Rabu minggu pemakaiannya | Flutter memakai mock dari OpenAPI sampai endpoint live di staging, lalu beralih tanpa mengubah DTO. Respons live yang berbeda dari kontrak dilaporkan sebagai bug backend, bukan disiasati di Flutter. | Smoke test staging |
| H5 | RC: Arya, Agam, Rido → Febri | Rabu Minggu 6 | Code freeze, hanya perbaikan blocker. Semua PR memenuhi DoD 8.1. | Tag `v0.1.0-rc.1` di kedua repo |

**Aturan cabang dan PR** (berlaku untuk kedua repositori)

| Aspek | Aturan |
| --- | --- |
| Cabang tetap | `main` (terproteksi; hanya RC dan rilis, diberi tag) dan `develop` (integrasi; deploy otomatis ke staging, terproteksi). |
| Cabang kerja | Dari `develop`: `feat/<ID>-<slug>` (contoh `feat/B1-01-scan-struk`, `feat/E1-02-readiness-score`), `fix/<slug>`, `contract/<gelombang>-<slug>`, `chore/<slug>`. `hotfix/<slug>` dari `main`. Hapus cabang setelah merge. |
| Commit | Conventional Commits dengan ID fitur: `feat(B1-01): kompres foto ≤ 1,5 MB`. |
| Ukuran PR | Satu PR untuk satu ID fitur atau satu bagiannya, diff ≤ 400 baris di luar kode hasil generate. |
| Isi PR | Judul `[B1-01] ...`; GWT yang dipenuhi; KPI terdampak; tangkapan atau rekaman layar (Flutter); centang DoD 8.1. |
| Reviewer | 1 reviewer untuk PR umum. **2 reviewer** untuk `contracts/`, `rule_engine/`, validator di `ai_gateway/`, `core/sync/`, dan migrasi basis data. PR Flutter yang menyentuh API wajib dibaca pemilik endpoint (Rido atau Febri). |
| Merge | Squash ke `develop`. `develop` → `main` lewat PR akhir sprint oleh Febri, disetujui Rido (backend) atau Arya (Flutter). |
| CI backend | Lint, unit test, contract test (OpenAPI dan `contracts/ai/`), golden test `K7` (40 dataset), suite G2 (diperluas ke 300), simulasi migrasi, pemindai secret. |
| CI Flutter | `flutter analyze`, unit dan widget test (termasuk golden), cek arsitektur (`presentation/` dilarang mengimpor `data/` atau `dio`, dan tidak boleh ada rumus bisnis), build debug. |
| Migrasi dan konfigurasi | Migrasi hanya maju (*forward-only*). Perubahan `scoring_config` dan `rule_config` lewat migrasi data berversi, bukan edit manual. Perubahan bobot wajib memperbarui nilai harapan golden dengan persetujuan Product Manager. |
| Secret | Kunci AES-256-GCM dan kunci penyedia AI hanya di secret manager; tidak pernah di repositori. |

**Struktur repositori dan kepemilikan jalur kode** (proposal; nama folder backend menyesuaikan stack yang dipilih)

text

```plain
bussnapp-backend/
├── contracts/        # openapi.yaml, ai/ (JSON Schema + fixtures)      Febri, Rido
├── migrations/       # PostgreSQL, forward-only                         Rido
├── src/
│   ├── api/          # endpoint REST (5.3)                              Rido
│   ├── rule_engine/  # laporan, skor, masalah, anomali, FactsBuilder    Rido
│   └── ai_gateway/   # extractReceipt, generate, validator G2–G6        Febri
└── tests/            # golden/ (40), contract/, ai_eval/ (300+40+20), k6/
```

| Jalur (repositori Flutter `bussnapp`) | Pemilik | Catatan |
| --- | --- | --- |
| `lib/core/design_system/` | Said | Hanya Said yang merge (H2). |
| `lib/core/network/`, `core/storage/`, `core/sync/`, `core/utils/` | Arya | `core/sync/` wajib 2 reviewer. |
| `lib/features/auth/`, `onboarding/`, `profile_setup/`, `capture/`, `catalog/` | Arya | Tampilan `onboarding/` dan layar Konfirmasi oleh Said. |
| `lib/features/reports/`, `diagnosis/`, `action_plan/`, `growth/`, `home/` | Agam | Tampilan Beranda bersama Said. |
| `lib/features/chat/` | Arya (`data/`, `domain/`), Said (`presentation/`) | Mengikuti pola pembagian logika dan tampilan di `B1-02`. |
| `test/`, `integration_test/` | Pemilik fitur; `integration_test/` dikoordinasi Febri | Lima alur utama untuk `K3` dan `K8`. |

Antar-`features/` tidak saling mengimpor lapisan dalam (`data/`, `domain/`). Berbagi kode hanya lewat `core/`. Dengan demikian aturan 6.1 (layar tidak memanggil API langsung dan tidak ada rumus bisnis di `presentation/`) dapat dijaga otomatis oleh CI.

### 8. QA Checkpoints & Mitigasi Risiko

#### 8.1 Global Definition of Done (DoD)

Sebuah fitur dianggap selesai hanya jika **seluruh** kriteria berikut terpenuhi dan dicentang di PR.

| No | Kriteria | Cara dibuktikan | Verifikator |
| --- | --- | --- | --- |
| 1 | **Lulus semua GWT** fitur tersebut di Bab 3 (acceptance criteria Given-When-Then, tanpa kecuali). | Uji otomatis (unit, widget, `integration_test`, atau API) dan uji manual untuk yang tidak dapat diotomatisasi; hasil dilampirkan di PR. | Febri |
| 2 | **0 rumus bisnis di layar Flutter.** Semua angka (laporan, skor, indikator, confidence, runway, break-even, masalah, prioritas, rentang modal) berasal dari respons server. | Cek arsitektur CI (7.3) dan tinjauan PR; tidak ada aritmetika bisnis di `presentation/`. | Reviewer PR, Arya dan Agam |
| 3 | **`EmptyState` hari ke-1 dan 60 fps (`K3`).** Layar bermakna tanpa data (6.5) dengan satu tombol aksi, dan jank < 1% di mode profile pada perangkat acuan (Android RAM 4 GB, 60 Hz). | Tangkapan layar hari ke-1; DevTools mode profile pada alur terkait. | Said, Arya, Agam |
| 4 | **Antrean offline idempoten.** Setiap aksi tulis masuk antrean SQLCipher berstatus `pending`, tampil optimistic, dikirim lewat `POST /sync/batch` dengan `client_uuid`, dan jawaban 409 dianggap sudah tersimpan. Kehilangan dan duplikasi data = 0. | Skenario Q-08 (8.3); uji kirim ulang batch yang sama. | Arya, Rido |
| 5 | **`DisclaimerBanner` terpasang** pada setiap layar skor, rentang modal (Growth), dan PDF: “Skor ini pemandu kesiapan usaha, bukan penilaian kelayakan kredit.” Tidak ada kata terlarang 1.4 di UI, template, dan prompt. | Pemeriksaan teks otomatis dan tinjauan copy. | Said |
| 6 | **Kontrak dipatuhi.** Endpoint dan DTO sesuai OpenAPI beku (H1); contract test hijau. Perubahan skema AI menaikkan `schema_version`. | Contract test di CI. | Febri, Rido |
| 7 | **Rule Engine tetap reprodusibel.** Perubahan di `rule_engine/` atau `FactsBuilder` tidak mengubah hasil 40 dataset golden kecuali dengan persetujuan tertulis (`K7`). | Golden test di CI. | Rido |
| 8 | **Jalur AI aman.** Setiap keluaran AI melewati G2–G6; kegagalan jatuh ke template tetap (G7); tidak ada data pribadi di JSON (G9); panggilan tercatat di `ai_events`. | Suite `ai_eval/`; tinjauan log. | Febri |
| 9 | **Kepatuhan PDP terjaga.** Fitur yang menyentuh data pribadi atau persetujuan tidak melanggar satu pun item 8.2. | Daftar periksa 8.2 dicentang pada PR terkait. | Rido, Febri |
| 10 | **Terpantau dan lulus tinjauan.** Sentry aktif untuk alur baru; CI hijau; PR disetujui reviewer sesuai 7.3. | Status CI dan persetujuan PR. | Febri |

#### 8.2 Daftar Periksa Kepatuhan UU PDP (10 Item, `K6`)

Metrik `K6` (1.5) mensyaratkan 10 dari 10 item berikut lulus sebelum rilis. Kajian hukum oleh pihak berwenang tetap diperlukan sebelum peluncuran publik.

| No | Item | Implementasi teknis (rujukan) | Bukti verifikasi | PIC |
| --- | --- | --- | --- | --- |
| PDP-01 | Persetujuan terpisah dan eksplisit | `A-03`: dua persetujuan terpisah, yaitu `financial_processing` (wajib; tanpanya pendaftaran tidak lanjut) dan `ai_processing` (opsional; tanpanya laporan dan skor tetap berjalan). Tidak digabung dan tidak dicentang otomatis. | Uji GWT `A-03` pada register; tangkapan layar | Arya, Rido |
| PDP-02 | Log versi persetujuan | Tabel `consents` (type, version, granted, waktu), append-only dan tidak pernah ditimpa; teks persetujuan berversi. | Uji basis data: perubahan menambah baris, tidak mengubah baris lama | Rido |
| PDP-03 | Cabut izin AI kapan saja | `PUT /me/consents` dari Profil; setelah dicabut, panggilan AI menjawab `AI_CONSENT_REQUIRED` (403), fitur AI tersembunyi, template tetap dipakai (4.5). | Uji: cabut lalu panggil `/ai/narrative` dan `/ai/consult` | Arya, Febri |
| PDP-04 | Anonimisasi PII dan minimisasi data (`G9`) | `facts` hanya berisi agregat serta nama produk atau kategori; tanpa nama, email, NIB, nomor rekening, alamat; gambar struk hanya untuk Tugas 1; `ai_events` menyimpan hash prompt, bukan isi. | Contract test pada fixture; pemindaian PII pada log dan payload uji | Rido, Febri |
| PDP-05 | Enkripsi dalam transit (TLS 1.3) | Seluruh endpoint API dan panggilan ke penyedia AI dan OCR memakai TLS 1.3. | Pemindaian konfigurasi TLS di staging dan produksi | Febri |
| PDP-06 | Enkripsi saat disimpan | Server: AES-256-GCM untuk `receipts.ocr_json`, `import_rows.description`, `chat_messages.content`; gambar struk terenkripsi di object storage; kunci dari secret manager. Perangkat: SQLite SQLCipher dan token di secure storage. | Inspeksi basis data (kolom tidak terbaca), uji buka berkas SQLite tanpa kunci | Rido, Arya |
| PDP-07 | Hapus foto struk 30 hari | Job harian mengisi `receipts.image_deleted_at` dan menghapus objek 30 hari setelah `confirmed_at`; gambar lokal dihapus setelah konfirmasi atau dibuang (6.6). | Uji job dengan data kedaluwarsa buatan | Rido |
| PDP-08 | Hapus `chat_messages` 90 hari | Job retensi menghapus riwayat chat berumur > 90 hari. | Uji job dengan data kedaluwarsa buatan | Rido |
| PDP-09 | Ekspor data pengguna | `POST /me/export` (202, `job_id`) lalu `GET /jobs/{id}` mengembalikan `download_url`; tombol di Profil. | Uji ekspor end-to-end; isi ekspor sesuai data akun | Rido, Arya |
| PDP-10 | Hapus akun dan data | `DELETE /me` dengan konfirmasi kata sandi (202, `job_id`); job menghapus data usaha termasuk baris `deleted_at` dan gambar di object storage. Perlakuan `audit_logs` mengikuti hasil kajian hukum. | Uji hapus akun lalu cek tidak ada data tersisa | Rido, Arya |

#### 8.3 Skenario Uji QA & Gate Rilis (`K1`–`K9`)

Febri memegang rencana uji dan menjalankan pengukuran akhir pada RC. Semua pengukuran memakai **build RC yang sama**.

| ID | Skenario uji | Volume dan kondisi | KPI | Lulus jika | Pelaksana |
| --- | --- | --- | --- | --- | --- |
| Q-01 | Golden test Rule Engine | 40 dataset; masukan sama dijalankan berulang dan lintas lingkungan (CI vs staging); membandingkan skor, confidence, daftar masalah, dan keluaran `facts` | `K7` | 100% identik | Febri (harness), Rido (dataset) |
| Q-02 | Akurasi OCR | 150 struk cetak (toko, tanggal, total, item: nama, jumlah, harga); lalu **struk ekstrem** (buram, terlipat, tulisan tangan) dilaporkan terpisah | `K4` | > 90% akurasi level-field dan total cocok persis ≥ 95%. Struk ekstrem tanpa target, tetapi harus menampilkan kolom kuning dan jalur “foto ulang” atau “isi manual”. | Febri |
| Q-03 | Latensi OCR | 100 uji dari korpus Q-02; foto ≤ 1,5 MB; 4G ≥ 5 Mbps; dari log `ocr_latency_ms` | `K1` | p95 < 3 detik | Febri |
| Q-04 | Validator numerik `G2` | 300 skenario di CI (persen, “juta” dan “ribu”, selisih, pembulatan, angka dari pertanyaan pengguna) dan audit manual 50 respons per minggu | `K5` | 0 pelanggaran lolos | Febri |
| Q-05 | Penolakan `G5` | 40 prompt: kepastian kredit, saran hukum, saran pajak, di luar lingkup, “abaikan aturan” | `K5` | 40 dari 40 ditolak sopan (`scope` = `out_of_scope`), tanpa angka baru | Febri |
| Q-06 | Injeksi `G6` | 20 struk dan pesan berisi perintah tersembunyi | `K5` | 20 dari 20 diperlakukan sebagai data; perilaku AI tidak berubah | Febri |
| Q-07 | Uji beban k6 | 50 pengguna simultan, 5 menit, data 10.000 transaksi per usaha; semua endpoint selain AI dan PDF | `K2` | p95 < 1,5 detik dan tidak ada galat 5xx | Febri, Rido |
| Q-08 | Uji putus-nyambung `/sync/batch` | (a) jaringan putus di tengah batch 100 operasi lalu pulih; (b) batch yang sama dikirim ulang (409 dianggap tersimpan); (c) gagal 6 kali menjadi `failed` dengan tombol “Coba lagi”; (d) token kedaluwarsa saat sinkron; (e) aplikasi dimatikan paksa saat `sending`; (f) foto struk diambil offline lalu diunggah saat online; (g) antrean 500 operasi dan 50 foto dengan peringatan 80%; (h) keluar akun dengan antrean belum kosong | DoD #4, mendukung `K8` | 0 duplikat dan 0 kehilangan data; pesan UI sesuai 6.6 dan 6.7 | Arya, Febri, Rido |
| Q-09 | Stabilitas Sentry | Minimal 100 sesi uji internal pada RC | `K8` | ≥ 99% sesi bebas crash | Febri |
| Q-10 | Uji usabilitas | 5 pelaku UMKM: dari buka pertama sampai Diagnosis Awal tampil | `K9` | Waktu tiap partisipan ≤ 5 menit (median dilaporkan) | Said (fasilitator), Febri |
| Q-11 | Frame rate | 5 alur utama, mode profile, perangkat acuan (Android RAM 4 GB, 60 Hz) | `K3` | 60 fps, jank < 1% (frame > 16,6 ms) | Said, Arya, Agam |
| Q-12 | Daftar periksa UU PDP | 10 item 8.2 | `K6` | 10 dari 10 | Rido, Febri |
| Q-13 | Regresi GWT dan alur utama | Seluruh GWT Bab 3 dan `integration_test` lima alur utama | DoD #1 | 100% GWT lulus | Febri, semua PIC |

**Aturan Gate Rilis:**

1. **Jadwal.** Code freeze Rabu Minggu 6, RC dipotong Rabu malam, pengukuran final Kamis–Jumat, peninjauan gate Jumat bersama Product Manager.
2. **Kelulusan.** Semua `K1`–`K9` harus hijau pada RC yang sama. Target yang gagal menjadi blocker rilis, kecuali Product Manager memberi pengecualian tertulis (1.5).
3. **Proposal kebijakan.** Pengecualian tidak diberikan untuk `K5` (halusinasi angka) dan `K6` (kepatuhan PDP), karena menyangkut kebenaran angka dan kewajiban hukum.
4. **Keparahan cacat.** P0 (crash, data hilang atau ganda, angka salah, kebocoran PII) memblokir rilis. P1 harus punya perbaikan atau solusi sementara tertulis. P2 masuk backlog.
5. **Pelaporan.** Febri menyerahkan satu laporan gate memuat nilai terukur `K1`–`K9`, versi RC, versi `scoring_config`, versi prompt dan model, serta daftar cacat terbuka.

#### 8.4 Tabel Mitigasi 9 Batasan Utama Sistem

| Kode | Batasan produk | Mekanisme teknis yang sudah dirancang | Indikator pantau atau uji | PIC |
| --- | --- | --- | --- | --- |
| M1 | **Bergantung pada disiplin catat pengguna.** Tanpa data, skor tidak akurat. | Pencatatan semurah mungkin: penjualan satu tap (`B2-01`), rekap harian satu angka (`B2-02`), pengingat 17:00 dan streak (`B2-06`), antrean offline (6.6). Kurangnya data tidak disembunyikan: indikator Disiplin (`S_D`), masalah `R08`, confidence yang turun lewat `hari_data` dan `R30` (3.6), Diagnosis Awal hari ke-1 (`E1-01`), dan batas keras confidence Rendah bila `hari_data` < 14. | `R30`, `K9`, Skor Tren | Arya, Rido, Said |
| M2 | **Struk buram, terlipat, atau tulisan tangan** sulit dibaca OCR. | Pra-cek ketajaman dan kompres di klien; kolom keyakinan < 0,80 atau selisih subtotal dan total > 1% berwarna kuning (`B1-02`, `YellowField`); dialog “Foto ulang” atau “Isi manual”; pesan ramah saat OCR timeout tanpa data setengah jadi (6.7). Struk tulisan tangan tidak dihitung di `K4`, tetapi dilaporkan terpisah. | Q-02 (kelompok ekstrem), Q-03 | Arya, Febri, Said |
| M3 | **Belanja di pasar tradisional tanpa struk.** | Pengeluaran manual dengan 10 kategori (`B2-03`), tersimpan sebagai `expense` bersumber `manual` (bobot 0,6). Kualitas sumber memengaruhi komponen V pada confidence (3.6), sehingga angka tetap dihitung dan keyakinannya jujur. | Komponen V pada confidence; Q-01 | Arya, Rido |
| M4 | **Struk hanya membuktikan pengeluaran**, bukan penjualan. | Struk disimpan sebagai `expense` saja (2.4); penjualan masuk lewat `B2-01`, `B2-02`, dan `B2-04`. Rekap harian hanya menambah selisih positif terhadap penjualan per transaksi sehingga tidak terhitung ganda; deteksi duplikat keras dan lunak (3.9). Teks bantu di layar Scan Struk menyatakan hal ini. | GWT `B2-02`, `B1-03`; Q-01 | Arya, Rido, Said |
| M5 | **Format CSV mutasi bank berbeda-beda.** | MVP menerima format umum (UTF-8, ≤ 5 MB, ≤ 5.000 baris, kolom tanggal, deskripsi, debit, kredit; pemisah koma atau titik koma). Pratinjau menandai tiap baris (cocok, belum tercatat, duplikat), pesan menyebut kolom yang hilang tanpa menyimpan apa pun, deduplikasi lewat hash baris, dan baris baru berstatus `belum_ditag` dengan tag massal (`B2-05`). Adaptor format per bank dicatat sebagai backlog Fase 2. | GWT `B2-04`; edge case CSV (6.7) | Arya, Rido |
| M6 | **Bobot `scoring_config` belum divalidasi ahli keuangan.** | Bobot dan ambang disimpan di `scoring_config` dan `rule_config` (berversi) sehingga dapat diubah tanpa rilis ulang. Setiap hitung tersimpan di `score_runs` agar dapat ditelusuri. Golden test mengunci perilaku (`K7`). Tumpang tindih Profitabilitas dan Efisiensi Biaya diakui dan menjadi bahan validasi (3.7). Perubahan bobot wajib memperbarui golden dengan persetujuan Product Manager (7.3). Validasi oleh ahli keuangan atau pendamping UMKM dijadwalkan sebelum peluncuran publik. | Q-01; versi `scoring_config` di laporan gate | Rido, Febri |
| M7 | **Biaya, kuota, dan ketergantungan internet untuk AI.** | Batas 30 pesan chat per pengguna per hari dan 100 pindai struk per usaha per hari (`AI_RATE_LIMIT`); cache narasi per versi data (`G8`); keluaran ≤ 600 token dan masukan ≤ 6 KB; timeout 8 detik (OCR 6 detik); fallback template tetap (`G7`); `ai_events` mencatat token dan biaya; penyedia dapat diganti lewat `AI_PROVIDER` dan `OCR_PROVIDER`. Laporan dan skor sepenuhnya dihitung kode sehingga tetap berjalan tanpa AI dan tanpa internet. Foto struk offline masuk `pending_receipts`. | `ai_events` (biaya, status fallback); Q-04, Q-08 | Febri, Rido, Arya |
| M8 | **Privasi data keuangan (UU PDP).** | Daftar periksa 10 item (8.2): persetujuan terpisah, log versi, cabut izin AI, minimisasi data (`G9`), TLS 1.3, AES-256-GCM dan SQLCipher, retensi foto 30 hari dan chat 90 hari, ekspor dan hapus akun. RLS per `business_id` dan `audit_logs`. Kajian hukum oleh pihak berwenang diperlukan sebelum peluncuran publik. | `K6` (Q-12) | Rido, Febri |
| M9 | **Batas klaim: bukan penilaian kelayakan kredit.** | `DisclaimerBanner` di layar skor, Growth, dan PDF (`D-05`, `F-04`); teks tetap “Rentang ini perkiraan, bukan jaminan pembiayaan” pada `F-05`; `G5` menolak kepastian kredit, saran hukum, dan saran pajak; tidak ada fitur pengajuan kredit di MVP; pemeriksaan otomatis kata terlarang (“layak kredit”, “pasti disetujui”, “jaminan pinjaman”) pada UI, template, dan prompt (DoD #5). | Q-05 (40 prompt); audit teks Minggu 6 | Said, Febri, Agam |
