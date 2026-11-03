"""Create a versioned, directory-labelled CropCure training export.

This script deliberately keeps downloaded sources under ``dataset/sources`` and
copies only the documented, mapped labels into ``dataset/curated/CropCure-v2``.
Run it after reviewing sources; it does not train or replace the deployed model.
"""
from __future__ import annotations

import io
import json
import shutil
from collections import Counter
from pathlib import Path

import pyarrow.parquet as pq
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / 'dataset' / 'sources'
OUTPUT = ROOT / 'dataset' / 'curated' / 'CropCure-v2'

RICE_LABELS = {
    'healthy_rice_leaf': 'Rice___Healthy',
    'bacterial_leaf_blight': 'Rice___Bacterial_leaf_blight',
    'brown_spot': 'Rice___Brown_spot',
    'leaf_blast': 'Rice___Leaf_blast',
    'leaf_scald': 'Rice___Leaf_scald',
    'sheath_blight': 'Rice___Sheath_blight',
}
BANANA_LABELS = {
    0: 'Banana___Healthy',
    1: 'Banana___Black_sigatoka',
    2: 'Banana___Bract_mosaic_virus',
    3: 'Banana___Insect_pest',
    4: 'Banana___Moko_disease',
    5: 'Banana___Panama_disease',
    6: 'Banana___Yellow_sigatoka',
}


def prepare_rice(counts: Counter):
    source_root = SOURCES / 'rice_leaf_disease_classification' / 'rice_leaves'
    for source_name, target_name in RICE_LABELS.items():
        image_dir = source_root / source_name / 'images'
        if not image_dir.is_dir():
            raise SystemExit(f'Rice source folder missing: {image_dir}')
        target = OUTPUT / target_name
        target.mkdir(parents=True, exist_ok=True)
        for image_path in image_dir.iterdir():
            if image_path.suffix.lower() not in {'.jpg', '.jpeg', '.png'}:
                continue
            destination = target / f'rice_{source_name}_{image_path.name}'
            shutil.copy2(image_path, destination)
            counts[target_name] += 1


def prepare_banana(counts: Counter):
    source_root = SOURCES / 'banana_disease_classification' / 'data'
    for parquet_path in sorted(source_root.glob('*.parquet')):
        table = pq.read_table(parquet_path, columns=['image', 'label'])
        for row_index, (image, label) in enumerate(zip(table['image'].to_pylist(), table['label'].to_pylist())):
            target_name = BANANA_LABELS.get(label)
            image_bytes = image.get('bytes') if isinstance(image, dict) else None
            if not target_name or not image_bytes:
                raise SystemExit(f'Unexpected banana record in {parquet_path.name}, row {row_index}')
            target = OUTPUT / target_name
            target.mkdir(parents=True, exist_ok=True)
            # Decode/re-encode to a regular RGB JPEG, so Keras can use it as a
            # normal directory image dataset without Hugging Face dependencies.
            with Image.open(io.BytesIO(image_bytes)) as decoded:
                decoded.convert('RGB').save(target / f'banana_{parquet_path.stem}_{row_index:04d}.jpg', quality=95)
            counts[target_name] += 1


def main():
    if OUTPUT.exists() and any(OUTPUT.iterdir()):
        raise SystemExit(f'{OUTPUT} already contains data. Choose a new curated version rather than overwriting it.')
    OUTPUT.mkdir(parents=True, exist_ok=True)
    counts: Counter = Counter()
    prepare_rice(counts)
    prepare_banana(counts)
    manifest = {
        'version': 'CropCure-v2',
        'sources': [
            {'name': 'rice_leaf_disease_classification', 'license_file': 'dataset/sources/rice_leaf_disease_classification/LICENSE'},
            {'name': 'banana-disease-classification', 'license': 'CC-BY-4.0', 'repository': 'https://huggingface.co/datasets/as-cle-bert/banana-disease-classification'},
        ],
        'class_counts': dict(sorted(counts.items())),
        'note': 'This export is a training candidate. Validate labels and hold out field images before deployment.',
    }
    (OUTPUT / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
