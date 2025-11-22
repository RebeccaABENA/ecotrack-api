


from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from .database import engine
from .models import Base
from .auth import router as auth_router
from .indicators_routes import router as indicators_router
Base.metadata.create_all(bind=engine)
from pathlib import Path
app = FastAPI(title="EcoTrack API")
BASE_DIR = Path(__file__).resolve().parent
INDEX_FILE = BASE_DIR / "index.html"


@app.get("/", response_class=HTMLResponse)
def serve_index():
    """
    Sert le front-end (index.html) situé directement dans le dossier app/.
    """
    if not INDEX_FILE.exists():
        # Petit message clair si jamais le fichier n'est pas trouvé
        return HTMLResponse(
            "<h1>index.html introuvable</h1><p>Place le fichier dans le dossier app/.</p>",
            status_code=500,
        )
    return INDEX_FILE.read_text(encoding="utf-8")


# Inclusion des routes API
app.include_router(auth_router)
app.include_router(indicators_router)
