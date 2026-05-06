import pandas as pd


def test_filter_benin():
    from processing import filter_benin

    data = {
        51: ["BN", "US", "BN"]  # colonne pays GDELT
    }

    df = pd.DataFrame(data)

    result = filter_benin(df)

    assert len(result) == 2


def test_filter_empty():
    from processing import filter_benin

    df = pd.DataFrame({51: ["US", "FR"]})

    result = filter_benin(df)

    assert result.empty
