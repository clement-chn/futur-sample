import demucs.separate


def separate_file(file_path: str, output_folder: str) -> None:
    demucs.separate.main([
        "--two-stems=other",
        "-o", output_folder,
        file_path,
    ])
