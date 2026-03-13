import os

def list_images(folder: str, extensions=(".png", ".jpg", ".jpeg", ".webp")):
    """
    Lists image files in a folder with supported extensions.

    Args:
        folder (str): Path to the folder.
        extensions (tuple): Allowed image extensions.

    Returns:
        List[str]: Full paths to image files.
    """
    return [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.lower().endswith(extensions)
    ]

def validate_paths(paths):
    """
    Filters out paths that don't exist.

    Args:
        paths (List[str]): List of file paths.

    Returns:
        List[str]: Valid paths only.
    """
    return [p for p in paths if os.path.exists(p)]
