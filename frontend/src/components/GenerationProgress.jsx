export default function GenerationProgress({ steps, stepIndex, title = 'Working on your letter' }) {
  if (!steps?.length) return null

  return (
    <section className="rounded-2xl border border-brand-100 bg-brand-50/60 p-5 shadow-sm">
      <h2 className="text-sm font-semibold text-brand-800">{title}</h2>
      <ol className="mt-4 space-y-3">
        {steps.map((step, idx) => {
          const done = idx < stepIndex
          const current = idx === stepIndex
          return (
            <li key={step.id} className="flex items-center gap-3 text-sm">
              <span
                className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-semibold ${
                  done
                    ? 'bg-brand-600 text-white'
                    : current
                      ? 'bg-white text-brand-700 ring-2 ring-brand-400'
                      : 'bg-white/80 text-slate-400 ring-1 ring-slate-200'
                }`}
              >
                {done ? '✓' : idx + 1}
              </span>
              <span
                className={
                  done
                    ? 'text-slate-600'
                    : current
                      ? 'font-medium text-brand-900'
                      : 'text-slate-400'
                }
              >
                {step.label}
                {current && (
                  <span className="ml-2 inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-brand-500" />
                )}
              </span>
            </li>
          )
        })}
      </ol>
    </section>
  )
}
