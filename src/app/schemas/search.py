from pydantic import BaseModel, Field
from typing import List, Optional

class DateRange(BaseModel):
    start: str
    end: str

class SearchFilterParams(BaseModel):
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    amenities: List[str] = Field(default_factory=list)
    modes: List[str] = Field(default_factory=list)
