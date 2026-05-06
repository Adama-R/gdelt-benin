def test_get_gdelt_files_valid_range():
    from ingestion import get_gdelt_files

    files = get_gdelt_files("20240101", "20240103")

    assert isinstance(files, list)
    assert len(files) >= 1
    assert all(f.endswith(".CSV.zip") for f in files)


def test_get_gdelt_files_invalid_range():
    from ingestion import get_gdelt_files

    files = get_gdelt_files("20250105", "20250101")

    assert files == []
