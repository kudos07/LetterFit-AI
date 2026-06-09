import { useState } from 'react'

const STYLE_HINTS = {
  Professional: 'Balanced, polished, corporate-safe.',
  Qualifications: 'Facts-first, credential-heavy, low hype.',
  Hype: 'Confident, enthusiastic, impact-driven.',
  Mix: 'Professional polish plus clear proof points.',
  Bold: 'High-energy, memorable, attention-grabbing.',
}

export default function StyleSelector({
  styles,
  presets,
  value,
  onChange,
  letterLength,
  onLetterLengthChange,
}) {
  const [showExample, setShowExample] = useState(false)
  const preset = presets?.find((p) => p.id === value)
  const hint = preset?.summary || STYLE_HINTS[value] || ''
  const exampleOpening = preset?.example_opening || ''

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
        Letter style
      </h2>
      <p className="mt-1 text-sm text-slate-600">
        Pick how bold or formal the letter should feel. All letters are in English.
      </p>

      <div className="mt-4 grid gap-2 sm:grid-cols-2">
        {styles.map((style) => (
          <button
            key={style}
            type="button"
            onClick={() => onChange(style)}
            className={`rounded-xl border px-4 py-3 text-left text-sm transition ${
              value === style
                ? 'border-brand-400 bg-brand-50 text-brand-900 ring-2 ring-brand-100'
                : 'border-slate-200 bg-white text-slate-700 hover:border-slate-300'
            }`}
          >
            <span className="font-semibold">{style}</span>
            <span className="mt-0.5 block text-xs text-slate-500">
              {STYLE_HINTS[style] || ''}
            </span>
          </button>
        ))}
      </div>

      <div className="mt-4">
        <span className="text-sm font-medium text-slate-700">Length</span>
        <div className="mt-2 flex gap-2">
          {[
            { id: 'short', label: 'Short', hint: '150-200 words' },
            { id: 'standard', label: 'Standard', hint: '220-280 words' },
          ].map((opt) => (
            <button
              key={opt.id}
              type="button"
              onClick={() => onLetterLengthChange(opt.id)}
              className={`flex-1 rounded-xl border px-3 py-2 text-left text-sm transition ${
                letterLength === opt.id
                  ? 'border-brand-400 bg-brand-50 text-brand-900'
                  : 'border-slate-200 bg-white text-slate-700 hover:border-slate-300'
              }`}
            >
              <span className="font-medium">{opt.label}</span>
              <span className="block text-xs text-slate-500">{opt.hint}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="mt-3 rounded-lg bg-slate-50 px-3 py-3 text-sm text-slate-600">
        <p>
          <span className="font-medium text-slate-800">{value}: </span>
          {hint}
        </p>

        {(preset?.salutation || preset?.closing) && (
          <p className="mt-2 text-xs text-slate-500">
            Sign-off: {preset.salutation} … {preset.closing}
          </p>
        )}

        {exampleOpening && (
          <div className="mt-3">
            <button
              type="button"
              onClick={() => setShowExample((v) => !v)}
              className="text-xs font-medium text-brand-600 hover:text-brand-700"
            >
              {showExample ? 'Hide example opening' : 'See example opening'}
            </button>
            {showExample && (
              <p className="mt-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm italic text-slate-700">
                &ldquo;{exampleOpening}&rdquo;
              </p>
            )}
          </div>
        )}
      </div>
    </section>
  )
}
