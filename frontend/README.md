# Frontend (Flutter)

Status: skeleton belum dibuat.

## Membuat skeleton (satu orang saja, disarankan Arya)
1. `git pull` dari `develop`, buat cabang `chore/frontend-skeleton`.
2. Sepakati dulu `--org` bersama tim (menjadi application ID; sulit diubah setelah rilis).
3. Dari folder `frontend/`:
   `flutter create --org <org-id> --project-name bussnapp .`
4. Buat PR. Yang lain menunggu sampai merge supaya tidak konflik di android/, ios/, pubspec.yaml.

## Struktur kode yang dituju (PRD 7.3)
- `lib/core/{design_system,network,storage,sync,utils}`
- `lib/features/<fitur>/{presentation,domain,data}`
- Antar-fitur tidak saling mengimpor lapisan dalam; berbagi kode hanya lewat `core/`.
- Tidak ada rumus bisnis di layar: semua angka berasal dari respons server.

## Terhubung ke backend lokal
- Emulator Android: `http://10.0.2.2:8000`. iOS Simulator: `http://localhost:8000`.
- HP fisik: jalankan backend dengan `--host 0.0.0.0`, lalu pakai IP laptop di jaringan yang sama.
- Kontrak resmi pertama (auth) menyusul. Sebelum itu kerjakan `design_system` dan `core/`
  dengan data tiruan.
