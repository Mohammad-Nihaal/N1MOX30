import { Video } from "lucide-react";
export const CREATOR_OS_STAGES = [
  { id: "research", label: "Research" },
  { id: "strategy", label: "Strategy" },
  { id: "hooks", label: "Hooks" },
  { id: "script", label: "Script" },
  { id: "voice", label: "Voice" },
  { id: "visuals", label: "Visuals" },
  { id: "video", label: "Video" },
  { id: "captions", label: "Captions" },
  { id: "thumbnail", label: "Thumbnail" },
  { id: "metadata", label: "Metadata" },
  { id: "quality_check", label: "Quality Check" },
  { id: "scheduling", label: "Scheduling" },
  { id: "publishing", label: "Publishing" },
];

export function stageLabel(stage) {
  const item = CREATOR_OS_STAGES.find(
    (entry) => entry.id === stage
  );

  return item?.label || stage || "Preparing";
}

export function workflowStatusLabel(status) {
  const labels = {
    pending: "Pending",
    running: "Running",
    completed: "Completed",
    failed: "Failed",
    paused: "Paused",
    cancelled: "Cancelled",
  };

  return labels[status] || status || "Unknown";
}

export function workflowStatusClass(status) {
  return String(status || "unknown")
    .toLowerCase()
    .replace(/[^a-z0-9_-]/g, "-");
}

export function stageStatusClass(status) {
  return String(status || "pending")
    .toLowerCase()
    .replace(/[^a-z0-9_-]/g, "-");
}


