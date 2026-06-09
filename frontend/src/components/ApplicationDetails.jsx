const COUNTRY_LANGUAGES = {
  germany: 'German',
  france: 'French',
  japan: 'Japanese',
  spain: 'Spanish',
  italy: 'Italian',
  netherlands: 'Dutch',
  canada: 'French',
  singapore: 'Mandarin',
  brazil: 'Portuguese',
  india: 'Hindi',
  china: 'Mandarin',
  korea: 'Korean',
  'south korea': 'Korean',
  mexico: 'Spanish',
  sweden: 'Swedish',
  norway: 'Norwegian',
  denmark: 'Danish',
  poland: 'Polish',
  ireland: 'Irish',
  'united kingdom': 'English',
  uk: 'English',
}

function suggestLanguage(country) {
  if (!country?.trim()) return null
  return COUNTRY_LANGUAGES[country.trim().toLowerCase()] || null
}

export default function ApplicationDetails({
  country,
  onCountryChange,
  language,
  onLanguageChange,
  isCitizen,
  onIsCitizenChange,
  companyName,
  onCompanyNameChange,
  roleTitle,
  onRoleTitleChange,
  hiringManagerName,
  onHiringManagerNameChange,
}) {
  const hasCountry = Boolean(country?.trim())
  const suggestedLang = suggestLanguage(country)

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
        Application details
      </h2>
      <p className="mt-1 text-sm text-slate-600">
        Optional context for personalization, company research, and language notes.
      </p>

      <div className="mt-4 grid gap-4 sm:grid-cols-2">
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Role title</span>
          <input
            type="text"
            value={roleTitle}
            onChange={(e) => onRoleTitleChange(e.target.value)}
            placeholder="e.g. Senior Software Engineer"
            className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-800 placeholder:text-slate-400 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-100"
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Hiring manager</span>
          <input
            type="text"
            value={hiringManagerName}
            onChange={(e) => onHiringManagerNameChange(e.target.value)}
            placeholder="e.g. Alex Smith"
            className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-800 placeholder:text-slate-400 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-100"
          />
        </label>
      </div>
      <p className="mt-1 text-xs text-slate-500">
        Used in the opening and salutation (Dear Alex Smith,).
      </p>

      <label className="mt-4 block">
        <span className="text-sm font-medium text-slate-700">Company name</span>
        <input
          type="text"
          value={companyName}
          onChange={(e) => onCompanyNameChange(e.target.value)}
          placeholder="e.g. Spotify, SAP, Revolut"
          className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-800 placeholder:text-slate-400 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-100"
        />
      </label>

      <label className="mt-4 block">
        <span className="text-sm font-medium text-slate-700">Country (optional)</span>
        <input
          type="text"
          value={country}
          onChange={(e) => onCountryChange(e.target.value)}
          placeholder="e.g. Germany, Japan, Canada"
          className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-800 placeholder:text-slate-400 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-100"
        />
      </label>

      <label className="mt-4 block">
        <span className="text-sm font-medium text-slate-700">Language (optional)</span>
        <input
          type="text"
          value={language}
          onChange={(e) => onLanguageChange(e.target.value)}
          placeholder="e.g. German, French, Japanese"
          className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-800 placeholder:text-slate-400 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-100"
        />
        {suggestedLang && !language?.trim() && (
          <button
            type="button"
            onClick={() => onLanguageChange(suggestedLang)}
            className="mt-2 rounded-full bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700 ring-1 ring-brand-100 hover:bg-brand-100"
          >
            Suggest: {suggestedLang}
          </button>
        )}
      </label>

      {hasCountry && (
        <label className="mt-4 flex cursor-pointer items-start gap-3 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3">
          <input
            type="checkbox"
            checked={isCitizen}
            onChange={(e) => onIsCitizenChange(e.target.checked)}
            className="mt-0.5 h-4 w-4 rounded border-slate-300 text-brand-600 focus:ring-brand-500"
          />
          <span>
            <span className="text-sm font-medium text-slate-800">
              I am a citizen of this country
            </span>
            <span className="mt-0.5 block text-xs text-slate-500">
              Skips language-learning and relocation notes.
            </span>
          </span>
        </label>
      )}
    </section>
  )
}
