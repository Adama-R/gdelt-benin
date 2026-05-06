def test_preprocess_gdelt_basic():
    import pandas as pd
    from metrics import preprocess_gdelt

    df = pd.DataFrame({
        "SQLDATE": ["20250101"],
        "AvgTone": ["5.2"],
        "GoldsteinScale": ["3"]
    })

    result = preprocess_gdelt(df)

    assert "date" in result
    assert "tone" in result
    assert "impact" in result
    assert result["tone"].iloc[0] == 5.2

def test_preprocess_invalid_values():
    import pandas as pd
    from metrics import preprocess_gdelt

    df = pd.DataFrame({
        "SQLDATE": ["invalid"],
        "AvgTone": ["abc"],
        "GoldsteinScale": [None]
    })

    result = preprocess_gdelt(df)

    assert result["date"].isna().iloc[0]
    assert result["tone"].isna().iloc[0]

def test_analyze_gdelt_basic():
    import pandas as pd
    from metrics import analyze_gdelt

    df = pd.DataFrame({
        "date": pd.to_datetime(["2025-01-01"]),
        "Actor1Name": ["France"],
        "EventCode": ["010"],
        "tone": [2.0]
    })

    result = analyze_gdelt(df)

    assert result["total_events"] == 1
    assert len(result["top_actors"]) == 1
