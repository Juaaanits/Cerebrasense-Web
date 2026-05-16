import type { APIRoute } from "astro";
import { createSupabaseAdmin } from "@/lib/supabase/server";
import type { ModelPrediction } from "../types/analysis";

export const prerender = false;

const ALLOWED_IMAGE_TYPES = new Set(["image/jpeg", "image/png"]);
const SCAN_BUCKET = "brain-scans";

const getFileExtension = (type: string) => {
  if (type === "image/png") {
    return "png";
  }

  return "jpg";
};

export const POST: APIRoute = async ({ request }) => {
  const formData = await request.formData();
  const file = formData.get("scan");

  if (!(file instanceof File)) {
    return Response.json({ error: "MRI image is required." }, { status: 400 });
  }

  if (!ALLOWED_IMAGE_TYPES.has(file.type)) {
    return Response.json(
      { error: "Only JPEG and PNG files are allowed." },
      { status: 400 },
    );
  }

  const modelApiUrl = import.meta.env.MODEL_API_URL;

  if (!modelApiUrl) {
    return Response.json(
      { error: "MODEL_API_URL is not configured." },
      { status: 500 },
    );
  }

  const supabase = createSupabaseAdmin();
  const analysisId = crypto.randomUUID();
  const imagePath = `anonymous/${analysisId}.${getFileExtension(file.type)}`;

  const { error: uploadError } = await supabase.storage
    .from(SCAN_BUCKET)
    .upload(imagePath, await file.arrayBuffer(), {
      contentType: file.type,
      upsert: false,
    });

  if (uploadError) {
    return Response.json({ error: uploadError.message }, { status: 500 });
  }

  const modelFormData = new FormData();
  modelFormData.append("file", file, file.name);

  const headers = new Headers();
  if (import.meta.env.MODEL_API_TOKEN) {
    headers.set("Authorization", `Bearer ${import.meta.env.MODEL_API_TOKEN}`);
  }

  const modelResponse = await fetch(`${modelApiUrl}/predict`, {
    method: "POST",
    headers,
    body: modelFormData,
  });

  if (!modelResponse.ok) {
    return Response.json(
      { error: "Model inference failed." },
      { status: 502 },
    );
  }

  const prediction = (await modelResponse.json()) as ModelPrediction;

  const { data, error } = await supabase
    .from("tumor_analyses")
    .insert({
      image_path: imagePath,
      original_filename: file.name,
      predicted_label: prediction.predicted_label,
      confidence: prediction.confidence,
      probabilities: prediction.probabilities,
      model_version: prediction.model_version ?? null,
    })
    .select()
    .single();

  if (error) {
    return Response.json({ error: error.message }, { status: 500 });
  }

  return Response.json({
    analysis: {
      ...data,
      display_label: prediction.display_label,
      is_uncertain: prediction.is_uncertain,
      confidence_threshold: prediction.confidence_threshold,
    },
  });
};

