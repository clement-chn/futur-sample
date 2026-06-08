from unittest.mock import patch, call
from api.core.separator import separate_file


def test_calls_demucs_with_correct_args():
    """
    Vérifie que separate_file appelle demucs.separate.main avec exactement
    les bons arguments : --two-stems=other pour isoler le stem mélodique,
    -o pour le dossier de sortie, et le chemin du fichier à traiter.

    Demucs est mocké (remplacé par un faux) pour ne pas lancer
    de vrai traitement audio pendant le test.
    """
    with patch("api.core.separator.demucs.separate.main") as mock_main:
        separate_file("/input/track.mp3", "/output")

    mock_main.assert_called_once_with([
        "--two-stems=other",
        "-o", "/output",
        "/input/track.mp3",
    ])


def test_propagates_demucs_exception():
    """
    Vérifie que si Demucs lève une exception (fichier corrompu,
    mémoire insuffisante...), separate_file la propage sans l'avaler.
    La route /process pourra ainsi la capturer et la mettre dans errors[].
    """
    with patch("api.core.separator.demucs.separate.main", side_effect=RuntimeError("demucs failed")):
        try:
            separate_file("/input/track.mp3", "/output")
            assert False, "expected RuntimeError"
        except RuntimeError as e:
            assert "demucs failed" in str(e)
