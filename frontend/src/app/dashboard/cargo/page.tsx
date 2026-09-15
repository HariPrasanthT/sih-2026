"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Topbar from "@/components/layout/Topbar";
import {
  Package, Calendar, FileText, ArrowRight, Save, Zap, Ship,
  Star, CheckCircle, AlertTriangle, TrendingDown, Filter,
  ChevronDown, ChevronUp, Search, Clock, Anchor, Globe, Gauge,
  Users, Info, Activity,
} from "lucide-react";
import { fetchRecommendations } from "@/lib/api";

// ─── Types & Data ─────────────────────────────────────────────────────────────
const commodities = ["Coal", "Iron Ore", "Limestone", "Other Bulk Cargo"];
const priorities = ["Cost", "Speed", "Reliability", "Balanced"];
const contractPreferences = ["Spot", "Short-Term", "Medium-Term", "AI Recommended"];
const vesselTypes = ["Any", "Panamax", "Supramax", "Capesize", "Handymax"];

const defaultVessels = [
  {
    id: 1,
    name: "MV Pacific Voyager",
    imo: "9412567",
    flag: "🇵🇦",
    type: "Panamax",
    capacity: 82000,
    built: 2018,
    draft: "14.2m",
    loa: "225m",
    beam: "32.2m",
    availability: "10–15 Sep 2026",
    availStatus: "available",
    freight: 17.4,
    portFit: "Excellent",
    portFitLevel: "excellent",
    aiScore: 94,
    owner: "Pacific Bulk Carriers",
    broker: "Clarksons",
    position: "Port Hedland, Australia",
    eta: "Sep 10",
    recommended: true,
    strengths: ["Best freight rate", "Draft compatible with Paradip", "Within laycan window"],
  },
  {
    id: 2,
    name: "MV Eastern Star",
    imo: "9501234",
    flag: "🇸🇬",
    type: "Panamax",
    capacity: 78500,
    built: 2016,
    draft: "13.8m",
    loa: "220m",
    beam: "32.0m",
    availability: "12–18 Sep 2026",
    availStatus: "available",
    freight: 17.9,
    portFit: "Good",
    portFitLevel: "good",
    aiScore: 87,
    owner: "Eastern Maritime",
    broker: "BRS Group",
    position: "Newcastle, Australia",
    eta: "Sep 12",
    recommended: false,
    strengths: ["Good draft clearance", "Reliable operator"],
  },
  {
    id: 3,
    name: "MV Atlas Pride",
    imo: "9388901",
    flag: "🇬🇷",
    type: "Supramax",
    capacity: 56000,
    built: 2015,
    draft: "12.5m",
    loa: "190m",
    beam: "28.5m",
    availability: "8–14 Sep 2026",
    availStatus: "available",
    freight: 16.2,
    portFit: "Excellent",
    portFitLevel: "excellent",
    aiScore: 81,
    owner: "Atlas Shipping",
    broker: "Fearnleys",
    position: "Singapore",
    eta: "Sep 8",
    recommended: false,
    strengths: ["Earliest availability", "Lowest freight rate"],
  },
  {
    id: 4,
    name: "MV Cape Meridian",
    imo: "9623445",
    flag: "🇳🇴",
    type: "Capesize",
    capacity: 175000,
    built: 2020,
    draft: "18.5m",
    loa: "292m",
    beam: "45.0m",
    availability: "20–28 Sep 2026",
    availStatus: "limited",
    freight: 14.8,
    portFit: "Restricted",
    portFitLevel: "restricted",
    aiScore: 63,
    owner: "Meridian Ocean",
    broker: "Ifchor-Galbraiths",
    position: "Dampier, Australia",
    eta: "Sep 22",
    recommended: false,
    strengths: ["Lowest $/MT rate", "New vessel (2020)"],
  },
  {
    id: 5,
    name: "MV Green Pioneer",
    imo: "9754321",
    flag: "🇯🇵",
    type: "Panamax",
    capacity: 80500,
    built: 2021,
    draft: "14.0m",
    loa: "228m",
    beam: "32.4m",
    availability: "15–22 Sep 2026",
    availStatus: "limited",
    freight: 18.1,
    portFit: "Good",
    portFitLevel: "good",
    aiScore: 76,
    owner: "NYK Line",
    broker: "Braemar",
    position: "Gladstone, Australia",
    eta: "Sep 16",
    recommended: false,
    strengths: ["Modern vessel", "Japanese owner reliability"],
  },
  {
    id: 6,
    name: "MV Baltic Crown",
    imo: "9298076",
    flag: "🇩🇰",
    type: "Handymax",
    capacity: 44500,
    built: 2013,
    draft: "11.8m",
    loa: "185m",
    beam: "28.0m",
    availability: "5–10 Sep 2026",
    availStatus: "available",
    freight: 19.5,
    portFit: "Good",
    portFitLevel: "good",
    aiScore: 58,
    owner: "Nordic Bulk",
    broker: "Lorentzen & Stemoco",
    position: "Colombo, Sri Lanka",
    eta: "Sep 6",
    recommended: false,
    strengths: ["Earliest arrival", "Compatible with all EC India ports"],
  },
];

