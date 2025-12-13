'use client'
import { useState } from 'react'

interface EmailCheckProps {
  onRouteDetected: (route: string, data: any) => void
}

export default function EmailCheck({ onRouteDetected }: EmailCheckProps) {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email) return

    setLoading(true)
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${API_BASE_URL}/api/auth/check-email`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      })
      
      const data = await response.json()
      onRouteDetected(data.route, { ...data, email })
    } catch (error) {
      console.error('Email check failed:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Enter your email"
          className="w-full px-4 py-3 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/60 focus:outline-none focus:border-primary"
          required
        />
      </div>
      
      <button
        type="submit"
        disabled={loading}
        className="w-full bg-primary text-background px-6 py-3 rounded-xl font-semibold hover:bg-primary/90 transition-colors disabled:opacity-50"
      >
        {loading ? 'Checking...' : 'Continue'}
      </button>
    </form>
  )
}