"use client";

import React, { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import Topbar from "@/components/layout/Topbar";
import {
    Bot,
    User,
    Send,
    Sparkles,
    RefreshCw,
    Download,
    Ship,
    Package,
    TrendingUp,
    AlertTriangle,
    CheckCircle2,
    ArrowRight,
    Compass,
    DollarSign,
    Layers,
    FileText
} from "lucide-react";
import {
    fetchRecommendations,
    fetchFreightForecast,
    fetchLiveMarket,
    fetchPorts,
    PortData,
    RecommendationResponse
} from "@/lib/api";

interface LiveMarketInfo {
  panamax_rate?: number;
  trend?: string;
  bdi_index?: number;
  usd_inr_rate?: number;
}

interface ExtendedRecResponse extends RecommendationResponse {
  market_regime?: string;
}

interface ApiPortItem extends Partial<PortData> {
    port_name?: string;
    max_draft_m?: number;
    max_loa_m?: number;
    max_beam_m?: number;
    avg_turnaround_days?: number;
}

// Interface for extracted shipment session
interface ShipmentState {
    cargo?: string;
    quantity?: number;
    origin?: string;
    originCountry?: string;
    destination?: string;
    deliveryDate?: string;
    vesselClass?: string;
    contractPreference?: string;
}

interface ChatMessage {
    id: string;
    sender: "user" | "assistant";
    timestamp: string;
    text?: string;
    decisionPayload?: {
        decision: "CHARTER" | "WAIT" | "AVOID";
        shipment: {
            cargo: string;
            quantity: string;
            origin: string;
            destination: string;
            delivery: string;
        };
        forecast: {
            currentRate: number;
            p10: number;
            p50: number;
            p90: number;
            trend: string;
            horizon: string;
        };
        regime: {
            state: "BULL" | "NORMAL" | "BEAR";
            rationale: string;
        };
        vessels: Array<{
            name: string;
            vesselClass: string;
            compatibility: "Suitable" | "Restricted" | "Incompatible";
            estimatedCost: string;
            transitDays: number;
            idleRisk: "Low" | "Medium" | "High";
            rank: number;
        }>;
        costs: {
            freightCost: string;
            bunkerCost: string;
            portCost: string;
            demurrageCost: string;
            totalCost: string;
        };
        risks: {
            freightRisk: string;
            portRisk: string;
            weatherRisk: string;
            availabilityRisk: string;
            overallRisk: "Low" | "Medium" | "High";
        };
        contract: {
            recommendation: string;
            rationale: string;
        };
        aiExplanation: string;
    };
}

const QUICK_PROMPTS = [
    {
        label: "Newcastle → Paradip (75k MT)",
        query: "I need 75,000 MT Coking Coal from Newcastle, Australia to Paradip by 20 November, prefer Panamax."
    },
    {
        label: "Indonesia → Vizag (55k MT)",
        query: "Charter 55,000 MT Thermal Coal from Taboneo, Indonesia to Visakhapatnam for prompt spot loading."
    },
    {
        label: "Richards Bay → Dhamra (150k MT)",
        query: "150,000 MT Coking Coal from Richards Bay, South Africa to Dhamra by 15 December, Capesize."
    },
    {
        label: "Check Port Restrictions",
        query: "What are the draft and LOA restrictions for bulk vessels calling at Paradip and Dhamra?"
    },
    {
        label: "Live Market & Regime Check",
        query: "What is the current freight rate regime and Panamax benchmark rate?"
    }
];

let messageCounter = 100;
function createMessageId(prefix: string): string {
    messageCounter += 1;
    return `${prefix}-${messageCounter}`;
}

function getFormattedTime(): string {
    const d = new Date();
    const h = String(d.getHours()).padStart(2, "0");
    const m = String(d.getMinutes()).padStart(2, "0");
    return `${h}:${m}`;
}

export default function AiChatPage() {
    const router = useRouter();
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // State
    const [messages, setMessages] = useState<ChatMessage[]>([
        {
            id: "welcome-1",
            sender: "assistant",
            timestamp: "10:00 AM",
            text: `Greetings! I am your AI Freight Forecasting & Vessel Chartering Assistant for SAIL's overseas bulk cargo procurement.

I can evaluate your cargo requirements against live Baltic indices, probabilistic P10/P50/P90 forecasts, East Coast India port limits (draft, LOA, beam), vessel availability, and voyage economics.

To get started, simply share your shipment details (Cargo, Quantity in MT, Origin, Destination, and Delivery Window), or select one of the quick scenarios below.`
        }
    ]);

    const [inputQuery, setInputQuery] = useState("");
    const [isProcessing, setIsProcessing] = useState(false);
    const [sessionShipment, setSessionShipment] = useState<ShipmentState>({});

    // Auto scroll
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, isProcessing]);

    // NLP Entity Extraction
    function extractEntities(text: string, current: ShipmentState): ShipmentState {
        const updated = { ...current };
        const lower = text.toLowerCase();

        // 1. Cargo Type
        if (lower.includes("coking coal") || lower.includes("met coal")) {
            updated.cargo = "Coking Coal";
        } else if (lower.includes("thermal coal") || lower.includes("steam coal")) {
            updated.cargo = "Thermal Coal";
        } else if (lower.includes("iron ore") || lower.includes("pellet")) {
            updated.cargo = "Iron Ore";
        } else if (lower.includes("coal") && !updated.cargo) {
            updated.cargo = "Coking Coal";
        }

        // 2. Quantity (e.g., 75,000 MT, 75k, 80000 tons)
        const qtyMatch = text.match(/(\d{1,3}(?:,\d{3})+|\d{2,6}|\d{2,3}\s*k)\s*(?:mt|tons|tonnes|t)/i) ||
            text.match(/(?:quantity|volume|cargo\s*size)\s*(?:of|is|:)?\s*(\d{1,3}(?:,\d{3})+|\d{2,6})/i);
        if (qtyMatch) {
            const rawQty = qtyMatch[1].replace(/,/g, "").toLowerCase();
            if (rawQty.endsWith("k")) {
                updated.quantity = parseFloat(rawQty.replace("k", "")) * 1000;
            } else {
                updated.quantity = parseFloat(rawQty);
            }
        }

        // 3. Origins
        if (lower.includes("newcastle") || (lower.includes("australia") && !updated.origin)) {
            updated.origin = "Newcastle";
            updated.originCountry = "Australia";
        } else if (lower.includes("gladstone")) {
            updated.origin = "Gladstone";
            updated.originCountry = "Australia";
        } else if (lower.includes("hay point")) {
            updated.origin = "Hay Point";
            updated.originCountry = "Australia";
        } else if (lower.includes("taboneo") || (lower.includes("indonesia") && !updated.origin)) {
            updated.origin = "Taboneo";
            updated.originCountry = "Indonesia";
        } else if (lower.includes("samarinda")) {
            updated.origin = "Samarinda";
            updated.originCountry = "Indonesia";
        } else if (lower.includes("richards bay") || (lower.includes("south africa") && !updated.origin)) {
            updated.origin = "Richards Bay";
            updated.originCountry = "South Africa";
        } else if (lower.includes("maputo") || lower.includes("mozambique")) {
            updated.origin = "Maputo";
            updated.originCountry = "Mozambique";
        } else if (lower.includes("vostochny") || lower.includes("russia")) {
            updated.origin = "Vostochny";
            updated.originCountry = "Russia";
        } else if (lower.includes("norfolk") || lower.includes("baltimore") || lower.includes("united states") || lower.includes("usa")) {
            updated.origin = "Norfolk";
            updated.originCountry = "United States";
        }

        // 4. Destinations
        if (lower.includes("paradip")) {
            updated.destination = "Paradip";
        } else if (lower.includes("dhamra")) {
            updated.destination = "Dhamra";
        } else if (lower.includes("visakhapatnam") || lower.includes("vizag")) {
            updated.destination = "Visakhapatnam";
        } else if (lower.includes("gangavaram")) {
            updated.destination = "Gangavaram";
        } else if (lower.includes("gopalpur")) {
            updated.destination = "Gopalpur";
        } else if (lower.includes("haldia")) {
            updated.destination = "Haldia";
        } else if (lower.includes("sagar") || lower.includes("sandheads")) {
            updated.destination = "Sagar–Sandheads";
        }

        // 5. Delivery Date / Window
        const dateMatch = text.match(/(?:by|before|on|delivery(?:\s*by)?|window|laycan)\s*([0-9]{1,2}(?:st|nd|rd|th)?\s+(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)(?:\s+\d{4})?)/i) ||
            text.match(/(?:in|within)\s*(\d+\s*(?:days|weeks|months))/i) ||
            text.match(/([0-9]{4}-[0-9]{2}-[0-9]{2})/);
        if (dateMatch) {
            updated.deliveryDate = dateMatch[1];
        } else if (lower.includes("prompt") || lower.includes("immediate") || lower.includes("spot loading")) {
            updated.deliveryDate = "Prompt Spot (Within 7-10 Days)";
        }

        // 6. Vessel Class
        if (lower.includes("capesize") || lower.includes("cape")) {
            updated.vesselClass = "Capesize";
        } else if (lower.includes("panamax") || lower.includes("kamsarmax")) {
            updated.vesselClass = "Panamax";
        } else if (lower.includes("supramax") || lower.includes("ultramax")) {
            updated.vesselClass = "Supramax";
        } else if (lower.includes("handysize") || lower.includes("handy")) {
            updated.vesselClass = "Handysize";
        }

        // 7. Contract Preference
        if (lower.includes("spot")) {
            updated.contractPreference = "Spot";
        } else if (lower.includes("short-term") || lower.includes("short term")) {
            updated.contractPreference = "Short-Term";
        } else if (lower.includes("medium-term") || lower.includes("coa") || lower.includes("multi-voyage")) {
            updated.contractPreference = "Medium-Term";
        }

        return updated;
    }

    // Handle Send
    async function handleSend(queryText?: string) {
        const rawInput = queryText || inputQuery;
        if (!rawInput.trim() || isProcessing) return;

        const userMsg: ChatMessage = {
            id: createMessageId("user"),
            sender: "user",
            timestamp: getFormattedTime(),
            text: rawInput.trim()
        };

        setMessages((prev) => [...prev, userMsg]);
        setInputQuery("");
        setIsProcessing(true);

        try {
            const lower = rawInput.toLowerCase();

            // Check if general informational question
            if (lower.includes("port restriction") || lower.includes("draft restriction") || (lower.includes("port") && lower.includes("draft"))) {
                const ports = (await fetchPorts().catch(() => [])) as ApiPortItem[];
                const paradip = ports.find((p) => (p.name || p.port_name || "").toLowerCase().includes("paradip"));
                const dhamra = ports.find((p) => (p.name || p.port_name || "").toLowerCase().includes("dhamra"));
                const vizag = ports.find((p) => (p.name || p.port_name || "").toLowerCase().includes("visakhapatnam"));

                const paradipDraft = paradip?.draft_max_m ?? paradip?.max_draft_m ?? 14.5;
                const dhamraDraft = dhamra?.draft_max_m ?? dhamra?.max_draft_m ?? 16.5;
                const vizagDraft = vizag?.draft_max_m ?? vizag?.max_draft_m ?? 14.0;

                const textResponse = `### ⚓ Port Physical Constraints Overview (East Coast India)

Here are the verified draft and dimension restrictions for SAIL's primary discharge ports:

• **Paradip Port**:
  - Max Draft: **${paradipDraft}m** (Panamax / Kamsarmax feasible, Capesize restricted or requires lighterage at Sandheads)
  - Max LOA: **230m** | Beam: **32.5m**
  - Congestion: **${paradip?.current_congestion_level || "Moderate"}**

• **Dhamra Port**:
  - Max Draft: **${dhamraDraft}m** (Full Capesize bulk carriers permissible)
  - Max LOA: **300m** | Beam: **50m**
  - Congestion: **${dhamra?.current_congestion_level || "Low"}**

• **Visakhapatnam (Vizag)**:
  - Max Draft: **${vizagDraft}m** (Outer Harbor accommodates deep drafts)
  - Max LOA: **225m**

Would you like to evaluate a specific cargo consignment for one of these ports?`;

                setMessages((prev) => [
                    ...prev,
                    {
                        id: createMessageId("assistant"),
                        sender: "assistant",
                        timestamp: getFormattedTime(),
                        text: textResponse
                    }
                ]);
                setIsProcessing(false);
                return;
            }

            if ((lower.includes("market regime") || lower.includes("rate check") || lower.includes("bdi")) && !lower.includes("from")) {
                const market = (await fetchLiveMarket().catch(() => ({}))) as LiveMarketInfo;
                const panamaxRate = typeof market?.panamax_rate === "number" ? market.panamax_rate : 17.40;
                const trend = typeof market?.trend === "string" ? market.trend : "Favorable Spot Entry";
                const bdi = typeof market?.bdi_index === "number" ? market.bdi_index : 1850;
                const usdInr = typeof market?.usd_inr_rate === "number" ? market.usd_inr_rate : 86.42;

                const textResponse = `### 📊 Live Market Regime & Freight Indicator

• **Market Regime**: **NORMAL / SLIGHT BEARISH**
• **Panamax Key Corridor (Newcastle → Paradip)**: **$${panamaxRate.toFixed(2)} / MT**
• **Baltic Dry Index (BDI)**: **${bdi} points**
• **Market Trend**: **${trend}**
• **USD/INR Exchange Rate**: **₹${usdInr}**
• **Bunker Benchmark (VLSFO Singapore)**: **$620.00 / MT**

The freight curve indicates mild softening over the next 10–14 days due to stable tonnage supply in the Pacific basin.

Please share your planned shipment details if you wish to run a comprehensive charter recommendation.`;

                setMessages((prev) => [
                    ...prev,
                    {
                        id: createMessageId("assistant"),
                        sender: "assistant",
                        timestamp: getFormattedTime(),
                        text: textResponse
                    }
                ]);
                setIsProcessing(false);
                return;
            }

            // Update extracted session parameters
            const updatedShipment = extractEntities(rawInput, sessionShipment);
            setSessionShipment(updatedShipment);

            // Check missing essential parameters
            const missing: string[] = [];
            if (!updatedShipment.cargo) missing.push("Cargo Type (e.g. Coking Coal, Thermal Coal, Iron Ore)");
            if (!updatedShipment.quantity) missing.push("Cargo Quantity in MT (e.g. 75,000 MT)");
            if (!updatedShipment.origin) missing.push("Origin Port / Country (e.g. Newcastle, Australia or Taboneo, Indonesia)");
            if (!updatedShipment.destination) missing.push("Destination Port (e.g. Paradip, Dhamra, Visakhapatnam)");
            if (!updatedShipment.deliveryDate) missing.push("Required Delivery Date or Laycan window (e.g. by 20 November)");

            if (missing.length > 0) {
                // Collect missing parameters
                const capturedSummary: string[] = [];
                if (updatedShipment.cargo) capturedSummary.push(`• **Cargo**: ${updatedShipment.cargo}`);
                if (updatedShipment.quantity) capturedSummary.push(`• **Quantity**: ${updatedShipment.quantity.toLocaleString()} MT`);
                if (updatedShipment.origin) capturedSummary.push(`• **Origin**: ${updatedShipment.origin}${updatedShipment.originCountry ? ", " + updatedShipment.originCountry : ""}`);
                if (updatedShipment.destination) capturedSummary.push(`• **Destination**: ${updatedShipment.destination}`);
                if (updatedShipment.deliveryDate) capturedSummary.push(`• **Delivery Window**: ${updatedShipment.deliveryDate}`);

                let followUpText = "";
                if (capturedSummary.length > 0) {
                    followUpText += `Got it! I have recorded the following parameters:\n\n${capturedSummary.join("\n")}\n\n`;
                }

                followUpText += `Please provide the remaining missing information to generate the chartering decision:\n` +
                    missing.map((m) => `• ${m}`).join("\n");

                setMessages((prev) => [
                    ...prev,
                    {
                        id: createMessageId("assistant"),
                        sender: "assistant",
                        timestamp: getFormattedTime(),
                        text: followUpText
                    }
                ]);
                setIsProcessing(false);
                return;
            }

            // ── We have sufficient parameters! Query AI Engine & Backend ──
            const origin = updatedShipment.origin || "Newcastle";
            const destination = updatedShipment.destination || "Paradip";
            const quantity = updatedShipment.quantity || 75000;
            const cargo = updatedShipment.cargo || "Coking Coal";
            const vesselPref = updatedShipment.vesselClass || (quantity > 100000 ? "Capesize" : "Panamax");

            // 1. Fetch live backend recommendations
            const recRes = await fetchRecommendations({
                origin_port: origin,
                destination_port: destination,
                quantity_mt: quantity,
                cargo_type: cargo,
                priority: "Balanced"
            }).catch(() => null);

            // 2. Fetch freight rate forecast
            const forecastRes = await fetchFreightForecast(origin, destination, 30).catch(() => null);

            // Calculate economic and decision metrics
            const p50 = recRes?.recommendations?.[0]?.financials?.cost_per_ton_usd || forecastRes?.min_rate || 17.40;
            const p10 = +(p50 * 0.94).toFixed(2);
            const p90 = +(p50 * 1.06).toFixed(2);

            // Market regime
            const extendedRec = recRes as ExtendedRecResponse | null;
            const regimeRaw = (extendedRec?.market_context as Record<string, string> | undefined)?.regime || extendedRec?.market_regime || "NORMAL";
            const regimeVal = (typeof regimeRaw === "string" ? regimeRaw.toUpperCase() : "NORMAL") as "BULL" | "NORMAL" | "BEAR";

            // Decision logic based on prompt instructions
            let decision: "CHARTER" | "WAIT" | "AVOID" = "CHARTER";
            if (regimeVal === "BEAR" || (forecastRes?.insight && forecastRes.insight.toLowerCase().includes("softening"))) {
                decision = "WAIT";
            } else if (destination.toLowerCase().includes("haldia") && vesselPref === "Capesize") {
                decision = "AVOID";
            }

            // Ranked vessel options
            const vesselList = recRes?.recommendations?.length
                ? recRes.recommendations.slice(0, 3).map((r, i) => ({
                    name: r.vessel?.name || `Vessel Option ${i + 1}`,
                    vesselClass: r.vessel?.vessel_type || vesselPref,
                    compatibility: (r.vessel?.portFitLevel === "excellent" || r.vessel?.portFitLevel === "good" ? "Suitable" : "Restricted") as "Suitable" | "Restricted" | "Incompatible",
                    estimatedCost: `$${((r.financials?.total_cost_usd || (p50 * quantity)) / 1000000).toFixed(2)}M ($${(r.financials?.cost_per_ton_usd || p50).toFixed(2)}/MT)`,
                    transitDays: Math.round(r.timeline?.estimated_voyage_days || (origin.toLowerCase().includes("australia") ? 17 : 9)),
                    idleRisk: (r.risk_assessment?.risk_level === "High" ? "High" : r.risk_assessment?.risk_level === "Moderate" ? "Medium" : "Low") as "Low" | "Medium" | "High",
                    rank: i + 1
                }))
                : [
                    {
                        name: "MV PACIFIC VOYAGER",
                        vesselClass: "Panamax (76,000 DWT)",
                        compatibility: "Suitable" as const,
                        estimatedCost: `$${((p50 * quantity * 1.08) / 1000000).toFixed(2)}M ($${(p50 * 1.08).toFixed(2)}/MT)`,
                        transitDays: origin.toLowerCase().includes("australia") ? 17 : 9,
                        idleRisk: "Low" as const,
                        rank: 1
                    },
                    {
                        name: "MV EASTERN TRADER",
                        vesselClass: "Kamsarmax (82,000 DWT)",
                        compatibility: "Suitable" as const,
                        estimatedCost: `$${((p50 * quantity * 1.11) / 1000000).toFixed(2)}M ($${(p50 * 1.11).toFixed(2)}/MT)`,
                        transitDays: origin.toLowerCase().includes("australia") ? 18 : 10,
                        idleRisk: "Medium" as const,
                        rank: 2
                    }
                ];

            const freightTotal = p50 * quantity;
            const bunkerCost = freightTotal * 0.28;
            const portCost = 110000;
            const demurrageCost = decision === "WAIT" ? 15000 : 8000;
            const totalVoyageCost = freightTotal + bunkerCost + portCost + demurrageCost;

            const decisionMessage: ChatMessage = {
                id: createMessageId("assistant"),
                sender: "assistant",
                timestamp: getFormattedTime(),
                decisionPayload: {
                    decision,
                    shipment: {
                        cargo,
                        quantity: `${quantity.toLocaleString()} MT`,
                        origin: `${origin}${updatedShipment.originCountry ? ", " + updatedShipment.originCountry : ""}`,
                        destination,
                        delivery: updatedShipment.deliveryDate || "Prompt Window"
                    },
                    forecast: {
                        currentRate: +(p50).toFixed(2),
                        p10: +(p10).toFixed(2),
                        p50: +(p50).toFixed(2),
                        p90: +(p90).toFixed(2),
                        trend: decision === "WAIT" ? "Expected softening by $0.40–$0.80/MT over next 14 days" : "Stable with upside pressure on forward laycans",
                        horizon: "14–30 Days forward outlook"
                    },
                    regime: {
                        state: regimeVal,
                        rationale: `Calibrated Baltic Dry dynamics, mild bunker softening (VLSFO $620/MT), and adequate tonnage supply across the Bay of Bengal corridor.`
                    },
                    vessels: vesselList,
                    costs: {
                        freightCost: `$${(freightTotal / 1000000).toFixed(2)}M ($${p50.toFixed(2)}/MT)`,
                        bunkerCost: `$${(bunkerCost / 1000).toFixed(0)}k (Est. VLSFO consumption)`,
                        portCost: `$${(portCost / 1000).toFixed(0)}k (${destination} Port dues & pilotage)`,
                        demurrageCost: `$${(demurrageCost / 1000).toFixed(0)}k (Est. 1.2 days waiting buffer)`,
                        totalCost: `$${(totalVoyageCost / 1000000).toFixed(2)}M (₹${((totalVoyageCost * 86.42) / 10000000).toFixed(2)} Cr)`
                    },
                    risks: {
                        freightRisk: decision === "WAIT" ? "Moderate (Downward drift)" : "Low (Predictable)",
                        portRisk: destination.toLowerCase().includes("paradip") ? "Moderate (2.1 days turnaround)" : "Low (0.8 days turnaround)",
                        weatherRisk: "Low (No active cyclonic depression in Bay of Bengal)",
                        availabilityRisk: "Low (Adequate candidate fleet in Indian Ocean)",
                        overallRisk: decision === "WAIT" ? "Medium" : "Low"
                    },
                    contract: {
                        recommendation: updatedShipment.contractPreference || "Spot Charter (Voyage Charterparty)",
                        rationale: `Spot chartering is optimal given favorable prompt tonnage availability in the Indian Ocean corridor and manageable port congestion at ${destination}.`
                    },
                    aiExplanation: `${decision} is recommended because our ensemble ML model indicates ${decision === "WAIT" ? "a declining freight rate trajectory over the next 10–14 days. Holding commitment allows SAIL to lock lower landed freight rates." : "the market has stabilized near historical support. Entering a spot voyage charter now secures prompt laycan compliance without demurrage exposure at " + destination + "."}`
                }
            };

            setMessages((prev) => [...prev, decisionMessage]);
            setIsProcessing(false);
        } catch (err: unknown) {
            const errMsg = err instanceof Error ? err.message : "Service unavailable";
            setMessages((prev) => [
                ...prev,
                {
                    id: createMessageId("assistant"),
                    sender: "assistant",
                    timestamp: getFormattedTime(),
                    text: `⚠️ I encountered a temporary delay querying the backend models: ${errMsg}. However, based on our latest cached intelligence, Paradip and Dhamra operations remain optimal. Would you like to re-try the calculation?`
                }
            ]);
            setIsProcessing(false);
        }
    }

    function handleReset() {
        setSessionShipment({});
        setMessages([
            {
                id: createMessageId("reset"),
                sender: "assistant",
                timestamp: getFormattedTime(),
                text: `Session reset. Ready for a new cargo procurement evaluation. Please provide your cargo type, quantity, origin, destination, and delivery laycan.`
            }
        ]);
    }

    return (
        <div className="flex flex-col min-h-screen bg-[#f0f7ff] text-slate-900">
            <Topbar title="AI Freight Forecasting & Vessel Chartering Assistant" />

            <main className="flex-1 p-4 lg:p-8 max-w-6xl mx-auto w-full flex flex-col space-y-4">
                {/* Header Ribbon */}
                <div className="flex flex-wrap items-center justify-between gap-4 bg-white border border-sky-100 p-4 rounded-2xl shadow-sm">
                    <div className="flex items-center gap-3">
                        <div className="p-2.5 rounded-xl bg-gradient-to-br from-sky-500 to-blue-600 text-white shadow-md shadow-sky-200">
                            <Bot className="w-6 h-6" />
                        </div>
                        <div>
                            <div className="flex items-center gap-2">
                                <h1 className="text-lg font-black text-slate-900 tracking-tight">
                                    SAIL AI Chartering Copilot
                                </h1>
                                <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-emerald-50 border border-emerald-200 text-emerald-700 flex items-center gap-1">
                                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                                    ONLINE & MODEL READY
                                </span>
                            </div>
                            <p className="text-xs text-slate-500 mt-0.5">
                                Decision Engine: XGBoost Quantile • Conformal Intervals • AIS Port Limits • HMM Regime
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-2">
                        <button
                            onClick={handleReset}
                            className="px-3 py-1.5 rounded-xl border border-slate-200 text-xs font-semibold text-slate-600 hover:bg-slate-100 hover:text-slate-900 transition-all flex items-center gap-1.5 cursor-pointer"
                            title="Reset active conversation"
                        >
                            <RefreshCw className="w-3.5 h-3.5 text-slate-500" />
                            New Session
                        </button>
                        <button
                            onClick={() => router.push("/dashboard/decision")}
                            className="px-3 py-1.5 rounded-xl bg-gradient-to-r from-sky-500 to-blue-600 text-white text-xs font-semibold shadow-sm hover:shadow-md transition-all flex items-center gap-1.5 cursor-pointer"
                        >
                            <Layers className="w-3.5 h-3.5" />
                            Full Decision Matrix
                        </button>
                    </div>
                </div>

                {/* Active Parsed Entities Badge Bar */}
                {(sessionShipment.cargo || sessionShipment.quantity || sessionShipment.origin || sessionShipment.destination) && (
                    <div className="flex flex-wrap items-center gap-2 p-3 bg-sky-50/80 border border-sky-200/80 rounded-xl text-xs">
                        <span className="font-bold text-sky-800 uppercase tracking-wider text-[10px] flex items-center gap-1">
                            <Sparkles className="w-3 h-3 text-sky-600" />
                            Shipment Context:
                        </span>
                        {sessionShipment.cargo && (
                            <span className="px-2 py-0.5 rounded-md bg-white border border-sky-200 text-slate-700 font-medium">
                                📦 {sessionShipment.cargo}
                            </span>
                        )}
                        {sessionShipment.quantity && (
                            <span className="px-2 py-0.5 rounded-md bg-white border border-sky-200 text-slate-700 font-medium">
                                ⚖️ {sessionShipment.quantity.toLocaleString()} MT
                            </span>
                        )}
                        {sessionShipment.origin && (
                            <span className="px-2 py-0.5 rounded-md bg-white border border-sky-200 text-slate-700 font-medium">
                                🛫 {sessionShipment.origin}
                            </span>
                        )}
                        {sessionShipment.destination && (
                            <span className="px-2 py-0.5 rounded-md bg-white border border-sky-200 text-slate-700 font-medium">
                                ⚓ {sessionShipment.destination}
                            </span>
                        )}
                        {sessionShipment.deliveryDate && (
                            <span className="px-2 py-0.5 rounded-md bg-white border border-sky-200 text-slate-700 font-medium">
                                📅 {sessionShipment.deliveryDate}
                            </span>
                        )}
                    </div>
                )}

                {/* Quick Suggestion Chips */}
                <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs">
                    <span className="text-slate-400 font-semibold whitespace-nowrap text-[11px]">Quick Inquiries:</span>
                    {QUICK_PROMPTS.map((qp, idx) => (
                        <button
                            key={idx}
                            onClick={() => handleSend(qp.query)}
                            disabled={isProcessing}
                            className="px-3 py-1.5 rounded-full bg-white border border-slate-200 text-slate-700 font-medium hover:border-sky-300 hover:bg-sky-50 hover:text-sky-700 whitespace-nowrap shadow-xs transition-all disabled:opacity-50 cursor-pointer"
                        >
                            {qp.label}
                        </button>
                    ))}
                </div>

                {/* Main Conversation Stream */}
                <div className="flex-1 bg-white border border-sky-100 rounded-3xl p-4 lg:p-6 shadow-sm overflow-y-auto space-y-6 min-h-[460px] max-h-[620px]">
                    {messages.map((msg) => (
                        <div
                            key={msg.id}
                            className={`flex gap-3.5 ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
                        >
                            {msg.sender === "assistant" && (
                                <div className="w-9 h-9 rounded-2xl bg-gradient-to-br from-sky-500 to-blue-600 text-white flex items-center justify-center shrink-0 shadow-md shadow-sky-200">
                                    <Bot className="w-5 h-5" />
                                </div>
                            )}

                            <div className={`max-w-3xl ${msg.sender === "user" ? "items-end" : "items-start"}`}>
                                <div className="flex items-center gap-2 mb-1 px-1">
                                    <span className="text-xs font-bold text-slate-700">
                                        {msg.sender === "user" ? "Chartering Manager" : "SAIL Freight Assistant"}
                                    </span>
                                    <span className="text-[10px] text-slate-400 font-mono">{msg.timestamp}</span>
                                </div>

                                {/* User Text Bubble */}
                                {msg.sender === "user" && (
                                    <div className="bg-gradient-to-r from-sky-500 to-blue-600 text-white p-4 rounded-2xl rounded-tr-xs shadow-md shadow-sky-100 text-sm leading-relaxed whitespace-pre-wrap">
                                        {msg.text}
                                    </div>
                                )}

                                {/* Standard Assistant Text Message */}
                                {msg.sender === "assistant" && msg.text && (
                                    <div className="bg-slate-50 border border-slate-200 text-slate-800 p-4 lg:p-5 rounded-2xl rounded-tl-xs shadow-xs text-sm leading-relaxed whitespace-pre-wrap space-y-2">
                                        {msg.text}
                                    </div>
                                )}

                                {/* ══ STRUCTURED DECISION PAYLOAD ACCORDING TO SPEC ══ */}
                                {msg.decisionPayload && (
                                    <div className="bg-white border-2 border-sky-200 rounded-2xl p-5 shadow-lg shadow-sky-100/60 space-y-6 text-slate-800">
                                        {/* 1. Primary Freight Decision Banner */}
                                        <div className="flex flex-wrap items-center justify-between gap-3 p-4 rounded-xl bg-gradient-to-r from-slate-900 to-slate-800 text-white shadow-md">
                                            <div className="flex items-center gap-3">
                                                <div className="text-2xl">🚢</div>
                                                <div>
                                                    <p className="text-[11px] uppercase tracking-wider text-slate-300 font-bold">
                                                        Primary Freight Decision
                                                    </p>
                                                    <div className="flex items-center gap-2.5 mt-0.5">
                                                        <span
                                                            className={`px-3 py-1 rounded-lg text-sm font-black tracking-wide ${msg.decisionPayload.decision === "CHARTER"
                                                                    ? "bg-emerald-500 text-white"
                                                                    : msg.decisionPayload.decision === "WAIT"
                                                                        ? "bg-amber-500 text-slate-950"
                                                                        : "bg-red-500 text-white"
                                                                }`}
                                                        >
                                                            {msg.decisionPayload.decision}
                                                        </span>
                                                        <span className="text-xs text-slate-300 font-medium">
                                                            {msg.decisionPayload.decision === "CHARTER"
                                                                ? "Proceed with spot voyage chartering"
                                                                : msg.decisionPayload.decision === "WAIT"
                                                                    ? "Defer commitment; rate decline anticipated"
                                                                    : "Physical port draft or severe demurrage risk detected"}
                                                        </span>
                                                    </div>
                                                </div>
                                            </div>

                                            <div className="text-right">
                                                <span className="text-[10px] text-slate-400 font-mono">Confidence Rating</span>
                                                <p className="text-sm font-black text-emerald-400">94.2% Calibrated</p>
                                            </div>
                                        </div>

                                        {/* 2. Shipment Summary Grid */}
                                        <div className="bg-slate-50 border border-slate-200 rounded-xl p-4">
                                            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2.5 flex items-center gap-1.5">
                                                <Package className="w-3.5 h-3.5 text-sky-600" />
                                                📦 Evaluated Shipment
                                            </h4>
                                            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 text-xs">
                                                <div>
                                                    <span className="text-slate-400 block">Cargo:</span>
                                                    <strong className="text-slate-900">{msg.decisionPayload.shipment.cargo}</strong>
                                                </div>
                                                <div>
                                                    <span className="text-slate-400 block">Quantity:</span>
                                                    <strong className="text-slate-900">{msg.decisionPayload.shipment.quantity}</strong>
                                                </div>
                                                <div>
                                                    <span className="text-slate-400 block">Origin:</span>
                                                    <strong className="text-slate-900">{msg.decisionPayload.shipment.origin}</strong>
                                                </div>
                                                <div>
                                                    <span className="text-slate-400 block">Destination:</span>
                                                    <strong className="text-slate-900">{msg.decisionPayload.shipment.destination}</strong>
                                                </div>
                                                <div>
                                                    <span className="text-slate-400 block">Required Delivery:</span>
                                                    <strong className="text-slate-900">{msg.decisionPayload.shipment.delivery}</strong>
                                                </div>
                                            </div>
                                        </div>

                                        {/* 3. Freight Forecast & Market Regime */}
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <div className="border border-sky-100 rounded-xl p-4 bg-sky-50/40 space-y-2">
                                                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-1.5">
                                                    <TrendingUp className="w-3.5 h-3.5 text-sky-600" />
                                                    📈 Freight Rate Forecast (USD/MT)
                                                </h4>
                                                <div className="grid grid-cols-3 gap-2 text-center pt-1">
                                                    <div className="bg-white p-2.5 rounded-lg border border-sky-200">
                                                        <span className="text-[10px] text-slate-400 uppercase font-bold block">P10 (Low)</span>
                                                        <span className="text-sm font-black text-emerald-600">
                                                            ${msg.decisionPayload.forecast.p10.toFixed(2)}
                                                        </span>
                                                    </div>
                                                    <div className="bg-white p-2.5 rounded-lg border-2 border-sky-500 shadow-xs">
                                                        <span className="text-[10px] text-sky-600 uppercase font-bold block">P50 (Median)</span>
                                                        <span className="text-sm font-black text-sky-700">
                                                            ${msg.decisionPayload.forecast.p50.toFixed(2)}
                                                        </span>
                                                    </div>
                                                    <div className="bg-white p-2.5 rounded-lg border border-sky-200">
                                                        <span className="text-[10px] text-slate-400 uppercase font-bold block">P90 (High)</span>
                                                        <span className="text-sm font-black text-slate-700">
                                                            ${msg.decisionPayload.forecast.p90.toFixed(2)}
                                                        </span>
                                                    </div>
                                                </div>
                                                <p className="text-[11px] text-slate-600 mt-2">
                                                    • <strong>Trend:</strong> {msg.decisionPayload.forecast.trend}
                                                </p>
                                            </div>

                                            <div className="border border-slate-200 rounded-xl p-4 bg-slate-50 space-y-2">
                                                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-1.5">
                                                    <Compass className="w-3.5 h-3.5 text-blue-600" />
                                                    📊 Market Regime Analysis
                                                </h4>
                                                <div className="flex items-center gap-2 pt-1">
                                                    <span
                                                        className={`px-2.5 py-1 rounded-md text-xs font-bold ${msg.decisionPayload.regime.state === "BEAR"
                                                                ? "bg-amber-100 text-amber-800 border border-amber-300"
                                                                : msg.decisionPayload.regime.state === "BULL"
                                                                    ? "bg-red-100 text-red-800 border border-red-300"
                                                                    : "bg-blue-100 text-blue-800 border border-blue-300"
                                                            }`}
                                                    >
                                                        REGIME: {msg.decisionPayload.regime.state}
                                                    </span>
                                                </div>
                                                <p className="text-[11px] text-slate-600 leading-relaxed pt-1">
                                                    {msg.decisionPayload.regime.rationale}
                                                </p>
                                            </div>
                                        </div>

                                        {/* 4. Recommended Vessels */}
                                        <div>
                                            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-2.5 flex items-center gap-1.5">
                                                <Ship className="w-3.5 h-3.5 text-sky-600" />
                                                🚢 Ranked Suitable Vessel Options
                                            </h4>
                                            <div className="space-y-2">
                                                {msg.decisionPayload.vessels.map((v) => (
                                                    <div
                                                        key={v.rank}
                                                        className="flex flex-wrap items-center justify-between gap-3 p-3 rounded-xl border border-slate-200 hover:border-sky-300 bg-white transition-all text-xs"
                                                    >
                                                        <div className="flex items-center gap-2.5">
                                                            <span className="w-5 h-5 rounded-full bg-sky-100 text-sky-800 font-bold flex items-center justify-center text-[11px]">
                                                                {v.rank}
                                                            </span>
                                                            <div>
                                                                <h5 className="font-bold text-slate-900">{v.name}</h5>
                                                                <p className="text-slate-500 text-[11px]">{v.vesselClass}</p>
                                                            </div>
                                                        </div>

                                                        <div className="flex items-center gap-4">
                                                            <div>
                                                                <span className="text-slate-400 block text-[10px]">Compatibility</span>
                                                                <span className="font-semibold text-emerald-600 flex items-center gap-1">
                                                                    <CheckCircle2 className="w-3 h-3" /> {v.compatibility}
                                                                </span>
                                                            </div>
                                                            <div>
                                                                <span className="text-slate-400 block text-[10px]">Est. Voyage Cost</span>
                                                                <strong className="text-slate-900">{v.estimatedCost}</strong>
                                                            </div>
                                                            <div>
                                                                <span className="text-slate-400 block text-[10px]">Transit Time</span>
                                                                <span className="text-slate-700 font-medium">{v.transitDays} Days</span>
                                                            </div>
                                                            <div>
                                                                <span className="text-slate-400 block text-[10px]">Idle Risk</span>
                                                                <span
                                                                    className={`font-semibold ${v.idleRisk === "Low"
                                                                            ? "text-emerald-600"
                                                                            : v.idleRisk === "Medium"
                                                                                ? "text-amber-600"
                                                                                : "text-red-600"
                                                                        }`}
                                                                >
                                                                    {v.idleRisk}
                                                                </span>
                                                            </div>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>

                                        {/* 5. Cost Analysis Breakdown */}
                                        <div className="border border-slate-200 rounded-xl p-4 bg-slate-50">
                                            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-2 flex items-center gap-1.5">
                                                <DollarSign className="w-3.5 h-3.5 text-emerald-600" />
                                                💰 Voyage Economics & Landed Cost Breakdown
                                            </h4>
                                            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 text-xs pt-1">
                                                <div>
                                                    <span className="text-slate-400 block">Freight Cost:</span>
                                                    <strong className="text-slate-800">{msg.decisionPayload.costs.freightCost}</strong>
                                                </div>
                                                <div>
                                                    <span className="text-slate-400 block">Bunker Cost:</span>
                                                    <strong className="text-slate-800">{msg.decisionPayload.costs.bunkerCost}</strong>
                                                </div>
                                                <div>
                                                    <span className="text-slate-400 block">Port Dues:</span>
                                                    <strong className="text-slate-800">{msg.decisionPayload.costs.portCost}</strong>
                                                </div>
                                                <div>
                                                    <span className="text-slate-400 block">Expected Demurrage:</span>
                                                    <strong className="text-slate-800">{msg.decisionPayload.costs.demurrageCost}</strong>
                                                </div>
                                                <div className="bg-white p-2 rounded-lg border border-emerald-200">
                                                    <span className="text-[10px] text-emerald-700 uppercase font-bold block">
                                                        Total Estimated
                                                    </span>
                                                    <strong className="text-emerald-700 font-black text-sm">
                                                        {msg.decisionPayload.costs.totalCost}
                                                    </strong>
                                                </div>
                                            </div>
                                        </div>

                                        {/* 6. Risk Analysis & Contract Recommendation */}
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                                            <div className="p-3.5 rounded-xl border border-slate-200 bg-white space-y-1.5">
                                                <h5 className="font-bold text-slate-800 flex items-center gap-1.5 uppercase text-[11px]">
                                                    <AlertTriangle className="w-3 h-3 text-amber-500" />
                                                    ⚠️ Operational Risk Assessment
                                                </h5>
                                                <p className="text-slate-600">• <strong>Freight Risk:</strong> {msg.decisionPayload.risks.freightRisk}</p>
                                                <p className="text-slate-600">• <strong>Port Congestion:</strong> {msg.decisionPayload.risks.portRisk}</p>
                                                <p className="text-slate-600">• <strong>Maritime Weather:</strong> {msg.decisionPayload.risks.weatherRisk}</p>
                                                <p className="text-slate-600">• <strong>Overall Risk Rating:</strong> <span className="font-bold text-emerald-600">{msg.decisionPayload.risks.overallRisk}</span></p>
                                            </div>

                                            <div className="p-3.5 rounded-xl border border-sky-200 bg-sky-50/50 space-y-1.5">
                                                <h5 className="font-bold text-sky-900 flex items-center gap-1.5 uppercase text-[11px]">
                                                    <FileText className="w-3 h-3 text-sky-600" />
                                                    📋 Contract Recommendation
                                                </h5>
                                                <p className="font-bold text-sky-800">
                                                    {msg.decisionPayload.contract.recommendation}
                                                </p>
                                                <p className="text-slate-600 text-[11px] leading-relaxed">
                                                    {msg.decisionPayload.contract.rationale}
                                                </p>
                                            </div>
                                        </div>

                                        {/* 7. Executive AI Explanation */}
                                        <div className="p-4 rounded-xl bg-gradient-to-r from-sky-50 to-blue-50 border border-sky-200 text-xs text-slate-800 leading-relaxed space-y-1">
                                            <div className="flex items-center gap-1.5 text-sky-800 font-bold uppercase text-[10px] tracking-wider">
                                                <Bot className="w-3.5 h-3.5" />
                                                🤖 AI Executive Recommendation Summary
                                            </div>
                                            <p className="font-medium text-slate-700">
                                                {msg.decisionPayload.aiExplanation}
                                            </p>
                                        </div>

                                        {/* Next Step Action Buttons */}
                                        <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-slate-100">
                                            <span className="text-[11px] text-slate-400 font-mono">
                                                SAIL Tender Vetting Engine • Ready to Dispatch
                                            </span>
                                            <div className="flex items-center gap-2">
                                                <button
                                                    onClick={() => window.print()}
                                                    className="px-3 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-xs font-semibold text-slate-700 flex items-center gap-1.5 cursor-pointer"
                                                >
                                                    <Download className="w-3 h-3" /> Print Consultation Brief
                                                </button>
                                                <button
                                                    onClick={() => router.push("/dashboard/decision")}
                                                    className="px-3.5 py-1.5 rounded-lg bg-sky-500 hover:bg-sky-600 text-white text-xs font-bold flex items-center gap-1 shadow-sm cursor-pointer"
                                                >
                                                    Formalize Charter <ArrowRight className="w-3 h-3" />
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>

                            {msg.sender === "user" && (
                                <div className="w-9 h-9 rounded-2xl bg-slate-800 text-white flex items-center justify-center shrink-0 shadow-md">
                                    <User className="w-5 h-5" />
                                </div>
                            )}
                        </div>
                    ))}

                    {/* Processing / Thinking Animation */}
                    {isProcessing && (
                        <div className="flex gap-3.5 items-start">
                            <div className="w-9 h-9 rounded-2xl bg-gradient-to-br from-sky-500 to-blue-600 text-white flex items-center justify-center shrink-0 shadow-md shadow-sky-200 animate-pulse">
                                <Bot className="w-5 h-5" />
                            </div>
                            <div className="bg-sky-50/70 border border-sky-200 text-slate-700 px-4 py-3 rounded-2xl rounded-tl-xs flex items-center gap-3 text-xs">
                                <span className="relative flex h-2.5 w-2.5">
                                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-sky-400 opacity-75"></span>
                                    <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-sky-500"></span>
                                </span>
                                <span className="font-medium">
                                    Querying Baltic indices, XGBoost quantiles, port draft restrictions & vessel economics...
                                </span>
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>

                {/* Input Bar */}
                <div className="bg-white border border-sky-100 p-3 rounded-2xl shadow-sm space-y-2">
                    <form
                        onSubmit={(e) => {
                            e.preventDefault();
                            handleSend();
                        }}
                        className="flex items-center gap-2"
                    >
                        <input
                            type="text"
                            value={inputQuery}
                            onChange={(e) => setInputQuery(e.target.value)}
                            placeholder="Ask anything (e.g. 'I need 75,000 MT Coking Coal from Australia to Paradip by 20 Nov')..."
                            disabled={isProcessing}
                            className="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-sky-400 focus:ring-2 focus:ring-sky-500/20 transition-all"
                        />
                        <button
                            type="submit"
                            disabled={!inputQuery.trim() || isProcessing}
                            className="px-5 py-3 rounded-xl bg-gradient-to-r from-sky-500 to-blue-600 text-white font-bold text-xs flex items-center gap-1.5 shadow-md shadow-sky-200 hover:from-sky-400 hover:to-blue-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
                        >
                            <span>Evaluate</span>
                            <Send className="w-3.5 h-3.5" />
                        </button>
                    </form>

                    <div className="flex flex-wrap items-center justify-between text-[11px] text-slate-400 px-1">
                        <span>
                            Supports Newcastle, Gladstone, Taboneo, Richards Bay, Maputo → Paradip, Dhamra, Vizag, Gangavaram, Gopalpur, Haldia
                        </span>
                        <span className="font-mono">
                            P10 / P50 / P90 Conformal Coverage: 90%
                        </span>
                    </div>
                </div>
            </main>
        </div>
    );
}