const portFitStyles: Record<string, string> = {
  excellent: "text-emerald-700 bg-emerald-50 border-emerald-200",
  good: "text-sky-700 bg-sky-50 border-sky-200",
  restricted: "text-amber-700 bg-amber-50 border-amber-200",
};

const availStyles: Record<string, string> = {
  available: "text-emerald-600 font-semibold",
  limited: "text-amber-600 font-semibold",
  unavailable: "text-red-500 font-semibold",
};

// ─── Sub-components ────────────────────────────────────────────────────────────
function Label({ children }: { children: React.ReactNode }) {
  return <label className="block text-xs font-bold text-slate-600 uppercase tracking-wider mb-1.5">{children}</label>;
}

function FormInput({ ...props }) {
  return (
    <input
      {...props}
      className="w-full bg-sky-50/80 border border-sky-200 rounded-xl px-4 py-2.5 text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:border-sky-400 focus:ring-2 focus:ring-sky-500/20 transition-all font-medium"
    />
  );
}

function FormSelect({ children, ...props }: React.SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <select
      {...props}
      className="w-full bg-sky-50/80 border border-sky-200 rounded-xl px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-sky-400 focus:ring-2 focus:ring-sky-500/20 transition-all font-medium"
    >
      {children}
    </select>
  );
}

function ChipGroup({ options, value, onChange }: { options: string[]; value: string; onChange: (v: string) => void }) {
  return (
    <div className="flex flex-wrap gap-2">
      {options.map((opt) => (
        <button
          key={opt}
          type="button"
          onClick={() => onChange(opt)}
          className={`px-3 py-1.5 rounded-xl text-xs font-semibold border transition-all ${
            value === opt
              ? "bg-gradient-to-r from-sky-500 to-blue-600 border-sky-500 text-white shadow-sm shadow-sky-200"
              : "bg-slate-50 border-slate-200 text-slate-600 hover:border-sky-200 hover:bg-sky-50 hover:text-sky-700"
          }`}
        >
          {opt}
        </button>
      ))}
    </div>
  );
}

function ScoreMeter({ score }: { score: number }) {
  const color = score >= 90 ? "#059669" : score >= 75 ? "#0284c7" : score >= 60 ? "#d97706" : "#dc2626";
  return (
    <div className="flex items-center gap-2">
      <div className="relative w-10 h-10">
        <svg viewBox="0 0 36 36" className="w-10 h-10 -rotate-90">
          <circle cx="18" cy="18" r="15" fill="none" stroke="#e2e8f0" strokeWidth="3" />
          <circle
            cx="18" cy="18" r="15" fill="none"
            stroke={color} strokeWidth="3"
            strokeDasharray={`${(score / 100) * 94.2} 94.2`}
            strokeLinecap="round"
          />
        </svg>
        <span className="absolute inset-0 flex items-center justify-center text-[11px] font-black" style={{ color }}>
          {score}
        </span>
      </div>
    </div>
  );
}

