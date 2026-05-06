import pandas as pd


def test_event_count():
    from analysis.metrics import count_events

    df = pd.DataFrame({0: [1, 2, 3]})

    assert count_events(df) == 3
