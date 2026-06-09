import { useRef } from 'react'
import { uploadResume } from '../api/client.js'

export default function ResumeUpload({
  onParsed,
  uploadLoading,
  setUploadLoading,
  setError,
  resumeFilename,
}) {
  const inputRef = useRef(null)

  const handleFile = async (file) => {
    if (!file) return

    const ext = file.name.split('.').pop()?.toLowerCase()
    if (!['pdf', 'docx'].includes(ext)) {
      setError('Only PDF and DOCX files are supported.')
      return
    }

    setUploadLoading(true)
    setError('')

    try {
      const result = await uploadResume(file)
      onParsed({ text: result.resume_text, filename: result.filename })
    } catch (err) {
      setError(err.message || 'Failed to upload resume.')
    } finally {
      setUploadLoading(false)
    }
  }

  const onDrop = (e) => {
    e.preventDefault()
    const file = e.dataTransfer.files?.[0]
    handleFile(file)
  }

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
        Resume
      </h2>
      <p className="mt-1 text-sm text-slate-600">
        Upload PDF or DOCX. Try the sample in{' '}
        <code className="rounded bg-slate-100 px-1.5 py-0.5 text-xs">samples/sample_resume.docx</code>
      </p>

      <div
        onDragOver={(e) => e.preventDefault()}
        onDrop={onDrop}
        className="mt-4 flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-200 bg-slate-50/50 px-4 py-8 transition hover:border-brand-300 hover:bg-brand-50/30"
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          className="hidden"
          onChange={(e) => handleFile(e.target.files?.[0])}
        />

        {uploadLoading ? (
          <p className="text-sm text-slate-600">Extracting text…</p>
        ) : resumeFilename ? (
          <div className="text-center">
            <p className="font-medium text-slate-900">{resumeFilename}</p>
            <p className="mt-1 text-sm text-green-600">Resume parsed successfully</p>
            <button
              type="button"
              onClick={() => inputRef.current?.click()}
              className="mt-3 text-sm font-medium text-brand-600 hover:text-brand-700"
            >
              Replace file
            </button>
          </div>
        ) : (
          <>
            <p className="text-sm text-slate-600">Drag & drop or</p>
            <button
              type="button"
              onClick={() => inputRef.current?.click()}
              className="mt-2 rounded-lg bg-white px-4 py-2 text-sm font-medium text-brand-600 shadow-sm ring-1 ring-slate-200 hover:bg-slate-50"
            >
              Choose file
            </button>
          </>
        )}
      </div>
    </section>
  )
}
