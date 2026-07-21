/**
 * Settings Page (index.jsx)
 *
 * Enterprise settings dashboard with dedicated panels:
 * 1. AI Configuration: provider, model selects, temperature slider, max tokens, health status.
 * 2. Knowledge Base: upload clinical documents (PDF, DOCX, TXT, MD), search RAG documents with scores,
 *    and view/delete indexed document chunks.
 * 3. System Preferences: Alert preferences, compliance, etc.
 *
 * All dynamic changes applied at runtime without server restarts.
 */

import React, { useState, useEffect, useCallback } from "react";
import {
  Bell, Database, Shield, Settings as SettingsIcon,
  Brain, RefreshCw, Save, Loader2, CheckCircle,
  AlertTriangle, Cpu, Sliders, Trash2, Search,
  UploadCloud, FileText, Check, AlertCircle,
} from "lucide-react";
import { aiService } from "../../services/aiService";
import { knowledgeService } from "../../services/knowledgeService";

export default function Settings() {
  const [activeTab, setActiveTab] = useState("ai");

  // AI Configuration state
  const [config, setConfig] = useState({
    provider: "mock",
    model: "mock-model",
    temperature: 0.2,
    max_tokens: 1024,
    streaming: true,
  });

  const [providers, setProviders] = useState([]);
  const [availableModels, setAvailableModels] = useState([]);
  const [healthStatus, setHealthStatus] = useState({
    healthy: true,
    status: "healthy",
    details: "Mock provider active",
  });

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [healthLoading, setHealthLoading] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // ---------- Knowledge Base (RAG) state ----------
  const [kbUpload, setKbUpload] = useState({
    title: "",
    source: "",
    category: "",
    section: "",
    tags: "",
    file: null,
  });
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState({ type: "", text: "" });

  const [searchQuery, setSearchQuery] = useState("");
  const [searchCategory, setSearchCategory] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);

  const [kbDocs, setKbDocs] = useState([]);
  const [loadingKbDocs, setLoadingKbDocs] = useState(false);
  const [deletingId, setDeletingId] = useState(null);

  // ---------- Load Configuration & Metadata ----------
  const loadSettings = useCallback(async () => {
    setLoading(true);
    try {
      // 1. Fetch current config
      const configRes = await aiService.getConfig();
      if (configRes.status === "success") {
        setConfig(configRes.config);
      }

      // 2. Fetch providers list
      const providersRes = await aiService.getProviders();
      if (providersRes.status === "success") {
        setProviders(providersRes.providers);
      }

      // 3. Fetch active models
      const modelsRes = await aiService.getModels();
      setAvailableModels(modelsRes.models || []);

      // 4. Fetch active health check
      const healthRes = await aiService.getHealth();
      setHealthStatus(healthRes);
    } catch (err) {
      console.error("[Settings] Error loading AI configurations:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  // ---------- Load RAG guidelines ----------
  const loadGuidelines = async () => {
    setLoadingKbDocs(true);
    try {
      const res = await knowledgeService.listDocuments();
      if (res.status === "success") {
        setKbDocs(res.documents || []);
      }
    } catch (err) {
      console.error("[Settings] Failed to fetch indexed RAG documents:", err);
    } finally {
      setLoadingKbDocs(false);
    }
  };

  useEffect(() => {
    loadSettings();
  }, [loadSettings]);

  useEffect(() => {
    if (activeTab === "kb") {
      loadGuidelines();
    }
  }, [activeTab]);

  // ---------- Triggered on Provider Change ----------
  const handleProviderChange = async (newProvider) => {
    setConfig((prev) => ({ ...prev, provider: newProvider }));
    try {
      await aiService.updateConfig({ provider: newProvider });
      
      const modelsRes = await aiService.getModels();
      setAvailableModels(modelsRes.models || []);
      if (modelsRes.models && modelsRes.models.length > 0) {
        setConfig((prev) => ({ ...prev, model: modelsRes.models[0] }));
      }
      
      const healthRes = await aiService.getHealth();
      setHealthStatus(healthRes);
    } catch (err) {
      console.error("[Settings] Provider change failed:", err);
    }
  };

  // ---------- Refresh Provider Health ----------
  const checkHealth = async () => {
    setHealthLoading(true);
    try {
      const healthRes = await aiService.getHealth();
      setHealthStatus(healthRes);
    } catch (err) {
      console.error("[Settings] Health check failed:", err);
    } finally {
      setHealthLoading(false);
    }
  };

  // ---------- Save AI Configuration ----------
  const handleSaveAIConfig = async (e) => {
    e.preventDefault();
    setSaving(true);
    setSaveSuccess(false);
    try {
      const res = await aiService.updateConfig(config);
      if (res.status === "success") {
        setConfig(res.config);
        setSaveSuccess(true);
        const healthRes = await aiService.getHealth();
        setHealthStatus(healthRes);
        setTimeout(() => setSaveSuccess(false), 3000);
      }
    } catch (err) {
      console.error("[Settings] Saving settings failed:", err);
    } finally {
      setSaving(false);
    }
  };

  // ---------- Handle File Selection ----------
  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setKbUpload((prev) => ({ ...prev, file: e.target.files[0] }));
    }
  };

  // ---------- Upload Document Handler ----------
  const handleUploadDocument = async (e) => {
    e.preventDefault();
    if (!kbUpload.file) {
      setUploadMessage({ type: "error", text: "Please select a guideline document file to upload." });
      return;
    }

    setUploading(true);
    setUploadMessage({ type: "", text: "" });

    try {
      const formData = new FormData();
      formData.append("title", kbUpload.title);
      formData.append("source", kbUpload.source);
      formData.append("category", kbUpload.category);
      formData.append("section", kbUpload.section);
      formData.append("tags", kbUpload.tags);
      formData.append("file", kbUpload.file);

      const res = await knowledgeService.uploadDocument(formData);
      if (res.status === "success") {
        setUploadMessage({
          type: "success",
          text: `Successfully ingested "${res.filename}" into vector database. Generated ${res.chunks_count} chunks.`,
        });
        setKbUpload({
          title: "",
          source: "",
          category: "",
          section: "",
          tags: "",
          file: null,
        });
        // Reload docs list
        loadGuidelines();
      }
    } catch (err) {
      setUploadMessage({
        type: "error",
        text: err.response?.data?.detail || "Upload ingestion pipeline failed.",
      });
    } finally {
      setUploading(false);
    }
  };

  // ---------- Search RAG Guidelines ----------
  const handleSearchGuidelines = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setSearching(true);
    try {
      const res = await knowledgeService.searchGuidelines(searchQuery, searchCategory);
      setSearchResults(res.results || []);
    } catch (err) {
      console.error("[Settings] Search query failed:", err);
    } finally {
      setSearching(false);
    }
  };

  // ---------- Delete RAG Document Chunk/File ----------
  const handleDeleteGuideline = async (identifier) => {
    if (!window.confirm("Are you sure you want to delete this guideline chunk/file from the database?")) {
      return;
    }

    setDeletingId(identifier);
    try {
      const res = await knowledgeService.deleteDocument(identifier);
      if (res.status === "success") {
        // Reload docs list
        loadGuidelines();
        // Remove from search results if present
        setSearchResults((prev) => prev.filter((r) => r.id !== identifier && r.filename !== identifier));
      }
    } catch (err) {
      console.error("[Settings] Failed to delete document chunk:", err);
      alert(err.response?.data?.detail || "Failed to delete item.");
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="rounded-2xl bg-gradient-to-r from-slate-900 via-[#071B35] to-[#0B2942] p-6 text-white shadow-lg">
        <div className="flex items-center gap-4">
          <div className="rounded-xl bg-white/10 p-3 border border-white/10">
            <SettingsIcon size={24} />
          </div>
          <div>
            <h1 className="text-2xl font-black">Control Panel</h1>
            <p className="mt-1 text-xs text-slate-400">
              Configure system alerts, indexing parameters, and local AI engines
            </p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-slate-200 pb-px">
        {[
          { id: "ai", label: "AI Configuration", icon: Brain },
          { id: "kb", label: "Knowledge Base (RAG)", icon: Database },
          { id: "system", label: "System Preferences", icon: Sliders },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-3 text-xs font-black uppercase tracking-wider border-b-2 cursor-pointer transition ${
                isActive
                  ? "border-slate-900 text-slate-900"
                  : "border-transparent text-slate-400 hover:text-slate-600"
              }`}
            >
              <Icon size={14} />
              {tab.label}
            </button>
          );
        })}
      </div>

      {loading ? (
        <div className="clinical-card p-12 flex flex-col items-center justify-center text-slate-400">
          <Loader2 size={24} className="animate-spin mb-3 text-cyan-500" />
          <p className="text-xs font-black uppercase tracking-wider">Loading Configuration settings...</p>
        </div>
      ) : (
        <div className="grid grid-cols-12 gap-6">
          {activeTab === "ai" && (
            <>
              {/* Form Config */}
              <div className="col-span-12 lg:col-span-8">
                <form onSubmit={handleSaveAIConfig} className="clinical-card p-6 space-y-6">
                  <div>
                    <h2 className="text-sm font-black text-slate-800 uppercase tracking-wider mb-1">
                      Local & Cloud Inference Settings
                    </h2>
                    <p className="text-[10px] text-slate-400 font-semibold">
                      Fine-tune clinical copilot models and generation properties.
                    </p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                    {/* Provider Select */}
                    <div className="flex flex-col">
                      <label className="text-[10px] font-black uppercase text-slate-500 mb-2">
                        Active Provider
                      </label>
                      <select
                        value={config.provider}
                        onChange={(e) => handleProviderChange(e.target.value)}
                        className="input-clinical py-2.5"
                      >
                        {providers.map((p) => (
                          <option key={p.id} value={p.id}>
                            {p.name}
                          </option>
                        ))}
                      </select>
                    </div>

                    {/* Model Select */}
                    <div className="flex flex-col">
                      <label className="text-[10px] font-black uppercase text-slate-500 mb-2">
                        Model ID
                      </label>
                      <select
                        value={config.model}
                        onChange={(e) => setConfig({ ...config, model: e.target.value })}
                        className="input-clinical py-2.5"
                      >
                        {availableModels.map((m) => (
                          <option key={m} value={m}>
                            {m}
                          </option>
                        ))}
                        {availableModels.length === 0 && (
                          <option value={config.model}>{config.model}</option>
                        )}
                      </select>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                    {/* Temperature Slider */}
                    <div className="flex flex-col">
                      <div className="flex justify-between items-center mb-2">
                        <label className="text-[10px] font-black uppercase text-slate-500">
                          Temperature ({config.temperature})
                        </label>
                        <span className="text-[9px] font-bold text-slate-400">
                          {config.temperature <= 0.2 ? "Focused" : "Creative"}
                        </span>
                      </div>
                      <input
                        type="range"
                        min="0.0"
                        max="1.5"
                        step="0.1"
                        value={config.temperature}
                        onChange={(e) => setConfig({ ...config, temperature: parseFloat(e.target.value) })}
                        className="h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-slate-900"
                      />
                    </div>

                    {/* Max Tokens */}
                    <div className="flex flex-col">
                      <label className="text-[10px] font-black uppercase text-slate-500 mb-2">
                        Max Tokens Limit
                      </label>
                      <input
                        type="number"
                        value={config.max_tokens}
                        onChange={(e) => setConfig({ ...config, max_tokens: parseInt(e.target.value) || 256 })}
                        className="input-clinical"
                      />
                    </div>
                  </div>

                  {/* Streaming Toggle */}
                  <div className="flex items-center justify-between p-4 rounded-xl bg-slate-50/60 border border-slate-100">
                    <div>
                      <p className="text-[11px] font-black text-slate-700">Token Streaming</p>
                      <p className="text-[9px] text-slate-400 font-semibold mt-0.5">
                        Stream tokens in real-time. Uncheck for standard batch operations.
                      </p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={config.streaming}
                        onChange={(e) => setConfig({ ...config, streaming: e.target.checked })}
                        className="sr-only peer"
                      />
                      <div className="w-9 h-5 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-slate-900"></div>
                    </label>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-3 pt-3">
                    <button
                      type="submit"
                      disabled={saving}
                      className="btn-clinical-primary py-2.5 px-5 flex items-center gap-2"
                    >
                      {saving ? (
                        <Loader2 size={14} className="animate-spin" />
                      ) : (
                        <Save size={14} />
                      )}
                      Save Settings
                    </button>

                    {saveSuccess && (
                      <div className="flex items-center gap-1.5 text-emerald-600 text-xs font-bold animate-pulse">
                        <CheckCircle size={14} /> Settings applied dynamically!
                      </div>
                    )}
                  </div>
                </form>
              </div>

              {/* Health Panel */}
              <div className="col-span-12 lg:col-span-4 space-y-4">
                <div className="clinical-card p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-xs font-black uppercase text-slate-800 tracking-wider">
                      AI Health Status
                    </h3>
                    <button
                      onClick={checkHealth}
                      disabled={healthLoading}
                      type="button"
                      className="text-slate-400 hover:text-slate-600 cursor-pointer"
                    >
                      <RefreshCw size={13} className={healthLoading ? "animate-spin" : ""} />
                    </button>
                  </div>

                  <div className="flex items-center gap-3 p-4 rounded-xl bg-slate-50 border border-slate-100">
                    <div className={`h-3 w-3 rounded-full shrink-0 ${
                      healthStatus.healthy ? "bg-emerald-500 animate-pulse" : "bg-red-500 animate-pulse"
                    }`} />
                    <div>
                      <p className="text-[11px] font-black uppercase text-slate-800">
                        {healthStatus.provider} Provider
                      </p>
                      <p className={`text-[9px] font-extrabold uppercase mt-0.5 ${
                        healthStatus.healthy ? "text-emerald-700" : "text-red-600"
                      }`}>
                        {healthStatus.status}
                      </p>
                    </div>
                  </div>

                  <p className="text-[10px] text-slate-500 font-semibold leading-relaxed mt-4 bg-slate-50 p-3.5 rounded-xl border border-slate-100">
                    {healthStatus.details || "No diagnostics available."}
                  </p>

                  <div className="mt-4 pt-4 border-t border-slate-100">
                    <div className="flex items-start gap-2.5 text-[9px] text-slate-400 font-semibold">
                      <Cpu size={12} className="shrink-0 text-slate-300 mt-0.5" />
                      <p>
                        In case of offline local models (Ollama/LM Studio), the system automatically triggers a zero-delay fallback to the mock reasoning provider to guarantee uninterrupted ICU services.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </>
          )}

          {activeTab === "kb" && (
            <>
              {/* Upload Guideline Form */}
              <div className="col-span-12 lg:col-span-5 space-y-6">
                <form onSubmit={handleUploadDocument} className="clinical-card p-6 space-y-4">
                  <div>
                    <h2 className="text-sm font-black text-slate-800 uppercase tracking-wider mb-1">
                      Ingest Clinical Guideline
                    </h2>
                    <p className="text-[10px] text-slate-400 font-semibold">
                      Upload clinical guidelines (PDF, DOCX, TXT, MD) to ChromaDB.
                    </p>
                  </div>

                  {uploadMessage.text && (
                    <div className={`p-3 rounded-xl text-xs font-semibold flex gap-2 ${
                      uploadMessage.type === "success" 
                        ? "bg-emerald-50 text-emerald-700 border border-emerald-100" 
                        : "bg-red-50 text-red-700 border border-red-100"
                    }`}>
                      {uploadMessage.type === "success" ? <Check size={16} /> : <AlertCircle size={16} />}
                      <span>{uploadMessage.text}</span>
                    </div>
                  )}

                  <div className="space-y-3 text-xs font-semibold text-slate-500">
                    <div className="grid grid-cols-2 gap-3">
                      <div className="space-y-1">
                        <label className="text-[9px] font-black uppercase tracking-wider text-slate-400">Title</label>
                        <input
                          type="text"
                          required
                          placeholder="e.g. Surviving Sepsis Guide"
                          value={kbUpload.title}
                          onChange={(e) => setKbUpload({ ...kbUpload, title: e.target.value })}
                          className="input-clinical py-2"
                        />
                      </div>
                      <div className="space-y-1">
                        <label className="text-[9px] font-black uppercase tracking-wider text-slate-400">Author/Source</label>
                        <input
                          type="text"
                          required
                          placeholder="e.g. WHO, SSC"
                          value={kbUpload.source}
                          onChange={(e) => setKbUpload({ ...kbUpload, source: e.target.value })}
                          className="input-clinical py-2"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <div className="space-y-1">
                        <label className="text-[9px] font-black uppercase tracking-wider text-slate-400">Category</label>
                        <input
                          type="text"
                          required
                          placeholder="e.g. Sepsis, Resuscitation"
                          value={kbUpload.category}
                          onChange={(e) => setKbUpload({ ...kbUpload, category: e.target.value })}
                          className="input-clinical py-2"
                        />
                      </div>
                      <div className="space-y-1">
                        <label className="text-[9px] font-black uppercase tracking-wider text-slate-400">Section</label>
                        <input
                          type="text"
                          required
                          placeholder="e.g. Fluids, Antibiotics"
                          value={kbUpload.section}
                          onChange={(e) => setKbUpload({ ...kbUpload, section: e.target.value })}
                          className="input-clinical py-2"
                        />
                      </div>
                    </div>

                    <div className="space-y-1">
                      <label className="text-[9px] font-black uppercase tracking-wider text-slate-400">Tags (comma separated)</label>
                      <input
                        type="text"
                        placeholder="sepsis, iv, guidelines"
                        value={kbUpload.tags}
                        onChange={(e) => setKbUpload({ ...kbUpload, tags: e.target.value })}
                        className="input-clinical py-2"
                      />
                    </div>

                    {/* File Selector */}
                    <div className="pt-2">
                      <label className="flex flex-col items-center justify-center border-2 border-dashed border-slate-200 rounded-2xl p-6 bg-slate-50/50 hover:bg-slate-50 cursor-pointer transition">
                        <UploadCloud size={32} className="text-slate-400 mb-2 animate-bounce" />
                        <span className="text-xs font-black text-slate-700">
                          {kbUpload.file ? kbUpload.file.name : "Select Guideline File"}
                        </span>
                        <span className="text-[9px] text-slate-400 mt-1">PDF, DOCX, TXT, MD up to 10MB</span>
                        <input
                          type="file"
                          accept=".pdf,.docx,.txt,.md"
                          className="hidden"
                          onChange={handleFileChange}
                        />
                      </label>
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={uploading}
                    className="btn-clinical-primary w-full py-3 justify-center gap-2"
                  >
                    {uploading ? (
                      <>
                        <Loader2 size={14} className="animate-spin" /> Ingesting Guideline...
                      </>
                    ) : (
                      <>
                        <FileText size={14} /> Index in ChromaDB
                      </>
                    )}
                  </button>
                </form>
              </div>

              {/* Search Sandbox & Documents inventory */}
              <div className="col-span-12 lg:col-span-7 space-y-6">
                {/* Search Sandbox */}
                <div className="clinical-card p-6 space-y-4">
                  <div>
                    <h2 className="text-xs font-black text-slate-800 uppercase tracking-wider mb-1">
                      RAG Retrieval Sandbox
                    </h2>
                    <p className="text-[10px] text-slate-400 font-semibold">
                      Perform query matching to verify ChromaDB similarity retrieves.
                    </p>
                  </div>

                  <form onSubmit={handleSearchGuidelines} className="flex gap-2">
                    <input
                      type="text"
                      required
                      placeholder="Enter query (e.g. septic shock fluids threshold)"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="input-clinical flex-1"
                    />
                    <button
                      type="submit"
                      disabled={searching}
                      className="btn-clinical-primary px-4 shrink-0"
                    >
                      {searching ? <Loader2 size={14} className="animate-spin" /> : <Search size={14} />}
                      Search
                    </button>
                  </form>

                  {/* Search Results list */}
                  {searchResults.length > 0 && (
                    <div className="space-y-3 pt-2 max-h-[300px] overflow-y-auto pr-1">
                      {searchResults.map((r, idx) => (
                        <div key={idx} className="p-4 rounded-xl border border-slate-100 bg-slate-50/50 space-y-2 text-xs">
                          <div className="flex justify-between items-start">
                            <div>
                              <h4 className="font-black text-slate-800">{r.title}</h4>
                              <span className="text-[9px] text-slate-450 font-bold uppercase block mt-0.5">
                                {r.source} • {r.category} ({r.section})
                              </span>
                            </div>
                            <span className="badge-clinical-success font-black tracking-wider text-[9px]">
                              {(r.score * 100).toFixed(1)}% Match
                            </span>
                          </div>
                          <p className="text-[11px] text-slate-500 leading-relaxed italic bg-white p-2.5 rounded-lg border border-slate-50">
                            "...{r.content}..."
                          </p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Documents Inventory */}
                <div className="clinical-card p-6 space-y-4">
                  <div>
                    <h2 className="text-xs font-black text-slate-800 uppercase tracking-wider mb-1">
                      Indexed Guideline Registry ({kbDocs.length} Chunks)
                    </h2>
                    <p className="text-[10px] text-slate-400 font-semibold">
                      ChromaDB vectors list. Delete guideline files to wipe them from the store.
                    </p>
                  </div>

                  {loadingKbDocs ? (
                    <div className="p-6 flex justify-center text-slate-400">
                      <Loader2 className="animate-spin text-cyan-500 mr-2" size={16} />
                      <span className="text-xs font-bold uppercase">Refreshing registry...</span>
                    </div>
                  ) : (
                    <div className="space-y-2.5 max-h-[300px] overflow-y-auto pr-1">
                      {kbDocs.map((doc) => (
                        <div
                          key={doc.chunk_id}
                          className="flex items-start justify-between p-3.5 rounded-xl border border-slate-100 hover:border-slate-200 bg-white transition gap-3"
                        >
                          <div className="min-w-0 space-y-1 text-xs">
                            <div className="flex items-center gap-2">
                              <h4 className="font-black text-slate-800 truncate">{doc.title || doc.filename}</h4>
                              <span className="text-[9px] text-slate-400 font-bold">Chunk {doc.chunk_index}</span>
                            </div>
                            <p className="text-[9px] text-slate-450 font-semibold truncate">
                              File: {doc.filename} | Category: {doc.category} ({doc.section})
                            </p>
                            <p className="text-[10px] text-slate-500 font-semibold leading-relaxed truncate">
                              {doc.preview}
                            </p>
                          </div>

                          <button
                            onClick={() => handleDeleteGuideline(doc.filename)}
                            disabled={deletingId === doc.filename}
                            type="button"
                            className="p-2 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-lg shrink-0 cursor-pointer transition"
                            title="Delete entire guideline file"
                          >
                            {deletingId === doc.filename ? (
                              <Loader2 size={13} className="animate-spin text-red-500" />
                            ) : (
                              <Trash2 size={13} />
                            )}
                          </button>
                        </div>
                      ))}

                      {kbDocs.length === 0 && (
                        <div className="p-6 text-center text-xs font-semibold text-slate-400 border-2 border-dashed border-slate-100 rounded-2xl">
                          No guidelines currently indexed in the vector store.
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </>
          )}

          {activeTab === "system" && (
            /* System Cards */
            <div className="col-span-12 grid grid-cols-1 md:grid-cols-3 gap-6">
              {[
                {
                  icon: Bell,
                  title: "Alert Preferences",
                  description: "Configure critical alert thresholds and notification channels.",
                },
                {
                  icon: Database,
                  title: "Knowledge Base",
                  description: "Manage RAG document sources and clinical guideline indexing.",
                },
                {
                  icon: Shield,
                  title: "Security & Compliance",
                  description: "HIPAA audit logs, role-based access, and session policies.",
                },
              ].map((section) => {
                const Icon = section.icon;
                return (
                  <div key={section.title} className="clinical-card p-6 flex flex-col justify-between">
                    <div>
                      <Icon className="text-slate-800" size={24} />
                      <h2 className="mt-4 text-base font-bold text-slate-800">{section.title}</h2>
                      <p className="mt-2 text-xs leading-relaxed text-slate-500">{section.description}</p>
                    </div>
                    <button type="button" className="mt-6 rounded-xl bg-slate-900 px-5 py-3 text-xs font-bold text-white hover:bg-slate-800 transition cursor-pointer">
                      Configure
                    </button>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
