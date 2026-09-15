"use client";

import React from "react";
import Link from "next/link";
import {
  Anchor,
  ArrowRight,
  BarChart3,
  CheckCircle2,
  Navigation,
  Ship,
  ShieldAlert,
  Cpu,
  Route,
  Settings2,
  Sparkles,
  Zap,
  Globe,
  Compass,
  TrendingUp,
  Shield,
  Activity,
} from "lucide-react";
import { MagneticButton } from "@/components/lightswind/magnetic-button";
import { CountUp } from "@/components/lightswind/count-up";
import { ElectroBorder } from "@/components/lightswind/electro-border";
import MovingShipBackground from "@/components/ui/MovingShipBackground";

export default function LandingDashboard() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-sky-50 via-white to-blue-50 text-slate-900 relative overflow-hidden selection:bg-sky-400 selection:text-white">

      {/* ── Subtle Background Orbs ── */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute -top-40 -right-40 w-[700px] h-[700px] rounded-full bg-gradient-to-br from-sky-200/40 to-blue-200/20 blur-3xl" />
        <div className="absolute top-1/2 -left-40 w-[500px] h-[500px] rounded-full bg-gradient-to-br from-cyan-100/50 to-sky-100/30 blur-3xl" />
        <div className="absolute -bottom-20 right-1/4 w-[400px] h-[400px] rounded-full bg-gradient-to-br from-blue-100/40 to-indigo-100/20 blur-3xl" />
      </div>

      {/* ── Premium Light Maritime Navbar ── */}
      <header className="sticky top-0 z-50 w-full border-b border-sky-200/60 bg-white/80 backdrop-blur-2xl shadow-sm shadow-sky-100 transition-all">
        <div className="max-w-7xl mx-auto flex items-center justify-between px-6 lg:px-8 py-4">
          
          {/* Brand Logo */}
          <Link href="/" className="flex items-center gap-3.5 group">
            <div className="relative">
              <div className="absolute -inset-1 rounded-2xl bg-gradient-to-r from-sky-400 to-blue-500 opacity-30 blur-sm group-hover:opacity-60 transition duration-300" />
              <div className="relative p-2.5 rounded-xl bg-gradient-to-br from-sky-500 to-blue-600 text-white flex items-center justify-center shadow-md">
                <Anchor className="w-5 h-5 group-hover:rotate-12 transition-transform duration-300" />
              </div>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-black tracking-tight text-slate-900 leading-none">
                  Freight<span className="text-transparent bg-clip-text bg-gradient-to-r from-sky-500 to-blue-600">IQ</span>
                </h1>
                <span className="px-1.5 py-0.5 rounded text-[9px] font-mono font-bold bg-sky-100 border border-sky-300 text-sky-700">
                  v2.6
                </span>
              </div>
              <p className="text-[10px] text-slate-500 font-semibold tracking-wider uppercase mt-0.5 flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                AI Maritime Chartering Terminal
              </p>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-1 p-1 rounded-full bg-slate-100/80 border border-slate-200 backdrop-blur-md">
            <Link href="/login" className="px-4 py-1.5 rounded-full text-xs font-semibold text-slate-700 hover:text-sky-700 hover:bg-white hover:shadow-sm transition-all">
              Control Center
            </Link>
            <Link href="#workflow" className="px-4 py-1.5 rounded-full text-xs font-semibold text-slate-500 hover:text-sky-700 hover:bg-white hover:shadow-sm transition-all">
              Workflow
            </Link>
            <Link href="#network" className="px-4 py-1.5 rounded-full text-xs font-semibold text-slate-500 hover:text-sky-700 hover:bg-white hover:shadow-sm transition-all">
              Maritime Network
            </Link>
            <Link href="#intelligence" className="px-4 py-1.5 rounded-full text-xs font-semibold text-slate-500 hover:text-sky-700 hover:bg-white hover:shadow-sm transition-all">
              AI Engine
            </Link>
          </nav>

          {/* Right Action Area */}
          <div className="flex items-center gap-4">
            {/* Live Status Pill */}
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-50 border border-emerald-200 text-[11px] font-mono text-emerald-700">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <span className="font-semibold tracking-wide">AI ENGINE ONLINE</span>
            </div>

            {/* CTA Button */}
            <Link href="/login">
              <MagneticButton
                variant="primary"
                size="md"
                className="bg-gradient-to-r from-sky-500 to-blue-600 text-white hover:from-sky-400 hover:to-blue-500 font-bold text-xs px-5 py-2.5 rounded-xl shadow-md shadow-sky-200 transition-all hover:scale-105 hover:shadow-lg hover:shadow-sky-300 flex items-center gap-1.5"
              >
                <span>Launch Dashboard</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </MagneticButton>
            </Link>
          </div>
        </div>
      </header>

      <main className="relative z-10 flex flex-col items-center">
        {/* ── Hero Section ── */}
        <section className="w-full max-w-7xl mx-auto px-6 py-16 lg:py-24 flex flex-col lg:flex-row items-center gap-12">
          {/* Left Column */}
          <div className="flex-1 space-y-7">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-sky-300/60 bg-sky-50 text-sky-700 text-xs font-semibold tracking-wider uppercase shadow-sm">
              <Sparkles className="w-3.5 h-3.5 text-sky-500" />
              <span>Bloomberg Terminal × Maritime Intelligence</span>
            </div>

            <h2 className="text-4xl sm:text-6xl lg:text-7xl font-black tracking-tight leading-[1.08] text-slate-900">
              AI-POWERED<br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-sky-500 via-blue-500 to-cyan-500">
                MARITIME CHARTERING
              </span><br />
              INTELLIGENCE.
            </h2>

            <p className="text-base sm:text-lg text-slate-600 max-w-2xl leading-relaxed">
              Transform raw material bulk cargo requirements into explainable, optimized chartering decisions. Predict freight trends, match certified vessels, and eliminate port demurrage.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-wrap items-center gap-5 pt-2">
              <Link href="/login">
                <MagneticButton
                  variant="primary"
                  size="lg"
                  className="bg-gradient-to-r from-sky-500 to-blue-600 text-white hover:from-sky-400 hover:to-blue-500 font-bold text-sm shadow-lg shadow-sky-200 hover:shadow-xl hover:shadow-sky-300 flex items-center gap-2 transition-all"
                >
                  GET STARTED →
                </MagneticButton>
              </Link>

              <Link href="/login">
                <MagneticButton
                  variant="outline"
                  size="lg"
                  className="border-sky-300 text-sky-700 hover:bg-sky-50 hover:border-sky-400 font-bold text-sm flex items-center gap-2 transition-all"
                >
                  <Zap className="w-4 h-4 text-sky-500" />
                  ANALYZE CARGO
                </MagneticButton>
              </Link>
            </div>

            {/* Quick Metrics */}
            <div className="pt-4 grid grid-cols-3 gap-4 border-t border-sky-200 max-w-lg">
              <div>
                <p className="text-2xl font-black text-slate-900">94.8%</p>
                <p className="text-[11px] text-slate-500 uppercase tracking-wider font-mono">Prediction Accuracy</p>
              </div>
              <div>
                <p className="text-2xl font-black text-sky-600">12 Vessels</p>
                <p className="text-[11px] text-slate-500 uppercase tracking-wider font-mono">Active in Laycan</p>
              </div>
              <div>
                <p className="text-2xl font-black text-emerald-600">$720K</p>
                <p className="text-[11px] text-slate-500 uppercase tracking-wider font-mono">Avg Voyage Savings</p>
              </div>
            </div>
          </div>

          {/* Right Column: AI Decision Preview Card */}
          <div className="flex-1 w-full max-w-lg relative">
            <ElectroBorder
              borderColor="#0ea5e9"
              borderWidth={2}
              radius="24px"
              glowBlur={20}
              animationSpeed={1}
              cardBackground="rgba(255, 255, 255, 0.97)"
              className="shadow-2xl shadow-sky-200"
            >
              <div className="p-7 space-y-5">
                <div className="flex items-center justify-between border-b border-sky-100 pb-4">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-ping" />
                    <span className="text-xs font-bold uppercase tracking-wider text-sky-700">
                      Live AI Recommendation
                    </span>
                  </div>
                  <span className="px-2.5 py-0.5 rounded-full bg-sky-100 border border-sky-300 text-[10px] font-mono font-bold text-sky-700">
                    MATCH SCORE 94%
                  </span>
                </div>

                <div>
                  <p className="text-xs text-slate-500 uppercase font-semibold">Optimal Panamax Match</p>
                  <h3 className="text-2xl font-black text-slate-900 mt-0.5 flex items-center gap-2">
                    <Ship className="w-6 h-6 text-sky-500 shrink-0" />
                    <span>MV PACIFIC VOYAGER</span>
                  </h3>
                  <p className="text-xs text-slate-500">Newcastle AU → Paradip IN • 82,000 MT Coking Coal</p>
                </div>

                <div className="grid grid-cols-2 gap-3 p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs">
                  <div>
                    <span className="text-slate-400">Freight Rate</span>
                    <p className="text-lg font-black text-sky-600">$17.40 <span className="text-xs font-normal text-slate-400">/ MT</span></p>
                  </div>
                  <div>
                    <span className="text-slate-400">Draft Compatibility</span>
                    <p className="text-lg font-black text-emerald-600">14.2m <span className="text-xs font-normal text-slate-400">(Fit)</span></p>
                  </div>
                  <div>
                    <span className="text-slate-400">Optimal Laycan</span>
                    <p className="font-semibold text-slate-800">10–15 Sep 2026</p>
                  </div>
                  <div>
                    <span className="text-slate-400">Demurrage Risk</span>
                    <p className="font-semibold text-emerald-600">Low (0.6d delay)</p>
                  </div>
                </div>

                <div className="space-y-2 text-xs">
                  <div className="flex items-center gap-2 text-slate-700">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                    <span>Meets Paradip Port draft limits and discharge gear</span>
                  </div>
                  <div className="flex items-center gap-2 text-slate-700">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                    <span>Saves $0.70/MT compared to alternate Capesize option</span>
                  </div>
                </div>

                <Link
                  href="/login"
                  className="w-full py-3 rounded-xl bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-400 hover:to-blue-500 text-white font-bold text-center text-xs block transition-all shadow-md shadow-sky-200 hover:shadow-lg hover:shadow-sky-300 hover:scale-[1.02]"
                >
                  EXPLORE FULL CONTROL TERMINAL →
                </Link>
              </div>
            </ElectroBorder>
          </div>
        </section>

        {/* ── Stats Banner ── */}
        <section className="w-full bg-gradient-to-r from-sky-500 via-blue-600 to-cyan-500 py-10 px-6 relative overflow-hidden">
          <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PHBhdGggZD0iTTM2IDM0di00aC0ydjRoLTR2MmgzdjRoMnYtNGgzdi0yaC0zem0wLTMwVjBoLTJ2NGgtNHYyaDN2NGgyVjZoM1Y0aC0zek02IDM0di00SDR2NGgzdjRoMnYtNGgzdi0ySDZ6bTAtMzBWMEg0djRIOnYyaDN2NGgyVjZoM1Y0SDZ6Ii8+PC9nPjwvZz48L3N2Zz4=')] opacity-100" />
          <div className="max-w-7xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-8 text-white text-center relative">
            {[
              { val: 94.8, suffix: "%", label: "AI Prediction Accuracy", dec: 1 },
              { val: 12, suffix: "+", label: "Vessels in Active Laycan", dec: 0 },
              { val: 720, suffix: "K", label: "Avg. Voyage Savings ($)", dec: 0 },
              { val: 6, suffix: " Ports", label: "East Coast India Coverage", dec: 0 },
            ].map((stat, i) => (
              <div key={i}>
                <div className="flex items-baseline justify-center gap-0.5">
                  <CountUp value={stat.val} decimals={stat.dec} duration={2} className="text-3xl font-black" />
                  <span className="text-xl font-black">{stat.suffix}</span>
                </div>
                <p className="text-xs text-white/75 font-semibold mt-1 uppercase tracking-wider">{stat.label}</p>
              </div>
            ))}
          </div>
        </section>

        {/* ── Workflow Steps Section ── */}
        <section id="workflow" className="w-full max-w-7xl mx-auto px-6 py-20">
          <div className="text-center mb-16 space-y-3">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-sky-100 border border-sky-200 text-xs font-bold tracking-widest text-sky-700 uppercase">
              <Activity className="w-3 h-3" />
              Explainable Decision Intelligence
            </span>
            <h3 className="text-3xl lg:text-4xl font-black text-slate-900">
              From Cargo Requirement to Optimal Charter Booking
            </h3>
            <p className="text-slate-500 text-sm max-w-xl mx-auto">
              FreightIQ provides full transparency into rate forecasts, vessel compatibility, and risk mitigations.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
            {[
              { num: "01", title: "Cargo Requirement", desc: "Specify commodity, grade, volume, and target East Coast India laycan.", icon: "📦" },
              { num: "02", title: "Route Intelligence", desc: "Analyze overseas origin corridors (Australia, Indonesia, South Africa).", icon: "🗺️" },
              { num: "03", title: "Vessel Matching", desc: "Filter active fleet by DWT, draft, age, owner reliability, and position.", icon: "🚢" },
              { num: "04", title: "Port Compatibility", desc: "Verify draft, LOA, beam, and discharge capacity at reception terminals.", icon: "⚓" },
              { num: "05", title: "Freight Forecast", desc: "Predict future rate cycles to lock in spot or short-term charters.", icon: "📈" },
              { num: "06", title: "Strategy Comparison", desc: "Compare Spot vs COA vs Medium-Term effective voyage cost.", icon: "⚖️" },
              { num: "07", title: "Risk & Demurrage", desc: "Assess monsoon swell, congestion idle time, and bunker fluctuations.", icon: "🛡️" },
              { num: "08", title: "AI Decision Report", desc: "Generate boardroom-ready PDF and explainable audit trails.", icon: "📋" },
            ].map((step, idx) => (
              <div
                key={idx}
                className="p-6 rounded-2xl bg-white border border-sky-100 hover:border-sky-300 transition-all duration-300 hover:-translate-y-1 shadow-sm hover:shadow-lg hover:shadow-sky-100 group"
              >
                <div className="flex items-center justify-between mb-3">
                  <span className="text-3xl">{step.icon}</span>
                  <span className="text-3xl font-black text-slate-100 group-hover:text-sky-100 transition-colors font-mono">
                    {step.num}
                  </span>
                </div>
                <h4 className="text-sm font-bold text-slate-800 mb-1.5">{step.title}</h4>
                <p className="text-xs text-slate-500 leading-relaxed">{step.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* ── Maritime Corridor Strip ── */}
        <section id="network" className="w-full bg-white border-y border-sky-100 py-16 px-6">
          <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-8">
            <div className="space-y-2 max-w-md">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-sky-50 border border-sky-200 text-xs font-bold text-sky-700 uppercase tracking-widest">
                <Globe className="w-3 h-3" />
                East Coast India Focus
              </span>
              <h3 className="text-2xl font-black text-slate-900">Dedicated Maritime Gateway Network</h3>
              <p className="text-xs text-slate-500 leading-relaxed">
                Direct integration with Paradip, Visakhapatnam, Kamarajar (Ennore), Chennai, and V.O. Chidambaranar Port terminals.
              </p>
            </div>

            <div className="flex flex-wrap gap-3">
              {["Paradip 🇮🇳", "Visakhapatnam 🇮🇳", "Dhamra 🇮🇳", "Gangavaram 🇮🇳", "Kamarajar 🇮🇳", "Tuticorin 🇮🇳"].map((port) => (
                <div key={port} className="px-4 py-2 rounded-xl bg-sky-50 border border-sky-200 text-xs font-semibold text-sky-800 flex items-center gap-2 hover:bg-sky-100 hover:border-sky-300 transition-all cursor-default">
                  <span className="w-1.5 h-1.5 rounded-full bg-sky-500" />
                  {port}
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── CTA Section ── */}
        <section className="w-full max-w-4xl mx-auto px-6 py-24 text-center">
          <div className="bg-gradient-to-br from-sky-500 via-blue-600 to-cyan-500 rounded-3xl p-12 shadow-2xl shadow-sky-200 relative overflow-hidden">
            <div className="absolute inset-0 bg-white/5 backdrop-blur-sm" />
            <div className="relative">
              <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/20 text-white text-xs font-bold uppercase tracking-wider mb-6">
                <Sparkles className="w-3.5 h-3.5" />
                Ready to Transform Your Freight Operations?
              </span>
              <h3 className="text-3xl lg:text-4xl font-black text-white mb-4">
                Start Making Smarter<br />Chartering Decisions Today
              </h3>
              <p className="text-white/80 text-sm mb-8 max-w-lg mx-auto">
                Join SAIL and leading raw material importers using FreightIQ to reduce costs and eliminate guesswork.
              </p>
              <Link href="/login">
                <MagneticButton
                  variant="primary"
                  size="lg"
                  className="bg-white text-sky-700 hover:bg-sky-50 font-bold text-sm shadow-xl shadow-sky-900/20 flex items-center gap-2 mx-auto"
                >
                  Launch Control Terminal
                  <ArrowRight className="w-4 h-4" />
                </MagneticButton>
              </Link>
            </div>
          </div>
        </section>
      </main>

      {/* ── Footer ── */}
      <footer className="relative z-10 border-t border-sky-100 bg-white py-8 px-8 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400 gap-4">
        <div className="flex items-center gap-2 text-slate-700">
          <div className="p-1.5 rounded-lg bg-gradient-to-br from-sky-500 to-blue-600">
            <Anchor className="w-3.5 h-3.5 text-white" />
          </div>
          <span className="font-bold text-slate-900">FreightIQ</span> — AI Maritime Chartering Intelligence
        </div>
        <p>© 2026 FreightIQ. Developed for Maritime Chartering & Supply Chain Optimization.</p>
      </footer>
    </div>
  );
}
