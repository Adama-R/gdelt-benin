# test_filter.py

import pytest
import pandas as pd
from fastapi import HTTPException
from ingestion.filter import link_mentions_to_events

def test_link_mentions_to_events():
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

    events = pd.DataFrame({
        "GLOBALEVENTID": [1],
        "ActionGeo_CountryCode": ["FR"]
    })

    mentions = pd.DataFrame({
        "GLOBALEVENTID": [1]
    })

    with pytest.raises(HTTPException):
        link_mentions_to_events(mentions, events, "BN")
