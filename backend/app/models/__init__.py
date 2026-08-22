"""SQLAlchemy models.

Importing this package registers every mapper on ``Base.metadata`` which is what
Alembic autogenerate and ``create_all`` rely on.
"""

from app.db.base import Base
from app.models.associations import collection_tools, tool_categories, tool_tags
from app.models.category import Category
from app.models.collection import Collection
from app.models.favorite import Favorite
from app.models.free_access import FreeAccessGrant
from app.models.pricing import PricingPlan
from app.models.tag import Tag
from app.models.tool import Tool

__all__ = [
    "Base",
    "Category",
    "Collection",
    "Favorite",
    "FreeAccessGrant",
    "PricingPlan",
    "Tag",
    "Tool",
    "collection_tools",
    "tool_categories",
    "tool_tags",
]
