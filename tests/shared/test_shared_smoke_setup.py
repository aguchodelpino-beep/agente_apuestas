from pathlib import Path


def test_shared_paths_exist():
    assert Path("shared").exists()
    assert Path("tests/shared").exists()


def test_history_dir_exists():
    assert Path("data/history").exists()
