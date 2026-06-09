function ScoreBar({ label, score }) {
  const color =
    score >= 75 ? 'bg-green-500' : score >= 50 ? 'bg-amber-500' : 'bg-red-400'

  return (
    <div>
      <div className="mb-1 flex justify-between text-sm">
        <span className="text-slate-600">{label}</span>
        <span className="font-semibold text-slate-900">{score}%</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-slate-100">
        <div
          className={`h-full rounded-full transition-all ${color}`}
          style={{ width: `${Math.min(100, Math.max(0, score))}%` }}
        />
      </div>
    </div>
  )
}

function TagList({ title, items, variant = 'neutral' }) {
  if (!items?.length) {
    return (
      <div>
        <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
          {title}
        </h3>
        <p className="mt-2 text-sm text-slate-400">None identified</p>
      </div>
    )
  }

  const colors =
    variant === 'match'
      ? 'bg-green-50 text-green-800 ring-green-100'
      : variant === 'missing'
        ? 'bg-amber-50 text-amber-800 ring-amber-100'
        : 'bg-slate-50 text-slate-700 ring-slate-100'

  return (
    <div>
      <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
        {title}
      </h3>
      <ul className="mt-2 flex flex-wrap gap-2">
        {items.map((item) => (
          <li
            key={item}
            className={`rounded-full px-3 py-1 text-xs font-medium ring-1 ${colors}`}
          >
            {item}
          </li>
        ))}
      </ul>
    </div>
  )
}

export default function QualityPanel({
  analysis,
  loading,
  onAddressSkill,
  addressingSkill,
  hasCoverLetter,
}) {
  if (loading) {
    return (
      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
          Quality analysis
        </h2>
        <p className="mt-4 text-sm text-slate-500">Analyzing match and tone…</p>
      </section>
    )
  }

  if (!analysis) {
    return (
      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
          Quality analysis
        </h2>
        <p className="mt-4 text-sm text-slate-500">
          Generate a cover letter to see ATS keyword match, missing skills, and tone score.
        </p>
      </section>
    )
  }

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
        Quality analysis
      </h2>

      <div className="mt-5 space-y-4">
        <ScoreBar label="ATS keyword match" score={analysis.ats_keyword_match_score} />
        <ScoreBar label="Style tone fit" score={analysis.tone_score} />
      </div>

      <div className="mt-6 space-y-5">
        <TagList
          title="Strongest resume-job matches"
          items={analysis.strongest_matches}
          variant="match"
        />

        <div>
          <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            Missing skills (from JD)
          </h3>
          {!analysis.missing_skills?.length ? (
            <p className="mt-2 text-sm text-slate-400">None identified</p>
          ) : (
            <ul className="mt-2 space-y-2">
              {analysis.missing_skills.map((skill) => (
                <li
                  key={skill}
                  className="flex flex-wrap items-center justify-between gap-2 rounded-lg bg-amber-50 px-3 py-2 ring-1 ring-amber-100"
                >
                  <span className="text-sm font-medium text-amber-900">{skill}</span>
                  {hasCoverLetter && onAddressSkill && (
                    <button
                      type="button"
                      onClick={() => onAddressSkill(skill)}
                      disabled={addressingSkill === skill}
                      className="rounded-md bg-white px-2 py-1 text-xs font-medium text-brand-700 ring-1 ring-brand-200 hover:bg-brand-50 disabled:opacity-50"
                    >
                      {addressingSkill === skill ? 'Updating proof…' : 'Address in letter'}
                    </button>
                  )}
                </li>
              ))}
            </ul>
          )}
          {hasCoverLetter && analysis.missing_skills?.length > 0 && (
            <p className="mt-2 text-xs text-slate-500">
              Address in letter regenerates the proof paragraph to reference that skill.
            </p>
          )}
        </div>

        {analysis.improvement_suggestions?.length > 0 && (
          <div>
            <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
              Suggestions
            </h3>
            <ul className="mt-2 space-y-2">
              {analysis.improvement_suggestions.map((tip, i) => (
                <li key={i} className="flex gap-2 text-sm text-slate-600">
                  <span className="text-brand-500">•</span>
                  {tip}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </section>
  )
}
