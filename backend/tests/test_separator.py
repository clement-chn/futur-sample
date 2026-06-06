from unittest.mock import patch, call
from api.core.separator import separate_file


def test_calls_demucs_with_correct_args():
    with patch("api.core.separator.demucs.separate.main") as mock_main:
        separate_file("/input/track.mp3", "/output")

    mock_main.assert_called_once_with([
        "--two-stems=other",
        "-o", "/output",
        "/input/track.mp3",
    ])


def test_propagates_demucs_exception():
    with patch("api.core.separator.demucs.separate.main", side_effect=RuntimeError("demucs failed")):
        try:
            separate_file("/input/track.mp3", "/output")
            assert False, "expected RuntimeError"
        except RuntimeError as e:
            assert "demucs failed" in str(e)
