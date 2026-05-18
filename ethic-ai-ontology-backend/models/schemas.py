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
    user_area: Optional[str] = None
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


class EthicalImpact(BaseModel):
    """Explainable ethical concern inferred from the graph."""
    principle: str
    reason: str
    impact: str
    severity: str
    harm_type: str


class KeywordMatch(BaseModel):
    """A single keyword hit returned by the ontology-driven analysis."""
    keyword: str
    mapped_category: str
    risk_level: str
    regulations: List[str] = Field(default_factory=list)
    ethical_analysis: List[EthicalImpact] = Field(default_factory=list)


class AnalyzeTextResponse(BaseModel):
    matched_keywords: List[KeywordMatch] = Field(default_factory=list)
    inferred_categories: List[str] = Field(default_factory=list)
    inferred_risks: List[str] = Field(default_factory=list)
    inferred_regulations: List[str] = Field(default_factory=list)
    ethical_analysis: List[EthicalImpact] = Field(default_factory=list)

class ReportResponse(BaseModel):
    system: str
    dynamic_profile: dict
    inferred_data: Optional[dict] = None
    legal_sources_used: List[str]
    report: dict  # contains executive_summary, risk_assessment, etc.
    gemini_model: Optional[str] = None  # hangi model yanıt üretti (fallback sonrası)


class IncompleteCategory(BaseModel):
    category: str
    missing: List[str]

class DuplicatedKeyword(BaseModel):
    term: str
    occurrences: int

class DisconnectedNode(BaseModel):
    labels: List[str]
    identifier: str

class OntologyHealthResponse(BaseModel):
    total_categories: int
    healthy_categories: int
    completeness_score: float
    incomplete_categories: List[IncompleteCategory]
    categories_without_keywords: List[str]
    orphan_categories: List[str]
    duplicated_keywords: List[DuplicatedKeyword]
    disconnected_nodes: List[DisconnectedNode]

class ReloadOntologyResponse(BaseModel):
    status: str
    loaded_keywords: int
    loaded_categories: int
