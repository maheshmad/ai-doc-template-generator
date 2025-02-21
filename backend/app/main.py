from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import router
from app.templates_service import router as pdf_router
from app.config import Config
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(router)
app.include_router(pdf_router)

@app.head('/health')
@app.get('/health')
def health_check():
    return 'ok'