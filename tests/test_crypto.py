"""Tests for envchain.crypto module."""

import pytest
from envchain.crypto import encrypt, decrypt, generate_salt, derive_key, SALT_SIZE


def test_generate_salt_length():
    salt = generate_salt()
    assert len(salt) == SALT_SIZE


def test_generate_salt_is_random():
    assert generate_salt() != generate_salt()


def test_derive_key_deterministic():
    salt = generate_salt()
    key1 = derive_key("password", salt)
    key2 = derive_key("password", salt)
    assert key1 == key2


def test_derive_key_different_passwords():
    salt = generate_salt()
    assert derive_key("password1", salt) != derive_key("password2", salt)


def test_encrypt_returns_bytes():
    result = encrypt("hello", "secret")
    assert isinstance(result, bytes)


def test_encrypt_includes_salt():
    result = encrypt("hello", "secret")
    assert len(result) > SALT_SIZE


def test_encrypt_decrypt_roundtrip():
    plaintext = "MY_SECRET_VALUE"
    password = "strongpassword"
    token = encrypt(plaintext, password)
    assert decrypt(token, password) == plaintext


def test_decrypt_wrong_password_raises():
    token = encrypt("value", "correct")
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt(token, "wrong")


def test_decrypt_corrupted_data_raises():
    token = encrypt("value", "password")
    corrupted = token[:SALT_SIZE] + b"corrupted_garbage_data_here_1234"
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt(corrupted, "password")


def test_encrypt_different_ciphertexts_same_input():
    """Each encryption should produce a unique ciphertext due to random salt."""
    t1 = encrypt("same", "same")
    t2 = encrypt("same", "same")
    assert t1 != t2
