export default function CompanyResearchPanel({ research, loading, companyName }) {
  if (loading && companyName?.trim()) {
    return (
      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
          Company research
        </h2>
        <p className="mt-3 text-sm text-slate-500">
          Researching {companyName}…
        </p>
      </section>
    )
  }

  if (!research) {
    return (
      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
          Company research
        </h2>
        <p className="mt-3 text-sm text-slate-500">
          Enter a company name to research it before generating your cover letter.
        </p>
      </section>
    )
  }

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
          Company research
        </h2>
        <span
          className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${
            research.found
              ? 'bg-green-50 text-green-700 ring-1 ring-green-100'
              : 'bg-amber-50 text-amber-700 ring-1 ring-amber-100'
          }`}
        >
          {research.found ? 'Found' : 'Limited data'}
        </span>
      </div>

      <p className="mt-2 text-sm font-medium text-slate-800">{research.company_name}</p>

      {research.sources?.length > 0 && (
        <p className="mt-1 text-xs text-slate-500">
          Sources: {research.sources.join(', ')}
        </p>
      )}

      <p className="mt-3 text-sm leading-relaxed text-slate-600 whitespace-pre-wrap">
        {research.summary}
      </p>
    </section>
  )
}
