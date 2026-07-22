import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { motion } from "framer-motion";
import { Shield, Lock, User, AlertCircle, Activity } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const redirectPath = location.state?.from?.pathname || "/dashboard";

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
    <div className="h-screen w-full bg-[#0a0e1a] text-slate-100 font-sans overflow-hidden relative flex flex-col justify-center">
      {/* Background ambient glowing nodes */}
      <div className="absolute top-[-10%] left-[-10%] h-[500px] w-[500px] rounded-full bg-cyan-900/10 blur-[150px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] h-[500px] w-[500px] rounded-full bg-indigo-900/15 blur-[150px] pointer-events-none" />

      {/* Grid wrapper */}
      <div className="grid w-full h-full grid-cols-1 lg:grid-cols-12 z-10">
        
        {/* Left column - Branding / Visual elements (Hidden on mobile) */}
        <div className="hidden lg:flex lg:col-span-7 flex-col justify-between p-6 xl:p-10 border-r border-slate-900 relative bg-slate-900/10 backdrop-blur-3xl h-full">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-600 shadow-lg shadow-cyan-500/20">
              <Activity className="text-white" size={20} />
            </div>
            <div>
              <span className="text-base font-black tracking-wider uppercase text-white bg-clip-text">
                IntelliICU
              </span>
              <span className="text-[9px] block font-bold text-cyan-400 tracking-widest uppercase">
                Clinical AI Command Center
              </span>
            </div>
          </div>

          <div className="max-w-md my-auto space-y-4 xl:space-y-5">
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="text-3xl xl:text-4xl font-extrabold leading-tight tracking-tight text-white"
            >
              Real-Time <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-indigo-400">Clinical Intelligence</span> & Patient Surveillance.
            </motion.h1>
            
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="text-xs xl:text-sm text-slate-400 leading-relaxed"
            >
              A secure, enterprise-grade interface providing automated sepsis risk predictions, physiological alert auditing, and real-time clinical timelines.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="rounded-2xl border border-slate-800 bg-slate-900/50 p-4 xl:p-5 backdrop-blur-md shadow-xl"
            >
              <span className="text-[10px] font-extrabold uppercase text-slate-400 tracking-wider">
                Role-Based Security
              </span>
              <div className="mt-3 space-y-2">
                <div className="flex items-center justify-between text-xs border-b border-slate-800/50 pb-2">
                  <span className="font-semibold text-slate-300">Admin Clearance</span>
                  <span className="font-mono text-purple-400 bg-purple-950/40 px-2 py-0.5 rounded border border-purple-800/40 text-[10px] font-semibold">
                    Full System Controls
                  </span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-slate-300">Intensivist / MD Clearance</span>
                  <span className="font-mono text-cyan-400 bg-cyan-950/40 px-2 py-0.5 rounded border border-cyan-800/40 text-[10px] font-semibold">
                    Patient & Ward Surveillance
                  </span>
                </div>
              </div>
            </motion.div>
          </div>

          <div className="text-[11px] text-slate-500 font-medium">
            IntelliICU System v2.0.0. All connections are fully audited and encrypted.
          </div>
        </div>

        {/* Right column - Login Card */}
        <div className="col-span-1 lg:col-span-5 flex items-center justify-center p-4 sm:p-6 lg:p-8 h-full">
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
            className="w-full max-w-[420px] rounded-3xl border border-slate-800/80 bg-slate-900/30 p-6 sm:p-7 backdrop-blur-2xl shadow-2xl relative"
          >
            {/* Mobile Branding (Visible only on small screens) */}
            <div className="flex lg:hidden items-center gap-3 mb-6">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-600 shadow-md">
                <Activity className="text-white" size={18} />
              </div>
              <div>
                <span className="text-sm font-black tracking-wider uppercase text-white">
                  IntelliICU
                </span>
                <span className="text-[8px] block font-bold text-cyan-400 tracking-widest uppercase">
                  Clinical AI Command
                </span>
              </div>
            </div>

            <div className="mb-5">
              <h2 className="text-xl sm:text-2xl font-black text-white tracking-tight">
                Portal Authentication
              </h2>
              <p className="mt-1 text-xs text-slate-400 font-medium">
                Enter your credentials or select quick role access to proceed
              </p>
            </div>

            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-4 flex items-start gap-2 rounded-xl border border-red-950 bg-red-950/30 p-3 text-xs text-red-400 font-semibold"
              >
                <AlertCircle size={15} className="shrink-0 mt-0.5" />
                <span>{error}</span>
              </motion.div>
            )}

            {/* Quick Role-Based Login Buttons */}
            <div className="space-y-1.5 mb-4">
              <label className="text-[10px] font-black uppercase text-slate-400 tracking-wider block">
                Quick Role Access
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                <button
                  type="button"
                  disabled={loading}
                  onClick={() => handleRoleLogin("admin", "admin123")}
                  className="flex items-center justify-center gap-1.5 rounded-xl border border-purple-500/30 bg-purple-950/30 px-3 py-2.5 text-[11px] font-bold text-purple-300 transition duration-200 hover:bg-purple-900/50 hover:border-purple-500/60 active:scale-[0.98] disabled:opacity-50"
                >
                  <Shield size={13} className="text-purple-400 shrink-0" />
                  <span>Login as Admin</span>
                </button>
                <button
                  type="button"
                  disabled={loading}
                  onClick={() => handleRoleLogin("reyes", "intensivist123")}
                  className="flex items-center justify-center gap-1.5 rounded-xl border border-cyan-500/30 bg-cyan-950/30 px-3 py-2.5 text-[11px] font-bold text-cyan-300 transition duration-200 hover:bg-cyan-900/50 hover:border-cyan-500/60 active:scale-[0.98] disabled:opacity-50"
                >
                  <Activity size={13} className="text-cyan-400 shrink-0" />
                  <span>Login as Doctor/Intensivist</span>
                </button>
              </div>
            </div>

            <div className="relative flex items-center my-4">
              <div className="flex-grow border-t border-slate-800/80"></div>
              <span className="shrink-0 px-2.5 text-[9px] font-bold text-slate-500 uppercase tracking-widest">
                Or manual sign in
              </span>
              <div className="flex-grow border-t border-slate-800/80"></div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-1">
                <label className="text-[10px] font-black uppercase text-slate-400 tracking-wider">
                  Username or Email
                </label>
                <div className="relative">
                  <User size={15} className="absolute left-3.5 top-3 text-slate-400" />
                  <input
                    type="text"
                    required
                    disabled={loading}
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="Enter your username"
                    className="w-full rounded-xl border border-slate-800/80 bg-slate-950/60 py-2.5 pl-9 pr-3 text-xs outline-none transition focus:border-cyan-500 focus:bg-slate-950 text-slate-100 font-semibold disabled:opacity-50"
                  />
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-[10px] font-black uppercase text-slate-400 tracking-wider">
                  Secret Passcode
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
                    className="w-full rounded-xl border border-slate-800/80 bg-slate-950/60 py-2.5 pl-9 pr-3 text-xs outline-none transition focus:border-cyan-500 focus:bg-slate-950 text-slate-100 font-semibold disabled:opacity-50"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 text-white font-bold py-3 text-xs transition duration-300 hover:shadow-lg hover:shadow-cyan-500/25 active:scale-[0.98] disabled:opacity-50 mt-1"
              >
                {loading ? (
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
                ) : (
                  <>
                    <Shield size={14} />
                    Secure Login
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
