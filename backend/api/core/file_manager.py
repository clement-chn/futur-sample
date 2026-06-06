import os

AUDIO_EXTENSIONS = {"mp3", "wav", "flac", "ogg"}


def scan_folder(folder: str) -> list[str]:
    return [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if os.path.isfile(os.path.join(folder, f))
        and f.rsplit(".", 1)[-1].lower() in AUDIO_EXTENSIONS
    ]
