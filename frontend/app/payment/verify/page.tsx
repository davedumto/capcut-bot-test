'use client'
import { useEffect, useState, Suspense } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'

function PaymentVerifyContent() {
  const [status, setStatus] = useState<'verifying' | 'success' | 'error'>('verifying')
  const searchParams = useSearchParams()
  const router = useRouter()
  const reference = searchParams.get('reference')

  useEffect(() => {
    if (reference) {
      verifyPayment()
    } else {
      setStatus('error')
    }
  }, [reference])

  const verifyPayment = async () => {
    try {
      const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const res = await fetch(`${API_BASE}/api/payments/verify/${reference}`)
      const data = await res.json()

      if (data.status === 'success') {
        setStatus('success')
        // Redirect to dashboard after successful payment
        setTimeout(() => {
          router.push('/dashboard')
        }, 2000)
      } else {
        setStatus('error')
      }
    } catch (error) {
      setStatus('error')
    }
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="text-center space-y-4">
        {status === 'verifying' && (
          <>
            <div className="text-6xl animate-spin">⭕</div>
            <h1 className="text-2xl font-bold text-white">Verifying Payment...</h1>
          </>
        )}
        
        {status === 'success' && (
          <>
            <div className="text-6xl">✅</div>
            <h1 className="text-2xl font-bold text-green-400">Payment Successful!</h1>
            <p className="text-white/60">Redirecting to complete booking...</p>
          </>
        )}
        
        {status === 'error' && (
          <>
            <div className="text-6xl">❌</div>
            <h1 className="text-2xl font-bold text-red-400">Payment Failed</h1>
            <button
              onClick={() => router.push('/book-slot')}
              className="bg-primary text-background px-6 py-2 rounded-xl font-semibold"
            >
              Try Again
            </button>
          </>
        )}
      </div>
    </div>
  )
}

export default function PaymentVerifyPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-background flex items-center justify-center p-4">
        <div className="text-center space-y-4">
          <div className="text-6xl animate-spin">⭕</div>
          <h1 className="text-2xl font-bold text-white">Loading...</h1>
        </div>
      </div>
    }>
      <PaymentVerifyContent />
    </Suspense>
  )
}
