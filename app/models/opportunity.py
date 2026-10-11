
from datetime import date
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional


class Opportunity(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    opportunity_id: Optional[int] = None

    title: str = Field(min_length=3, max_length=200)
    organization: str
    category: str
    description: str

    eligibility: str = ""
    required_skills: List[str] = Field(default_factory=list)

    location: str = "India"
    is_paid: bool = False
    stipend: Optional[str] = None

    deadline: Optional[date] = None
    source_url: str = Field(min_length=8, max_length=2000)
