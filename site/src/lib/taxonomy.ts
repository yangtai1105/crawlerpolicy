export const TRACKS = [
  "policy-regulation",
  "litigation-legal",
  "search-discovery",
  "crawler-controls",
  "agentic-web",
  "licensing-monetization",
  "standards-protocols",
  "asset-rights",
  "measurement-economics",
] as const;

export type Track = (typeof TRACKS)[number];

export const FRONTS = [
  "access-discovery",
  "agents-identity",
  "rights-markets",
  "governance-law",
  "measurement-economics",
] as const;

export type Front = (typeof FRONTS)[number];

export const FRONT_TRACKS: Record<Front, readonly Track[]> = {
  "access-discovery": ["crawler-controls", "search-discovery"],
  "agents-identity": ["agentic-web", "standards-protocols"],
  "rights-markets": ["licensing-monetization", "asset-rights"],
  "governance-law": ["policy-regulation", "litigation-legal"],
  "measurement-economics": ["measurement-economics"],
};

export const TRACK_LABELS: Record<Track, string> = {
  "policy-regulation": "Policy & Regulation",
  "litigation-legal": "Litigation & Legal",
  "search-discovery": "Search & AI Discovery",
  "crawler-controls": "Crawlers & Content Controls",
  "agentic-web": "Agentic Web",
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

export type LegacyPillar = "crawler" | "ecosystem" | "agent";

export function legacyPillarForTracks(tracks: readonly Track[]): LegacyPillar {
  if (tracks.includes("crawler-controls")) return "crawler";
  if (tracks.includes("agentic-web") || tracks.includes("standards-protocols")) return "agent";
  return "ecosystem";
}
