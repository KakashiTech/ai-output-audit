import random

from solution import crc16_modbus


def _reference(data: bytes) -> int:
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc


def test_standard_check_value():
    # CRC-16/MODBUS check value for "123456789"
    assert crc16_modbus(b"123456789") == 0x4B37


def test_empty_input():
    assert crc16_modbus(b"") == 0xFFFF


def test_matches_reference_implementation():
    rng = random.Random(1234)
    for _ in range(50):
        payload = bytes(rng.randrange(256) for _ in range(rng.randrange(0, 32)))
        assert crc16_modbus(payload) == _reference(payload)
