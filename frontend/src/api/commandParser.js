import { Video } from "lucide-react";
export function parseCreatorCommand(rawCommand) {
  const raw = String(rawCommand || "").trim();

  if (!raw) {
    return {
      valid: false,
      command: "",
      platform: "youtube",
      topic: "",
    };
  }

  const normalized = raw
    .replace(/\s+/g, " ")
    .trim();

  let platform = "youtube";

  if (/\b(instagram|ig|reel|reels)\b/i.test(normalized)) {
    platform = "instagram";
  } else if (/\b(tiktok|tik tok)\b/i.test(normalized)) {
    platform = "tiktok";
  } else if (/\b(youtube|yt)\b/i.test(normalized)) {
    platform = "youtube";
  }

  let topic = normalized
    .replace(
      /^(hey\s+n1mox[,\s]*)/i,
      ""
    )
    .replace(
      /^(n1mox[,\s]*)/i,
      ""
    )
    .replace(
      /^(please\s+)?(create|make|generate|produce|build)\s+/i,
      ""
    )
    .replace(
      /^(a\s+|an\s+)?(youtube|yt|instagram|ig|tiktok|tik\s+tok)\s*/i,
      ""
    )
    .replace(
      /^(video|short|reel|reels)\s*/i,
      ""
    )
    .replace(
      /^(about|on|regarding|for)\s+/i,
      ""
    )
    .trim();

  if (!topic) {
    topic = normalized
      .replace(
        /^(hey\s+n1mox[,\s]*)/i,
        ""
      )
      .replace(
        /^(n1mox[,\s]*)/i,
        ""
      )
      .trim();
  }

  return {
    valid: topic.length >= 2,
    command: normalized,
    platform,
    topic,
  };
}

export function buildCreatorCommand({
  platform,
  topic,
}) {
  return `Create a ${platform} video about ${topic}`;
}


