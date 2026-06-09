const API_BASE = import.meta.env.VITE_API_URL || '/api'

async function handleResponse(response) {
  if (!response.ok) {
    let message = `Request failed (${response.status})`
    try {
      const data = await response.json()
      message = data.detail || data.message || message
      if (Array.isArray(message)) {
        message = message.map((e) => e.msg || JSON.stringify(e)).join(', ')
      }
    } catch {
      // keep default message
    }
    throw new Error(message)
  }
  return response
}

function buildLetterBody({
  resumeText,
  jobDescription,
  letterStyle,
  letterLength,
  country,
  language,
  isCitizen,
  companyName,
  roleTitle,
  hiringManagerName,
  softSkills,
  focusSkill,
  paragraph,
  coverLetter,
}) {
  const body = {
    resume_text: resumeText,
    job_description: jobDescription,
    letter_style: letterStyle,
    letter_length: letterLength || 'short',
  }
  if (country?.trim()) body.country = country.trim()
  if (language?.trim()) body.language = language.trim()
  if (country?.trim()) body.is_citizen = Boolean(isCitizen)
  if (companyName?.trim()) body.company_name = companyName.trim()
  if (roleTitle?.trim()) body.role_title = roleTitle.trim()
  if (hiringManagerName?.trim()) body.hiring_manager_name = hiringManagerName.trim()
  if (softSkills?.length) body.soft_skills = softSkills
  if (paragraph) body.paragraph = paragraph
  if (coverLetter) body.cover_letter = coverLetter
  if (focusSkill?.trim()) body.focus_skill = focusSkill.trim()
  return body
}

export async function uploadResume(file) {
  const formData = new FormData()
  formData.append('file', file)
  const response = await fetch(`${API_BASE}/upload-resume`, {
    method: 'POST',
    body: formData,
  })
  await handleResponse(response)
  return response.json()
}

export async function generateCoverLetter(payload) {
  const body = buildLetterBody(payload)
  const response = await fetch(`${API_BASE}/generate-cover-letter`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  await handleResponse(response)
  return response.json()
}

export async function compareStyles(payload) {
  const body = buildLetterBody(payload)
  body.style_a = payload.styleA
  body.style_b = payload.styleB
  const response = await fetch(`${API_BASE}/compare-styles`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  await handleResponse(response)
  return response.json()
}

async function downloadBlob(response, filename) {
  const blob = await response.blob()
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}

export async function regenerateParagraph(payload) {
  const body = buildLetterBody(payload)
  const response = await fetch(`${API_BASE}/regenerate-paragraph`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  await handleResponse(response)
  return response.json()
}

export async function exportDocx(coverLetter, filename = 'cover_letter.docx') {
  const response = await fetch(`${API_BASE}/export-docx`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ cover_letter: coverLetter, filename }),
  })
  await handleResponse(response)
  const name = filename.endsWith('.docx') ? filename : `${filename}.docx`
  await downloadBlob(response, name)
}

export async function exportPdf(coverLetter, filename = 'cover_letter.pdf') {
  const response = await fetch(`${API_BASE}/export-pdf`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ cover_letter: coverLetter, filename }),
  })
  await handleResponse(response)
  const name = filename.endsWith('.pdf') ? filename : `${filename}.pdf`
  await downloadBlob(response, name)
}

export async function fetchStyles() {
  const response = await fetch(`${API_BASE}/styles`)
  await handleResponse(response)
  const data = await response.json()
  return { styles: data.styles || [], presets: data.presets || [] }
}
