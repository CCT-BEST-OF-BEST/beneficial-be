"""Backward-compatible imports for learning repositories.

New code should import from app.domains.learning.repositories.
"""

from app.domains.learning.repositories.base import LearningRecordRepository
from app.domains.learning.repositories.mongo import MongoLearningRecordRepository

__all__ = ["LearningRecordRepository", "MongoLearningRecordRepository"]
