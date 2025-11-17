from pathlib import Path

def get_file_and_path(full_path: str):
    path_obj = Path(full_path)
    filename_stem = path_obj.stem
    directory_path = path_obj.parent
    return filename_stem, directory_path


def xml_escape(text):
    """转义XML特殊字符"""
    return (str(text).replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                    .replace("\"", "&quot;")
                    .replace("'", "&apos;")
                    .replace("\u3000", "　"))