import React, { useState, useEffect, useRef } from "react";
import { MessageSquare, RefreshCw, XCircle, FileText } from "lucide-react";
import ChatBubble from "./ChatBubble";
import ChatInput from "./ChatInput";
import SuggestedQuestions from "./SuggestedQuestions";
import LoadingBubble from "./LoadingBubble";
import { clinicalCopilotService } from "../../services/clinicalCopilotService";
import ReportPreview from "../clinicalReport/ReportPreview";

export default function ChatPanel({ patientId }) {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showReportModal, setShowReportModal] = useState(false);
  
  const chatEndRef = useRef(null);
  const scrollContainerRef = useRef(null);
  const shouldAutoScrollRef = useRef(true);
  const lastScrollTimeRef = useRef(0);
  const prevLengthRef = useRef(0);
  const prevStreamingRef = useRef(false);

  const scrollToBottom = (behavior = "auto") => {
    const container = scrollContainerRef.current;
    if (!container) return;
    container.scrollTo({
      top: container.scrollHeight,
      behavior
    });
  };

  const handleScroll = () => {
    const container = scrollContainerRef.current;
    if (!container) return;
    const { scrollTop, scrollHeight, clientHeight } = container;
    // Auto-scroll only if already near bottom (within 100px)
    const isNearBottom = scrollHeight - scrollTop - clientHeight < 100;
    shouldAutoScrollRef.current = isNearBottom;
  };

  // Smart Auto Scroll Controller
  useEffect(() => {
    if (messages.length === 0) return;

    const latestMessage = messages[messages.length - 1];
    const isStreaming = latestMessage?.isStreaming;

    const prevLength = prevLengthRef.current || 0;
    const prevStreaming = prevStreamingRef.current || false;
    
    prevLengthRef.current = messages.length;
    prevStreamingRef.current = isStreaming;

    const isNewMessage = messages.length > prevLength;
    const justFinished = !isStreaming && prevStreaming;

    if (isNewMessage || justFinished) {
      if (shouldAutoScrollRef.current) {
        scrollToBottom("smooth");
      }
    } else if (isStreaming) {
      const now = Date.now();
      if (now - lastScrollTimeRef.current > 250) {
        if (shouldAutoScrollRef.current) {
          scrollToBottom("auto");
        }
        lastScrollTimeRef.current = now;
      }
    }
  }, [messages, loading]);

  // Initial welcome message
  useEffect(() => {
    setMessages([
      {
        id: "welcome",
        sender: "copilot",
        content: {
          summary: "Hello! I am your Clinical Copilot. I have full read-access to this patient's charts, vital telemetries, lab history, active alerts, and AI prediction markers. How can I assist you with clinical assessment today?",
          findings: [],
          risk: "",
          recommendations: [],
          evidence: [],
          confidence: 1.0
        },
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
    ]);
  }, [patientId]);

  const handleSend = async (question) => {
    if (!question.trim()) return;

    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const userMessage = {
      id: `user-${Date.now()}`,
      sender: "user",
      content: question,
      timestamp
    };

    const streamId = `copilot-${Date.now()}`;
    const placeholderMsg = {
      id: streamId,
      sender: "copilot",
      content: {
        summary: "",
        findings: [],
        risk: "",
        recommendations: [],
        evidence: [],
        confidence: 0.95
      },
      isStreaming: true,
      timestamp
    };

    setMessages((prev) => [...prev, userMessage, placeholderMsg]);
    setLoading(true);
    setError(null);

    try {
      await clinicalCopilotService.askQuestionStream(
        patientId,
        question,
        (token) => {
          setLoading(false);
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === streamId
                ? {
                    ...msg,
                    content: {
                      ...msg.content,
                      summary: (msg.content?.summary || "") + token
                    }
                  }
                : msg
            )
          );
        },
        (finalResponse) => {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === streamId
                ? {
                    ...msg,
                    content: finalResponse,
                    isStreaming: false
                  }
                : msg
            )
          );
        }
      );
    } catch (err) {
      console.error("Clinical Copilot query failed:", err);
      setError("Failed to consult the Clinical Copilot. Please check network connectivity.");
      setMessages((prev) => prev.filter((msg) => msg.id !== streamId));
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setMessages([
      {
        id: "welcome",
        sender: "copilot",
        content: {
          summary: "Clinical Copilot logs cleared. Context builder refreshed. How can I assist you?",
          findings: [],
          risk: "",
          recommendations: [],
          evidence: [],
          confidence: 1.0
        },
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
    ]);
    setError(null);
  };

  return (
    <div className="clinical-card flex flex-col h-[580px] bg-slate-50/50 overflow-hidden relative">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-150 bg-white px-5 py-4 shrink-0">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-cyan-50 border border-cyan-100 text-cyan-600">
            <MessageSquare size={16} />
          </div>
          <div>
            <h3 className="text-xs font-black uppercase tracking-wider text-slate-800">Clinical Copilot</h3>
            <p className="text-[10px] text-slate-400 font-semibold mt-0.5">EHR-Aware Conversational Assistant</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Generate Report Button */}
          <button
            onClick={() => setShowReportModal(true)}
            className="flex items-center gap-1 px-3 py-1.5 rounded-xl bg-cyan-600 hover:bg-cyan-700 text-white text-[10px] font-bold transition shadow-sm"
            title="Generate structured AI clinical report"
          >
            <FileText size={12} />
            <span>Generate Report</span>
          </button>

          <button
            onClick={handleReset}
            className="p-2 text-slate-400 hover:text-slate-655 hover:bg-slate-100 rounded-xl transition"
            title="Reset Chat Session"
          >
            <RefreshCw size={14} />
          </button>
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div ref={scrollContainerRef} onScroll={handleScroll} className="flex-1 overflow-y-auto p-5 space-y-4">
        {messages.map((msg) => (
          <ChatBubble key={msg.id} message={msg} />
        ))}
        
        {loading && <LoadingBubble />}

        {error && (
          <div className="flex items-center gap-2 text-xs text-red-600 bg-red-50 border border-red-100 rounded-2xl p-4.5">
            <XCircle size={14} className="shrink-0" />
            <span className="font-semibold">{error}</span>
          </div>
        )}

        <div ref={chatEndRef} />
      </div>

      {/* Footer / Input Area */}
      <div className="border-t border-slate-150 bg-white p-5 space-y-4 shrink-0">
        <SuggestedQuestions onSelect={handleSend} disabled={loading} />
        <ChatInput onSend={handleSend} disabled={loading} />
      </div>

      {/* Report Preview Modal Overlay */}
      {showReportModal && (
        <ReportPreview
          patientId={patientId}
          onClose={() => setShowReportModal(false)}
        />
      )}
    </div>
  );
}
