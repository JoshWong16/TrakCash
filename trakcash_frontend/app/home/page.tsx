'use client'
import { useRouter } from 'next/navigation'

export default function HomePage() {
  const router = useRouter()

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Your Expenses</h1>
      <button
        onClick={() => router.push('/upload')}
        className="bg-blue-600 text-white px-4 py-2 rounded"
      >
        Add More Data
      </button>

      {/* TODO: Render transaction summary here */}
    </div>
  )
}