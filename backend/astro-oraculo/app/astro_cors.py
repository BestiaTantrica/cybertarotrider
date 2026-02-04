from fastapi.middleware.cors import CORSMiddleware
from .astro_main import app  # import the existing app with endpoints

# Configure CORS to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api = app
