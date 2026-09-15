"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import Topbar from "@/components/layout/Topbar";
import MaritimeRouteMap from "@/components/dashboard/MaritimeRouteMap";
import FreightForecastChart from "@/components/dashboard/FreightForecastChart";
import LiquidAlertsPanel from "@/components/dashboard/LiquidAlertsPanel";
import MovingShipBackground from "@/components/ui/MovingShipBackground";
import { ElectroBorder } from "@/components/lightswind/electro-border";
import { MagneticButton } from "@/components/lightswind/magnetic-button";
import { CountUp } from "@/components/lightswind/count-up";
import {
  Ship,
  TrendingDown,
  ShieldCheck,
  CheckCircle2,
  ArrowRight,
  Anchor,
  Compass,
  Zap,
  Star,
  Layers,
  Sparkles,
  BarChart2,
  Navigation,
  TrendingUp,
  Activity,
} from "lucide-react";
import {
  fetchLiveMarket,
  fetchVessels,
  fetchRecommendations,
  fetchModelMetrics,
} from "@/lib/api";

export default function DashboardOverviewPage() {
  const [freightRate, setFreightRate] = useState<number>(17.4);
  const [availableCount, setAvailableCount] = useState<number>(12);
  const [marketTrend, setMarketTrend] = useState<string>("Bearish");
  const [waitingDays, setWaitingDays] = useState<number>(1.4);
  const [confidencePct, setConfidencePct] = useState<string>("94.8%");
  const [topVessel, setTopVessel] = useState<{
    name: string;
    sub: string;
    score: number;
    rate: string;
  }>({
    name: "MV PACIFIC VOYAGER",
    sub: "Panamax Bulk Carrier • Built 2018 • Pacific Bulk Carriers",
    score: 94,
    rate: "$17.40 / MT ($1.39M total)",
  });
  const [isLiveTelemetry, setIsLiveTelemetry] = useState(false);

  useEffect(() => {
    let isMounted = true;

    // 1. Live market
    fetchLiveMarket()
      .then((m) => {
        if (!isMounted || !m) return;
        if (m.panamax_rate) setFreightRate(m.panamax_rate);
        if (m.trend) setMarketTrend(m.trend);
        setIsLiveTelemetry(true);
      })
      .catch(() => {});

    // 2. Available vessels
    fetchVessels("available")
      .then((v) => {
        if (!isMounted || !v) return;
        if (v.length > 0) setAvailableCount(v.length);
      })
      .catch(() => {});

    // 3. Top recommendation
    fetchRecommendations({
      origin_port: "Newcastle",
      destination_port: "Paradip",
      quantity_mt: 80000,
      priority: "Balanced",
      cargo_type: "Coal",
    })
      .then((res) => {
        if (!isMounted || !res?.recommendations?.length) return;
        const top = res.recommendations[0];
        setTopVessel({
          name: (top.vessel?.name || "MV PACIFIC VOYAGER").toUpperCase(),
          sub: `${top.vessel?.vessel_type || "Panamax"} • Built ${top.vessel?.built_year || 2018} • ${top.vessel?.operator || "Pacific Bulk Carriers"}`,
          score: Math.round(top.scores?.composite_score || 94),
          rate: `$${(top.financials?.cost_per_ton_usd || 17.4).toFixed(2)} / MT`,
        });
      })
      .catch(() => {});

    // 4. Model metrics
    fetchModelMetrics()
      .then((met) => {
        if (!isMounted || !met) return;
        if (met.conformal_metrics?.coverage_rate) {
          setConfidencePct(`${(met.conformal_metrics.coverage_rate * 100).toFixed(1)}%`);
        }
      })
      .catch(() => {});

    return () => {
      isMounted = false;
    };
  }, []);
  return (
    <div className="flex flex-col min-h-screen bg-gradient-to-br from-sky-50 via-white to-blue-50 text-slate-900">
      <Topbar title="Maritime Control Center — Executive Terminal" />

      <main className="flex-1 p-6 lg:p-8 space-y-6">
        {/* ══ 1. HERO SECTION ══ */}
        <section className="relative rounded-3xl overflow-hidden border border-sky-200 shadow-lg shadow-sky-100 bg-gradient-to-br from-sky-500 via-blue-600 to-cyan-500 min-h-[280px]">
          {/* Subtle pattern overlay */}
          <div className="absolute inset-0 opacity-10">
            <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4xIj48cGF0aCBkPSJNMzYgMzR2LTRoLTJ2NGgtNHYyaDN2NGgydi00aDN2LTJoLTN6bTAtMzBWMGgtMnY0aC00djJoM3Y0aDJWNmgzVjRoLTN6TTYgMzR2LTRINHYyaDN2NGgydi00aDN2LTJINnoiLz48L2c+PC9nPjwvc3ZnPg==')]" />
          </div>

          {/* Hero Content */}
          <div className="relative z-10 p-8 lg:p-10 flex flex-col lg:flex-row lg:items-center justify-between gap-8">
            <div className="max-w-2xl space-y-4">
              <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-white/30 bg-white/20 backdrop-blur-md text-white text-xs font-semibold tracking-wider uppercase">
                <span className={`w-2 h-2 rounded-full ${isLiveTelemetry ? "bg-emerald-300 animate-ping" : "bg-amber-300"}`} />
                <span>
                  {isLiveTelemetry
                    ? "SAIL MARITIME INTELLIGENCE • FASTAPI & LIVE TELEMETRY CONNECTED"
                    : "SAIL MARITIME INTELLIGENCE • CONNECTING TO FASTAPI BACKEND..."}
                </span>
              </div>

              <h1 className="text-3xl lg:text-4xl font-black tracking-tight text-white leading-tight">
                FREIGHT INTELLIGENCE<br />
                <span className="text-white/80">AT A GLANCE</span>
              </h1>

              <p className="text-sm lg:text-base text-white/75 leading-relaxed max-w-xl">
                Real-time AI chartering optimization for raw material imports. Predict freight swings, match certified bulk carriers, and eliminate port demurrage delays.
              </p>

              {/* CTA Buttons */}
              <div className="pt-2 flex flex-wrap items-center gap-4">
                <Link href="/dashboard/cargo">
                  <MagneticButton
                    variant="primary"
                    size="lg"
                    className="bg-white text-sky-700 hover:bg-sky-50 font-bold shadow-lg shadow-sky-900/20 transition-all flex items-center gap-2 text-sm"
                  >
                    <Zap className="w-4 h-4 text-sky-500" />
                    AI ANALYZE CARGO REQUIREMENT
                    <ArrowRight className="w-4 h-4" />
                  </MagneticButton>
                </Link>

                <Link
                  href="/dashboard/forecast"
                  className="px-6 py-3 rounded-full border border-white/30 bg-white/15 hover:bg-white/25 text-white text-sm font-semibold transition-all backdrop-blur-md flex items-center gap-2"
                >
                  <BarChart2 className="w-4 h-4" />
                  View 30-Day Forecast
                </Link>
              </div>
            </div>

            {/* Quick Live Telemetry Strip */}
            <div className="grid grid-cols-2 gap-3 lg:w-72 shrink-0">
              <div className="p-4 rounded-2xl bg-white/15 border border-white/20 backdrop-blur-md">
                <p className="text-[10px] uppercase font-bold tracking-wider text-white/70">Optimal Window</p>
                <p className="text-base font-bold text-emerald-300 mt-1">10–20 Sep</p>
                <p className="text-[11px] text-white/60">Save up to $720K</p>
              </div>
              <div className="p-4 rounded-2xl bg-white/15 border border-white/20 backdrop-blur-md">
                <p className="text-[10px] uppercase font-bold tracking-wider text-white/70">Top Destination</p>
                <p className="text-base font-bold text-white mt-1">Paradip Port</p>
                <p className="text-[11px] text-sky-200">Draft 14.5m Fit</p>
              </div>
              <div className="p-4 rounded-2xl bg-white/15 border border-white/20 backdrop-blur-md col-span-2 flex items-center justify-between">
                <div>
                  <p className="text-[10px] uppercase font-bold tracking-wider text-white/70">AI Confidence Index</p>
                  <p className="text-xl font-black text-white">{confidencePct}</p>
                </div>
                <div className="text-right">
                  <span className="px-2 py-0.5 rounded bg-emerald-400/20 text-emerald-200 border border-emerald-300/30 text-[10px] font-bold uppercase">
                    Optimal
                  </span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ══ 2. KPI CARDS ══ */}
        <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Card 1: Freight Rate */}
          <div className="group p-5 rounded-2xl bg-white border border-sky-100 hover:border-sky-300 transition-all duration-300 shadow-sm hover:shadow-lg hover:shadow-sky-100 hover:-translate-y-1">
            <div className="flex items-center justify-between text-xs mb-2">
              <span className="font-bold tracking-wider uppercase text-sky-600 flex items-center gap-1.5">
                <Zap className="w-3.5 h-3.5" />
                Panamax Freight Rate
              </span>
              <span className="text-emerald-700 font-bold bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full text-[10px]">
                ↓ 3.2%
              </span>
            </div>
            <div className="flex items-baseline gap-1 my-2">
              <span className="text-3xl font-black text-slate-900">${freightRate ? freightRate.toFixed(2) : "17.40"}</span>
              <span className="text-xs text-slate-400 font-medium ml-1">/ MT</span>
            </div>
            <p className="text-xs text-slate-500">Newcastle → Paradip • Softening trend</p>
            <div className="mt-3 h-1.5 bg-sky-100 rounded-full overflow-hidden">
              <div className="h-full w-4/5 bg-gradient-to-r from-sky-400 to-blue-500 rounded-full" />
            </div>
          </div>

          {/* Card 2: Available Vessels */}
          <div className="group p-5 rounded-2xl bg-white border border-slate-100 hover:border-sky-300 transition-all duration-300 shadow-sm hover:shadow-lg hover:shadow-sky-100 hover:-translate-y-1">
            <div className="flex items-center justify-between text-xs mb-2">
              <span className="font-bold tracking-wider uppercase text-slate-600 flex items-center gap-1.5">
                <Ship className="w-3.5 h-3.5 text-sky-500" />
                Available Vessels
              </span>
              <span className="text-sky-700 font-bold bg-sky-50 border border-sky-200 px-2 py-0.5 rounded-full text-[10px]">
                +3 Today
              </span>
            </div>
            <div className="flex items-baseline gap-1 my-2">
              <span className="text-3xl font-black text-slate-900">{availableCount || 12}</span>
              <span className="text-xs text-slate-400 font-medium ml-1">Panamax & Supramax</span>
            </div>
            <p className="text-xs text-slate-500">Positioned in Bay of Bengal & Aussie laycan</p>
          </div>

          {/* Card 3: Market Trend */}
          <div className="group p-5 rounded-2xl bg-white border border-slate-100 hover:border-emerald-300 transition-all duration-300 shadow-sm hover:shadow-lg hover:shadow-emerald-50 hover:-translate-y-1">
            <div className="flex items-center justify-between text-xs mb-2">
              <span className="font-bold tracking-wider uppercase text-slate-600 flex items-center gap-1.5">
                <TrendingDown className="w-3.5 h-3.5 text-emerald-500" />
                Charter Market Trend
              </span>
              <span className="text-emerald-700 font-bold bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full text-[10px]">
                {marketTrend}
              </span>
            </div>
            <div className="my-2">
              <p className="text-lg font-black text-emerald-600">Favorable Spot Entry</p>
            </div>
            <p className="text-xs text-slate-500">Tonnage surplus exerting downward pressure</p>
          </div>

          {/* Card 4: Port Risk */}
          <div className="group p-5 rounded-2xl bg-white border border-slate-100 hover:border-sky-300 transition-all duration-300 shadow-sm hover:shadow-lg hover:shadow-sky-100 hover:-translate-y-1">
            <div className="flex items-center justify-between text-xs mb-2">
              <span className="font-bold tracking-wider uppercase text-slate-600 flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-sky-500" />
                East Coast Port Risk
              </span>
              <span className="text-sky-700 font-bold bg-sky-50 border border-sky-200 px-2 py-0.5 rounded-full text-[10px]">
                Low Risk
              </span>
            </div>
            <div className="flex items-baseline gap-1 my-2">
              <span className="text-3xl font-black text-slate-900">{waitingDays}</span>
              <span className="text-xs text-slate-400 font-medium ml-1">Days Avg. Waiting</span>
            </div>
            <p className="text-xs text-slate-500">Paradip & Vizag berths operating smoothly</p>
          </div>
        </section>

        {/* ══ 3. AI RECOMMENDATION CARD + MARITIME NETWORK MAP ══ */}
        <section className="grid grid-cols-1 xl:grid-cols-12 gap-6">
          {/* Left: AI Recommendation Card */}
          <div className="xl:col-span-5 flex flex-col">
            <ElectroBorder
              borderColor="#0ea5e9"
              borderWidth={2}
              radius="20px"
              glowBlur={16}
              animationSpeed={1}
              cardBackground="rgba(255, 255, 255, 0.98)"
              className="flex-1 shadow-xl shadow-sky-100"
            >
              <div className="p-6 lg:p-7 flex flex-col justify-between h-full space-y-5">
                {/* Header */}
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2 text-sky-600 text-xs font-bold uppercase tracking-widest">
                      <Sparkles className="w-4 h-4" />
                      <span>✦ AI Market Intelligence</span>
                    </div>
                    <span className="px-2.5 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-700 text-[10px] font-bold uppercase">
                      Top Match
                    </span>
                  </div>

                  <p className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Recommended Vessel</p>
                  <h2 className="text-xl font-black text-slate-900 tracking-tight mt-1 flex items-center gap-2">
                    <Ship className="w-5 h-5 text-sky-500 shrink-0" />
                    <span>{topVessel.name}</span>
                  </h2>
                  <p className="text-xs text-slate-400 mt-1">{topVessel.sub}</p>
                </div>

                {/* AI Match Score */}
                <div className="bg-sky-50 p-4 rounded-xl border border-sky-100">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-xs font-bold text-slate-700">AI MATCH SCORE</span>
                    <span className="text-xl font-black text-sky-600">{topVessel.score} / 100</span>
                  </div>
                  <div className="h-2.5 bg-sky-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-sky-500 via-blue-400 to-emerald-400 rounded-full transition-all duration-500"
                      style={{ width: `${topVessel.score}%` }}
                    />
                  </div>
                </div>

                {/* Validation Criteria */}
                <div className="space-y-2">
                  <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Charter Validation Criteria</p>
                  {[
                    { label: "Capacity Compatible", val: "82,000 MT Coking Coal", check: true },
                    { label: "Draft Fit (Paradip)", val: "14.2m (Max 14.5m allowed)", check: true },
                    { label: "Laycan Window", val: "10–15 Sep 2026 aligned", check: true },
                    { label: "Voyage Rate", val: topVessel.rate, check: true },
                  ].map((item, idx) => (
                    <div key={idx} className="flex items-center justify-between text-xs bg-slate-50 px-3 py-2 rounded-lg border border-slate-100">
                      <span className="flex items-center gap-2 text-slate-700 font-medium">
                        <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                        {item.label}
                      </span>
                      <span className="font-semibold text-sky-600">{item.val}</span>
                    </div>
                  ))}
                </div>

                {/* Action CTA */}
                <Link
                  href="/dashboard/cargo"
                  className="w-full py-3.5 rounded-xl bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-400 hover:to-blue-500 text-white font-bold text-center text-sm shadow-md shadow-sky-200 hover:shadow-lg hover:shadow-sky-300 transition-all flex items-center justify-center gap-2"
                >
                  VIEW VESSEL ANALYSIS & CHARTER
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
            </ElectroBorder>
          </div>

          {/* Right: Maritime Route Map */}
          <div className="xl:col-span-7">
            <MaritimeRouteMap />
          </div>
        </section>

        {/* ══ 4. FREIGHT RATE FORECAST & ALERTS ══ */}
        <section className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Freight Forecast Chart */}
          <div className="lg:col-span-7">
            <FreightForecastChart />
          </div>

          {/* Liquid Alerts Panel */}
          <div className="lg:col-span-5">
            <LiquidAlertsPanel />
          </div>
        </section>
      </main>
    </div>
  );
}