function VesselCard({
  vessel,
  selected,
  expanded,
  onSelect,
  onExpand,
}: {
  vessel: typeof defaultVessels[0];
  selected: boolean;
  expanded: boolean;
  onSelect: () => void;
  onExpand: () => void;
}) {
  return (
    <div
      className={`relative bg-white border rounded-2xl transition-all ${
        selected
          ? "border-sky-500 shadow-md shadow-sky-100 ring-2 ring-sky-500/20"
          : "border-sky-100 hover:border-sky-300 shadow-sm"
      }`}
    >
      {selected && <div className="absolute left-0 top-3 bottom-3 w-1.5 bg-gradient-to-b from-sky-500 to-blue-600 rounded-r" />}

      {vessel.recommended && (
        <div className="absolute -top-3 right-4 flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-0.5 rounded-full shadow-sm">
          <Star className="w-3 h-3 fill-emerald-500 text-emerald-500" /> AI Recommended
        </div>
      )}

      <div className="p-5">
        <div className="grid grid-cols-12 gap-3 items-center">
          {/* Select + Score */}
          <div className="col-span-1 flex flex-col items-center gap-2">
            <input
              type="radio"
              checked={selected}
              onChange={onSelect}
              className="w-4 h-4 accent-sky-500 cursor-pointer"
            />
            <ScoreMeter score={vessel.aiScore} />
          </div>

          {/* Vessel Identity */}
          <div className="col-span-4">
            <div className="flex items-center gap-2 mb-0.5">
              <span className="text-lg">{vessel.flag}</span>
              <p className="font-bold text-slate-900 text-sm">{vessel.name}</p>
            </div>
            <p className="text-xs text-slate-500">IMO: {vessel.imo} · {vessel.owner}</p>
            <p className="text-xs text-slate-400 mt-0.5">{vessel.broker}</p>
            <div className="flex items-center gap-1.5 mt-2">
              <span className={`px-2 py-0.5 text-[10px] font-bold uppercase border rounded-md ${portFitStyles[vessel.portFitLevel]}`}>
                {vessel.portFit}
              </span>
              <span className="px-2 py-0.5 text-[10px] font-medium text-slate-600 bg-slate-100 border border-slate-200 rounded-md">
                {vessel.type}
              </span>
            </div>
          </div>

          {/* Specs */}
          <div className="col-span-3 grid grid-cols-2 gap-x-4 gap-y-1 text-xs">
            <div>
              <p className="text-slate-400 font-medium">Capacity</p>
              <p className="text-slate-800 font-semibold">{vessel.capacity.toLocaleString()} MT</p>
            </div>
            <div>
              <p className="text-slate-400 font-medium">Built</p>
              <p className="text-slate-800 font-semibold">{vessel.built}</p>
            </div>
            <div>
              <p className="text-slate-400 font-medium">Draft</p>
              <p className="text-slate-800 font-semibold">{vessel.draft}</p>
            </div>
            <div>
              <p className="text-slate-400 font-medium">Position</p>
              <p className="text-slate-800 font-semibold truncate">{vessel.position}</p>
            </div>
          </div>

          {/* Availability */}
          <div className="col-span-2 text-xs">
            <p className="text-slate-400 font-medium mb-1">Laycan</p>
            <p className={availStyles[vessel.availStatus]}>{vessel.availability}</p>
            <div className="flex items-center gap-1 mt-1">
              <Clock className="w-3 h-3 text-slate-400" />
              <span className="text-slate-500">ETA: {vessel.eta}</span>
            </div>
          </div>

          {/* Freight + Expand */}
          <div className="col-span-2 text-right">
            <p className="text-2xl font-black text-sky-600">${vessel.freight}</p>
            <p className="text-xs text-slate-500">/ MT</p>
            <button
              onClick={onExpand}
              className="mt-2 flex items-center gap-1 text-xs text-slate-500 hover:text-sky-600 transition-colors ml-auto font-medium"
            >
              {expanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
              {expanded ? "Less" : "Details"}
            </button>
          </div>
        </div>

        {/* Expanded Details */}
        {expanded && (
          <div className="mt-4 pt-4 border-t border-slate-100 grid grid-cols-1 md:grid-cols-3 gap-4 bg-slate-50/70 p-4 rounded-xl">
            <div className="space-y-2">
              <p className="text-xs font-bold uppercase tracking-wider text-slate-700">Technical Specs</p>
              {[
                ["LOA", vessel.loa],
                ["Beam", vessel.beam],
                ["Draft", vessel.draft],
              ].map(([k, v]) => (
                <div key={k} className="flex justify-between text-xs">
                  <span className="text-slate-500">{k}</span>
                  <span className="text-slate-800 font-semibold">{v}</span>
                </div>
              ))}
            </div>
            <div className="space-y-2">
              <p className="text-xs font-bold uppercase tracking-wider text-slate-700">Commercial</p>
              {[
                ["Freight Rate", `$${vessel.freight} / MT`],
                ["Owner", vessel.owner],
                ["Broker", vessel.broker],
              ].map(([k, v]) => (
                <div key={k} className="flex justify-between text-xs">
                  <span className="text-slate-500">{k}</span>
                  <span className="text-slate-800 font-semibold">{v}</span>
                </div>
              ))}
            </div>
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">AI Strengths</p>
              <ul className="space-y-1.5">
                {vessel.strengths.map((s) => (
                  <li key={s} className="flex items-start gap-1.5 text-xs text-slate-700">
                    <CheckCircle className="w-3.5 h-3.5 text-emerald-600 mt-0.5 shrink-0" />
                    {s}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Main Page ─────────────────────────────────────────────────────────────────
export default function CargoPage() {
  const router = useRouter();

  // Cargo requirement state
  const [commodity, setCommodity] = useState("Coal");
  const [quantity, setQuantity] = useState("80000");
  const [grade, setGrade] = useState("6000 GAR, 10% Ash");
  const [origin, setOrigin] = useState("Newcastle, Australia");
  const [destination, setDestination] = useState("Paradip, India");
  const [deliveryDate, setDeliveryDate] = useState("2026-10-15");
  const [laycanStart, setLaycanStart] = useState("2026-09-10");
  const [laycanEnd, setLaycanEnd] = useState("2026-09-24");
  const [priority, setPriority] = useState("Balanced");
  const [voyages, setVoyages] = useState("3");
  const [vesselTypeFilter, setVesselTypeFilter] = useState("Any");
  const [contract, setContract] = useState("AI Recommended");

  // Vessel state
  const [vesselList, setVesselList] = useState(defaultVessels);
  const [selectedVessel, setSelectedVessel] = useState<number | string | null>(1);
  const [expandedVessel, setExpandedVessel] = useState<number | string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [showFilters, setShowFilters] = useState(false);
  const [analyzed, setAnalyzed] = useState(false);
  const [isLiveRanked, setIsLiveRanked] = useState(false);

  useEffect(() => {
    let isMounted = true;
    const reqPayload = {
      origin_port: origin.split(",")[0].trim(),
      destination_port: destination.split(",")[0].trim(),
      quantity_mt: Number(quantity) || 80000,
      cargo_type: commodity,
      laycan_start: laycanStart,
      laycan_end: laycanEnd,
      contract_type: contract,
      priority: priority as any,
    };

    fetchRecommendations(reqPayload)
      .then((res) => {
        if (!isMounted || !res?.recommendations?.length) return;
        const recMap = new Map();
        res.recommendations.forEach((r) => {
          recMap.set(r.vessel?.name, r);
        });

        setVesselList((prev) =>
          prev.map((v) => {
            const match = recMap.get(v.name);
            if (match) {
              return {
                ...v,
                aiScore: Math.round(match.scores?.composite_score ?? v.aiScore),
                freight: match.financials?.cost_per_ton_usd ? Number(match.financials.cost_per_ton_usd.toFixed(2)) : v.freight,
                recommended: match.rank === 1,
              };
            }
            return v;
          }).sort((a, b) => b.aiScore - a.aiScore)
        );
        setIsLiveRanked(true);
      })
      .catch((err) => {
        console.warn("Recommendations API fallback:", err);
      });

    return () => {
      isMounted = false;
    };
  }, [priority, commodity, quantity, origin, destination]);

  const filteredVessels = vesselList.filter((v) => {
    const matchesSearch = v.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      v.owner.toLowerCase().includes(searchQuery.toLowerCase()) ||
      v.type.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = vesselTypeFilter === "Any" || v.type === vesselTypeFilter;
    return matchesSearch && matchesType;
  });

  const selectedVesselData = vesselList.find((v) => v.id === selectedVessel) || vesselList[0];

  const handleAnalyze = async () => {
    setAnalyzed(true);
    const reqPayload = {
      origin_port: origin.split(",")[0].trim(),
      destination_port: destination.split(",")[0].trim(),
      quantity_mt: Number(quantity) || 80000,
      cargo_type: commodity,
      laycan_start: laycanStart,
      laycan_end: laycanEnd,
      contract_type: contract,
      priority: priority as any,
    };

    try {
      const rec = await fetchRecommendations(reqPayload);
      if (typeof window !== "undefined") {
        sessionStorage.setItem("freightiq_decision", JSON.stringify(rec));
        sessionStorage.setItem("freightiq_cargo", JSON.stringify(reqPayload));
        if (selectedVesselData) {
          sessionStorage.setItem("freightiq_selected_vessel", JSON.stringify(selectedVesselData));
        }
      }
    } catch (e) {
      console.warn("Using offline decision context:", e);
      if (typeof window !== "undefined") {
        sessionStorage.setItem("freightiq_cargo", JSON.stringify(reqPayload));
        if (selectedVesselData) {
          sessionStorage.setItem("freightiq_selected_vessel", JSON.stringify(selectedVesselData));
        }
      }
    }

    setTimeout(() => router.push("/dashboard/decision"), 800);
  };

  return (
    <div className="flex flex-col min-h-screen bg-[#f0f7ff] text-slate-900">
      <Topbar title="Cargo Requirement & Vessel Search" />

      <main className="flex-1 p-6 lg:p-8 space-y-6">
        {/* ── Page Header ── */}
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">SAIL Cargo Requirement</h1>
            <p className="text-slate-500 text-sm mt-1">
              Define your cargo needs, then select an available vessel. FreightIQ will optimize the chartering decision.
            </p>
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-sky-50 border border-sky-200">
            <Zap className="w-3.5 h-3.5 text-sky-500" />
            <span className="text-xs font-semibold text-sky-700">AI Analysis Ready</span>
          </div>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-5 gap-6">
          {/* ═══════════════════════════════════════════════════════
              LEFT PANEL — Cargo Requirement Form (2/5 width)
          ═══════════════════════════════════════════════════════ */}
          <div className="xl:col-span-2 space-y-5">
            {/* Cargo Details */}
            <div className="bg-white border border-sky-100 rounded-2xl p-5 shadow-sm">
              <div className="flex items-center gap-2 mb-4">
                <div className="p-2 rounded-xl bg-sky-50 text-sky-600 border border-sky-100"><Package className="w-4 h-4" /></div>
                <h3 className="text-sm font-bold text-slate-900">Cargo Details</h3>
              </div>
              <div className="space-y-4">
                <div>
                  <Label>Commodity</Label>
                  <ChipGroup options={commodities} value={commodity} onChange={setCommodity} />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <Label>Quantity (MT)</Label>
                    <FormInput
                      type="number"
                      value={quantity}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) => setQuantity(e.target.value)}
                      placeholder="80,000"
                    />
                  </div>
                  <div>
                    <Label>No. of Voyages</Label>
                    <FormInput
                      type="number"
                      value={voyages}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) => setVoyages(e.target.value)}
                      min={1}
                    />
                  </div>
                </div>
                <div>
                  <Label>Cargo Grade / Specification</Label>
                  <FormInput
                    type="text"
                    value={grade}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setGrade(e.target.value)}
                    placeholder="e.g. 6000 GAR, 10% Ash"
                  />
                </div>
              </div>
            </div>

            {/* Route */}
            <div className="bg-white border border-sky-100 rounded-2xl p-5 shadow-sm">
              <div className="flex items-center gap-2 mb-4">
                <div className="p-2 rounded-xl bg-sky-50 text-sky-600 border border-sky-100"><Globe className="w-4 h-4" /></div>
                <h3 className="text-sm font-bold text-slate-900">Route</h3>
              </div>
              <div className="space-y-3">
                <div>
                  <Label>Origin Port</Label>
                  <FormInput
                    type="text"
                    value={origin}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setOrigin(e.target.value)}
                    placeholder="Newcastle, Australia"
                  />
                </div>
                <div>
                  <Label>Destination Port (East Coast India)</Label>
                  <FormSelect
                    value={destination}
                    onChange={(e) => setDestination(e.target.value)}
                  >
                    {["Paradip, India", "Dhamra, India", "Visakhapatnam, India", "Gangavaram, India", "Gopalpur, India", "Haldia, India"].map(d => (
                      <option key={d}>{d}</option>
                    ))}
                  </FormSelect>
                </div>
              </div>
            </div>

            {/* Delivery */}
            <div className="bg-white border border-sky-100 rounded-2xl p-5 shadow-sm">
              <div className="flex items-center gap-2 mb-4">
                <div className="p-2 rounded-xl bg-sky-50 text-sky-600 border border-sky-100"><Calendar className="w-4 h-4" /></div>
                <h3 className="text-sm font-bold text-slate-900">Delivery Requirement</h3>
              </div>
              <div className="space-y-3">
                <div>
                  <Label>Required Delivery Date</Label>
                  <FormInput
                    type="date"
                    value={deliveryDate}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setDeliveryDate(e.target.value)}
                  />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <Label>Laycan Start</Label>
                    <FormInput
                      type="date"
                      value={laycanStart}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) => setLaycanStart(e.target.value)}
                    />
                  </div>
                  <div>
                    <Label>Laycan End</Label>
                    <FormInput
                      type="date"
                      value={laycanEnd}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) => setLaycanEnd(e.target.value)}
                    />
                  </div>
                </div>
                <div>
                  <Label>Priority</Label>
                  <ChipGroup options={priorities} value={priority} onChange={setPriority} />
                </div>
              </div>
            </div>

            {/* Charter Preference */}
            <div className="bg-white border border-sky-100 rounded-2xl p-5 shadow-sm">
              <div className="flex items-center gap-2 mb-4">
                <div className="p-2 rounded-xl bg-sky-50 text-sky-600 border border-sky-100"><FileText className="w-4 h-4" /></div>
                <h3 className="text-sm font-bold text-slate-900">Charter Preference</h3>
              </div>
              <div>
                <Label>Contract Type</Label>
                <ChipGroup options={contractPreferences} value={contract} onChange={setContract} />
              </div>
            </div>

            {/* Selected Vessel Summary Card */}
            {selectedVesselData && (
              <div className="bg-gradient-to-br from-sky-50 to-blue-50 border border-sky-200 rounded-2xl p-5 shadow-sm">
                <p className="text-xs font-bold uppercase tracking-widest text-sky-700 mb-3">Selected Vessel Summary</p>
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="font-bold text-slate-900">{selectedVesselData.flag} {selectedVesselData.name}</p>
                    <p className="text-xs text-slate-600 mt-0.5">{selectedVesselData.type} · {selectedVesselData.capacity.toLocaleString()} MT</p>
                    <p className="text-xs text-slate-500">{selectedVesselData.availability}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-black text-sky-600">${selectedVesselData.freight}</p>
                    <p className="text-xs text-slate-500">/ MT</p>
                  </div>
                </div>
                <div className="mt-3 pt-3 border-t border-sky-200/60 flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    <Star className="w-3.5 h-3.5 text-sky-500 fill-sky-500" />
                    <span className="text-xs text-slate-700 font-medium">AI Score: <strong className="text-sky-700">{selectedVesselData.aiScore} / 100</strong></span>
                  </div>
                  <span className={`px-2 py-0.5 text-[10px] font-bold uppercase border rounded-md ${portFitStyles[selectedVesselData.portFitLevel]}`}>
                    {selectedVesselData.portFit}
                  </span>
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex flex-col gap-3 pb-8">
              <button
                type="button"
                onClick={handleAnalyze}
                disabled={!selectedVessel || analyzed}
                className="flex items-center justify-center gap-2 w-full px-6 py-3.5 rounded-xl bg-gradient-to-r from-sky-500 to-blue-600 text-white font-bold hover:from-sky-400 hover:to-blue-500 transition-all shadow-md shadow-sky-200 hover:shadow-lg hover:shadow-sky-300 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {analyzed ? (
                  <><CheckCircle className="w-4 h-4" /> Analyzing... Redirecting</>
                ) : (
                  <><Zap className="w-4 h-4" /> Analyze Charter Requirement <ArrowRight className="w-4 h-4" /></>
                )}
              </button>
              <button
                type="button"
                className="flex items-center justify-center gap-2 w-full px-6 py-3 rounded-xl border border-slate-200 bg-white text-slate-700 font-semibold hover:bg-slate-50 hover:border-sky-300 transition-all shadow-sm"
              >
                <Save className="w-4 h-4 text-slate-400" /> Save Draft
              </button>
            </div>
          </div>

          {/* ═══════════════════════════════════════════════════════
              RIGHT PANEL — Vessel Search & Availability (3/5 width)
          ═══════════════════════════════════════════════════════ */}
          <div className="xl:col-span-3 space-y-5">
            {/* Vessel Search Header */}
            <div className="bg-white border border-sky-100 rounded-2xl p-5 shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <div className="p-2 rounded-xl bg-sky-50 text-sky-600 border border-sky-100"><Ship className="w-4 h-4" /></div>
                  <h3 className="text-sm font-bold text-slate-900">Available Vessel Search</h3>
                  <span className="ml-2 px-2 py-0.5 rounded-full bg-emerald-50 border border-emerald-200 text-[10px] font-bold text-emerald-700">
                    {filteredVessels.length} FOUND
                  </span>
                </div>
                <button
                  onClick={() => setShowFilters(!showFilters)}
                  className="flex items-center gap-1.5 text-xs text-slate-600 hover:text-sky-700 transition-colors border border-slate-200 bg-slate-50 rounded-xl px-3 py-1.5 hover:border-sky-300 font-medium"
                >
                  <Filter className="w-3.5 h-3.5 text-slate-400" /> Filters
                </button>
              </div>

              {/* Search Bar */}
              <div className="relative mb-3">
                <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-sky-400" />
                <input
                  type="text"
                  placeholder="Search vessel name, type or owner..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full bg-sky-50/80 border border-sky-200 rounded-xl pl-10 pr-4 py-2.5 text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:border-sky-400 focus:ring-2 focus:ring-sky-500/20 transition-all font-medium"
                />
              </div>

              {/* Filter Row */}
              {showFilters && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-3 pt-3 border-t border-slate-100">
                  <div>
                    <Label>Vessel Type</Label>
                    <ChipGroup options={vesselTypes} value={vesselTypeFilter} onChange={setVesselTypeFilter} />
                  </div>
                </div>
              )}

              {/* Availability Legend */}
              <div className="flex items-center gap-5 mt-3 pt-3 border-t border-slate-100">
                <span className="text-xs text-slate-500 font-semibold">Availability:</span>
                {[
                  { color: "bg-emerald-500", label: "Available" },
                  { color: "bg-amber-500", label: "Limited" },
                  { color: "bg-red-500", label: "Unavailable" },
                ].map(({ color, label }) => (
                  <span key={label} className="flex items-center gap-1.5 text-xs text-slate-600">
                    <span className={`w-2 h-2 rounded-full ${color}`} /> {label}
                  </span>
                ))}
                <span className="ml-auto text-xs text-slate-400 flex items-center gap-1">
                  <Info className="w-3 h-3" /> Select a vessel to proceed
                </span>
              </div>
            </div>

            {/* AI Insight Banner */}
            <div className="bg-gradient-to-r from-sky-50 to-blue-50 border border-sky-200 rounded-2xl p-4 flex items-start gap-3 shadow-sm">
              <div className="p-2 bg-white rounded-xl shadow-sm border border-sky-100 shrink-0 text-sky-600">
                <Gauge className="w-4 h-4" />
              </div>
              <div>
                <p className="text-xs font-bold text-sky-800 mb-1">AI Market Intelligence — Live</p>
                <p className="text-xs text-slate-600 leading-relaxed">
                  <strong className="text-slate-900">MV Pacific Voyager</strong> is the optimal match for your requirement —
                  best combination of freight rate (<strong className="text-sky-700 font-bold">$17.40/MT</strong>),
                  draft compatibility with Paradip, and availability within your laycan window of
                  <strong className="text-slate-900"> 10–24 Sep 2026</strong>. Freight rates are softening — favourable for spot/short-term entry.
                </p>
              </div>
            </div>

            {/* Market Summary Strip */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {[
                { label: "Panamax Rate", value: "$17.40 – $18.10", sub: "/ MT", icon: <TrendingDown className="w-4 h-4 text-emerald-600" /> },
                { label: "Available Panamax", value: "12 Vessels", sub: "NE Australia", icon: <Ship className="w-4 h-4 text-sky-500" /> },
                { label: "Avg. Laycan", value: "8–18 Sep", sub: "Current window", icon: <Clock className="w-4 h-4 text-amber-500" /> },
                { label: "Market Trend", value: "Bearish", sub: "Softening", icon: <Anchor className="w-4 h-4 text-blue-500" /> },
              ].map((stat) => (
                <div key={stat.label} className="bg-white border border-sky-100 rounded-2xl p-4 shadow-sm">
                  <div className="flex items-center gap-2 mb-1.5">{stat.icon}<p className="text-xs text-slate-500 font-medium">{stat.label}</p></div>
                  <p className="text-base font-bold text-slate-900">{stat.value}</p>
                  <p className="text-[10px] text-slate-400 mt-0.5">{stat.sub}</p>
                </div>
              ))}
            </div>

            {/* Vessel List */}
            <div className="space-y-4">
              {filteredVessels.length === 0 ? (
                <div className="text-center py-12 text-slate-400 bg-white rounded-2xl border border-sky-100 p-8">
                  <Ship className="w-10 h-10 mx-auto mb-3 opacity-30 text-slate-400" />
                  <p>No vessels found matching your filters.</p>
                </div>
              ) : (
                filteredVessels.map((v) => (
                  <VesselCard
                    key={v.id}
                    vessel={v}
                    selected={selectedVessel === v.id}
                    expanded={expandedVessel === v.id}
                    onSelect={() => setSelectedVessel(v.id)}
                    onExpand={() => setExpandedVessel(expandedVessel === v.id ? null : v.id)}
                  />
                ))
              )}
            </div>

            {/* Comparison note */}
            <div className="flex items-center gap-2 px-4 py-3 rounded-xl bg-sky-50/70 border border-sky-100">
              <Users className="w-4 h-4 text-sky-600 shrink-0" />
              <p className="text-xs text-slate-600">
                Showing <strong className="text-slate-900">{filteredVessels.length}</strong> vessels available for your route.
                All scores are computed by FreightIQ AI based on your cargo, route, and laycan parameters.
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
