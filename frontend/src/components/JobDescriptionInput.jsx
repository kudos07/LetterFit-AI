export default function JobDescriptionInput({ value, onChange, onLoadSample }) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
          Job description
        </h2>
        <button
          type="button"
          onClick={onLoadSample}
          className="text-xs font-medium text-brand-600 hover:text-brand-700"
        >
          Load sample JD
        </button>
      </div>

      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        rows={12}
        placeholder="Paste the full job description here…"
        className="mt-4 w-full resize-y rounded-xl border border-slate-200 bg-slate-50/50 px-4 py-3 text-sm leading-relaxed text-slate-800 placeholder:text-slate-400 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-100"
      />
    </section>
  )
}
