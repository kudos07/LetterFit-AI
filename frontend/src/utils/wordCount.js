import { parseCoverLetter } from './letterParser.js'

export function countBodyWords(text) {
  if (!text?.trim()) return 0
  const parts = parseCoverLetter(text)
  const body = [parts.opening, parts.proof, parts.soft_skills, parts.close]
    .filter(Boolean)
    .join(' ')
  return body.split(/\s+/).filter(Boolean).length
}

export function lengthLimits(letterLength) {
  if (letterLength === 'standard') {
    return { target: 250, warn: 280, max: 300 }
  }
  return { target: 175, warn: 200, max: 220 }
}
