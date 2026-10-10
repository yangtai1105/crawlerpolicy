export const TRACKS = [
  "policy-regulation",
  "litigation-legal",
  "search-discovery",
  "access-controls",
  "platform-ecosystem",
  "identity-authorization",
  "licensing-monetization",
  "standards-protocols",
  "asset-rights",
  "measurement-economics",
] as const;

export type Track = (typeof TRACKS)[number];

/** Slugs used before 2026-10. Content on disk keeps them; readers resolve. */
export const LEGACY_TRACK_ALIASES: Record<string, Track> = {
  "crawler-controls": "access-controls",
  "agentic-web": "platform-ecosystem",
};

export function normalizeTrack(value: string): Track {
  const alias = LEGACY_TRACK_ALIASES[value];
  if (alias) return alias;
  if ((TRACKS as readonly string[]).includes(value)) return value as Track;
  throw new Error(`Unknown track: ${value}`);
}

export const SUBJECTS = ["crawler", "agent", "both", "unknown"] as const;
export type Subject = (typeof SUBJECTS)[number];

export const SUBJECT_LABELS: Record<Subject, string> = {
  crawler: "Crawlers",
  agent: "Agents",
  both: "Crawlers & Agents",
  unknown: "Unspecified",
};

export const FRONTS = [
  "access-discovery",
  "agents-identity",
  "rights-markets",
  "governance-law",
  "measurement-economics",
] as const;

export type Front = (typeof FRONTS)[number];

export const FRONT_TRACKS: Record<Front, readonly Track[]> = {
  "access-discovery": ["access-controls", "search-discovery"],
  "agents-identity": ["platform-ecosystem", "standards-protocols", "identity-authorization"],
  "rights-markets": ["licensing-monetization", "asset-rights"],
  "governance-law": ["policy-regulation", "litigation-legal"],
  "measurement-economics": ["measurement-economics"],
};

export const TRACK_LABELS: Record<Track, string> = {
  "policy-regulation": "Policy & Regulation",
  "litigation-legal": "Litigation & Legal",
  "search-discovery": "Search & AI Discovery",
  "access-controls": "Access Controls",
  "platform-ecosystem": "Platform & Ecosystem",
  "identity-authorization": "Identity & Authorization",
  "licensing-monetization": "Licensing & Monetization",
  "standards-protocols": "Standards & Protocols",
  "asset-rights": "Asset Rights",
  "measurement-economics": "Measurement & Economics",
};

export const FRONT_LABELS: Record<Front, string> = {
  "access-discovery": "Access & Discovery",
  "agents-identity": "Agents & Identity",
  "rights-markets": "Rights & Markets",
  "governance-law": "Governance & Law",
  "measurement-economics": "Measurement & Economics",
};

const flattened = FRONTS.flatMap((front) => FRONT_TRACKS[front]);
if (flattened.length !== TRACKS.length || new Set(flattened).size !== TRACKS.length) {
  throw new Error("Every track must belong to exactly one public front");
}

export function frontForTrack(track: Track): Front {
  const front = FRONTS.find((candidate) => FRONT_TRACKS[candidate].includes(track));
  if (!front) throw new Error(`No front configured for track: ${track}`);
  return front;
}
