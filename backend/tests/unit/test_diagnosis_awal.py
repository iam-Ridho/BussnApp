"""Nilai harapan dihitung tangan (bukan dari keluaran kode):
NIB=ya, Rek=tidak, Setup=ya -> S_A0 = 100*(30+15)/70 = 64.2857...
DAR = 4.500.000 / 10.000.000 = 0.45 -> S_B0 = 50
Skor0 = (64.2857 + 50) / 2 = 57.14 -> 57
"""

from decimal import Decimal as D

from app.rule_engine.diagnosis_awal import DiagnosisAwalInput, diagnosis_awal


def test_contoh_hitung_tangan():
    r = diagnosis_awal(
        DiagnosisAwalInput(True, False, True, total_utang=4_500_000, total_aset=10_000_000)
    )
    assert r.skor == 57
    assert r.s_b0 == D(50)
    assert r.provisional and r.n_ind == 2


def test_semua_terpenuhi_tanpa_utang():
    r = diagnosis_awal(DiagnosisAwalInput(True, True, True, 0, 10_000_000))
    assert r.skor == 100


def test_aset_nol_utang_nol():
    r = diagnosis_awal(DiagnosisAwalInput(False, False, False, 0, 0))
    assert r.dar == 0 and r.skor == 50  # S_A0=0, S_B0=100


def test_aset_nol_utang_ada_terburuk():
    r = diagnosis_awal(DiagnosisAwalInput(False, False, False, 1_000_000, 0))
    assert r.dar == 1 and r.skor == 0


def test_deterministik_berulang():
    inp = DiagnosisAwalInput(True, False, True, 3_000_000, 7_000_000)
    assert len({diagnosis_awal(inp).skor for _ in range(100)}) == 1
