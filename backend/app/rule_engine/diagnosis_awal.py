"""Diagnosis Awal, hari_data = 0 (PRD 3.6, E1-01).

S_A0 = 100 * (30*NIB + 25*Rek + 15*Setup) / 70
S_B0 = lin(DAR; 0.7, 0.2)
Skor0 = (S_A0 + S_B0) / 2
"""

from dataclasses import dataclass
from decimal import Decimal

from app.rule_engine.money import HUNDRED, lin, round_score


@dataclass(frozen=True)
class DiagnosisAwalInput:
    nib_punya: bool
    rekening_terpisah: bool
    setup_lengkap: bool
    total_utang: int
    total_aset: int


@dataclass(frozen=True)
class DiagnosisAwalResult:
    skor: int
    s_a0: Decimal
    s_b0: Decimal
    dar: Decimal
    n_ind: int = 2
    provisional: bool = True


def debt_to_asset_ratio(utang: int, aset: int) -> Decimal:
    """Keputusan MVP: aset 0 dan utang 0 -> 0; aset 0 dan utang > 0 -> 1 (terburuk)."""
    if aset == 0:
        return Decimal(0) if utang == 0 else Decimal(1)
    return Decimal(utang) / Decimal(aset)


def diagnosis_awal(inp: DiagnosisAwalInput) -> DiagnosisAwalResult:
    s_a0 = (
        HUNDRED
        * Decimal(30 * inp.nib_punya + 25 * inp.rekening_terpisah + 15 * inp.setup_lengkap)
        / Decimal(70)
    )
    dar = debt_to_asset_ratio(inp.total_utang, inp.total_aset)
    s_b0 = lin(dar, Decimal("0.7"), Decimal("0.2"))
    return DiagnosisAwalResult(skor=round_score((s_a0 + s_b0) / 2), s_a0=s_a0, s_b0=s_b0, dar=dar)
