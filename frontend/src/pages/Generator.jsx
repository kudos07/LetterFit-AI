import { useCallback, useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import ResumeUpload from '../components/ResumeUpload.jsx'
import JobDescriptionInput from '../components/JobDescriptionInput.jsx'
import StyleSelector from '../components/StyleSelector.jsx'
import StyleCompare from '../components/StyleCompare.jsx'
import ApplicationDetails from '../components/ApplicationDetails.jsx'
import SoftSkillsSelector, { DEFAULT_SELECTED } from '../components/SoftSkillsSelector.jsx'
import CoverLetterEditor from '../components/CoverLetterEditor.jsx'
import QualityPanel from '../components/QualityPanel.jsx'
import CompanyResearchPanel from '../components/CompanyResearchPanel.jsx'
import GenerationProgress from '../components/GenerationProgress.jsx'
import { useGenerationProgress } from '../hooks/useGenerationProgress.js'
import { loadFormSession, saveFormSession } from '../utils/formPersistence.js'
import {
  exportDocx,
  exportPdf,
  fetchStyles,
  compareStyles,
  generateCoverLetter,
  regenerateParagraph,
} from '../api/client.js'

const SAMPLE_JOB = `Senior Software Engineer - Amsterdam, Europe (Hybrid)

We are looking for a Senior Software Engineer to join our platform team building scalable B2B SaaS products.

Requirements:
- 5+ years of experience with Python and TypeScript
- Strong experience with React, FastAPI, and PostgreSQL
- Experience designing REST APIs and microservices
- Familiarity with AWS, Docker, and CI/CD pipelines
- Experience with Agile/Scrum in cross-functional teams
- Excellent communication skills in English; additional European languages are a plus

Nice to have:
- Experience with event-driven architectures (Kafka)
- Prior work in fintech or regulated industries
- Contributions to open source

What we offer:
- Competitive salary and 30 days holiday
- Hybrid work (2 days in office)
- Learning budget and conference attendance`

const FALLBACK_STYLES = ['Professional', 'Qualifications', 'Hype', 'Mix', 'Bold']

function getInitialState() {
  const saved = loadFormSession()
  if (!saved) {
    return {
      resumeText: '',
      resumeFilename: '',
      jobDescription: '',
      letterStyle: 'Professional',
      letterLength: 'short',
      country: '',
      language: '',
      isCitizen: false,
      roleTitle: '',
      hiringManagerName: '',
      companyName: '',
      softSkills: DEFAULT_SELECTED,
      compareStyleA: 'Professional',
      compareStyleB: 'Bold',
      coverLetter: '',
    }
  }
  return {
    resumeText: saved.resumeText || '',
    resumeFilename: saved.resumeFilename || '',
    jobDescription: saved.jobDescription || '',
    letterStyle: saved.letterStyle || 'Professional',
    letterLength: saved.letterLength || 'short',
    country: saved.country || '',
    language: saved.language || '',
    isCitizen: Boolean(saved.isCitizen),
    roleTitle: saved.roleTitle || '',
    hiringManagerName: saved.hiringManagerName || '',
    companyName: saved.companyName || '',
    softSkills: saved.softSkills?.length ? saved.softSkills : DEFAULT_SELECTED,
    compareStyleA: saved.compareStyleA || 'Professional',
    compareStyleB: saved.compareStyleB || 'Bold',
    coverLetter: saved.coverLetter || '',
  }
}

export default function Generator() {
  const initial = useRef(getInitialState()).current
  const [styles, setStyles] = useState(FALLBACK_STYLES)
  const [presets, setPresets] = useState([])
  const [resumeText, setResumeText] = useState(initial.resumeText)
  const [resumeFilename, setResumeFilename] = useState(initial.resumeFilename)
  const [jobDescription, setJobDescription] = useState(initial.jobDescription)
  const [letterStyle, setLetterStyle] = useState(initial.letterStyle)
  const [letterLength, setLetterLength] = useState(initial.letterLength)
  const [country, setCountry] = useState(initial.country)
  const [language, setLanguage] = useState(initial.language)
  const [isCitizen, setIsCitizen] = useState(initial.isCitizen)
  const [roleTitle, setRoleTitle] = useState(initial.roleTitle)
  const [hiringManagerName, setHiringManagerName] = useState(initial.hiringManagerName)
  const [companyName, setCompanyName] = useState(initial.companyName)
  const [softSkills, setSoftSkills] = useState(initial.softSkills)
  const [customSoftSkill, setCustomSoftSkill] = useState('')
  const [coverLetter, setCoverLetter] = useState(initial.coverLetter)
  const [qualityAnalysis, setQualityAnalysis] = useState(null)
  const [companyResearch, setCompanyResearch] = useState(null)
  const [loading, setLoading] = useState(false)
  const [paragraphLoading, setParagraphLoading] = useState(false)
  const [addressingSkill, setAddressingSkill] = useState(null)
  const [compareStyleA, setCompareStyleA] = useState(initial.compareStyleA)
  const [compareStyleB, setCompareStyleB] = useState(initial.compareStyleB)
  const [compareResults, setCompareResults] = useState(null)
  const [compareQuality, setCompareQuality] = useState(null)
  const [compareTab, setCompareTab] = useState('Professional')
  const [comparing, setComparing] = useState(false)
  const [uploadLoading, setUploadLoading] = useState(false)
  const [exportLoading, setExportLoading] = useState(false)
  const [exportPdfLoading, setExportPdfLoading] = useState(false)
  const [copySuccess, setCopySuccess] = useState(false)
  const [error, setError] = useState('')

  const generateProgress = useGenerationProgress(loading, {
    hasCompany: Boolean(companyName.trim()),
  })
  const compareProgress = useGenerationProgress(comparing, {
    hasCompany: Boolean(companyName.trim()),
  })

  useEffect(() => {
    saveFormSession({
      resumeText,
      resumeFilename,
      jobDescription,
      letterStyle,
      letterLength,
      country,
      language,
      isCitizen,
      roleTitle,
      hiringManagerName,
      companyName,
      softSkills,
      compareStyleA,
      compareStyleB,
      coverLetter,
    })
  }, [
    resumeText,
    resumeFilename,
    jobDescription,
    letterStyle,
    letterLength,
    country,
    language,
    isCitizen,
    roleTitle,
    hiringManagerName,
    companyName,
    softSkills,
    compareStyleA,
    compareStyleB,
    coverLetter,
  ])

  useEffect(() => {
    fetchStyles()
      .then(({ styles: list, presets: info }) => {
        setStyles(list.length ? list : FALLBACK_STYLES)
        setPresets(info)
      })
      .catch(() => {
        setStyles(FALLBACK_STYLES)
        setPresets([])
      })
  }, [])

  const handleResumeParsed = useCallback(({ text, filename }) => {
    setResumeText(text)
    setResumeFilename(filename)
    setError('')
  }, [])

  const buildGeneratePayload = (overrides = {}) => ({
    resumeText,
    jobDescription,
    letterStyle,
    letterLength,
    country,
    language,
    isCitizen,
    roleTitle,
    hiringManagerName,
    companyName,
    softSkills,
    ...overrides,
  })

  const handleGenerate = async (overrides = {}) => {
    if (!resumeText.trim()) {
      setError('Please upload a resume first.')
      return
    }
    if (!jobDescription.trim()) {
      setError('Please paste a job description.')
      return
    }

    setLoading(true)
    setError('')
    setCopySuccess(false)
    if (companyName.trim()) setCompanyResearch(null)

    try {
      const result = await generateCoverLetter(buildGeneratePayload(overrides))
      setCoverLetter(result.cover_letter)
      setQualityAnalysis(result.quality_analysis)
      setCompanyResearch(result.company_research || null)
      if (overrides.letterStyle) setLetterStyle(overrides.letterStyle)
    } catch (err) {
      setError(err.message || 'Failed to generate cover letter.')
    } finally {
      setLoading(false)
    }
  }

  const handleRegenerateParagraph = async (paragraph, focusSkill) => {
    if (!coverLetter.trim()) return
    setParagraphLoading(true)
    setError('')
    try {
      const result = await regenerateParagraph({
        paragraph,
        coverLetter,
        focusSkill,
        ...buildGeneratePayload(),
      })
      setCoverLetter(result.cover_letter)
    } catch (err) {
      setError(err.message || 'Failed to regenerate paragraph.')
    } finally {
      setParagraphLoading(false)
      setAddressingSkill(null)
    }
  }

  const handleAddressSkill = async (skill) => {
    setAddressingSkill(skill)
    await handleRegenerateParagraph('proof', skill)
  }

  const handleCompare = async () => {
    if (!resumeText.trim() || !jobDescription.trim()) {
      setError('Upload a resume and paste a job description first.')
      return
    }
    if (compareStyleA === compareStyleB) {
      setError('Pick two different styles to compare.')
      return
    }

    setComparing(true)
    setError('')
    try {
      const base = buildGeneratePayload()
      const result = await compareStyles({
        ...base,
        styleA: compareStyleA,
        styleB: compareStyleB,
      })
      setCompareResults(result.letters)
      setCompareQuality(result.quality_analysis || null)
      setCompareTab(compareStyleA)
    } catch (err) {
      setError(err.message || 'Failed to compare styles.')
    } finally {
      setComparing(false)
    }
  }

  const handleUseComparedLetter = (letter, style) => {
    setCoverLetter(letter)
    setLetterStyle(style)
    if (compareQuality?.[style]) setQualityAnalysis(compareQuality[style])
    setError('')
  }

  const handleCopy = async () => {
    if (!coverLetter) return
    try {
      await navigator.clipboard.writeText(coverLetter)
      setCopySuccess(true)
      setTimeout(() => setCopySuccess(false), 2000)
    } catch {
      setError('Could not copy to clipboard.')
    }
  }

  const exportBasename = () => {
    const parts = [letterStyle]
    if (country.trim()) parts.push(country.trim())
    return parts.join('_').replace(/\s+/g, '_').toLowerCase()
  }

  const handleExport = async () => {
    if (!coverLetter) return
    setExportLoading(true)
    setError('')
    try {
      await exportDocx(coverLetter, `cover_letter_${exportBasename()}.docx`)
    } catch (err) {
      setError(err.message || 'Failed to export DOCX.')
    } finally {
      setExportLoading(false)
    }
  }

  const handleExportPdf = async () => {
    if (!coverLetter) return
    setExportPdfLoading(true)
    setError('')
    try {
      await exportPdf(coverLetter, `cover_letter_${exportBasename()}.pdf`)
    } catch (err) {
      setError(err.message || 'Failed to export PDF.')
    } finally {
      setExportPdfLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <Link to="/" className="text-sm font-semibold text-brand-600 hover:text-brand-700">
            ← LetterFit AI
          </Link>
          <span className="text-sm text-slate-500">Generator</span>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-slate-900">Cover letter generator</h1>
          <p className="mt-1 text-slate-600">
            Pick a tone, set length, and optionally add role, manager, country, and language.
          </p>
        </div>

        {error && (
          <div className="mb-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}

        <div className="grid gap-8 lg:grid-cols-2">
          <div className="space-y-6">
            <ResumeUpload
              onParsed={handleResumeParsed}
              uploadLoading={uploadLoading}
              setUploadLoading={setUploadLoading}
              setError={setError}
              resumeFilename={resumeFilename}
            />
            <JobDescriptionInput
              value={jobDescription}
              onChange={setJobDescription}
              onLoadSample={() => setJobDescription(SAMPLE_JOB)}
            />
            <StyleSelector
              styles={styles}
              presets={presets}
              value={letterStyle}
              onChange={setLetterStyle}
              letterLength={letterLength}
              onLetterLengthChange={setLetterLength}
            />
            <ApplicationDetails
              country={country}
              onCountryChange={(v) => {
                setCountry(v)
                if (!v.trim()) setIsCitizen(false)
              }}
              language={language}
              onLanguageChange={setLanguage}
              isCitizen={isCitizen}
              onIsCitizenChange={setIsCitizen}
              companyName={companyName}
              onCompanyNameChange={setCompanyName}
              roleTitle={roleTitle}
              onRoleTitleChange={setRoleTitle}
              hiringManagerName={hiringManagerName}
              onHiringManagerNameChange={setHiringManagerName}
            />
            <SoftSkillsSelector
              selected={softSkills}
              onChange={setSoftSkills}
              customSkill={customSoftSkill}
              onCustomSkillChange={setCustomSoftSkill}
            />
            <button
              type="button"
              onClick={() => handleGenerate()}
              disabled={loading}
              className="w-full rounded-xl bg-brand-600 px-6 py-3.5 font-semibold text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading
                ? 'Generating…'
                : coverLetter
                  ? 'Regenerate cover letter'
                  : 'Generate cover letter'}
            </button>
            {loading && (
              <GenerationProgress
                steps={generateProgress.steps}
                stepIndex={generateProgress.stepIndex}
              />
            )}
          </div>

          <div className="space-y-6">
            <CoverLetterEditor
              value={coverLetter}
              onChange={setCoverLetter}
              onCopy={handleCopy}
              onRegenerate={() => handleGenerate()}
              onRegenerateParagraph={handleRegenerateParagraph}
              onExport={handleExport}
              onExportPdf={handleExportPdf}
              loading={loading}
              paragraphLoading={paragraphLoading}
              exportLoading={exportLoading}
              exportPdfLoading={exportPdfLoading}
              copySuccess={copySuccess}
              letterLength={letterLength}
            />
            {comparing && (
              <GenerationProgress
                steps={compareProgress.steps}
                stepIndex={compareProgress.stepIndex}
                title="Comparing styles"
              />
            )}
            <StyleCompare
              styles={styles}
              styleA={compareStyleA}
              styleB={compareStyleB}
              onStyleAChange={setCompareStyleA}
              onStyleBChange={setCompareStyleB}
              onCompare={handleCompare}
              comparing={comparing}
              results={compareResults}
              qualityResults={compareQuality}
              activeTab={compareTab}
              onActiveTabChange={setCompareTab}
              onUseLetter={handleUseComparedLetter}
            />
            <CompanyResearchPanel
              research={companyResearch}
              loading={loading}
              companyName={companyName}
            />
            <QualityPanel
              analysis={qualityAnalysis}
              loading={loading}
              onAddressSkill={handleAddressSkill}
              addressingSkill={addressingSkill}
              hasCoverLetter={Boolean(coverLetter.trim())}
            />
          </div>
        </div>
      </main>
    </div>
  )
}
