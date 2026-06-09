const PRESET_SKILLS = [
  'Disciplined and reliable',
  'Hardworking',
  'Self-directed',
  'Handles ambiguous or vague problems',
  'Turns unclear requirements into clear plans',
  'Strong communicator',
  'Collaborative team player',
  'Calm under pressure',
  'Proactive ownership',
  'Detail-oriented',
  'Fast learner',
  'Adaptable to changing priorities',
]

const DEFAULT_SELECTED = [
  'Disciplined and reliable',
  'Self-directed',
  'Handles ambiguous or vague problems',
  'Collaborative team player',
]

export { DEFAULT_SELECTED }

export default function SoftSkillsSelector({ selected, onChange, customSkill, onCustomSkillChange }) {
  const toggle = (skill) => {
    if (selected.includes(skill)) {
      onChange(selected.filter((s) => s !== skill))
    } else if (selected.length < 6) {
      onChange([...selected, skill])
    }
  }

  const addCustom = () => {
    const trimmed = customSkill.trim()
    if (!trimmed || selected.includes(trimmed) || selected.length >= 6) return
    onChange([...selected, trimmed])
    onCustomSkillChange('')
  }

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
        Soft skills (work-style paragraph)
      </h2>
      <p className="mt-1 text-sm text-slate-600">
        Pick up to 6 traits for the second paragraph - how you work, not technical skills.
      </p>

      <div className="mt-4 flex flex-wrap gap-2">
        {PRESET_SKILLS.map((skill) => {
          const isOn = selected.includes(skill)
          const disabled = !isOn && selected.length >= 6
          return (
            <button
              key={skill}
              type="button"
              onClick={() => toggle(skill)}
              disabled={disabled}
              className={`rounded-full px-3 py-1.5 text-xs font-medium transition ${
                isOn
                  ? 'bg-brand-600 text-white shadow-sm'
                  : disabled
                    ? 'cursor-not-allowed bg-slate-100 text-slate-400'
                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              {skill}
            </button>
          )
        })}
      </div>

      <div className="mt-4 flex gap-2">
        <input
          type="text"
          value={customSkill}
          onChange={(e) => onCustomSkillChange(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addCustom())}
          placeholder="Add your own trait"
          className="flex-1 rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-100"
        />
        <button
          type="button"
          onClick={addCustom}
          disabled={!customSkill.trim() || selected.length >= 6}
          className="rounded-xl border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-40"
        >
          Add
        </button>
      </div>

      {selected.length > 0 && (
        <p className="mt-3 text-xs text-slate-500">
          Selected ({selected.length}/6): {selected.join(' · ')}
        </p>
      )}
    </section>
  )
}
