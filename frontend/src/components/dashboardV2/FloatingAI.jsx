import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  BrainCircuit,
  Send,
  Sparkles,
  X,
  Bot,
  User,
} from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import { hospitalAssistantService } from "../../services/hospitalAssistantService";
import StreamingMarkdown from "../clinicalCopilot/StreamingMarkdown";

export default function FloatingAI() {
  const { user } = useAuth();
  const role = user?.role?.toLowerCase();

  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [streaming, setStreaming] = useState(false);
  const [streamingText, setStreamingText] = useState("");

  const chatEndRef = useRef(null);

  // Define role specific contexts
  let assistantName = "IntelliAI Assistant";
  let placeholderText = "Ask IntelliAI...";
  let initialGreeting = "Hello! How can I assist you with clinical decision support today?";
  let suggestions = [
    "Show critical patients",
    "Why is Amelia Chen high risk?",
    "Explain Sepsis prediction",
  ];

  if (role === "hospitaladmin" || role === "superadmin") {
    assistantName = "Admin Assistant";
    placeholderText = "Ask Admin Assistant...";
    initialGreeting = "Hello Admin 👋 I'm your Admin Assistant. I can help with system health, user administration, or settings.";
    suggestions = [
      "Show system status",
      "How many users are active?",
      "Database connection overview",
    ];
  } else if (role === "nurse") {
    assistantName = "Nurse Assistant";
    placeholderText = "Ask Nurse Assistant...";
    initialGreeting = "Hello Nurse 👋 I'm your Nurse Assistant. Ask me about active alerts, vital summaries, or nursing workflows.";
    suggestions = [
      "Check active nursing tasks",
      "Show recent critical alerts",
      "Review vital signs summary",
    ];
  } else if (role === "icumanager") {
    assistantName = "ICU Manager Assistant";
    placeholderText = "Ask ICU Manager Assistant...";
    initialGreeting = "Hello Operations Manager 👋 I'm your ICU Manager Assistant. Ask me about bed utilization, response times, or unit analytics.";
    suggestions = [
      "Show bed utilization",
      "Show alert response times",
      "ICU analytics overview",
    ];
  } else if (role === "doctor") {
    assistantName = "IntelliAI Hospital Assistant";
    placeholderText = "Ask Hospital Assistant...";
    initialGreeting = "Hello Doctor 👋 I'm your IntelliAI Hospital Assistant. Ask me about patients, alerts, reports, or workflow. (No patient diagnosis)";
    suggestions = [
      "Which patients need immediate attention?",
      "Which patients have worsening vital trends?",
      "Give me a sepsis overview",
    ];
  }

  // Reset chat history when role changes or on initial load
  useEffect(() => {
    setMessages([
      {
        role: "assistant",
        text: initialGreeting,
      }
    ]);
  }, [role, initialGreeting]);

  // Scroll to bottom on new messages
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingText]);

  const handleSend = async (textToSend) => {
    const text = textToSend || input;
    if (!text.trim() || streaming) return;

    setInput("");
    setMessages((prev) => [...prev, { role: "user", text }]);
    setStreaming(true);
    setStreamingText("");

    const lowerQ = text.toLowerCase();

    // STRICT ROLE PERMISSION AND SHORTCUT VALIDATION
    if (role === "hospitaladmin" || role === "superadmin") {
      const isValid = ["system", "health", "status", "user", "account", "directory", "add", "remove", "password", "setting", "limit", "config", "port", "database"].some(k => lowerQ.includes(k));
      if (!isValid) {
        setMessages((prev) => [...prev, {
          role: "assistant",
          text: "As the **Admin Assistant**, I can only assist with system administration, user accounts, system status, and configuration settings. For clinical queries, please refer to clinical workspaces."
        }]);
        setStreaming(false);
        return;
      }
    } else if (role === "nurse") {
      const isValid = ["task", "checklist", "nursing", "vital", "alert", "warning", "patient", "bed", "medication", "dose", "drug", "heart", "spo2", "temp", "blood pressure", "bp"].some(k => lowerQ.includes(k));
      if (!isValid) {
        setMessages((prev) => [...prev, {
          role: "assistant",
          text: "As the **Nurse Assistant**, I can only assist with nursing care workflows, checklists, vital status logs, medications, and active alerts."
        }]);
        setStreaming(false);
        return;
      }
    } else if (role === "icumanager") {
      const isValid = ["bed", "occupancy", "capacity", "utilization", "analytics", "staff", "response", "time", "census", "critical", "serious", "stable", "report", "manager"].some(k => lowerQ.includes(k));
      if (!isValid) {
        setMessages((prev) => [...prev, {
          role: "assistant",
          text: "As the **ICU Manager Assistant**, I can only assist with bed occupancy rates, operations statistics, response times, and general unit analytics."
        }]);
        setStreaming(false);
        return;
      }
    }

    try {
      // Append role identifier to question to give LLM proper context
      const formattedQuestion = `[Role: ${user?.role || "Doctor"}] ${text}`;
      
      await hospitalAssistantService.chatStream(
        formattedQuestion,
        (token) => {
          setStreamingText((prev) => prev + token);
        },
        (final) => {
          const reasoning = final?.reasoning || final?.answer || "Analysis complete.";
          setMessages((prev) => [...prev, { role: "assistant", text: reasoning }]);
          setStreamingText("");
          setStreaming(false);
        },
        `floating-${role}`
      );
    } catch (err) {
      // Fallback batch mode
      try {
        const res = await hospitalAssistantService.chat(text, `floating-${role}`);
        const textRes = res?.reasoning || res?.answer || "Unable to complete request.";
        setMessages((prev) => [...prev, { role: "assistant", text: textRes }]);
      } catch (fallbackErr) {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", text: "Unable to process request. Please check connection." }
        ]);
      }
      setStreamingText("");
      setStreaming(false);
    }
  };

  return (
    <>
      {/* Floating Button */}
      <motion.button
        whileHover={{ scale: 1.08 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setOpen(true)}
        className="fixed bottom-8 right-8 z-50 flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-cyan-500 to-blue-700 text-white shadow-2xl cursor-pointer"
      >
        <BrainCircuit size={30} />
      </motion.button>

      {/* Chat Window */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: 40, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 40 }}
            className="fixed bottom-28 right-8 z-50 w-[440px] overflow-hidden rounded-[28px] border border-slate-200 bg-white shadow-2xl flex flex-col"
          >
            {/* Header */}
            <div className="bg-gradient-to-r from-slate-900 via-cyan-900 to-blue-900 p-5 text-white flex items-center justify-between">
              <div className="flex items-center gap-3">
                <BrainCircuit className="text-cyan-400" />
                <div>
                  <h2 className="font-bold text-sm">{assistantName}</h2>
                  <p className="text-xs text-cyan-200">ICU Decision Workspace</p>
                </div>
              </div>
              <button onClick={() => setOpen(false)} className="p-1 hover:bg-white/10 rounded-lg transition cursor-pointer">
                <X size={18} />
              </button>
            </div>

            {/* Messages */}
            <div className="h-[360px] overflow-y-auto bg-slate-50 p-5 space-y-4 font-clinical-messages">
              {messages.map((msg, index) => (
                <div
                  key={index}
                  className={`flex gap-3 ${msg.role === "assistant" ? "" : "justify-end"}`}
                >
                  {msg.role === "assistant" && (
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-cyan-600 text-white shrink-0">
                      <Bot size={16} />
                    </div>
                  )}
                  <div
                    className={`max-w-[300px] rounded-2xl p-3.5 text-xs font-semibold leading-relaxed ${
                      msg.role === "assistant"
                        ? "bg-white text-slate-700 shadow-sm border border-slate-100"
                        : "bg-cyan-600 text-white"
                    }`}
                  >
                    {msg.role === "assistant" ? (
                      <StreamingMarkdown text={msg.text} />
                    ) : (
                      msg.text
                    )}
                  </div>
                  {msg.role === "user" && (
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-800 text-white shrink-0">
                      <User size={16} />
                    </div>
                  )}
                </div>
              ))}

              {/* Streaming placeholder */}
              {streamingText && (
                <div className="flex gap-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-cyan-600 text-white shrink-0">
                    <Bot size={16} />
                  </div>
                  <div className="max-w-[300px] rounded-2xl p-3.5 text-xs font-semibold leading-relaxed bg-white text-slate-700 shadow-sm border border-slate-100">
                    <StreamingMarkdown text={streamingText} isStreaming={streaming} />
                  </div>
                </div>
              )}

              {/* Suggestions */}
              {!streaming && (
                <div className="pt-2">
                  <p className="mb-2 text-[10px] font-black uppercase text-slate-400 tracking-wider">
                    Suggested Tasks
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {suggestions.map((item) => (
                      <button
                        key={item}
                        onClick={() => handleSend(item)}
                        className="rounded-xl border border-cyan-100 bg-cyan-50/50 px-3 py-2 text-[11px] font-bold text-cyan-800 hover:bg-cyan-100 transition cursor-pointer text-left"
                      >
                        {item}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              <div ref={chatEndRef} />
            </div>

            {/* Input */}
            <div className="border-t bg-white p-4">
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSend();
                }}
                className="flex items-center gap-3"
              >
                <input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder={placeholderText}
                  disabled={streaming}
                  className="flex-1 rounded-xl border border-slate-200 px-4 py-3 text-xs outline-none focus:border-cyan-500 font-semibold disabled:opacity-50"
                />
                <button
                  type="submit"
                  disabled={streaming || !input.trim()}
                  className="rounded-xl bg-cyan-600 p-3 text-white hover:bg-cyan-700 transition disabled:opacity-50 cursor-pointer"
                >
                  <Send size={16} />
                </button>
              </form>
              <div className="mt-3 flex items-center gap-2 text-[10px] text-slate-400 font-bold">
                <Sparkles size={12} className="text-cyan-500" />
                Active Work context: {user?.role || "Doctor"}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}