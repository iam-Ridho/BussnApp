# BussnApp

Aplikasi kesiapan keuangan UMKM. Acuan: `docs/PRD_Teknis_BussnApp_Fix.md`.

## Struktur
- `backend/`: FastAPI + PostgreSQL + Redis (Rido, Febri)
- `frontend/`: Flutter (Arya, Agam, Said)
- `contracts/`: kontrak API; sumber kebenaran bersama backend dan frontend
- `docs/`: PRD, MVP, UML/ERD

## Alur kerja (PRD 7.3)
- Cabang tetap: `main` (hanya RC/rilis) dan `develop` (integrasi). Keduanya terproteksi.
- Cabang kerja dari `develop`: `feat/<ID>-<slug>` (mis. `feat/A-02-login`), `fix/<slug>`,
  `contract/<gelombang>-<slug>`, `chore/<slug>`. Hapus cabang setelah merge.
- Commit: Conventional Commits + ID fitur, mis. `feat(A-02): login JWT`.
- PR: judul `[A-02] ...`, satu ID fitur per PR, diff <= 400 baris di luar kode hasil generate.
- Merge: squash ke `develop`.
- Reviewer: 1 untuk PR umum; 2 untuk `contracts/`, `rule_engine/`, validator `ai_gateway/`,
  `core/sync/`, dan migrasi DB. PR Flutter yang menyentuh API wajib dibaca Rido atau Febri.
- Rahasia (kunci AES, kunci AI) tidak pernah di-commit.

## Kontrak API
`contracts/openapi.json` dihasilkan dari backend; jangan diedit tangan. Perubahan kontrak
lewat cabang `contract/<gelombang>-<slug>` dan butuh persetujuan backend dan frontend.

## Menjalankan
- Backend: menyusul setelah `backend/` di-push (lihat `backend/README.md`).
- Frontend: lihat `frontend/README.md`.