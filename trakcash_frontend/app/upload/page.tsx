'use client'
import { useRouter } from 'next/navigation'
import { useState } from 'react'

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null)
  const router = useRouter()

  const handleUpload = async () => {
    // TODO: Upload file to backend / parse
    router.push('/categorize')
  }

  return (
    <div className="p-6">
      <h1 className="text-xl font-bold mb-4">Upload CSV</h1>
      <input type="file" accept=".csv" onChange={(e) => setFile(e.target.files?.[0] || null)} />
      <button onClick={handleUpload} className="mt-4 bg-green-600 text-white px-4 py-2 rounded">
        Next
      </button>
    </div>
  )
}