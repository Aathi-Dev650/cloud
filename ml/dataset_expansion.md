# CropCure dataset expansion plan

The deployed model currently supports only the labels in
`ml/artifacts/class_names.json`. A crop is **not supported** merely because a
folder has been created for it; it becomes supported only after a retrained
model and matching `class_names.json` are deployed together.

## Data storage

Keep the master image collection outside this repository, in Google Drive,
Hugging Face, Kaggle, or object storage. Download a versioned training export
only for a training run. Do not store farmer-uploaded photos without explicit
consent and a retention policy.

## Folder format

Use one folder for each verified crop-condition label:

```text
dataset/CropCure-v2/
  Rice___Healthy/
  Rice___Bacterial_leaf_blight/
  Rice___Brown_spot/
  Rice___Leaf_blast/
  Banana___Healthy/
  Banana___Black_sigatoka/
  Banana___Panama_wilt/
  Chilli___Healthy/
  Chilli___Leaf_curl_virus/
  Chilli___Anthracnose/
  Brinjal___Healthy/
  Brinjal___Phomopsis_blight/
  Groundnut___Healthy/
  Groundnut___Tikka_leaf_spot/
  Cotton___Healthy/
  Cotton___Bacterial_blight/
  Sugarcane___Healthy/
  Sugarcane___Red_rot/
  Maize___Healthy/
  Maize___Leaf_blight/
  Unknown__non_crop_or_unusable/
```

Use only diagnoses verified by an agriculture expert or a trusted labelled
source. Keep a CSV alongside the images with `image_id`, `label`, `source`,
`district`, `season`, `device`, `field_or_lab`, and `expert_verified`.

## Minimum quality gate

For each label, collect at least 300 varied images before a first experiment;
aim for 1,000+ field images for production. Include different districts,
lighting, stages, varieties, phones, angles, and background clutter. Keep an
unseen field-only test set from different farms.

The `Unknown__non_crop_or_unusable` class should include healthy unsupported
crops, soil, hands, blurred photos, multiple leaves, insects, and unrelated
objects. It complements, but does not replace, the runtime confidence guard.

## Train and deploy

Run training outside the web server, preferably in Colab/Kaggle with a GPU:

```powershell
venv\Scripts\python.exe ml\train.py --data-dir "dataset\CropCure-v2" --epochs 15
```

Evaluate per-class precision/recall on the held-out field test set. Only then
replace both `ml/artifacts/disease_model.keras` and
`ml/artifacts/class_names.json` together, restart Django, and add reviewed
guidance for every new label.
