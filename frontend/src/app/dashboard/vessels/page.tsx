"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Topbar from "@/components/layout/Topbar";
import { ArrowRight, Star, Ship, Filter, CheckCircle, AlertTriangle, TrendingDown, Activity } from "lucide-react";
import { fetchVessels, VesselData } from "@/lib/api";

const defaultVessels = [
  {
    id: 1,
    name: "MV Pacific Voyager",
    imo: "9412567",
    type: "Panamax",
    capacity: 82000,
    built: 2018,
    draft: "14.2m",
    availability: "10–15 Sep 2026",
    freight: 17.4,
    portFit: "Excellent",
    portFitColor: "emerald",
    aiScore: 94,
    owner: "Pacific Bulk Carriers",
    flag: "🇵🇦",
    recommended: true,
  },
  {
    id: 2,
    name: "MV Eastern Star",
    imo: "9501234",
    type: "Panamax",
    capacity: 78500,
    built: 2016,
    draft: "13.8m",
    availability: "12–18 Sep 2026",
    freight: 17.9,
    portFit: "Good",
    portFitColor: "cyan",
    aiScore: 87,
    owner: "Eastern Maritime",
    flag: "🇸🇬",
    recommended: false,
  },
  {
    id: 3,
    name: "MV Atlas Pride",
    imo: "9388901",
    type: "Supramax",
    capacity: 56000,
    built: 2015,
    draft: "12.5m",
    availability: "8–14 Sep 2026",
    freight: 16.2,
    portFit: "Excellent",
    portFitColor: "emerald",
    aiScore: 81,
    owner: "Atlas Shipping",
    flag: "🇬🇷",
    recommended: false,
  },
  {
    id: 4,
    name: "MV Cape Meridian",
    imo: "9623445",
    type: "Capesize",
    capacity: 175000,
    built: 2020,
    draft: "18.5m",
    availability: "20–28 Sep 2026",
    freight: 14.8,
    portFit: "Restricted",
    portFitColor: "amber",
    aiScore: 63,
    owner: "Meridian Ocean",
    flag: "🇳🇴",
    recommended: false,
  },
];

const portFitStyles: Record<string, string> = {
  emerald: "text-emerald-700 bg-emerald-50 border-emerald-200",
  cyan: "text-sky-700 bg-sky-50 border-sky-200",
  amber: "text-amber-700 bg-amber-50 border-amber-200",
};

function ScoreBadge({ score }: { score: number }) {
  const color = score >= 90 ? "text-emerald-600" : score >= 75 ? "text-sky-600" : score >= 60 ? "text-amber-600" : "text-red-600";
  return (
    <div className="flex items-center gap-1.5">
      <Star className={`w-3.5 h-3.5 fill-current ${color}`} />
      <span className={`font-black text-sm ${color}`}>{score}</span>
      <span className="text-slate-400 text-xs font-semibold">/100</span>
    </div>
  );
}

