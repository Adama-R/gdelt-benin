def test_filter_by_date():
    from ingestion import filter_files_by_date

    files = [
        "20250101.export.CSV.zip",
        "20250102.export.CSV.zip",
        "20240101.export.CSV.zip",
    ]

    filtered = filter_files_by_date(files, "20250101", "20250102")

    assert len(filtered) == 2

def test_link_mentions_to_events():
    import pandas as pd
    from filtre import link_mentions_to_events

    events = pd.DataFrame({
        "GLOBALEVENTID": [1],
        "ActionGeo_CountryCode": ["BN"]
    })

    mentions = pd.DataFrame({
        "GLOBALEVENTID": [1]
    })

    result = link_mentions_to_events(mentions, events, "BN")

    assert len(result) == 1

def test_no_match():
    import pandas as pd
    from filtre import link_mentions_to_events
    from fastapi import HTTPException

    events = pd.DataFrame({
        "GLOBALEVENTID": [1],
        "ActionGeo_CountryCode": ["FR"]
    })

    mentions = pd.DataFrame({
        "GLOBALEVENTID": [1]
    })

    with pytest.raises(HTTPException):
        link_mentions_to_events(mentions, events, "BN")
