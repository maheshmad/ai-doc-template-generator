import logging
import traceback
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api import router
from app.templates_service import templates_router
from app.config import Config

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s\n%(pathname)s:%(lineno)d\n'
)

logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Add exception handler for all exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Add more detailed debugging for NoneType errors
    if isinstance(exc, AttributeError) and str(exc).endswith("object is not callable"):
        logger.error(
            f"NoneType error detected:\n"
            f"Path: {request.url.path}\n"
            f"Method: {request.method}\n"
            f"Request headers: {request.headers}\n"
            f"Request body: {await request.body()}\n"
            f"Local variables: {locals()}\n"
            f"Exception: {str(exc)}\n"
            f"Stack trace:\n{''.join(traceback.format_tb(exc.__traceback__))}"
        )
    else:
        logger.error(
            f"Unhandled exception occurred:\n"
            f"Path: {request.url.path}\n"
            f"Method: {request.method}\n"
            f"Exception: {str(exc)}\n"
            f"Stack trace:\n{''.join(traceback.format_tb(exc.__traceback__))}"
        )
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "stack_trace": traceback.format_exc(),
            "path": request.url.path,
            "method": request.method
        }
    )

app.include_router(router)
app.include_router(templates_router)

@app.head('/health')
@app.get('/health')
def health_check():
    return 'ok'

# Add startup event to verify all routes
@app.on_event("startup")
async def startup_event():
    # Log all registered routes
    for route in app.routes:
        logger.info(f"Registered route: {route.path} [{route.methods}]")