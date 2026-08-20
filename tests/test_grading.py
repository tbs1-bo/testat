import pytest

from utils import gym_grading, ihk_grading


def test_gym_grading_liefert_0_7_ab_95_prozent():
    assert gym_grading(95) == 0.7


def test_gym_grading_liefert_1_0_ab_90_prozent():
    assert gym_grading(90) == 1


def test_gym_grading_liefert_1_3_ab_85_prozent():
    assert gym_grading(85) == 1.3


def test_gym_grading_liefert_1_7_ab_80_prozent():
    assert gym_grading(80) == 1.7


def test_gym_grading_liefert_2_0_ab_75_prozent():
    assert gym_grading(75) == 2


def test_gym_grading_liefert_2_3_ab_70_prozent():
    assert gym_grading(70) == 2.3


def test_gym_grading_liefert_2_7_ab_65_prozent():
    assert gym_grading(65) == 2.7


def test_gym_grading_liefert_3_0_ab_60_prozent():
    assert gym_grading(60) == 3


def test_gym_grading_liefert_3_3_ab_55_prozent():
    assert gym_grading(55) == 3.3


def test_gym_grading_liefert_3_7_ab_50_prozent():
    assert gym_grading(50) == 3.7


def test_gym_grading_liefert_4_0_ab_45_prozent():
    assert gym_grading(45) == 4


def test_gym_grading_liefert_4_3_ab_40_prozent():
    assert gym_grading(40) == 4.3


def test_gym_grading_liefert_4_7_ab_33_prozent():
    assert gym_grading(33) == 4.7


def test_gym_grading_liefert_5_0_ab_27_prozent():
    assert gym_grading(27) == 5


def test_gym_grading_liefert_5_3_ab_20_prozent():
    assert gym_grading(20) == 5.3


def test_gym_grading_liefert_6_0_unter_20_prozent():
    assert gym_grading(19) == 6


def test_ihk_grading_liefert_6_0_bei_0_prozent():
    assert ihk_grading(0) == 6.0


def test_ihk_grading_liefert_4_4_bei_50_prozent():
    assert ihk_grading(50) == 4.4


def test_ihk_grading_liefert_1_0_bei_100_prozent():
    assert ihk_grading(100) == 1.0


def test_ihk_grading_wirft_keyerror_bei_prozentwert_ausserhalb_von_0_bis_100():
    with pytest.raises(KeyError):
        ihk_grading(101)
