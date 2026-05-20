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
  inferred_risks: string[];
  inferred_regulations: string[];
  ethical_analysis: EthicalAnalysis[];
}

export interface TraceStep {
  step: string;
  value: string;
}

export interface GraphTraceResponse {
  trace: TraceStep[];
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
