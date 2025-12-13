"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export default function ManagerSubscribe() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleSubscribe = async () => {
    setLoading(true)
    setError("")

    try {
      const res = await fetch(`${API_URL}/api/manager/subscribe`, {
        method: "POST",
        credentials: "include"
      })

      const data = await res.json()

      if (!res.ok) {
        throw new Error(data.detail || "Subscription failed")
      }

      // Redirect to Paystack
      window.location.href = data.authorization_url

    } catch (err: any) {
      setError(err.message)
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white/5 border border-white/20 rounded-xl p-8">
        <h1 className="text-3xl font-bold text-white mb-2">Subscribe to Slotio</h1>
        <p className="text-white/60 mb-8">Activate your manager account to start adding team members</p>

        <div className="bg-white/10 rounded-xl p-6 mb-6">
          <div className="text-4xl font-bold text-primary mb-2">₦5,000</div>
          <div className="text-white/80">per month</div>
        </div>

        <div className="space-y-3 mb-8">
          <div className="flex items-start gap-3">
            <div className="w-6 h-6 rounded-full bg-primary/20 flex items-center justify-center mt-0.5">
              <div className="w-2 h-2 rounded-full bg-primary"></div>
            </div>
            <div className="text-white/80">Add up to 12 team members</div>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-6 h-6 rounded-full bg-primary/20 flex items-center justify-center mt-0.5">
              <div className="w-2 h-2 rounded-full bg-primary"></div>
            </div>
            <div className="text-white/80">Team members get free CapCut Pro access</div>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-6 h-6 rounded-full bg-primary/20 flex items-center justify-center mt-0.5">
              <div className="w-2 h-2 rounded-full bg-primary"></div>
            </div>
            <div className="text-white/80">Auto-renewal with saved card</div>
          </div>
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4 mb-6">
            <p className="text-red-400">{error}</p>
          </div>
        )}

        <button
          onClick={handleSubscribe}
          disabled={loading}
          className="w-full bg-primary text-background py-4 rounded-xl font-semibold text-lg hover:bg-primary/90 disabled:opacity-50"
        >
          {loading ? "Processing..." : "Subscribe Now"}
        </button>

        <p className="text-white/40 text-sm mt-4 text-center">
          Secure payment powered by Paystack
        </p>
      </div>
    </div>
  )
}
