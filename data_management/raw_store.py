
import hashlib
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def save_raw(
    data: bytes,
    municipality: str,
    resource_type: str
) -> tuple[str, str]:

    extensions = {
        "html": ".html",
        "pdf": ".pdf",
    }

    if resource_type not in extensions:
        raise ValueError(
            f"Nieobsługiwany typ zasobu: {resource_type}"
        )

    checksum = hashlib.sha256(data).hexdigest()

    directory = (
        PROJECT_ROOT
        / "data"
        / "raw"
        / municipality
        / resource_type
    )

    directory.mkdir(parents=True, exist_ok=True)

    filename = checksum + extensions[resource_type]
    file_path = directory / filename

    if not file_path.exists():
        file_path.write_bytes(data)

    relative_path = file_path.relative_to(PROJECT_ROOT)

    return relative_path.as_posix(), checksum
