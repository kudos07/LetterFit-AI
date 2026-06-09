import { Link } from 'react-router-dom'

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-indigo-50/30 to-slate-100">
      <header className="mx-auto flex max-w-5xl items-center justify-between px-6 py-6">
        <span className="text-sm font-semibold tracking-wide text-brand-600">
          LetterFit AI
        </span>
      </header>

      <main className="mx-auto flex max-w-5xl flex-col items-center px-6 pb-24 pt-16 text-center">
        <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-indigo-200 bg-white/80 px-4 py-1.5 text-sm text-indigo-700 shadow-sm">
          <span className="h-2 w-2 rounded-full bg-brand-500" />
          Built for global tech hiring
        </div>

        <h1 className="max-w-3xl text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
          AI cover letters in the{' '}
          <span className="text-brand-600">tone you choose</span>
        </h1>

        <p className="mt-6 max-w-2xl text-lg leading-relaxed text-slate-600">
          Upload your resume, paste a job description, pick a style from professional to bold,
          and optionally add country and language context. Powered by Mistral AI.
        </p>

        <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
          <Link
            to="/generator"
            className="rounded-xl bg-brand-600 px-8 py-3.5 text-base font-semibold text-white shadow-lg shadow-indigo-200 transition hover:bg-brand-700"
          >
            Start generating
          </Link>
        </div>

        <div className="mt-20 grid w-full max-w-3xl gap-4 text-left sm:grid-cols-3">
          {[
            { title: 'Tone presets', desc: 'Professional, qualifications, hype, mix, or bold. You control the voice.' },
            { title: 'ATS analysis', desc: 'Keyword match, missing skills, and strongest resume alignments.' },
            { title: 'Export ready', desc: 'Edit, copy, regenerate, or download as DOCX.' },
          ].map((item) => (
            <div
              key={item.title}
              className="rounded-2xl border border-slate-200/80 bg-white/70 p-5 shadow-sm backdrop-blur"
            >
              <h3 className="font-semibold text-slate-900">{item.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-slate-600">{item.desc}</p>
            </div>
          ))}
        </div>
      </main>
    </div>
  )
}
