'use client'
import { useState } from 'react'

interface PaystackButtonProps {
  amount: number  // In kobo
  email: string
  type: 'session' | 'subscription'
  onSuccess?: () => void
}

export default function PaystackButton({ amount, email, type, onSuccess }: PaystackButtonProps) {
  const [loading, setLoading] = useState(false)

  const initiate = async () => {
    setLoading(true)
    try {
      const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const res = await fetch(`${API_BASE}/api/payments/initialize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ amount, email, type })
      })

      const data = await res.json()
      
      if (data.authorization_url) {
        window.location.href = data.authorization_url
      }
    } catch (error) {
      console.error('Payment failed:', error)
      alert('Payment initialization failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <button
      onClick={initiate}
      disabled={loading}
      className="w-full bg-primary text-background px-6 py-3 rounded-xl font-semibold hover:bg-primary/90 disabled:opacity-50"
    >
      {loading ? 'Processing...' : `Pay ₦${amount / 100}`}
    </button>
  )
}
