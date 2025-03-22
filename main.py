from fastapi import FastAPI, APIRouter
import uvicorn
from app.api.v1.fact_check import router as fact_check_router
from app.api.v1.creative_writing import router as creative_router
from app.api.v1.documents import router as documents_router
from app.api.v1.history import router as history_router
from app.api.v1.auth import router as auth_router
from app.core.database import init_db


router = APIRouter()
router.include_router(fact_check_router, prefix="", tags=["Fact Check"])
router.include_router(creative_router, prefix="", tags=["Creative Writing"])
router.include_router(documents_router, prefix="", tags=["Documents"])
router.include_router(history_router, prefix="", tags=["History"])
router.include_router(auth_router, prefix="", tags=["Authentication"])

app = FastAPI()
app.include_router(router)
init_db()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8009)
