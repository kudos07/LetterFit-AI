const CLOSING_PREFIXES = [
  'yours sincerely',
  'yours faithfully',
  'kind regards',
  'best regards',
  'warm regards',
  'sincerely',
  'regards',
]

function isSalutation(text) {
  return text.toLowerCase().startsWith('dear ')
}

function isClosingLine(text) {
  const lower = text.toLowerCase().replace(/,$/, '')
  return CLOSING_PREFIXES.some((p) => lower.startsWith(p))
}

function looksLikeSignature(text) {
  if (!text || text.length > 80) return false
  if (text.endsWith('.')) return false
  return !text.includes('\n')
}

function splitClosingBlock(text) {
  const lines = text.split('\n').map((l) => l.trim()).filter(Boolean)
  if (!lines.length) return { closingLine: '', signature: '' }
  if (isClosingLine(lines[0])) {
    return { closingLine: lines[0], signature: lines[1] || '' }
  }
  return { closingLine: '', signature: text }
}

export function parseCoverLetter(text) {
  const paragraphs = text
    .trim()
    .split(/\n\s*\n/)
    .map((p) => p.trim())
    .filter(Boolean)

  let salutation = ''
  let closingLine = ''
  let signature = ''
  const rest = [...paragraphs]

  if (rest.length && isSalutation(rest[0])) {
    salutation = rest.shift()
  }

  if (rest.length) {
    const last = rest[rest.length - 1]
    if (
      isClosingLine(last) ||
      (last.includes('\n') && isClosingLine(last.split('\n')[0].trim()))
    ) {
      const split = splitClosingBlock(last)
      closingLine = split.closingLine
      signature = split.signature
      rest.pop()
    } else if (looksLikeSignature(last)) {
      signature = rest.pop()
      if (rest.length && isClosingLine(rest[rest.length - 1])) {
        closingLine = rest.pop()
      }
    }
  }

  const body = rest
  let opening = body[0] || ''
  let proof = body[1] || ''
  let softSkills = body[2] || ''
  let close = body[3] || ''

  if (body.length === 3) {
    softSkills = body[2]
    close = ''
  } else if (body.length === 2) {
    softSkills = ''
    close = ''
  }

  return { salutation, opening, proof, soft_skills: softSkills, close, closing_line: closingLine, signature }
}

export function mergeCoverLetter(parts) {
  const blocks = []
  if (parts.salutation?.trim()) blocks.push(parts.salutation.trim())
  for (const key of ['opening', 'proof', 'soft_skills', 'close']) {
    if (parts[key]?.trim()) blocks.push(parts[key].trim())
  }
  if (parts.closing_line?.trim()) blocks.push(parts.closing_line.trim())
  if (parts.signature?.trim()) blocks.push(parts.signature.trim())
  return blocks.join('\n\n')
}

export const SECTION_LABELS = {
  opening: 'Opening',
  proof: 'Proof',
  soft_skills: 'Work style',
  close: 'Close',
}
