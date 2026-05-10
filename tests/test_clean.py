import pandas as pd
import pytest

def test_filter_benin():
    from processing.clean import filter_benin

    data = {
        51: ["BN", "US", "BN"]  # colonne pays GDELT
    }

    df = pd.DataFrame(data)

    with pytest.raises(ValueError):
        filter_benin(df, 'mention')


def test_filter_empty():
    from processing.clean import filter_benin

    df = pd.DataFrame({51: ["US", "FR"]})

    with pytest.raises(KeyError):
        filter_benin(df, 'gkg')

def test_filter_benin_event():
    import pandas as pd
    from processing.clean import filter_benin

    df = pd.DataFrame({
        "ActionGeo_CountryCode": ["BN", "FR"]
    })

    result = filter_benin(df, "event")

    assert len(result) == 1
