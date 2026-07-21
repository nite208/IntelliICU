from fastapi import APIRouter

from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.patients import router as patients_router
from app.api.v1.endpoints.admissions import router as admissions_router
from app.api.v1.endpoints.vital_signs import router as vital_signs_router
from app.api.v1.endpoints.lab_results import router as lab_results_router
from app.api.v1.endpoints.predictions import router as predictions_router

router = APIRouter()

router.include_router(health_router)
router.include_router(patients_router)
router.include_router(admissions_router)
router.include_router(vital_signs_router)
router.include_router(lab_results_router)
router.include_router(predictions_router)