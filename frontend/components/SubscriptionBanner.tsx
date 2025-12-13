"use client"

import { useEffect, useState } from "react"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

interface SubscriptionStatus {
  status: string
  expires_at: string | null
  days_remaining: number | null
}

export default function SubscriptionBanner() {
  const [subscription, setSubscription] = useState<SubscriptionStatus | null>(null)

  useEffect(() => {
    fetchStatus()
  }, [])

  const fetchStatus = async () => {
    try {
      const res = await fetch(`${API_URL}/api/manager/subscription/status`, {
        credentials: "include"
      })
      if (res.ok) {
        const data = await res.json()
        setSubscription(data)
      }
    } catch (err) {
      console.error("Failed to fetch subscription:", err)
    }
  }

  if (!subscription || subscription.status === 'active' && (subscription.days_remaining || 0) > 7) {
    return null
  }

  if (subscription.status === 'expired') {
    return (
      <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-red-400 font-semibold">Subscription Expired</h3>
            <p className="text-white/60 text-sm">Your team members cannot book sessions until you renew</p>
          </div>
          <a
            href="/manager/subscribe"
            className="bg-red-500 text-white px-4 py-2 rounded-lg font-medium hover:bg-red-600"
          >
            Renew Now
          </a>
        </div>
      </div>
    )
  }

  if (subscription.status === 'active' && (subscription.days_remaining || 0) <= 7) {
    return (
      <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-xl p-4 mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-yellow-400 font-semibold">Subscription Expiring Soon</h3>
            <p className="text-white/60 text-sm">
              {subscription.days_remaining} days remaining - Auto-renewal on {new Date(subscription.expires_at!).toLocaleDateString()}
            </p>
          </div>
        </div>
      </div>
    )
  }

  return null
}
