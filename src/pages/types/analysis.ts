export type TumorProbabilities = Record<string, number>;

export interface TumorAnalysis {
  id: string;
  created_at: string;
  user_id: string | null;
  image_path: string;
  original_filename: string;
  predicted_label: string;
  confidence: number;
  probabilities: TumorProbabilities;
  model_version: string | null;
  display_label?: string;
  is_uncertain?: boolean;
  confidence_threshold?: number;
  status: "completed" | "failed" | string;
  error_message: string | null;
}

export interface ModelPrediction {
  predicted_label: string;
  display_label?: string;
  confidence: number;
  probabilities: TumorProbabilities;
  model_version?: string;
  is_uncertain?: boolean;
  confidence_threshold?: number;
}
