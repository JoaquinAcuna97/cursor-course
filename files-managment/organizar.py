from __future__ import annotations

import argparse
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


"""
Organiza archivos en subcarpetas por tipo, basándose en su extensión.

Uso básico:
  - Por defecto actúa sobre la carpeta Descargas del usuario.
  - Se puede especificar otra carpeta con --target.
  - Utiliza --dry-run para ver qué haría sin mover archivos.

Ejemplos:
  python organizar.py
  python organizar.py --target "C:/Users/usuario/Downloads"
  python organizar.py --dry-run
"""


# Categorías y sus extensiones asociadas
CATEGORIES: Dict[str, List[str]] = {
    "Imagenes": [
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".bmp",
        ".tiff",
        ".webp",
        ".svg",
        ".heic",
        ".avif",
    ],
    "Documentos": [
        ".pdf",
        ".doc",
        ".docx",
        ".txt",
        ".rtf",
        ".md",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
        ".csv",
        ".odt",
        ".ods",
        ".odp",
    ],
    "Videos": [
        ".mp4",
        ".mkv",
        ".mov",
        ".avi",
        ".wmv",
        ".flv",
        ".webm",
        ".m4v",
    ],
    "Audio": [
        ".mp3",
        ".wav",
        ".flac",
        ".aac",
        ".ogg",
        ".m4a",
        ".wma",
    ],
    "Comprimidos": [
        ".zip",
        ".rar",
        ".7z",
        ".tar",
        ".gz",
        ".bz2",
        ".xz",
        ".tar.gz",
        ".tar.bz2",
        ".tar.xz",
    ],
    "Instaladores": [
        ".exe",
        ".msi",
        ".pkg",
        ".dmg",
    ],
    "Codigo": [
        ".py",
        ".ipynb",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
        ".java",
        ".c",
        ".h",
        ".cpp",
        ".hpp",
        ".cs",
        ".rb",
        ".go",
        ".php",
        ".sh",
        ".bat",
        ".ps1",
        ".html",
        ".css",
        ".scss",
        ".json",
        ".yml",
        ".yaml",
        ".xml",
        ".toml",
        ".ini",
        ".cfg",
    ],
}

DEFAULT_OTHER_CATEGORY = "Otros"


@dataclass
class MovePlan:
    source: Path
    destination: Path
    category: str


def get_downloads_folder() -> Path:
    """Devuelve la carpeta de Descargas por defecto (Path.home()/"Downloads")."""
    return Path.home() / "Downloads"


def infer_category_from_extension(extension: str) -> str:
    lower_extension = extension.lower()
    for category_name, extensions in CATEGORIES.items():
        if lower_extension in extensions:
            return category_name
    return DEFAULT_OTHER_CATEGORY


def is_hidden_file(path: Path) -> bool:
    name = path.name
    return name.startswith(".")


def build_move_plan_for_directory(
    directory: Path,
    *,
    include_hidden: bool = False,
) -> List[MovePlan]:
    if not directory.exists() or not directory.is_dir():
        raise ValueError(f"La ruta objetivo no es válida: {directory}")

    plans: List[MovePlan] = []
    for child in directory.iterdir():
        if child.is_dir():
            continue
        if not include_hidden and is_hidden_file(child):
            continue

        file_extension = child.suffix.lower()
        category = infer_category_from_extension(file_extension)
        destination_dir = directory / category
        destination = destination_dir / child.name
        plans.append(MovePlan(source=child, destination=destination, category=category))

    return plans


def ensure_directory(path: Path) -> None:
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)


def generate_unique_destination_path(destination: Path) -> Path:
    """Si existe un archivo con el mismo nombre, genera un nombre único con sufijo.

    Ejemplo: archivo.txt -> archivo (1).txt, archivo (2).txt, ...
    """
    if not destination.exists():
        return destination

    stem = destination.stem
    suffix = destination.suffix
    parent = destination.parent

    counter = 1
    while True:
        candidate = parent / f"{stem} ({counter}){suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def apply_move_plan(plans: Iterable[MovePlan], *, dry_run: bool = False) -> Tuple[int, Dict[str, int]]:
    moved_count = 0
    per_category: Dict[str, int] = {}

    for plan in plans:
        ensure_directory(plan.destination.parent)
        unique_destination = generate_unique_destination_path(plan.destination)

        if dry_run:
            print(f"DRY-RUN: movería '{plan.source.name}' -> '{plan.destination.parent.name}/{unique_destination.name}'")
        else:
            shutil.move(str(plan.source), str(unique_destination))
            moved_count += 1
            per_category[plan.category] = per_category.get(plan.category, 0) + 1

    return moved_count, per_category


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Organiza archivos en subcarpetas por tipo (extensión)",
    )
    parser.add_argument(
        "--target",
        "-t",
        type=Path,
        default=get_downloads_folder(),
        help="Carpeta objetivo. Por defecto, Descargas del usuario",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Muestra qué acciones se realizarían sin mover archivos",
    )
    parser.add_argument(
        "--include-hidden",
        action="store_true",
        help="Incluye archivos ocultos (nombres que comienzan con '.')",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    target_dir: Path = args.target
    dry_run: bool = args.dry_run
    include_hidden: bool = args.include_hidden

    print(f"Objetivo: {target_dir}")
    if dry_run:
        print("Modo simulación (dry-run) activado: no se moverán archivos")

    plans = build_move_plan_for_directory(target_dir, include_hidden=include_hidden)
    moved_count, per_category = apply_move_plan(plans, dry_run=dry_run)

    if dry_run:
        print(f"Se planificaron {len(list(plans))} archivos para mover.")
    else:
        print(f"Archivos movidos: {moved_count}")
        if per_category:
            print("Detalle por categoría:")
            for category_name, count in sorted(per_category.items()):
                print(f"  - {category_name}: {count}")


if __name__ == "__main__":
    main()


