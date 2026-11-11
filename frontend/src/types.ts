// Bio-House 核心数据类型定义

export interface Scenario {
  id: string;
  title: string;
  emoji: string;
  description: string;
  input: string;
  entities: string[];
}

export interface Hypothesis {
  id: string;
  title: string;
  mechanism: string;
  confidence: number;
  key_biomarker: string;
  house_quip: string;
}

export interface HouseOutput {
  house_comment: string;
  hypotheses: Hypothesis[];
  priority_investigation: string;
}

export interface EvidenceItem {
  hypothesis_id: string;
  support_evidence: string[];
  evidence_strength: '强' | '中' | '弱';
  causal_chain: string;
  vulnerability: string;
}

export interface CascadeNode {
  from: string;
  to: string;
  type: 'activates' | 'inhibits' | 'converts';
  label: string;
}

export interface CameronOutput {
  cameron_note: string;
  evidence_analysis: EvidenceItem[];
  metabolic_cascade_nodes: CascadeNode[];
}

export interface CESAnalysis {
  hypothesis_id: string;
  support_set: string[];
  refute_set: string[];
  verdict: 'CONFIRMED' | 'PROBABLE' | 'REFUTED' | 'INSUFFICIENT_EVIDENCE';
  updated_confidence: number;
  refute_reason?: string;
}

export interface FinalDiagnosis {
  confirmed_hypothesis: string;
  mechanism_summary: string;
  intervention: string;
  safety_warning?: string;
}

export interface CuddyOutput {
  cuddy_verdict: string;
  ces_analysis: CESAnalysis[];
  final_diagnosis: FinalDiagnosis;
  whiteboard_summary: string;
}

export type DiagnosisStage =
  | 'idle'
  | 'house_thinking'
  | 'house_done'
  | 'cameron_thinking'
  | 'cameron_done'
  | 'cuddy_thinking'
  | 'cuddy_done'
  | 'complete'
  | 'error';

export interface SSEEvent {
  stage: DiagnosisStage;
  message?: string;
  data?: {
    house?: HouseOutput;
    cameron?: CameronOutput;
    cuddy?: CuddyOutput;
  } | HouseOutput | CameronOutput | CuddyOutput;
}

export interface DiagnosisState {
  stage: DiagnosisStage;
  house: HouseOutput | null;
  cameron: CameronOutput | null;
  cuddy: CuddyOutput | null;
  statusMessage: string;
  error: string | null;
}
