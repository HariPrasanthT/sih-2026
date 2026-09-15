"""
FastAPI Dependencies and Singletons.
"""
# pyrefly: ignore [missing-import]
from src.services.prediction_service import PredictionService
# pyrefly: ignore [missing-import]
from src.services.recommendation_service import RecommendationService
# pyrefly: ignore [missing-import]
from src.services.data_service import DataService

_pred_service = None
_rec_service = None


def get_prediction_service() -> PredictionService:
    global _pred_service
    if _pred_service is None:
        _pred_service = PredictionService()
    return _pred_service


def get_recommendation_service() -> RecommendationService:
    global _rec_service
    if _rec_service is None:
        pred_svc = get_prediction_service()
        _rec_service = RecommendationService(prediction_service=pred_svc)
    return _rec_service


def get_data_service() -> DataService:
    return DataService()
