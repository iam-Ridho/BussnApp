"""Primitif hitung deterministik (PRD 3.0). Semua memakai Decimal, tanpa float.

Aturan pembulatan (keputusan MVP):
- Nominal Rupiah: ROUND_HALF_UP ke bilangan bulat, per baris item.
- Rasio disimpan penuh; dibulatkan hanya saat ditampilkan.
- Skor akhir: ROUND_HALF_UP. Jangan pakai round() bawaan Python (membulatkan ke genap).
"""

from decimal import ROUND_HALF_UP, Decimal

ZERO = Decimal(0)
ONE = Decimal(1)
HUNDRED = Decimal(100)


def to_decimal(x: int | str | Decimal) -> Decimal:
    if isinstance(x, float):
        raise TypeError("float dilarang di Rule Engine; pakai int, str, atau Decimal")
    return Decimal(x)


def rupiah(x: Decimal) -> int:
    return int(x.quantize(ONE, rounding=ROUND_HALF_UP))


def round_score(x: Decimal) -> int:
    return int(x.quantize(ONE, rounding=ROUND_HALF_UP))


def clip(x: Decimal, a: Decimal, b: Decimal) -> Decimal:
    return max(a, min(b, x))


def lin(x: Decimal, a: Decimal, b: Decimal) -> Decimal:
    """100 * clip((x - a) / (b - a), 0, 1). Berlaku untuk a < b maupun a > b."""
    if a == b:
        raise ValueError("lin() butuh a != b")
    return HUNDRED * clip((x - a) / (b - a), ZERO, ONE)
