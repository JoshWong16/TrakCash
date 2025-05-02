'use client'
import { useRouter } from 'next/navigation'

export default function CategorizePage() {
  const router = useRouter()

  const handleSubmit = () => {
    // TODO: Save categorization results
    router.push('/home')
  }

  return (
    <div className="p-6">
      <h1 className="text-xl font-bold mb-4">Categorize Transactions</h1>
      {/* TODO: Render transactions and allow user to categorize */}
      <button onClick={handleSubmit} className="mt-4 bg-blue-600 text-white px-4 py-2 rounded">
        Finish
      </button>
    </div>
  )
}