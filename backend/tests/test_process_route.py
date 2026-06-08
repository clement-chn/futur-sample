import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from main import app

client = TestClient(app)


def test_process_returns_processed_files(tmp_path):
    """
    Scénario nominal : dossier avec 2 fichiers audio valides.
    Vérifie que la route retourne bien 2 entrées dans processed[],
    que errors[] est vide, et que Demucs a été appelé exactement 2 fois.
    """
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
    """
    Scénario dossier vide : aucun fichier audio présent.
    Vérifie que la route retourne processed: [] et errors: [],
    et que Demucs n'est jamais appelé.
    """
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
    """
    Scénario d'erreur partielle : 1 fichier traitable + 1 fichier
    qui fait crasher Demucs (ex: fichier corrompu).
    Vérifie que le fichier valide est bien traité, que l'erreur
    est capturée dans errors[], et que le traitement ne s'interrompt pas.
    """
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


# TESTS FONCTIONNELS


def test_process_missing_body():
    """
    Scénario body invalide : la requête n'envoie pas input_folder
    ni output_folder. Vérifie que FastAPI retourne une erreur 422
    (Unprocessable Entity) grâce à la validation Pydantic automatique.
    """
    response = client.post("/process", json={})
    assert response.status_code == 422


def test_process_non_existent_folder():
    """
    Scénario dossier inexistant : input_folder pointe vers un chemin
    qui n'existe pas sur le système de fichiers.
    Vérifie que la route retourne une erreur 500 avec un message explicite,
    plutôt qu'un crash Python cryptique.
    """
    response = client.post("/process", json={
        "input_folder": "/does/not/exist",
        "output_folder": "/output",
    })
    assert response.status_code == 500
