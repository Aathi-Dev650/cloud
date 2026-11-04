# CropCure AI

CropCure remains a crop disease assessment app. The Django API runs the supplied MobileNetV2 model, Auth0 handles farmer sign-in, Firestore stores profiles, reviewed disease guidance, and diagnosis history, and Dropbox stores uploaded leaf photos. Diagnosis documents keep only a private Dropbox path; the API creates short-lived preview links for the signed-in owner.

## Cloud setup

1. Copy `.env.example` to `.env` and set a long random `DJANGO_SECRET_KEY`.
2. In Auth0, create a **Single Page Application** and an API. Set the API identifier to the same value as `AUTH0_AUDIENCE`. Add `http://127.0.0.1:8000/` to the app's Allowed Callback URLs, Allowed Logout URLs, and Allowed Web Origins. Put the tenant domain, SPA client ID, and API identifier in `.env`.
3. In Firebase, create a project, enable Cloud Firestore, create/download a service account key, and save it at `secrets/firebase-service-account.json`. The `secrets/` folder is ignored by Git. Set `GOOGLE_APPLICATION_CREDENTIALS=secrets/firebase-service-account.json`. Create the `crop_analyses` composite index shown in `firebase/firestore.indexes.json` in the Firebase console.
4. Create a Dropbox app with **App folder** access. Grant `files.content.write` and `files.content.read`. Generate an access token, set `DROPBOX_ACCESS_TOKEN`, and keep it private. CropCure saves photos under `/CropCure/users/<private-user-folder>/`.
5. Install dependencies and initialize Django's staff/admin database:

   ```powershell
   python -m pip install -r requirements.txt
   python manage.py migrate
   python manage.py seed_disease_guidance
   python manage.py runserver
   ```

Open `http://127.0.0.1:8000/`. The browser loads the Auth0 SPA SDK from Auth0's CDN; the API validates the access token against the tenant JWKS and configured audience.

## Configuration

| Variable | Purpose |
| --- | --- |
| `AUTH0_DOMAIN` | Auth0 tenant domain, without `https://` |
| `AUTH0_CLIENT_ID` | Auth0 Single Page Application client ID |
| `AUTH0_AUDIENCE` | Identifier of the Auth0 API registered for CropCure |
| `AUTH0_CALLBACK_URL` | SPA redirect URL after sign-in |
| `AUTH0_LOGOUT_URL` | Approved return URL after sign-out |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to Firebase service account JSON |
| `FIREBASE_SERVICE_ACCOUNT_JSON` | Full Firebase service account JSON string (use this for Vercel environment variables) |
| `FIRESTORE_DATABASE` | Firestore database name, normally `(default)` |
| `DROPBOX_ACCESS_TOKEN` | Dropbox app token; do not commit it |
| `DROPBOX_ROOT` | Root folder for saved crop photos |

## Project folders

```text
cropcure_backend/              Django project settings and URL routing
disease_detection/             Crop disease app, API views, and model inference
auth0/                           Auth0 JWT authentication
firebase/                        Firestore client and Firestore indexes
dropbox_integration/             Dropbox photo storage (kept distinct from the Dropbox SDK package)
frontend/templates/             Django shell and farmer-facing pages
frontend/static/                CSS and browser JavaScript
frontend/legacy/                 Retained unused frontend helper
ml/                              Model training code and model artifacts
secrets/                         Local Firebase credentials; ignored by Git
```

## Data layout

- Firestore `users/{auth0-sub}` stores the farmer profile.
- Firestore `diseases/{model-label}` stores reviewed symptom, solution, and prevention guidance.
- Firestore `crop_analyses/{id}` stores an assessment, the Auth0 owner ID, and a private Dropbox path.
- Dropbox contains uploaded images. The API returns a temporary image link only after checking the signed-in owner's Firestore records.

The supplied PlantVillage subset has 15 classes across pepper, potato, and tomato. Train it with:

```powershell
python ml\train.py --data-dir "dataset\PlantVillage" --epochs 3
```

This creates `ml/artifacts/disease_model.keras` and `class_names.json`. Review model performance on representative local field images before relying on its confidence or guidance.

## API

- `GET/POST /api/disease/auth/me/` — read or update the signed-in farmer profile.
- `POST /api/disease/create/` — authenticated multipart image analysis; saves image to Dropbox and result to Firestore.
- `GET /api/disease/history/` — authenticated diagnosis history and temporary photo preview URLs.

The model supplies a crop/disease class only. Symptoms, recommended solution, and prevention come from the reviewed Firestore `diseases` collection. Seed the included catalogue with `python manage.py seed_disease_guidance` after configuring Firebase.

Existing MongoDB records and Django farmer accounts are not copied into Firestore/Auth0 automatically. The current service-account JSON, Auth0 secrets, Dropbox token, and `.env` must never be committed or pasted into chat.
