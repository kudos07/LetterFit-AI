const STORAGE_KEY = 'letterfit-ai-session'

const PERSISTED_KEYS = [
  'resumeText',
  'resumeFilename',
  'jobDescription',
  'letterStyle',
  'letterLength',
  'country',
  'language',
  'isCitizen',
  'roleTitle',
  'hiringManagerName',
  'companyName',
  'softSkills',
  'compareStyleA',
  'compareStyleB',
  'coverLetter',
]

export function loadFormSession() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return null
    const data = JSON.parse(raw)
    return typeof data === 'object' && data !== null ? data : null
  } catch {
    return null
  }
}

export function saveFormSession(state) {
  try {
    const payload = {}
    for (const key of PERSISTED_KEYS) {
      if (state[key] !== undefined) payload[key] = state[key]
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(payload))
  } catch {
    // ignore quota or private browsing errors
  }
}

export function clearFormSession() {
  try {
    localStorage.removeItem(STORAGE_KEY)
  } catch {
    // ignore
  }
}
