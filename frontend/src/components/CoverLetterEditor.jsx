import { useEffect, useMemo, useState } from 'react'
import {
  mergeCoverLetter,
  parseCoverLetter,
  SECTION_LABELS,
} from '../utils/letterParser.js'
import { countBodyWords, lengthLimits } from '../utils/wordCount.js'

const EDITABLE_SECTIONS = ['opening', 'proof', 'soft_skills', 'close']

function SectionBlock({ label, value, onChange, onRegenerate, regenerating, disabled }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50/50 p-3">
      <div className="mb-2 flex items-center justify-between gap-2">
        <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">
          {label}
        </span>
        <button
          type="button"
          onClick={onRegenerate}
          disabled={disabled || regenerating}
          className="rounded-md border border-slate-200 bg-white px-2 py-1 text-xs font-medium text-slate-600 hover:bg-slate-50 disabled:opacity-40"
        >
          {regenerating ? 'Rewriting…' : 'Regenerate'}
        </button>
      </div>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        rows={label === 'Opening' || label === 'Close' ? 3 : 4}
        className="w-full resize-y rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm leading-relaxed text-slate-800 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-100"
      />
    </div>
  )
}

export default function CoverLetterEditor({
  value,
  onChange,
  onCopy,
  onRegenerate,
  onRegenerateParagraph,
  onExport,
  onExportPdf,
  loading,
  paragraphLoading,
  exportLoading,
  exportPdfLoading,
  copySuccess,
  letterLength = 'short',
}) {
  const [viewMode, setViewMode] = useState('sections')
  const [regeneratingSection, setRegeneratingSection] = useState(null)

  const parts = useMemo(() => (value ? parseCoverLetter(value) : null), [value])

  useEffect(() => {
    if (!value) setViewMode('sections')
  }, [value])

  const updateSection = (key, text) => {
    if (!parts) return
    const updated = { ...parts, [key]: text }
    onChange(mergeCoverLetter(updated))
  }

  const handleRegenerateSection = async (section) => {
    if (!onRegenerateParagraph || !value) return
    setRegeneratingSection(section)
    try {
      await onRegenerateParagraph(section)
    } finally {
      setRegeneratingSection(null)
    }
  }

  const hasSections = parts && EDITABLE_SECTIONS.some((k) => parts[k]?.trim())
  const bodyWords = value ? countBodyWords(value) : 0
  const limits = lengthLimits(letterLength)
  const overLimit = bodyWords > limits.warn

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
          Cover letter
        </h2>
        <div className="flex flex-wrap gap-2">
          {value && (
            <button
              type="button"
              onClick={() => setViewMode((m) => (m === 'sections' ? 'full' : 'sections'))}
              className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50"
            >
              {viewMode === 'sections' ? 'Full text' : 'By paragraph'}
            </button>
          )}
          <button
            type="button"
            onClick={onCopy}
            disabled={!value}
            className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-40"
          >
            {copySuccess ? 'Copied!' : 'Copy'}
          </button>
          <button
            type="button"
            onClick={onRegenerate}
            disabled={loading || !value}
            className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-40"
          >
            {loading ? 'Regenerating…' : 'Regenerate all'}
          </button>
          <button
            type="button"
            onClick={onExport}
            disabled={!value || exportLoading || exportPdfLoading}
            className="rounded-lg border border-brand-200 bg-brand-50 px-3 py-1.5 text-xs font-medium text-brand-700 hover:bg-brand-100 disabled:opacity-40"
          >
            {exportLoading ? 'Exporting…' : 'DOCX'}
          </button>
          <button
            type="button"
            onClick={onExportPdf}
            disabled={!value || exportLoading || exportPdfLoading}
            className="rounded-lg bg-brand-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-brand-700 disabled:opacity-40"
          >
            {exportPdfLoading ? 'Exporting…' : 'PDF'}
          </button>
        </div>
      </div>

      {value && (
        <div
          className={`mt-3 flex items-center justify-between rounded-lg px-3 py-2 text-xs ${
            overLimit
              ? 'bg-amber-50 text-amber-800 ring-1 ring-amber-200'
              : 'bg-slate-50 text-slate-600'
          }`}
        >
          <span>
            <span className="font-semibold">{bodyWords}</span> body words
            <span className="text-slate-400"> / target ~{limits.target}</span>
          </span>
          {overLimit && (
            <span className="font-medium">Consider shortening or switch to Standard length</span>
          )}
        </div>
      )}

      {!value && (
        <p className="mt-4 text-sm text-slate-500">
          Your generated cover letter will appear here. Edit by paragraph or as full text.
        </p>
      )}

      {value && viewMode === 'sections' && hasSections && (
        <div className="mt-4 space-y-3">
          {parts.salutation && (
            <p className="text-sm text-slate-700">{parts.salutation}</p>
          )}

          {EDITABLE_SECTIONS.map((key) => {
            if (!parts[key]?.trim()) return null

            return (
              <SectionBlock
                key={key}
                label={SECTION_LABELS[key]}
                value={parts[key]}
                onChange={(text) => updateSection(key, text)}
                onRegenerate={() => handleRegenerateSection(key)}
                regenerating={regeneratingSection === key}
                disabled={loading || paragraphLoading}
              />
            )
          })}

          {(parts.closing_line || parts.signature) && (
            <div className="rounded-xl border border-dashed border-slate-200 px-3 py-2 text-sm text-slate-600">
              {parts.closing_line && <p>{parts.closing_line}</p>}
              {parts.signature && <p className="mt-1">{parts.signature}</p>}
            </div>
          )}
        </div>
      )}

      {value && (viewMode === 'full' || !hasSections) && (
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          rows={18}
          className="mt-4 w-full resize-y rounded-xl border border-slate-200 bg-slate-50/50 px-4 py-3 text-sm leading-relaxed text-slate-800 placeholder:text-slate-400 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-100"
        />
      )}
    </section>
  )
}
