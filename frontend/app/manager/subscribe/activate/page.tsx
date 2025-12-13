'use client'
import { useEffect, useState, Suspense } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

function SubscriptionActivateContent() {
  const [status, setStatus] = useState<'verifying' | 'success' | 'error'>('verifying')
  const searchParams = useSearchParams()
  const router = useRouter()
  const reference = searchParams.get('reference')

  useEffect(() => {
    if (reference) {
      verifySubscription()
    } else {
      setStatus('error')
    }
  }, [reference])

  const verifySubscription = async () => {
    try {
      const res = await fetch(`${API_URL}/api/payments/verify/${reference}`)
      const data = await res.json()

      if (data.status === 'success') {
        setStatus('success')
        setTimeout(() => {
          router.push('/manager/dashboard')
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
            <h1 className="text-2xl font-bold text-white">Activating Subscription...</h1>
          </>
        )}
        
        {status === 'success' && (
          <>
            <div className="text-6xl">✅</div>
            <h1 className="text-2xl font-bold text-green-400">Subscription Activated!</h1>
            <p className="text-white/60">Welcome to your manager account. Redirecting...</p>
          </>
        )}
        
        {status === 'error' && (
          <>
            <div className="text-6xl">❌</div>
            <h1 className="text-2xl font-bold text-red-400">Activation Failed</h1>
            <button
              onClick={() => router.push('/manager/subscribe')}
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

export default function SubscriptionActivatePage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-background flex items-center justify-center p-4">
        <div className="text-center space-y-4">
          <div className="text-6xl animate-spin">⭕</div>
          <h1 className="text-2xl font-bold text-white">Loading...</h1>
        </div>
      </div>
    }>
      <SubscriptionActivateContent />
    </Suspense>
  )
}