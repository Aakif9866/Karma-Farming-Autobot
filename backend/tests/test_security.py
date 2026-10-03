from app.core.security import hash_password, verify_password


def test_hash_roundtrip() -> None:
    h = hash_password("s3cret")
    assert h != "s3cret"
    assert verify_password(h, "s3cret")
    assert not verify_password(h, "wrong")
