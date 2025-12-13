'use client'
import { useEffect, useState } from 'react'

interface UserProfile {
  name: string
  email: string
  user_type: string
  total_sessions: number
  total_hours: string
  marketing_consent: boolean
}

interface Payment {
  id: number
  amount: number
  status: string
  created_at: string
  reference: string
}

export default function UserDashboard() {
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [payments, setPayments] = useState<Payment[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchProfile()
    fetchPayments()
  }, [])

  const fetchProfile = async () => {
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${API_BASE_URL}/api/users/profile`, {
        credentials: 'include'
      })
      if (response.ok) {
        const data = await response.json()
        setProfile(data)
      }
    } catch (error) {
      console.error('Failed to fetch profile:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchPayments = async () => {
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${API_BASE_URL}/api/payments/history`, {
        credentials: 'include'
      })
      if (response.ok) {
        const data = await response.json()
        setPayments(data.payments || [])
      }
    } catch (error) {
      console.error('Failed to fetch payments:', error)
    }
  }

  const handleLogout = async () => {
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      await fetch(`${API_BASE_URL}/api/auth/logout`, {
        method: 'POST',
        credentials: 'include'
      })
      window.location.href = '/auth'
    } catch (error) {
      console.error('Logout failed:', error)
      // Still redirect even if API call fails
      window.location.href = '/auth'
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
  }

  if (loading) {
    return <div className="text-center py-8">Loading...</div>
  }

  if (!profile) {
    return <div className="text-center py-8">Please log in to view your dashboard.</div>
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Greeting */}
      <div className="bg-background border rounded-xl p-6">
        <div className="flex items-center justify-between mb-2">
          <h1 className="text-2xl font-semibold text-white">
            Welcome back, {profile.name}! 👋
          </h1>
          <button
            onClick={handleLogout}
            className="px-4 py-2 border border-white/20 text-white text-sm rounded-lg hover:bg-white/5 transition-colors"
          >
            Logout
          </button>
        </div>
        <p className="text-white/60">{profile.email}</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-background border rounded-xl p-6">
          <h3 className="text-lg font-medium text-white mb-2">Total Sessions</h3>
          <p className="text-3xl font-bold text-primary">{profile.total_sessions}</p>
        </div>
        
        <div className="bg-background border rounded-xl p-6">
          <h3 className="text-lg font-medium text-white mb-2">Total Hours</h3>
          <p className="text-3xl font-bold text-primary">{profile.total_hours}</p>
        </div>
        
        <div className="bg-background border rounded-xl p-6">
          <h3 className="text-lg font-medium text-white mb-2">Account Type</h3>
          <p className="text-lg capitalize text-white">{profile.user_type.replace('_', ' ')}</p>
        </div>
      </div>

      {/* Payment History */}
      <div className="bg-background border rounded-xl p-6">
        <h3 className="text-lg font-medium text-white mb-4">Payment History</h3>
        <div className="space-y-4">
          {payments.length > 0 ? (
            payments.map((payment) => (
              <div key={payment.id} className="flex items-center justify-between p-4 bg-white/5 rounded-xl">
                <div>
                  <h4 className="text-white font-medium">Session Payment</h4>
                  <p className="text-white/60 text-sm">
                    {formatDate(payment.created_at)} - 1.5 hours
                  </p>
                  <p className="text-white/40 text-xs mt-1">Ref: {payment.reference}</p>
                </div>
                <div className="text-right">
                  <p className="text-white font-semibold">₦{(payment.amount / 100).toLocaleString()}</p>
                  <p className={`text-sm ${payment.status === 'success' ? 'text-green-400' : 'text-yellow-400'}`}>
                    {payment.status === 'success' ? 'Paid' : payment.status}
                  </p>
                </div>
              </div>
            ))
          ) : (
            <p className="text-white/60 text-sm text-center py-4">No payment history yet. Book your first session to get started!</p>
          )}
        </div>
      </div>

      {/* Actions */}
      <div className="bg-background border rounded-xl p-6">
        <h3 className="text-lg font-medium text-white mb-4">Quick Actions</h3>
        <div className="flex gap-4">
          <button 
            onClick={() => window.location.href = '/book-slot'}
            className="bg-primary text-background px-6 py-2 rounded-xl font-semibold hover:bg-primary/90 transition-colors"
          >
            Book New Session
          </button>
          <button 
            onClick={() => window.location.href = '/profile'}
            className="border border-white/20 text-white px-6 py-2 rounded-xl font-semibold hover:bg-white/5 transition-colors"
          >
            Edit Profile
          </button>
        </div>
      </div>
    </div>
  )
}