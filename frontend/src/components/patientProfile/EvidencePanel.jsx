import { motion } from "framer-motion";
import {
  BookOpen,
  Building2,
  FileText,
  FileCheck,
  ExternalLink,
  FileBadge,
} from "lucide-react";

import { useClinicalAI } from "../../context/ClinicalAIContext";

export default function EvidencePanel() {
  const { recommendation } = useClinicalAI();

  if (!recommendation) {
    return (
      <div className="rounded-[30px] border border-slate-200 bg-white p-8 shadow-xl">
        <div className="flex items-center gap-3">
          <BookOpen className="text-cyan-600" size={28} />

          <h2 className="text-2xl font-bold">
            Evidence Sources
          </h2>
        </div>

        <div className="mt-8 text-center">
          <BookOpen
            className="mx-auto text-slate-300"
            size={60}
          />

          <p className="mt-5 text-slate-500 leading-7">
            Run an AI analysis to view supporting clinical
            guidelines and research papers.
          </p>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="rounded-[30px] border border-slate-200 bg-white p-8 shadow-xl"
    >
      <div className="flex items-center gap-3">
        <BookOpen
          className="text-cyan-600"
          size={28}
        />

        <h2 className="text-2xl font-bold">
          Evidence Sources
        </h2>
      </div>

      <p className="mt-2 text-slate-500">
        Retrieved from the IntelliICU RAG Knowledge Base
      </p>

      <div className="mt-8 space-y-5">

        {(recommendation.sources ?? []).map((source, index) => (

          <motion.div
            key={index}
            whileHover={{ y: -4 }}
            className="rounded-2xl border border-slate-200 bg-slate-50 p-5 transition"
          >

            <div className="flex items-start justify-between">

              <FileText
                className="text-cyan-600"
                size={24}
              />

              <ExternalLink
                className="text-slate-400"
                size={18}
              />

            </div>

            <h3 className="mt-4 text-lg font-bold leading-7">
              {source.title}
            </h3>

            <div className="mt-5 flex flex-wrap gap-2">

              <span className="rounded-full bg-cyan-100 px-3 py-1 text-xs font-semibold text-cyan-700">
                {source.document_type}
              </span>

              {source.page && (
                <span className="rounded-full bg-slate-200 px-3 py-1 text-xs font-semibold text-slate-700">
                  Page {source.page}
                </span>
              )}

            </div>

            <div className="mt-5 space-y-3">

              <div className="flex items-center gap-3 text-slate-600">
                <Building2 size={16} />
                <span>{source.organization}</span>
              </div>

              {source.source_file && (
                <div className="flex items-center gap-3 text-slate-600">
                  <FileBadge size={16} />
                  <span>{source.source_file}</span>
                </div>
              )}

              {source.source_path && (
                <div className="flex items-center gap-3 text-xs text-slate-400 break-all">
                  <FileCheck size={15} />
                  <span>{source.source_path}</span>
                </div>
              )}

            </div>

          </motion.div>

        ))}

        {(!recommendation.sources ||
          recommendation.sources.length === 0) && (
          <div className="rounded-2xl border border-dashed border-slate-300 p-8 text-center text-slate-500">
            No evidence sources were returned by the Clinical AI engine.
          </div>
        )}

      </div>

      <div className="mt-8 rounded-2xl border border-cyan-100 bg-cyan-50 p-5">
        <p className="font-semibold text-cyan-700">
          ✓ Recommendations are supported by evidence retrieved from
          clinical guidelines and peer-reviewed literature.
        </p>
      </div>
    </motion.div>
  );
}