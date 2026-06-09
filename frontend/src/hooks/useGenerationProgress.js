import { useEffect, useRef, useState } from 'react'

const BASE_STEPS = [
  { id: 'evidence', label: 'Selecting resume evidence' },
  { id: 'writing', label: 'Writing cover letter' },
  { id: 'quality', label: 'Running quality analysis' },
]

const RESEARCH_STEP = { id: 'research', label: 'Researching company' }

function buildSteps(hasCompany) {
  if (!hasCompany) return BASE_STEPS
  return [BASE_STEPS[0], RESEARCH_STEP, BASE_STEPS[1], BASE_STEPS[2]]
}

export function useGenerationProgress(active, { hasCompany = false } = {}) {
  const steps = buildSteps(hasCompany)
  const [stepIndex, setStepIndex] = useState(0)
  const timersRef = useRef([])

  const clearTimers = () => {
    timersRef.current.forEach(clearTimeout)
    timersRef.current = []
  }

  useEffect(() => {
    if (!active) {
      clearTimers()
      setStepIndex(0)
      return undefined
    }

    setStepIndex(0)
    const delays = hasCompany ? [0, 2200, 5000, 8500] : [0, 2800, 6500]
    delays.forEach((delay, idx) => {
      if (idx === 0) return
      const timer = setTimeout(() => setStepIndex(idx), delay)
      timersRef.current.push(timer)
    })

    return clearTimers
  }, [active, hasCompany])

  const currentStep = steps[Math.min(stepIndex, steps.length - 1)]

  return { steps, stepIndex, currentStep }
}
