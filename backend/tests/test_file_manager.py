import os
import pytest
from api.core.file_manager import scan_folder


def test_returns_audio_files_only(tmp_path):
    """
    Vérifie que scan_folder ne retourne que les fichiers audio
    et ignore les autres types de fichiers (.txt, .png...).
    """
    (tmp_path / "track.mp3").touch()
    (tmp_path / "beat.wav").touch()
    (tmp_path / "notes.txt").touch()
    (tmp_path / "cover.png").touch()

    result = scan_folder(str(tmp_path))

    assert sorted(result) == sorted([
        str(tmp_path / "track.mp3"),
        str(tmp_path / "beat.wav"),
    ])


def test_all_supported_extensions(tmp_path):
    """
    Vérifie que les 4 extensions supportées sont toutes reconnues :
    mp3, wav, flac, ogg.
    """
    for name in ["a.mp3", "b.wav", "c.flac", "d.ogg"]:
        (tmp_path / name).touch()

    result = scan_folder(str(tmp_path))
    assert len(result) == 4


def test_case_insensitive_extension(tmp_path):
    """
    Vérifie que la détection d'extension est insensible à la casse :
    MP3 et WAV (majuscules) doivent être reconnus comme mp3 et wav.
    """
    (tmp_path / "track.MP3").touch()
    (tmp_path / "beat.WAV").touch()

    result = scan_folder(str(tmp_path))
    assert len(result) == 2


def test_empty_folder(tmp_path):
    """
    Vérifie que scan_folder retourne une liste vide
    si le dossier ne contient aucun fichier.
    """
    assert scan_folder(str(tmp_path)) == []


def test_no_audio_files(tmp_path):
    """
    Vérifie que scan_folder retourne une liste vide
    si le dossier contient des fichiers mais aucun fichier audio.
    """
    (tmp_path / "readme.md").touch()
    (tmp_path / "data.json").touch()

    assert scan_folder(str(tmp_path)) == []


def test_ignores_subdirectories(tmp_path):
    """
    Vérifie que scan_folder ignore les sous-dossiers,
    même si leur nom ressemble à un fichier audio (ex: "subdir.mp3").
    """
    subdir = tmp_path / "subdir.mp3"
    subdir.mkdir()

    result = scan_folder(str(tmp_path))
    assert result == []


def test_returns_absolute_paths(tmp_path):
    """
    Vérifie que les chemins retournés par scan_folder sont absolus
    (commencent par /), pas relatifs. Nécessaire pour passer les chemins
    directement à Demucs sans ambiguïté.
    """
    (tmp_path / "track.mp3").touch()

    result = scan_folder(str(tmp_path))
    assert all(os.path.isabs(p) for p in result)
