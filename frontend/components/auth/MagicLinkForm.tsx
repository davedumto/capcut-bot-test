'use client'
import { useState } from 'react'

interface MagicLinkFormProps {
  email: string
  name?: string
  marketingConsent?: boolean
  onSuccess: () => void
}

export default function MagicLinkForm({ email, name, marketingConsent, onSuccess }: MagicLinkFormProps) {
  const [loading, setLoading] = useState(false)
  const [sent, setSent] = useState(false)

  const sendMagicLink = async () => {
    setLoading(true)
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${API_BASE_URL}/api/auth/magic-link`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, name, marketing_consent: marketingConsent })
      })
      
      const data = await response.json()
      if (data.success) {
        setSent(true)
        onSuccess()
      }
    } catch (error) {
      console.error('Failed to send magic link:', error)
    } finally {
      setLoading(false)
    }
  }

  if (sent) {
    return (
      <div className="text-center space-y-4">
        <div className="text-6xl">📧</div>
        <h3 className="text-xl font-semibold">Check your email!</h3>
        <p className="text-white/60">
          We sent a magic link to <span className="text-primary">{email}</span>
        </p>
        <p className="text-sm text-white/40">
          The link expires in 15 minutes
        </p>
      </div>
    )
  }

  return (
    <div className="text-center space-y-4">
      <h3 className="text-xl font-semibold">Sign in to continue</h3>
      <p className="text-white/60">
        We'll send a magic link to <span className="text-primary">{email}</span>
      </p>
      
      <button
        onClick={sendMagicLink}
        disabled={loading}
        className="w-full bg-primary text-background px-6 py-3 rounded-xl font-semibold hover:bg-primary/90 transition-colors disabled:opacity-50"
      >
        {loading ? 'Sending...' : 'Send Magic Link'}
      </button>
    </div>
  )
}