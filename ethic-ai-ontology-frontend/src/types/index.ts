export interface EthicalAnalysis {
  principle: string;
  reason: string;
  impact: string;
  severity: string;
  harm_type: string;
}

export interface MatchedKeyword {
  keyword: string;
  mapped_category: string;
  risk_level: string;
  regulations: string[];
  ethical_analysis: EthicalAnalysis[];
}

export interface AnalyzeTextResponse {
  message?: string;
  matched_keywords: MatchedKeyword[];
  inferred_categories: string[];
  inferred_regulations: string[];
  ethical_analysis: EthicalAnalysis[];
  detected_risk_triggers: string[];
  detected_safeguards: string[];
  missing_safeguards: string[];
  initial_risk_level: string;
  final_risk_level: string;
  composite_score?: number;
  score_components?: Record<string, number>;
  reasoning_trace: string[];
}

export interface TraceStep {
  step: string;
  value: string;
}

export interface GraphTraceResponse {
  trace: TraceStep[];
  explanations?: string[];
}

export interface OntologyHealthResponse {
  total_categories: number;
  healthy_categories: number;
  completeness_score: number;
  incomplete_categories: any[];
  categories_without_keywords: string[];
  orphan_categories: string[];
  duplicated_keywords: any[];
  disconnected_nodes: any[];
}
