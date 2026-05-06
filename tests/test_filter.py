def test_filter_by_date():
    from ingestion import filter_files_by_date

    files = [
        "20250101.export.CSV.zip",
        "20250102.export.CSV.zip",
        "20240101.export.CSV.zip",
    ]

    filtered = filter_files_by_date(files, "20250101", "20250102")

    assert len(filtered) == 2
