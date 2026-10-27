from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

WorkMode = Literal["remote", "onsite", "hybrid"]
Status = Literal["open", "closed"]


class InternshipBase(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(min_length=3, max_length=120)
    company: str = Field(min_length=2, max_length=120)
    location: str = Field(min_length=1, max_length=120)
    work_mode: WorkMode
    stipend: Optional[int] = Field(default=None, ge=0)
    description: str = Field(default="", max_length=5000)
    deadline: Optional[date] = None
    status: Status = "open"


class InternshipCreate(InternshipBase):
    """POST body: required fields must be present."""


class InternshipReplace(InternshipBase):
    """PUT body: full replacement."""


class InternshipPatch(BaseModel):
    """PATCH body: any subset of fields."""
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: Optional[str] = Field(default=None, min_length=3, max_length=120)
    company: Optional[str] = Field(default=None, min_length=2, max_length=120)
    location: Optional[str] = Field(default=None, min_length=1, max_length=120)
    work_mode: Optional[WorkMode] = None
    stipend: Optional[int] = Field(default=None, ge=0)
    description: Optional[str] = Field(default=None, max_length=5000)
    deadline: Optional[date] = None
    status: Optional[Status] = None
