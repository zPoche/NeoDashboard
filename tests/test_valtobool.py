import pytest

from app import valtobool


def test_valtobool_truthy_strings():
    for value in ('y', 'yes', 't', 'true', 'on', '1', 'True', 'YES'):
        assert valtobool(value) is True


def test_valtobool_falsey_strings():
    for value in ('n', 'no', 'f', 'false', 'off', '0', 'False', 'NO'):
        assert valtobool(value) is False


def test_valtobool_bool_passthrough():
    assert valtobool(True) is True
    assert valtobool(False) is False


def test_valtobool_int_passthrough():
    assert valtobool(1) is True
    assert valtobool(0) is False


def test_valtobool_invalid_raises():
    with pytest.raises(ValueError, match="invalid truth value"):
        valtobool('maybe')
