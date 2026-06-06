import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from main import app

client = TestClient(app)


def test_process_returns_processed_files(tmp_path):
    (tmp_path / "track.mp3").touch()
    (tmp_path / "beat.wav").touch()

    with patch("api.routes.process.separate_file") as mock_sep:
        response = client.post("/process", json={
            "input_folder": str(tmp_path),
            "output_folder": "/output",
        })

    assert response.status_code == 200
    data = response.json()
    assert len(data["processed"]) == 2
    assert data["errors"] == []
    assert mock_sep.call_count == 2


def test_process_empty_folder(tmp_path):
    with patch("api.routes.process.separate_file") as mock_sep:
        response = client.post("/process", json={
            "input_folder": str(tmp_path),
            "output_folder": "/output",
        })

    assert response.status_code == 200
    data = response.json()
    assert data["processed"] == []
    assert data["errors"] == []
    mock_sep.assert_not_called()


def test_process_collects_errors_without_stopping(tmp_path):
    (tmp_path / "good.mp3").touch()
    (tmp_path / "bad.wav").touch()

    def fake_separate(file_path, output_folder):
        if "bad" in file_path:
            raise RuntimeError("demucs failed")

    with patch("api.routes.process.separate_file", side_effect=fake_separate):
        response = client.post("/process", json={
            "input_folder": str(tmp_path),
            "output_folder": "/output",
        })

    assert response.status_code == 200
    data = response.json()
    assert len(data["processed"]) == 1
    assert len(data["errors"]) == 1
    assert "demucs failed" in data["errors"][0]["error"]


def test_process_missing_body():
    response = client.post("/process", json={})
    assert response.status_code == 422


def test_process_non_existent_folder():
    response = client.post("/process", json={
        "input_folder": "/does/not/exist",
        "output_folder": "/output",
    })
    assert response.status_code == 500
