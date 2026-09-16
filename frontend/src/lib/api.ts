/**
 * FreightIQ API Client for FastAPI Backend (http://localhost:8000)
 */

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  (typeof window !== "undefined" && window.location.hostname.includes("vercel.app")
    ? "https://freightiq-api-dmtb.onrender.com"
    : "http://localhost:8000");

export interface ForecastPoint {
  date: string;
  historical: number | null;
  forecast: number | null;
  upper: number | null;
  lower: number | null;
  upperCI?: number | null;
  lowerCI?: number | null;
}

export interface ForecastResponse {
  route: string;
  origin: string;
  destination: string;
  confidence_pct: number;
  optimal_window: string;
  insight: string;
  min_rate: number;
  data: ForecastPoint[];
  y_domain: [number, number];
  today_marker: string;
}

export interface PortData {
  port_id?: string;
  name: string;
  code?: string;
  country?: string;
  state?: string;
  draft_max_m: number;
  maxDraft?: string;
  loa_max_m: number;
  maxLOA?: string;
  beam_max_m: number;
  maxBeam?: string;
  daily_handling_capacity_mt: number;
  handling?: string;
  average_waiting_days: number;
  waiting?: string;
  current_congestion_level: "low" | "moderate" | "medium" | "high";
  congestion?: string;
  berth?: string;
  predictedCongestion?: string;
  action?: string;
  risk?: "low" | "medium" | "high";
  demurrage_rate_usd_per_day?: number;
  status?: string;
}

export interface VesselData {
  vessel_id?: string;
  id?: number | string;
  name: string;
  imo?: string;
  vessel_type?: string;
  type?: string;
  deadweight_tonnage?: number;
  capacity?: number;
  built_year?: number;
  built?: number;
  max_draft_m?: number;
  draft?: string;
  loa_m?: number;
  loa?: string;
  beam_m?: number;
  beam?: string;
  availability?: string;
  availStatus?: "available" | "limited" | "unavailable";
  freight?: number;
  daily_hire_rate_usd?: number;
  portFit?: string;
  portFitColor?: string;
  portFitLevel?: "excellent" | "good" | "restricted";
  aiScore?: number;
  owner?: string;
  operator?: string;
  flag?: string;
  flag_country?: string;
  position?: string;
  current_location?: string;
  eta?: string;
  recommended?: boolean;
  strengths?: string[];
  status?: string;
}

export interface RecommendationRequest {
  origin_port?: string;
  destination_port?: string;
  cargo_size_tons?: number;
  quantity_mt?: number;
  cargo_type?: string;
  laycan_start?: string;
  laycan_end?: string;
  contract_type?: string;
  priority?: "Cost" | "Speed" | "Reliability" | "Balanced";
  cost_weight?: number;
  speed_weight?: number;
  reliability_weight?: number;
}

export interface RecommendationScore {
  composite_score: number;
  cost_efficiency: number;
  reliability: number;
  operational_fit: number;
}

export interface RecommendationFinancials {
  total_cost_usd: number;
  cost_per_ton_usd: number;
  estimated_demurrage_usd: number;
  estimated_savings_usd: number;
}

export interface LiveMarketResponse {
  status: string;
  usd_inr_rate?: number;
  brent_crude_usd_bbl?: number;
  wti_crude_usd_bbl?: number;
  panamax_rate?: number;
  trend?: string;
  bdi_index?: number;
  source?: string;
  [key: string]: unknown;
}

export interface LiveFleetVessel {
  vessel_name: string;
  vessel_class: string;
  dwt: number;
  lat: number;
  lng: number;
  sog: number;
  cog: number;
  heading: number;
  nav_status: string;
  destination: string;
  cargo: string;
  eta: string;
  imo: number;
  mmsi: number;
  draft_m: number;
  charter_status: string;
  [key: string]: unknown;
}

export interface LiveFleetResponse {
  source: string;
  vessel_count: number;
  vessels: LiveFleetVessel[];
  [key: string]: unknown;
}

export interface RecommendationItem {
  rank: number;
  vessel: VesselData;
  scores: RecommendationScore;
  financials: RecommendationFinancials;
  timeline: {
    laycan_window: string;
    estimated_voyage_days: number;
    eta_destination: string;
  };
  risk_assessment: {
    risk_level: string;
    risk_factors: string[];
    mitigations: string[];
  };
  explanation: string;
}

export interface RecommendationResponse {
  status: string;
  recommendation_id: string;
  timestamp: string;
  request_summary: Record<string, unknown>;
  recommendations: RecommendationItem[];
  market_context: Record<string, unknown>;
  executive_summary: string;
}

