from fleetlens.paths import ensure_parent


def test_ensure_parent_creates_directory(tmp_path):
    target = ensure_parent(tmp_path / "nested" / "file.txt")
    assert target.parent.exists()