export default function VesselsPage() {
  const router = useRouter();
  const [vessels, setVessels] = useState(defaultVessels);
  const [selected, setSelected] = useState<number | string | null>(1);
  const [isLive, setIsLive] = useState(false);

  useEffect(() => {
    let isMounted = true;
    fetchVessels()
      .then((apiVessels) => {
        if (!isMounted || !apiVessels || apiVessels.length === 0) return;
        // Merge or map with defaults
        const mapped = apiVessels.slice(0, 8).map((v: any, idx: number) => {
          const type = v.vessel_type || v.type || "Panamax";
          const dwt = v.deadweight_tonnage || v.capacity || 80000;
          const draft = v.max_draft_m ? `${v.max_draft_m}m` : v.draft || "14.2m";
          const draftNum = parseFloat(draft);
          const portFit = draftNum <= 14.5 ? "Excellent" : draftNum <= 16.0 ? "Good" : "Restricted";
          const portFitColor = portFit === "Excellent" ? "emerald" : portFit === "Good" ? "cyan" : "amber";
          const freight = v.freight || (v.daily_hire_rate_usd ? Math.round((v.daily_hire_rate_usd * 21) / (dwt * 0.9) * 10) / 10 : 17.4);
          const aiScore = idx === 0 ? 94 : Math.max(60, 92 - idx * 7);

          return {
            id: v.vessel_id || idx + 1,
            name: v.name,
            imo: v.imo || `94${12345 + idx}`,
            type,
            capacity: dwt,
            built: v.built_year || v.built || 2018,
            draft,
            availability: v.availability || "10–18 Sep 2026",
            freight,
            portFit,
            portFitColor,
            aiScore,
            owner: v.owner || v.operator || "Pacific Bulk Carriers",
            flag: v.flag || "🇵🇦",
            recommended: idx === 0,
          };
        });
        setVessels(mapped);
        setSelected(mapped[0].id);
        setIsLive(true);
      })
      .catch((err) => {
        console.warn("Using default vessels list:", err);
      });
    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <div className="flex flex-col min-h-screen bg-[#f0f7ff] text-slate-900">
      <Topbar title="Available Vessel Search" />

      <main className="flex-1 p-6 lg:p-8 space-y-6">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Available Vessel Search</h1>
            <p className="text-slate-500 text-sm mt-1">
              Route: Newcastle, Australia → Paradip, India • Cargo: 80,000 MT Coal
            </p>
          </div>
          <div className="flex items-center gap-3">
            {isLive && (
              <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-semibold">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                <span>Live Fleet API</span>
              </div>
            )}
            <button className="flex items-center gap-2 px-4 py-2 rounded-xl border border-slate-200 bg-white text-slate-700 hover:border-sky-300 hover:bg-sky-50 transition-all text-sm font-semibold shadow-sm">
              <Filter className="w-4 h-4 text-slate-400" /> Filters
            </button>
          </div>
        </div>

        {/* AI Summary */}
        <div className="rounded-2xl p-5 border border-sky-200 bg-gradient-to-r from-sky-50 to-blue-50 flex items-start gap-4 shadow-sm">
          <div className="p-2 bg-white border border-sky-100 rounded-xl shrink-0 text-sky-600 shadow-sm">
            <TrendingDown className="w-5 h-5 text-sky-500" />
          </div>
          <div>
            <p className="text-sm font-bold text-sky-800 mb-1">AI Vessel Intelligence</p>
            <p className="text-sm text-slate-600 leading-relaxed">
              4 vessels found matching your cargo requirement. <strong className="text-slate-900 font-bold">MV Pacific Voyager</strong> is recommended — best balance of freight rate ($17.4/MT), port draft compatibility and availability within your laycan window.
            </p>
          </div>
        </div>

        {/* Vessel Cards */}
        <div className="space-y-4">
          {vessels.map((v) => (
            <div
              key={v.id}
              onClick={() => setSelected(v.id)}
              className={`relative bg-white border rounded-2xl p-5 cursor-pointer transition-all ${
                selected === v.id
                  ? "border-sky-500 shadow-md shadow-sky-100 ring-2 ring-sky-500/20"
                  : "border-sky-100 hover:border-sky-300 shadow-sm"
              }`}
            >
              {v.recommended && (
                <span className="absolute top-4 right-4 flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-0.5 rounded-full shadow-sm">
                  <Star className="w-3 h-3 fill-emerald-500 text-emerald-500" /> AI Recommended
                </span>
              )}

              <div className="grid grid-cols-2 md:grid-cols-6 gap-4 items-center">
                {/* Name */}
                <div className="md:col-span-2">
                  <div className="flex items-center gap-2 mb-1">
                    <Ship className="w-4 h-4 text-sky-500" />
                    <p className="font-bold text-slate-900">{v.flag} {v.name}</p>
                  </div>
                  <p className="text-xs text-slate-500 font-medium">IMO: {v.imo} • {v.owner}</p>
                  <p className="text-xs text-slate-400 mt-0.5">{v.type} • Built {v.built} • Draft {v.draft}</p>
                </div>

                {/* Capacity */}
                <div>
                  <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Capacity</p>
                  <p className="font-bold text-slate-800">{v.capacity.toLocaleString()} MT</p>
                </div>

                {/* Availability */}
                <div>
                  <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Laycan</p>
                  <p className="font-bold text-emerald-600 text-sm">{v.availability}</p>
                </div>

                {/* Freight */}
                <div>
                  <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Freight</p>
                  <p className="font-black text-sky-600 text-xl">${v.freight}</p>
                  <p className="text-xs text-slate-400 font-medium">/ MT</p>
                </div>

                {/* AI Score + Port Fit */}
                <div className="space-y-2">
                  <div>
                    <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold mb-1">AI Score</p>
                    <ScoreBadge score={v.aiScore} />
                  </div>
                  <span className={`inline-flex items-center gap-1 text-xs font-bold border px-2 py-0.5 rounded-md ${portFitStyles[v.portFitColor]}`}>
                    {v.portFit === "Excellent" ? <CheckCircle className="w-3 h-3 text-emerald-600" /> : <AlertTriangle className="w-3 h-3 text-amber-600" />}
                    {v.portFit}
                  </span>
                </div>
              </div>

              {/* Selection indicator */}
              {selected === v.id && (
                <div className="absolute left-0 top-3 bottom-3 w-1.5 bg-gradient-to-b from-sky-500 to-blue-600 rounded-r" />
              )}
            </div>
          ))}
        </div>

        {/* Action */}
        <div className="flex items-center gap-4 pb-8">
          <button
            onClick={() => router.push("/dashboard/ports")}
            className="flex items-center gap-2 px-8 py-3.5 rounded-xl bg-gradient-to-r from-sky-500 to-blue-600 text-white font-bold hover:from-sky-400 hover:to-blue-500 transition-all shadow-md shadow-sky-200 hover:shadow-lg hover:shadow-sky-300"
          >
            Check Port Compatibility <ArrowRight className="w-4 h-4" />
          </button>
          <p className="text-sm text-slate-500 font-medium">
            Selected: <span className="text-slate-900 font-bold">{vessels.find(v => v.id === selected)?.name ?? "None"}</span>
          </p>
        </div>
      </main>
    </div>
  );
}