export interface ModelMetricsResponse {
  model_name: string;
  best_model?: string;
  validation_period?: string;
  test_metrics?: {
    mae: number;
    rmse: number;
    r2: number;
    mape: number;
  };
  conformal_metrics?: {
    coverage_rate: number;
    mean_interval_width: number;
  };
  overfitting_check?: {
    train_r2: number;
    test_r2: number;
    generalization_gap: number;
    overfitting_detected: boolean;
  };
  total_samples?: number;
  data_leakage_checks_passed?: boolean;
}

// ── Generic Fetch Helper ────────────────────────────────────────────────────────
async function fetchFromApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const cleanEndpoint = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;

  const isBrowser = typeof window !== "undefined";
  const isHttps = isBrowser && window.location.protocol === "https:";

  const candidateUrls: string[] = [];

  // 1. Configured or detected Base URL
  if (API_BASE_URL) {
    candidateUrls.push(`${API_BASE_URL}${cleanEndpoint}`);
  }

  // 2. Next.js server-side reverse proxy (avoids browser CORS and mixed content)
  if (isBrowser) {
    candidateUrls.push(`/api/proxy${cleanEndpoint}`);
  }

  // 3. Render cloud backend candidate
  candidateUrls.push(`https://freightiq-api-dmtb.onrender.com${cleanEndpoint}`);

  // 4. Local endpoints (only when on insecure HTTP to avoid browser mixed-content security blocks)
  if (!isHttps) {
    candidateUrls.push(`http://127.0.0.1:8000${cleanEndpoint}`);
    candidateUrls.push(`http://localhost:8000${cleanEndpoint}`);
  }

  const uniqueUrls = Array.from(new Set(candidateUrls));
  let lastError: unknown = null;

  for (const url of uniqueUrls) {
    try {
      const isCloud = url.includes("onrender.com");
      const controller = new AbortController();
      // Render free-tier can take up to 25s on cold starts
      const timeoutId = setTimeout(() => controller.abort(), isCloud ? 25000 : 5000);

      const res = await fetch(url, {
        headers: {
          "Content-Type": "application/json",
          ...options?.headers,
        },
        signal: controller.signal,
        ...options,
      });

      clearTimeout(timeoutId);

      if (res.ok) {
        return (await res.json()) as T;
      }
    } catch (err: unknown) {
      lastError = err;
    }
  }

  console.warn(`Fetch to all URLs failed for ${endpoint}:`, lastError instanceof Error ? lastError.message : lastError);
  throw lastError || new Error(`Failed to fetch from all endpoints for ${endpoint}`);
}

// ── Specific API Calls ──────────────────────────────────────────────────────────

/**
 * Health check
 */
export async function checkApiHealth(): Promise<{ status: string; version: string }> {
  return fetchFromApi<{ status: string; version: string }>("/health");
}

/**
 * Get AI Freight Rate Forecast for a route
 */
export async function fetchFreightForecast(
  origin = "Newcastle",
  destination = "Paradip",
  days = 30
): Promise<ForecastResponse> {
  const query = new URLSearchParams({
    origin,
    destination,
    days: String(days),
  });
  return fetchFromApi<ForecastResponse>(`/forecast?${query.toString()}`);
}

/**
 * Get East Coast India Ports and congestion intelligence
 */
export async function fetchPorts(): Promise<PortData[]> {
  return fetchFromApi<PortData[]>("/ports");
}

/**
 * Get available bulk carrier vessels
 */
export async function fetchVessels(status?: string): Promise<VesselData[]> {
  const query = status ? `?status=${encodeURIComponent(status)}` : "";
  return fetchFromApi<VesselData[]>(`/vessels${query}`);
}

/**
 * Request optimal vessel recommendations using Multi-Criteria Decision Making
 */
export async function fetchRecommendations(
  req: RecommendationRequest
): Promise<RecommendationResponse> {
  return fetchFromApi<RecommendationResponse>("/recommendations", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

/**
 * Get live market indices and bunker prices
 */
export async function fetchLiveMarket(): Promise<LiveMarketResponse> {
  return fetchFromApi<LiveMarketResponse>("/live/market");
}

/**
 * Get live fleet telemetry and AIS coordinates
 */
export async function fetchLiveFleet(): Promise<LiveFleetResponse> {
  return fetchFromApi<LiveFleetResponse>("/live/fleet");
}

/**
 * Get ML model validation metrics and conformal prediction status
 */
export async function fetchModelMetrics(): Promise<ModelMetricsResponse> {
  return fetchFromApi<ModelMetricsResponse>("/model/metrics");
}
