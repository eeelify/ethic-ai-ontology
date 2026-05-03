from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class SystemResponse(BaseModel):
    name: str


class RiskResponse(BaseModel):
    system: str
    risk_level: str


class ComplianceResponse(BaseModel):
    system: str
    risk_level: str
    regulations: List[str] = Field(default_factory=list)


class AnalyzeRequest(BaseModel):
    text: Optional[str] = None
    system_name: Optional[str] = None

    def model_post_init(self, __context):
        if (self.text is None or self.text.strip() == "") and (self.system_name is None or self.system_name.strip() == ""):
            raise ValueError("Provide either 'text' or 'system_name'.")


class ViolationsResponse(BaseModel):
    system: str
    violated_principles: List[str] = Field(default_factory=list)
    violation_count: int


class TensionsResponse(BaseModel):
    system: str
    ethical_tensions: List[str] = Field(default_factory=list)
    principle_conflicts: List[Dict[str, str]] = Field(default_factory=list)


class FullProfileResponse(BaseModel):
    system: str
    risk_level: Optional[str] = None
    sector: Optional[str] = None
    decision_type: Optional[str] = None
    automation_level: Optional[str] = None
    legal_basis: Optional[str] = None
    ethical_tensions: List[str] = Field(default_factory=list)
    requirements: List[str] = Field(default_factory=list)
    affected_parties: List[str] = Field(default_factory=list)
    violated_principles: List[str] = Field(default_factory=list)
    erc_score: int


class ERCLevel(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class AssessRequest(BaseModel):
    system_name: str


class AssessResponse(BaseModel):
    system: str
    risk_level: Optional[str] = None
    erc_score: int
    erc_level: ERCLevel
    sector: Optional[str] = None
    decision_type: Optional[str] = None
    violated_principles: List[str] = Field(default_factory=list)
    ethical_tensions: List[str] = Field(default_factory=list)
    requirements: List[str] = Field(default_factory=list)
    regulations: List[str] = Field(default_factory=list)
    summary: str


class ReportResponse(BaseModel):
    system: str
    ontology_profile: dict
    legal_sources_used: List[str]
    report: dict  # contains executive_summary, risk_assessment, etc.
    gemini_model: Optional[str] = None  # hangi model yanıt üretti (fallback sonrası)

