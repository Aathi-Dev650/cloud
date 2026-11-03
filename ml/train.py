"""Train a MobileNetV2 crop-disease classifier using directory-labelled images.

Supported structures:

1. A dataset root containing ``Train`` and ``Val`` folders.
2. A flat dataset root containing one folder per class, such as the supplied
   ``dataset/PlantVillage/Tomato_Early_blight`` folders.  In this form the
   script creates a deterministic training/validation split.
"""
import argparse
import json
from pathlib import Path

import tensorflow as tf


IMAGE_SIZE = (224, 224)
IMAGE_SUFFIXES = {'.bmp', '.gif', '.jpeg', '.jpg', '.png'}


def _class_folders_with_images(data_dir):
    """Return only labelled folders that actually contain image files."""
    return sorted(
        folder.name
        for folder in data_dir.iterdir()
        if folder.is_dir()
        and any(file.is_file() and file.suffix.lower() in IMAGE_SUFFIXES for file in folder.iterdir())
    )


def build_model(class_count):
    augment = tf.keras.Sequential([
        tf.keras.layers.RandomFlip('horizontal'),
        tf.keras.layers.RandomRotation(0.08),
        tf.keras.layers.RandomZoom(0.12),
    ], name='augmentation')
    base = tf.keras.applications.MobileNetV2(
        input_shape=(*IMAGE_SIZE, 3), include_top=False, weights='imagenet'
    )
    base.trainable = False
    inputs = tf.keras.Input(shape=(*IMAGE_SIZE, 3))
    x = augment(inputs)
    x = tf.keras.applications.mobilenet_v2.preprocess_input(x)
    x = base(x, training=False)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dropout(0.25)(x)
    outputs = tf.keras.layers.Dense(class_count, activation='softmax')(x)
    model = tf.keras.Model(inputs, outputs)
    model.compile(optimizer=tf.keras.optimizers.Adam(1e-3), loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model, base


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-dir', required=True, type=Path, help='Dataset root containing class folders, or Train and Val folders.')
    parser.add_argument('--output-dir', default=Path('ml/artifacts'), type=Path)
    parser.add_argument('--epochs', default=3, type=int)
    parser.add_argument('--batch-size', default=32, type=int)
    parser.add_argument('--validation-split', default=0.15, type=float, help='Validation fraction for a flat class-folder dataset.')
    args = parser.parse_args()
    if not args.data_dir.is_dir():
        raise SystemExit(f'Dataset directory not found: {args.data_dir}')
    train_dir, val_dir = (args.data_dir / name for name in ('Train', 'Val'))
    if train_dir.is_dir() and val_dir.is_dir():
        train = tf.keras.utils.image_dataset_from_directory(train_dir, image_size=IMAGE_SIZE, batch_size=args.batch_size, shuffle=True, seed=42)
        labels = train.class_names
        validation = tf.keras.utils.image_dataset_from_directory(val_dir, class_names=labels, image_size=IMAGE_SIZE, batch_size=args.batch_size, shuffle=False)
    else:
        if not 0 < args.validation_split < 1:
            raise SystemExit('--validation-split must be between 0 and 1.')
        labels = _class_folders_with_images(args.data_dir)
        if len(labels) < 2:
            raise SystemExit('Expected at least two non-empty class folders below --data-dir.')
        train = tf.keras.utils.image_dataset_from_directory(
            args.data_dir, validation_split=args.validation_split, subset='training',
            seed=42, image_size=IMAGE_SIZE, batch_size=args.batch_size, shuffle=True,
            class_names=labels,
        )
        validation = tf.keras.utils.image_dataset_from_directory(
            args.data_dir, validation_split=args.validation_split, subset='validation',
            seed=42, image_size=IMAGE_SIZE, batch_size=args.batch_size,
            shuffle=False, class_names=labels,
        )
    autotune = tf.data.AUTOTUNE
    train, validation = train.prefetch(autotune), validation.prefetch(autotune)
    model, base = build_model(len(labels))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    model.fit(train, validation_data=validation, epochs=args.epochs)
    model.save(args.output_dir / 'disease_model.keras')
    (args.output_dir / 'class_names.json').write_text(json.dumps(labels, indent=2), encoding='utf-8')
    print(f'Saved MobileNetV2 model and {len(labels)} labels to {args.output_dir}.')


if __name__ == '__main__':
    main()
