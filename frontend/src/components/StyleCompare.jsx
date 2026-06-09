import { countBodyWords } from '../utils/wordCount.js'

function ScoreBadge({ label, value }) {
  return (
    <span className="inline-flex items-center gap-1 rounded-md bg-slate-100 px-2 py-0.5 text-xs text-slate-700">
      <span className="text-slate-500">{label}</span>
      <span className="font-semibold">{value}</span>
    </span>
  )
}

export default function StyleCompare({
  styles,
  styleA,
  styleB,
  onStyleAChange,
  onStyleBChange,
  onCompare,
  comparing,
  results,
  qualityResults,
  activeTab,
  onActiveTabChange,
  onUseLetter,
}) {
  const scoreA = qualityResults?.[styleA]
  const scoreB = qualityResults?.[styleB]

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
        Compare styles
      </h2>
      <p className="mt-1 text-sm text-slate-600">
        Generate the same application in two tones side by side.
      </p>

      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        <label className="block text-sm">
          <span className="font-medium text-slate-700">Style A</span>
          <select
            value={styleA}
            onChange={(e) => onStyleAChange(e.target.value)}
            className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
          >
            {styles.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </label>
        <label className="block text-sm">
          <span className="font-medium text-slate-700">Style B</span>
          <select
            value={styleB}
            onChange={(e) => onStyleBChange(e.target.value)}
            className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
          >
            {styles.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </label>
      </div>

      <button
        type="button"
        onClick={onCompare}
        disabled={comparing || styleA === styleB}
        className="mt-4 w-full rounded-xl border border-brand-200 bg-brand-50 px-4 py-2.5 text-sm font-semibold text-brand-700 hover:bg-brand-100 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {comparing ? 'Comparing…' : 'Compare both styles'}
      </button>

      {qualityResults && scoreA && scoreB && (
        <div className="mt-4 grid gap-2 rounded-xl border border-slate-100 bg-slate-50/80 p-3 sm:grid-cols-2">
          {[styleA, styleB].map((style) => {
            const q = qualityResults[style]
            if (!q) return null
            return (
              <div key={style} className="text-xs">
                <p className="font-semibold text-slate-800">{style}</p>
                <div className="mt-1.5 flex flex-wrap gap-1.5">
                  <ScoreBadge label="ATS" value={q.ats_keyword_match_score} />
                  <ScoreBadge label="Tone" value={q.tone_score} />
                  {q.missing_skills?.length > 0 && (
                    <span className="text-slate-500">
                      {q.missing_skills.length} skill gap{q.missing_skills.length === 1 ? '' : 's'}
                    </span>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}

      {results && (
        <div className="mt-4">
          <div className="flex gap-1 rounded-lg bg-slate-100 p-1">
            {[styleA, styleB].map((style) => (
              <button
                key={style}
                type="button"
                onClick={() => onActiveTabChange(style)}
                className={`flex-1 rounded-md px-3 py-1.5 text-xs font-medium transition ${
                  activeTab === style
                    ? 'bg-white text-slate-900 shadow-sm'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                {style}
                {qualityResults?.[style] && (
                  <span className="ml-1 text-slate-400">
                    · ATS {qualityResults[style].ats_keyword_match_score}
                  </span>
                )}
              </button>
            ))}
          </div>

          {[styleA, styleB].map((style) => {
            if (activeTab !== style || !results[style]) return null
            const letter = results[style]
            const words = countBodyWords(letter)
            const q = qualityResults?.[style]
            return (
              <div key={style} className="mt-3">
                <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-xs text-slate-500">{words} body words</span>
                    {q && (
                      <>
                        <ScoreBadge label="ATS" value={q.ats_keyword_match_score} />
                        <ScoreBadge label="Tone" value={q.tone_score} />
                      </>
                    )}
                  </div>
                  <button
                    type="button"
                    onClick={() => onUseLetter(letter, style)}
                    className="rounded-md bg-brand-600 px-2 py-1 text-xs font-medium text-white hover:bg-brand-700"
                  >
                    Use this letter
                  </button>
                </div>
                <textarea
                  readOnly
                  value={letter}
                  rows={12}
                  className="w-full resize-y rounded-xl border border-slate-200 bg-slate-50/50 px-3 py-2 text-sm leading-relaxed text-slate-800"
                />
              </div>
            )
          })}
        </div>
      )}
    </section>
  )
}
