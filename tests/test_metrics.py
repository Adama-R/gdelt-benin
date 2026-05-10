# test_analysis.py

import pytest
import pandas as pd
from analysis.metrics import preprocess_gdelt, analyze_gdelt

# -------------------
# Tests pour preprocess_gdelt
# -------------------

def test_preprocess_invalid_values():
    df = pd.DataFrame({
        "SQLDATE": ["invalid"],
        "AvgTone": ["abc"],
        "GoldsteinScale": [None]
    })

    result = preprocess_gdelt(df)

    assert result["date"].isna().iloc[0]
    assert result["tone"].isna().iloc[0]

def test_preprocess_basic():
    df = pd.DataFrame({
        "SQLDATE": ["20230501", "20230502"],
        "AvgTone": ["1.5", "-0.2"],
        "GoldsteinScale": ["2.0", "3.5"]
    })

    df_processed = preprocess_gdelt(df)

    # Vérifie que les colonnes existent
    assert "date" in df_processed.columns
    assert "tone" in df_processed.columns
    assert "impact" in df_processed.columns

    # Vérifie le type
    assert pd.api.types.is_datetime64_any_dtype(df_processed["date"])
    assert pd.api.types.is_float_dtype(df_processed["tone"])
    assert pd.api.types.is_float_dtype(df_processed["impact"])

    # Vérifie la valeur correcte
    assert df_processed["tone"].iloc[0] == 1.5
    assert df_processed["impact"].iloc[1] == 3.5

def test_preprocess_invalid_values():
    df = pd.DataFrame({
        "SQLDATE": ["20230501", "invalid"],
        "AvgTone": ["1.0", "not_a_number"],
        "GoldsteinScale": ["NaN", "4.5"]
    })

    df_processed = preprocess_gdelt(df)

    # Date invalide devient NaT
    assert pd.isna(df_processed["date"].iloc[1])
    # Valeur non numérique devient NaN
    assert pd.isna(df_processed["tone"].iloc[1])
    assert pd.isna(df_processed["impact"].iloc[0])

def test_preprocess_copy_defensive():
    df = pd.DataFrame({
        "SQLDATE": ["20230501"],
        "AvgTone": ["1.0"],
        "GoldsteinScale": ["2.0"]
    })

    df_processed = preprocess_gdelt(df)
    # Modifier df_processed ne doit pas changer df original
    df_processed["tone"] = 999
    assert df["AvgTone"].iloc[0] == "1.0"

# -------------------
# Tests pour analyze_gdelt
# -------------------

def test_analyze_basic():
    df = pd.DataFrame({
        "SQLDATE": ["20230501", "20230501", "20230502"],
        "AvgTone": ["1.0", "2.0", "3.0"],
        "GoldsteinScale": ["0.5", "1.5", "2.5"],
        "Actor1Name": ["Alice", "Bob", "Alice"],
        "EventCode": ["01", "02", "01"]
    })

    df_processed = preprocess_gdelt(df)
    result = analyze_gdelt(df_processed)

    assert result["total_events"] == 3
    assert len(result["events_over_time"]) == 2
    assert result["top_actors"][0]["actor"] == "Alice"
    assert result["event_types"][0]["event_type"] == "01"
    assert result["tone"]["mean"] == pytest.approx(2.0)
    assert result["tone"]["min"] == 1.0
    assert result["tone"]["max"] == 3.0

def test_analyze_missing_columns():
    df = pd.DataFrame({
        "SQLDATE": ["20230501"],
        "AvgTone": ["1.0"],
        "GoldsteinScale": ["0.5"]
    })
    df_processed = preprocess_gdelt(df)
    result = analyze_gdelt(df_processed)

    # Colonnes manquantes
    assert result["top_actors"] == []
    assert result["event_types"] == []
    # Tone doit être calculé
    assert result["tone"]["mean"] == pytest.approx(1.0)

def test_analyze_empty_dataframe():
    df = pd.DataFrame(columns=["SQLDATE", "AvgTone", "GoldsteinScale", "Actor1Name", "EventCode"])
    df_processed = preprocess_gdelt(df)
    result = analyze_gdelt(df_processed)

    assert result["total_events"] == 0
    assert result["events_over_time"] == []
    assert result["top_actors"] == []
    assert result["event_types"] == []
    assert result["tone"]["mean"] != result["tone"]["mean"]  # NaN
