'use client'
import { Suspense } from 'react'
import { useEffect, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'

function VerifyContent() {
  const [status, setStatus] = useState<'verifying' | 'success' | 'error'>('verifying')
  const [message, setMessage] = useState('')
  const router = useRouter()
  const searchParams = useSearchParams()
  const token = searchParams.get('token')

  useEffect(() => {
    if (!token) {
      setStatus('error')
      setMessage('Invalid verification link')
      return
    }

    verifyToken()
  }, [token])

  const verifyToken = async () => {
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${API_BASE_URL}/api/auth/verify?token=${token}`, {
        credentials: 'include'
      })
      const data = await response.json()

      if (data.success) {
        setStatus('success')
        setMessage('Successfully signed in!')
        
        // Redirect based on user type and password change requirement
        setTimeout(() => {
          // Check if user needs to change password (for reset flow)
          if (data.user.must_change_password) {
            router.push('/auth/change-password')
          } else if (data.user.user_type === 'manager') {
            router.push('/manager/dashboard')
          } else if (data.user.user_type === 'team_member') {
            router.push('/team-member/dashboard')
          } else {
            router.push('/dashboard')
          }
        }, 1500)
      } else {
        setStatus('error')
        setMessage('Invalid or expired link')
      }
    } catch (error) {
      setStatus('error')
      setMessage('Verification failed')
    }
  }

  return (
    <div className="min-h-screen bg-background text-white flex items-center justify-center">
      <div className="text-center space-y-6">
        {status === 'verifying' && (
          <>
            <div className="text-6xl animate-spin">⭕</div>
            <h1 className="text-2xl font-semibold">Verifying...</h1>
          </>
        )}
        
        {status === 'success' && (
          <>
            <div className="text-6xl">✅</div>
            <h1 className="text-2xl font-semibold text-green-400">Success!</h1>
            <p className="text-white/60">{message}</p>
            <p className="text-sm text-white/40">Redirecting you now...</p>
          </>
        )}
        
        {status === 'error' && (
          <>
            <div className="text-6xl">❌</div>
            <h1 className="text-2xl font-semibold text-red-400">Error</h1>
            <p className="text-white/60">{message}</p>
            <button
              onClick={() => router.push('/')}
              className="mt-4 bg-primary text-background px-6 py-2 rounded-xl font-semibold hover:bg-primary/90 transition-colors"
            >
              Go Home
            </button>
          </>
        )}
      </div>
    </div>
  )
}

export default function VerifyPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-background text-white flex items-center justify-center">
        <div className="text-center space-y-6">
          <div className="text-6xl animate-spin">⭕</div>
          <h1 className="text-2xl font-semibold">Loading...</h1>
        </div>
      </div>
    }>
      <VerifyContent />
    </Suspense>
  )
}