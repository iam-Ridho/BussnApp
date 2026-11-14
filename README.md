# BussnApp

Aplikasi kesiapan keuangan UMKM. Acuan: `docs/PRD_Teknis_BussnApp_Fix.md`.

## Struktur
- `backend/`: FastAPI + PostgreSQL + Redis (Rido, Febri)
- `frontend/`: Flutter (Arya, Agam, Said)
- `contracts/`: kontrak API; sumber kebenaran bersama backend dan frontend
- `docs/`: PRD, MVP, UML/ERD

## Alur kerja (PRD 7.3)
- Cabang tetap: `main` (hanya RC/rilis) dan `develop` (integrasi).
- Cabang kerja dari `develop`: `feat/<ID>-<slug>` (mis. `feat/A-02-login`), `fix/<slug>`,
  `contract/<gelombang>-<slug>`, `chore/<slug>`. Hapus cabang setelah merge.
- Commit: Conventional Commits + ID fitur, mis. `feat(A-02): login JWT`.
- PR: judul `[A-02] ...`, satu ID fitur per PR.
- Merge: squash ke `develop`.
- Merge ke `develop` setelah CI hijau. Reviewer tidak diwajibkan.
- Perubahan di `contracts/` dan `backend/migrations/`: kabari grup sebelum merge.
- Rahasia (kunci AES, kunci AI) tidak pernah di-commit.

## Kontrak API
`contracts/openapi.json` dihasilkan dari backend; jangan diedit tangan. Perubahan kontrak
lewat cabang `contract/<gelombang>-<slug>` dan diumumkan ke tim.

## Menjalankan
- Backend: lihat `backend/README.md`.
- Frontend: lihat `frontend/README.md`.