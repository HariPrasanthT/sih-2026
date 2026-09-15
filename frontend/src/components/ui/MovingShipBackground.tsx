"use client";

import React, { useState, useEffect } from "react";
import Image from "next/image";

interface MovingShipBackgroundProps {
  className?: string;
  overlayOpacity?: number;
  showVideo?: boolean;
}

export default function MovingShipBackground({
  className = "",
  overlayOpacity = 0.6,
}: MovingShipBackgroundProps) {
  const [isHovered, setIsHovered] = useState(false);
  const [speedKnots, setSpeedKnots] = useState(14.8);

  // Slight random telemetry fluctuations for live realism
  useEffect(() => {
    const interval = setInterval(() => {
      setSpeedKnots(+(14.5 + Math.random() * 0.6).toFixed(1));
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div
      className={`absolute inset-0 overflow-hidden pointer-events-auto select-none z-0 ${className}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* ── 1. Base Cinematic Ocean Horizon Backdrop ── */}
      <div className="absolute inset-0 z-0 opacity-45 mix-blend-luminosity">
        <Image
          src="/cargo-ship.jpg"
          alt="Cargo Ship Maritime Background"
          fill
          priority
          sizes="100vw"
          className="object-cover object-center filter brightness-[0.6] contrast-[1.2] scale-105"
        />
      </div>

      {/* ── 2. Atmospheric Night Sea Gradients & Nautical Radar Grid ── */}
      <div
        className="absolute inset-0 z-1"
        style={{
          background: `radial-gradient(ellipse 80% 50% at 50% -10%, rgba(14, 116, 144, 0.25), transparent 70%),
                       linear-gradient(to bottom, 
                         rgba(4, 10, 24, ${Math.min(1, overlayOpacity * 1.1)}) 0%, 
                         rgba(6, 18, 40, ${overlayOpacity * 0.7}) 45%, 
                         rgba(4, 13, 30, ${overlayOpacity * 0.85}) 75%, 
                         rgba(3, 8, 20, 0.98) 100%)`,
        }}
      />

      {/* Nautical Distance Range Rings (Subtle Radar Overlays) */}
      <div className="absolute -top-24 right-1/4 w-[600px] h-[600px] rounded-full border border-cyan-500/10 pointer-events-none z-2" />
      <div className="absolute -top-12 right-1/4 translate-x-12 w-[400px] h-[400px] rounded-full border border-dashed border-cyan-400/15 pointer-events-none z-2 animate-[spin_60s_linear_infinite]" />
      <div className="absolute top-1/4 left-1/3 -translate-x-1/2 w-[500px] h-[300px] bg-cyan-500/10 rounded-full blur-[100px] z-2" />

      {/* ── 3. Distant Horizon Vessel (Sailing Leftward on Deep Sea) ── */}
      <div className="absolute bottom-[44%] w-full h-10 pointer-events-none z-3 overflow-hidden opacity-40">
        <div className="animate-distant-ship absolute bottom-1 flex items-end">
          {/* Distant Tanker Silhouette */}
          <svg
            width="90"
            height="18"
            viewBox="0 0 100 20"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            className="drop-shadow-[0_0_8px_rgba(6,182,212,0.4)]"
          >
            {/* Distant Hull */}
            <path
              d="M2 14 L12 18 L90 18 L98 12 L92 12 L85 8 L85 14 L20 14 L12 12 Z"
              fill="#0f2b48"
            />
            {/* Bridge */}
            <rect x="75" y="4" width="10" height="8" fill="#164e63" />
            <rect x="78" y="2" width="4" height="2" fill="#0891b2" />
            {/* Tiny Nav Light */}
            <circle cx="78" cy="1" r="1" fill="#38bdf8" className="animate-pulse" />
          </svg>
          {/* Distant Mini Wake */}
          <div className="w-16 h-0.5 bg-gradient-to-r from-transparent via-cyan-400/30 to-transparent -ml-2 mb-0.5" />
        </div>
      </div>

      {/* ── 4. Deep Sea Back Wave Layer ── */}
      <div className="absolute bottom-[18%] left-0 right-0 h-24 pointer-events-none z-4 opacity-35 overflow-hidden">
        <svg
          className="w-[200%] h-full animate-wave-slowest text-cyan-950/60 fill-current"
          viewBox="0 0 1200 120"
          preserveAspectRatio="none"
        >
          <path d="M0,40 C150,80 350,0 500,40 C650,80 850,0 1000,40 C1150,80 1350,0 1500,40 L1500,120 L0,120 Z" />
        </svg>
      </div>

      {/* ── 5. MAIN CARGO VESSEL (Majestic Bulk Carrier Riding Deep Ocean Swell) ── */}
      <div className="absolute bottom-[14%] w-full h-36 pointer-events-none z-10 flex justify-center items-end">
        <div className="relative flex items-end">
          {/* Main Ship Wrapper with Dynamic Sea Pitch & Roll Physics */}
          <div className="relative group pointer-events-auto cursor-pointer animate-ship-heave transition-transform duration-300 hover:scale-[1.03]">
            
            {/* ── Live AIS Vessel Telemetry HUD Tag ── */}
            <div className="absolute -top-12 left-1/2 -translate-x-1/2 flex items-center gap-2 px-3 py-1 rounded-full bg-slate-950/85 border border-cyan-400/50 backdrop-blur-md shadow-[0_0_20px_rgba(6,182,212,0.35)] text-[10px] font-mono whitespace-nowrap text-cyan-200">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-400"></span>
              </span>
              <span className="font-bold text-white tracking-wide">MV BENGAL VOYAGER</span>
              <span className="text-slate-400">|</span>
              <span className="text-cyan-300 font-semibold">{speedKnots} kts</span>
              <span className="text-slate-400">|</span>
              <span className="text-emerald-400">Bound: Paradip</span>
            </div>

            {/* ── Rotating Mast Radar Sweep Pulse ── */}
            <div className="absolute -top-6 left-[88px] w-12 h-12 rounded-full border border-cyan-400/40 pointer-events-none animate-ping opacity-60" />
            
            {/* ── Bow Water Splash Particles ── */}
            <div className="absolute bottom-2 -right-3 w-8 h-8 pointer-events-none">
              <div className="w-2.5 h-2.5 rounded-full bg-cyan-200/80 animate-ping absolute right-0 bottom-1" />
              <div className="w-4 h-1.5 rounded-full bg-white/90 blur-[1px] absolute -right-2 bottom-0 animate-pulse" />
              <div className="w-6 h-2 bg-gradient-to-r from-cyan-300 to-white/70 rounded-full blur-[2px] absolute right-0 bottom-0" />
            </div>

            {/* ── Detailed Vector Panamax Bulk Carrier ── */}
            <svg
              width="260"
              height="75"
              viewBox="0 0 320 90"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              className="filter drop-shadow-[0_8px_16px_rgba(0,0,0,0.8)]"
            >
              <defs>
                {/* Hull Gradients */}
                <linearGradient id="hullGradient" x1="0" y1="0" x2="0" y2="100%">
                  <stop offset="0%" stopColor="#1e293b" />
                  <stop offset="45%" stopColor="#0f172a" />
                  <stop offset="70%" stopColor="#090d16" />
                  <stop offset="72%" stopColor="#991b1b" />
                  <stop offset="100%" stopColor="#5b1111" />
                </linearGradient>

                <linearGradient id="bridgeGradient" x1="0" y1="0" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#334155" />
                  <stop offset="100%" stopColor="#1e293b" />
                </linearGradient>

                <linearGradient id="glowCyan" x1="0" y1="0" x2="100%" y2="0">
                  <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.8" />
                  <stop offset="100%" stopColor="#38bdf8" stopOpacity="0.3" />
                </linearGradient>

                {/* Bow Light Beam Gradient */}
                <linearGradient id="bowBeam" x1="0" y1="0" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#38bdf8" stopOpacity="0.4" />
                  <stop offset="100%" stopColor="#06b6d4" stopOpacity="0" />
                </linearGradient>
              </defs>

              {/* Forward Bow Searchlight Projection */}
              <polygon points="310,65 370,55 380,85 305,75" fill="url(#bowBeam)" opacity="0.4" />

              {/* 1. Main Steel Hull */}
              {/* Stern (Left) -> Cargo Holds (Middle) -> Bulbous Bow (Right) */}
              <path
                d="M 28 58 
                   L 42 78 
                   C 70 82, 260 82, 298 78 
                   C 310 74, 316 66, 314 58 
                   L 292 58 
                   L 28 58 Z"
                fill="url(#hullGradient)"
                stroke="#38bdf8"
                strokeWidth="0.8"
                strokeOpacity="0.4"
              />

              {/* Waterline Stripe (High Visibility Orange/Red Stripe) */}
              <path
                d="M 38 72 C 80 75, 250 75, 304 70"
                stroke="#06b6d4"
                strokeWidth="1.5"
                strokeOpacity="0.7"
                fill="none"
              />

              {/* Cargo Holds & Hatches (5 Heavy Bulk Holds for Iron Ore/Coal) */}
              <rect x="110" y="52" width="26" height="6" rx="1" fill="#334155" stroke="#475569" strokeWidth="0.5" />
              <rect x="144" y="52" width="26" height="6" rx="1" fill="#334155" stroke="#475569" strokeWidth="0.5" />
              <rect x="178" y="52" width="26" height="6" rx="1" fill="#334155" stroke="#475569" strokeWidth="0.5" />
              <rect x="212" y="52" width="26" height="6" rx="1" fill="#334155" stroke="#475569" strokeWidth="0.5" />
              <rect x="246" y="52" width="26" height="6" rx="1" fill="#334155" stroke="#475569" strokeWidth="0.5" />

              {/* Cargo Hold Coamings & Lashing Bridges */}
              <line x1="105" y1="58" x2="280" y2="58" stroke="#0ea5e9" strokeWidth="1" strokeOpacity="0.6" />

              {/* 2. Deck Cargo Cranes (4 Gantry Cranes along Deck) */}
              {[123, 157, 191, 225].map((xPos, idx) => (
                <g key={idx}>
                  {/* Crane Pedestal Base */}
                  <rect x={xPos} y="44" width="5" height="8" fill="#475569" />
                  {/* Crane Jib Arm pointing forward */}
                  <line x1={xPos + 2} y1="45" x2={xPos + 24} y2="38" stroke="#cbd5e1" strokeWidth="1.5" />
                  {/* Cable wire */}
                  <line x1={xPos + 24} y1="38" x2={xPos + 24} y2="50" stroke="#94a3b8" strokeWidth="0.5" strokeDasharray="1,1" />
                  {/* Pulley block */}
                  <circle cx={xPos + 24} cy={50} r="1" fill="#38bdf8" />
                </g>
              ))}

              {/* 3. Aft Superstructure (Navigation Bridge & Accommodation Tower) */}
              <g>
                {/* Lower Tier */}
                <rect x="48" y="38" width="46" height="20" rx="1" fill="url(#bridgeGradient)" stroke="#475569" strokeWidth="0.5" />
                {/* Mid Tier */}
                <rect x="52" y="26" width="38" height="12" rx="1" fill="url(#bridgeGradient)" stroke="#475569" strokeWidth="0.5" />
                {/* Bridge Deck Wing */}
                <path d="M 46 20 L 96 20 L 92 26 L 50 26 Z" fill="#475569" />
                {/* Wheelhouse Windows (Illuminated Cyan/Warm Glow) */}
                <rect x="52" y="21" width="38" height="4" fill="#38bdf8" fillOpacity="0.85" className="filter drop-shadow-[0_0_4px_#38bdf8]" />
                
                {/* Cabin Portholes / Windows */}
                <circle cx="58" cy="32" r="1.2" fill="#fef08a" />
                <circle cx="66" cy="32" r="1.2" fill="#fef08a" />
                <circle cx="74" cy="32" r="1.2" fill="#fef08a" />
                <circle cx="82" cy="32" r="1.2" fill="#fef08a" />

                <circle cx="58" cy="44" r="1.2" fill="#fef08a" />
                <circle cx="66" cy="44" r="1.2" fill="#fef08a" />
                <circle cx="74" cy="44" r="1.2" fill="#fef08a" />
                <circle cx="82" cy="44" r="1.2" fill="#fef08a" />

                {/* Funnel / Exhaust Stack with Company Logo Stripe */}
                <path d="M 44 14 L 52 14 L 50 32 L 44 32 Z" fill="#0f172a" stroke="#334155" strokeWidth="0.5" />
                <rect x="44.5" y="18" width="6.5" height="3" fill="#06b6d4" />
                {/* Exhaust heat shimmer dots */}
                <circle cx="47" cy="11" r="1.5" fill="#94a3b8" fillOpacity="0.4" className="animate-ping" />

                {/* Main Radar Mast & Navigation Sensors */}
                <line x1="72" y1="20" x2="72" y2="4" stroke="#e2e8f0" strokeWidth="1.5" />
                {/* Mast Yardarms */}
                <line x1="64" y1="10" x2="80" y2="10" stroke="#94a3b8" strokeWidth="1" />
                <line x1="68" y1="6" x2="76" y2="6" stroke="#94a3b8" strokeWidth="1" />

                {/* Rotating Scanner Antenna */}
                <line x1="69" y1="4" x2="75" y2="4" stroke="#38bdf8" strokeWidth="2" strokeLinecap="round" className="animate-pulse" />
                
                {/* Navigation Masthead Light (Pulsing White) */}
                <circle cx="72" cy="3" r="1.5" fill="#ffffff" className="animate-ping" />
                
                {/* Port Side Light (Red) */}
                <circle cx="48" cy="20" r="1.2" fill="#ef4444" className="animate-pulse" />

                {/* Safety Railings */}
                <line x1="48" y1="37" x2="94" y2="37" stroke="#64748b" strokeWidth="0.5" />
                <line x1="28" y1="56" x2="104" y2="56" stroke="#64748b" strokeWidth="0.5" />
                <line x1="280" y1="56" x2="310" y2="56" stroke="#64748b" strokeWidth="0.5" />
              </g>

              {/* 4. Bow Mast & Starboard Nav Light (Green) */}
              <line x1="300" y1="58" x2="300" y2="42" stroke="#cbd5e1" strokeWidth="1" />
              <line x1="297" y1="46" x2="303" y2="46" stroke="#94a3b8" strokeWidth="0.8" />
              <circle cx="300" cy="42" r="1.5" fill="#10b981" className="animate-pulse" />

              {/* 5. Anchor Pocket */}
              <circle cx="296" cy="63" r="2" fill="#090d16" stroke="#334155" strokeWidth="0.5" />
            </svg>

            {/* ── Stern Churning Propeller Wake & Foam Streamers ── */}
            <div className="absolute bottom-1 -left-28 w-32 h-6 pointer-events-none flex items-center">
              {/* Churning Propeller Foam */}
              <div className="w-10 h-3.5 rounded-full bg-gradient-to-l from-white/90 via-cyan-200/70 to-transparent blur-[1px] animate-pulse" />
              {/* Expanding Wake Streamers */}
              <div className="w-24 h-2 bg-gradient-to-l from-cyan-300/60 via-cyan-500/30 to-transparent rounded-full -ml-3 blur-[2px]" />
              <div className="w-32 h-1 bg-gradient-to-l from-cyan-400/40 to-transparent -ml-6" />
            </div>
          </div>
        </div>
      </div>

      {/* ── 6. Dynamic Foreground Wave Layers with Whitecap Crests ── */}
      {/* Midground Waves */}
      <div className="absolute bottom-[4%] left-0 right-0 h-20 pointer-events-none z-12 opacity-70 overflow-hidden">
        <svg
          className="w-[200%] h-full animate-wave-medium text-cyan-900/75 fill-current"
          viewBox="0 0 1200 120"
          preserveAspectRatio="none"
        >
          <path d="M0,60 C200,20 400,90 600,50 C800,10 1000,85 1200,45 C1400,15 1600,90 1800,50 C2000,15 2200,80 2400,45 L2400,120 L0,120 Z" />
        </svg>
      </div>

      {/* Foreground Choppy Sea Waves & Foam Lines */}
      <div className="absolute bottom-0 left-0 right-0 h-16 pointer-events-none z-20 overflow-hidden">
        <svg
          className="w-[200%] h-full animate-wave-fast text-[#07132a]/95 fill-current"
          viewBox="0 0 1200 100"
          preserveAspectRatio="none"
        >
          <path d="M0,45 C150,85 300,30 450,60 C600,90 750,35 900,65 C1050,95 1200,35 1350,65 C1500,95 1650,40 1800,70 L1800,100 L0,100 Z" />
        </svg>
        {/* Luminous Seafoam Crest Line */}
        <div className="absolute top-2 left-0 right-0 h-[1.5px] bg-gradient-to-r from-transparent via-cyan-400/40 to-transparent animate-pulse" />
      </div>

      {/* ── 7. Vignette & Contrast Gradients for Crisp Dashboard Text ── */}
      <div className="absolute inset-0 z-25 bg-gradient-to-r from-[#060e1e]/90 via-[#060e1e]/60 to-transparent w-2/3 pointer-events-none" />
      <div className="absolute bottom-0 left-0 right-0 h-16 bg-gradient-to-t from-[#060e1e] to-transparent z-25 pointer-events-none" />
    </div>
  );
}

