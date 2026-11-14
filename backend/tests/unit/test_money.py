from decimal import Decimal as D

import pytest

from app.rule_engine.money import clip, lin, round_score, rupiah, to_decimal


def test_lin_naik():
    assert lin(D("0.10"), D("0"), D("0.20")) == D(50)


def test_lin_turun_a_lebih_besar_dari_b():
    assert lin(D("0.45"), D("0.7"), D("0.2")) == D(50)


def test_lin_dijepit_di_ujung():
    assert lin(D("-1"), D("0"), D("0.2")) == D(0)
    assert lin(D("9"), D("0"), D("0.2")) == D(100)


def test_lin_a_sama_b_ditolak():
    with pytest.raises(ValueError):
        lin(D(1), D(1), D(1))


def test_pembulatan_half_up_bukan_ke_genap():
    assert round_score(D("0.5")) == 1
    assert round_score(D("2.5")) == 3  # round(2.5) bawaan Python = 2
    assert rupiah(D("1234.5")) == 1235


def test_float_ditolak():
    with pytest.raises(TypeError):
        to_decimal(0.1)


def test_clip():
    assert clip(D(5), D(0), D(3)) == D(3)
