"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import Image from "next/image";
import {
  Anchor,
  ArrowRight,
  User,
  Lock,
  Mail,
  ShieldCheck,
  Zap,
  ArrowLeft,
  Loader2,
  Sparkles,
} from "lucide-react";
import { MagneticButton } from "@/components/lightswind/magnetic-button";
import { ElectroBorder } from "@/components/lightswind/electro-border";
import MovingShipBackground from "@/components/ui/MovingShipBackground";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("chartering@sail.co.in");
  const [password, setPassword] = useState("••••••••••••");
  const [isLoading, setIsLoading] = useState(false);
  const [authStage, setAuthStage] = useState<string>("");

  const handleLogin = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setIsLoading(true);
    setAuthStage("Verifying Maritime AIS Credentials...");

    setTimeout(() => {
      setAuthStage("Connecting to SAIL Control Terminal...");
    }, 600);

    setTimeout(() => {
      router.push("/dashboard");
    }, 1200);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-sky-50 via-white to-blue-50 text-slate-900 flex flex-col relative overflow-hidden selection:bg-sky-400 selection:text-white">
      {/* Background Orbs */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute -top-40 -right-40 w-[600px] h-[600px] rounded-full bg-gradient-to-br from-sky-200/50 to-blue-200/30 blur-3xl" />
        <div className="absolute bottom-0 -left-20 w-[400px] h-[400px] rounded-full bg-gradient-to-br from-cyan-100/60 to-sky-100/40 blur-3xl" />
      </div>

      {/* ── Top Navigation Bar ── */}
      <div className="relative z-30 px-6 py-4 flex items-center justify-between border-b border-sky-100 bg-white/80 backdrop-blur-xl">
        <Link href="/" className="flex items-center gap-2.5 text-slate-600 hover:text-sky-700 transition-colors group">
          <div className="p-2 rounded-xl bg-slate-50 border border-slate-200 group-hover:border-sky-300 group-hover:text-sky-600 transition-all">
            <ArrowLeft className="w-4 h-4" />
          </div>
          <span className="text-xs font-semibold tracking-wider uppercase">Return to Overview</span>
        </Link>

        <div className="flex items-center gap-2 text-xs font-mono text-sky-600">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
          <span className="hidden sm:inline">SAIL Maritime Terminal • Auth Gateway</span>
        </div>
      </div>

      <div className="flex-1 flex flex-col lg:flex-row relative">
        {/* ── Left Side: Maritime Backdrop & Intel Overview ── */}
        <div className="hidden lg:flex flex-1 relative flex-col justify-between p-12 overflow-hidden border-r border-sky-100">
          {/* Animated Moving Ship Background */}
          <MovingShipBackground overlayOpacity={0.5} />

          <div className="relative z-20 flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-white/20 border border-white/30 text-white shadow-xl backdrop-blur-md">
              <Anchor className="w-8 h-8" />
            </div>
            <div>
              <h1 className="text-2xl font-black tracking-tight text-white">FreightIQ</h1>
              <p className="text-xs text-sky-200 font-bold tracking-widest uppercase">
                AI Maritime Intelligence Platform
              </p>
            </div>
          </div>

          <div className="relative z-20 max-w-xl space-y-5">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-white/30 bg-white/15 backdrop-blur-md text-white text-xs font-semibold tracking-wider uppercase">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Steel Authority of India Limited (SAIL)</span>
            </div>

            <h2 className="text-4xl xl:text-5xl font-black text-white leading-tight">
              Raw Material Import & Chartering Control
            </h2>

            <p className="text-sm xl:text-base text-white/75 leading-relaxed">
              Empowering chartering managers with real-time Baltic index forecasts, certified vessel vetting, port draft limits, and voyage risk analytics.
            </p>

            <div className="grid grid-cols-2 gap-3 pt-4 border-t border-white/20 max-w-md">
              <div className="p-3.5 rounded-xl bg-white/15 border border-white/20 backdrop-blur-md">
                <span className="text-[10px] text-white/60 uppercase font-mono">Live Tracking</span>
                <p className="text-base font-bold text-white mt-0.5">12 Panamax Vessels</p>
              </div>
              <div className="p-3.5 rounded-xl bg-white/15 border border-white/20 backdrop-blur-md">
                <span className="text-[10px] text-white/60 uppercase font-mono">Primary Terminal</span>
                <p className="text-base font-bold text-sky-200 mt-0.5">Paradip Berth #2</p>
              </div>
            </div>
          </div>

          <div className="relative z-20 text-xs text-white/40 flex items-center justify-between">
            <span>Encrypted 256-Bit Maritime AIS Stream</span>
            <span>Security Level 1 (ISPS Code)</span>
          </div>
        </div>

        {/* ── Right Side: Login Form ── */}
        <div className="flex-1 flex flex-col justify-center items-center p-6 sm:p-10 relative z-20">
          <div className="w-full max-w-md">
            <ElectroBorder
              borderColor="#0ea5e9"
              borderWidth={2}
              radius="24px"
              glowBlur={16}
              animationSpeed={0.9}
              cardBackground="rgba(255, 255, 255, 0.98)"
              className="shadow-2xl shadow-sky-100"
            >
              <div className="p-8 sm:p-10 space-y-6">
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <span className="w-2 h-2 rounded-full bg-sky-500 animate-pulse" />
                    <span className="text-xs uppercase font-mono font-bold text-sky-600 tracking-wider">
                      Executive Terminal
                    </span>
                  </div>
                  <h3 className="text-2xl font-black text-slate-900">Sign in to FreightIQ</h3>
                  <p className="text-slate-500 text-xs mt-1">
                    Enter your chartering credentials to access the live dashboard.
                  </p>
                </div>

                <form onSubmit={handleLogin} className="space-y-4">
                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold uppercase tracking-wider text-slate-600 flex items-center gap-1.5" htmlFor="email">
                      <Mail className="w-3.5 h-3.5 text-sky-500" />
                      Email / SAIL Official ID
                    </label>
                    <input
                      type="text"
                      id="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                      placeholder="chartering@sail.co.in"
                      className="w-full bg-sky-50/80 border border-sky-200 rounded-xl px-4 py-3 text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:border-sky-400 focus:ring-2 focus:ring-sky-500/20 transition-all font-mono"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between">
                      <label className="text-xs font-semibold uppercase tracking-wider text-slate-600 flex items-center gap-1.5" htmlFor="password">
                        <Lock className="w-3.5 h-3.5 text-sky-500" />
                        Password
                      </label>
                      <span className="text-[11px] text-sky-500 hover:text-sky-700 hover:underline cursor-pointer">
                        Forgot key?
                      </span>
                    </div>
                    <input
                      type="password"
                      id="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      placeholder="••••••••••••"
                      className="w-full bg-sky-50/80 border border-sky-200 rounded-xl px-4 py-3 text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:border-sky-400 focus:ring-2 focus:ring-sky-500/20 transition-all font-mono"
                    />
                  </div>

                  <div className="flex items-center justify-between pt-1">
                    <label className="flex items-center gap-2 cursor-pointer text-xs text-slate-600">
                      <input
                        type="checkbox"
                        defaultChecked
                        className="w-4 h-4 rounded border-sky-300 bg-sky-50 text-sky-500 focus:ring-sky-500/20 accent-sky-500"
                      />
                      <span>Keep terminal session active</span>
                    </label>
                  </div>

                  {/* Submit / Login Button */}
                  <div className="pt-2">
                    <button
                      type="submit"
                      disabled={isLoading}
                      className="w-full py-3.5 rounded-xl bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-400 hover:to-blue-500 text-white font-black text-sm transition-all shadow-lg shadow-sky-200 flex items-center justify-center gap-2 hover:scale-[1.02] active:scale-[0.98] disabled:opacity-80 hover:shadow-xl hover:shadow-sky-300"
                    >
                      {isLoading ? (
                        <>
                          <Loader2 className="w-4 h-4 animate-spin" />
                          <span>{authStage || "Authenticating..."}</span>
                        </>
                      ) : (
                        <>
                          <span>Login to FreightIQ Terminal</span>
                          <ArrowRight className="w-4 h-4" />
                        </>
                      )}
                    </button>
                  </div>
                </form>

                <div className="relative my-2">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-slate-100"></div>
                  </div>
                  <div className="relative flex justify-center text-[10px] uppercase tracking-widest font-mono">
                    <span className="px-3 bg-white text-slate-400">Quick Access</span>
                  </div>
                </div>

                {/* 1-Click Demo Login */}
                <button
                  type="button"
                  onClick={() => handleLogin()}
                  disabled={isLoading}
                  className="w-full py-3 rounded-xl bg-sky-50 border border-sky-200 hover:border-sky-400 hover:bg-sky-100 text-sky-700 text-xs font-bold transition-all flex items-center justify-center gap-2 shadow-sm group"
                >
                  <User className="w-3.5 h-3.5 text-sky-500 group-hover:scale-110 transition-transform" />
                  <span>Continue as Demo Chartering Manager</span>
                </button>
              </div>
            </ElectroBorder>
          </div>
        </div>
      </div>
    </div>
  );
}
