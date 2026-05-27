from app.domains.content.repository import MongoContentCatalogRepository
from app.domains.content.service import ContentCatalogService
from app.infrastructure.db.mongo.mongo_client import get_mongo_client


def get_content_catalog_service() -> ContentCatalogService:
    return ContentCatalogService(MongoContentCatalogRepository(get_mongo_client()))
