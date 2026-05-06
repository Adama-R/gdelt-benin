def test_load_invalid_paths():
    import pytest
    from loader import load_gdelt_data
    from fastapi import HTTPException

    with pytest.raises(HTTPException):
        load_gdelt_data([], "event")
