import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { motion } from "framer-motion";
import { Shield, Lock, User, AlertCircle, Activity, KeyRound, Sparkles } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import DNAHelixCanvas from "../components/common/DNAHelixCanvas";

export default function Login() {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const redirectPath = location.state?.from?.pathname || "/dashboard";

  useEffect(() => {
    if (user) {
      navigate(redirectPath, { replace: true });
    }
  }, [user, navigate, redirectPath]);

  const executeLogin = async (userVal, passVal) => {
    if (!userVal.trim() || !passVal.trim()) {
      setError("Please fill out all credentials.");
      return;
    }

    try {
      setError("");
      setLoading(true);
      await login(userVal, passVal);
      navigate(redirectPath, { replace: true });
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.detail || "Authentication failed. Please verify credentials."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    await executeLogin(username, password);
  };

  const handleRoleLogin = async (roleUser, rolePass) => {
    setUsername(roleUser);
    setPassword(rolePass);
    await executeLogin(roleUser, rolePass);
  };

  return (
    <div className="min-h-screen w-full bg-[#070b14] text-slate-100 font-sans overflow-hidden relative flex flex-col justify-center selection:bg-amber-500/30 selection:text-amber-200">
      {/* 3D DNA Helix background Canvas */}
      <DNAHelixCanvas className="opacity-70" />

      {/* Grid wrapper */}
      <div className="grid w-full h-full min-h-screen grid-cols-1 lg:grid-cols-12 z-10 relative">
        
        {/* Left column - Branding / Visual elements (Hidden on mobile) */}
        <div className="hidden lg:flex lg:col-span-7 flex-col justify-between p-10 xl:p-14 border-r border-slate-800/80 bg-slate-950/40 backdrop-blur-md">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-amber-500/20 via-sky-500/20 to-blue-600/30 border border-amber-500/40 shadow-md">
              <Activity className="text-amber-400" size={20} />
            </div>
            <div>
              <span className="text-base font-bold tracking-tight text-white flex items-center gap-2">
                IntelliICU
                <span className="text-[10px] font-semibold text-amber-400 bg-amber-950/60 px-2 py-0.5 rounded border border-amber-500/30 uppercase tracking-wider">
                  v2.0 Enterprise
                </span>
              </span>
              <span className="text-[10px] block font-medium text-slate-400 tracking-wider">
                Clinical Decision Support Command Portal
              </span>
            </div>
          </div>

          <div className="max-w-lg my-auto space-y-6">
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="text-3xl xl:text-4xl font-extrabold leading-tight tracking-tight text-white"
            >
              Enterprise <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-300 via-amber-400 to-sky-400">Clinical Surveillance</span> & Portal Authentication.
            </motion.h1>
            
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="text-xs xl:text-sm text-slate-300 leading-relaxed font-normal"
            >
              A high-trust healthcare platform featuring automated sepsis risk predictions, continuous telemetry analysis, RAG clinical copilot, and audit-logged RBAC permissions.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, scale: 0.96 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 backdrop-blur-xl shadow-xl space-y-3"
            >
              <div className="flex items-center gap-2 text-amber-400 text-xs font-bold uppercase tracking-wider">
                <Sparkles size={14} />
                <span>8-Tier Security Clearance</span>
              </div>
              <div className="space-y-2 text-xs">
                <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
                  <span className="font-medium text-slate-300">HospitalAdmin Clearance</span>
                  <span className="font-mono text-purple-300 bg-purple-950/60 px-2.5 py-0.5 rounded border border-purple-500/30 text-[10px] font-semibold">
                    Full System Governance
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="font-medium text-slate-300">ICUManager / Doctor Clearance</span>
                  <span className="font-mono text-sky-300 bg-sky-950/60 px-2.5 py-0.5 rounded border border-sky-500/30 text-[10px] font-semibold">
                    Patient Workspaces & Copilot
                  </span>
                </div>
              </div>
            </motion.div>
          </div>

          <div className="text-xs text-slate-400 font-medium">
            IntelliICU System v2.0.0 • Encrypted JWT Authentication & Telemetry Logging
          </div>
        </div>

        {/* Right column - Login Card */}
        <div className="col-span-1 lg:col-span-5 flex items-center justify-center p-6 sm:p-8 lg:p-10 h-full">
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
            className="w-full max-w-[420px] rounded-2xl border border-slate-800 bg-slate-900/80 p-7 sm:p-8 backdrop-blur-xl shadow-2xl relative border-t-2 border-t-amber-500/60 space-y-6"
          >
            {/* Mobile Branding */}
            <div className="flex lg:hidden items-center gap-3 mb-2">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-amber-500/20 to-sky-500/20 border border-amber-500/40">
                <Activity className="text-amber-400" size={18} />
              </div>
              <div>
                <span className="text-sm font-bold text-white tracking-tight">
                  IntelliICU Enterprise
                </span>
                <span className="text-[9px] block font-medium text-slate-400 uppercase tracking-widest">
                  Clinical Portal
                </span>
              </div>
            </div>

            <div>
              <h2 className="text-2xl font-bold text-white tracking-tight">
                Portal Sign In
              </h2>
              <p className="mt-1 text-xs text-slate-300">
                Authenticate with your credentials or choose sandbox role access
              </p>
            </div>

            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-start gap-2.5 rounded-xl border border-red-500/30 bg-red-950/40 p-3 text-xs text-red-300 font-medium"
              >
                <AlertCircle size={15} className="shrink-0 mt-0.5 text-red-400" />
                <span>{error}</span>
              </motion.div>
            )}

            {/* Quick Role Access Shortcuts */}
            <div className="space-y-2">
              <label className="text-[10px] font-bold uppercase text-slate-400 tracking-wider block">
                Sandbox Quick Access
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                <button
                  type="button"
                  disabled={loading}
                  onClick={() => handleRoleLogin("admin", "admin123")}
                  className="flex items-center justify-center gap-1 rounded-xl border border-purple-500/30 bg-purple-950/30 px-2.5 py-2.5 text-[10px] font-bold text-purple-300 transition hover:bg-purple-900/50 hover:border-purple-500/60 active:scale-[0.98] disabled:opacity-50"
                >
                  <Shield size={12} className="text-purple-400 shrink-0" />
                  <span>Admin</span>
                </button>
                <button
                  type="button"
                  disabled={loading}
                  onClick={() => handleRoleLogin("reyes", "intensivist123")}
                  className="flex items-center justify-center gap-1 rounded-xl border border-sky-500/30 bg-sky-950/30 px-2.5 py-2.5 text-[10px] font-bold text-sky-300 transition hover:bg-sky-900/50 hover:border-sky-500/60 active:scale-[0.98] disabled:opacity-50"
                >
                  <Activity size={12} className="text-sky-400 shrink-0" />
                  <span>Intensivist</span>
                </button>
                <button
                  type="button"
                  disabled={loading}
                  onClick={() => handleRoleLogin("miller", "miller123")}
                  className="flex items-center justify-center gap-1 rounded-xl border border-emerald-500/30 bg-emerald-950/30 px-2.5 py-2.5 text-[10px] font-bold text-emerald-300 transition hover:bg-emerald-900/50 hover:border-emerald-500/60 active:scale-[0.98] disabled:opacity-50"
                >
                  <User size={12} className="text-emerald-400 shrink-0" />
                  <span>Doctor</span>
                </button>
              </div>
            </div>

            <div className="relative flex items-center my-4">
              <div className="flex-grow border-t border-slate-800"></div>
              <span className="shrink-0 px-3 text-[9px] font-bold text-slate-500 uppercase tracking-widest">
                Or enter credentials
              </span>
              <div className="flex-grow border-t border-slate-800"></div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-[11px] font-semibold text-slate-300">
                  Username
                </label>
                <div className="relative">
                  <User size={15} className="absolute left-3.5 top-3 text-slate-400" />
                  <input
                    type="text"
                    required
                    disabled={loading}
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="e.g. admin or reyes"
                    className="w-full rounded-xl border border-slate-800 bg-slate-950/80 py-2.5 pl-9 pr-3 text-xs outline-none transition focus:border-amber-500/80 focus:bg-slate-950 text-white font-medium disabled:opacity-50"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-[11px] font-semibold text-slate-300">
                  Passcode
                </label>
                <div className="relative">
                  <Lock size={15} className="absolute left-3.5 top-3 text-slate-400" />
                  <input
                    type="password"
                    required
                    disabled={loading}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••••••"
                    className="w-full rounded-xl border border-slate-800 bg-slate-950/80 py-2.5 pl-9 pr-3 text-xs outline-none transition focus:border-amber-500/80 focus:bg-slate-950 text-white font-medium disabled:opacity-50"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 text-slate-950 font-bold py-3 text-xs transition duration-200 hover:brightness-110 shadow-lg shadow-amber-500/20 active:scale-[0.98] disabled:opacity-50 mt-2"
              >
                {loading ? (
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-slate-950 border-t-transparent"></div>
                ) : (
                  <>
                    <KeyRound size={14} />
                    Authenticate Session
                  </>
                )}
              </button>
            </form>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
