'use client'
import { useEffect, useState } from 'react'

interface TeamMember {
  id: number
  email: string
  added_at: string
}

export default function ManagerDashboard() {
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([])
  const [newMemberEmail, setNewMemberEmail] = useState('')
  const [allowMultipleBookings, setAllowMultipleBookings] = useState(false)
  const [credentials, setCredentials] = useState({ 
    capcut_email: '', 
    capcut_password: '',
    gmail_email: '',
    gmail_password: ''
  })
  const [loading, setLoading] = useState(true)
  const [subscriptionStatus, setSubscriptionStatus] = useState<any>(null)

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  useEffect(() => {
    fetchTeam()
    fetchSubscriptionStatus()
  }, [])

  const fetchTeam = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/managers/team`, { credentials: 'include' })
      if (res.ok) {
        const data = await res.json()
        setTeamMembers(data.team_members || [])
        const creds = data.credentials || {}
        setCredentials({
          capcut_email: creds.capcut_email || '',
          capcut_password: '',
          gmail_email: creds.gmail_email || '',
          gmail_password: ''
        })
        // Load settings
        if (data.settings) {
          setAllowMultipleBookings(data.settings.allow_multiple_bookings || false)
        }
      }
    } catch (error) {
      console.error('Failed to fetch team:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchSubscriptionStatus = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/manager/status`, { credentials: 'include' })
      if (res.ok) {
        const data = await res.json()
        setSubscriptionStatus(data)
      }
    } catch (error) {
      console.error('Failed to fetch subscription status:', error)
    }
  }

  const addMember = async () => {
    if (!newMemberEmail) return
    
    try {
      const res = await fetch(`${API_BASE}/api/managers/team`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ email: newMemberEmail })
      })
      
      if (res.ok) {
        setNewMemberEmail('')
        fetchTeam()
      } else {
        const err = await res.json()
        alert(err.detail || 'Failed to add member')
      }
    } catch (error) {
      console.error('Failed to add member:', error)
    }
  }

  const removeMember = async (id: number) => {
    if (!confirm('Remove this team member?')) return
    
    try {
      const res = await fetch(`${API_BASE}/api/managers/team/${id}`, {
        method: 'DELETE',
        credentials: 'include'
      })
      
      if (res.ok) fetchTeam()
    } catch (error) {
      console.error('Failed to remove member:', error)
    }
  }

  const saveCredentials = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/managers/credentials`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(credentials)
      })
      
      if (res.ok) alert('Credentials saved!')
    } catch (error) {
      console.error('Failed to save credentials:', error)
    }
  }

  const handleLogout = async () => {
    try {
      await fetch(`${API_BASE}/api/auth/logout`, {
        method: 'POST',
        credentials: 'include'
      })
      window.location.href = '/auth'
    } catch (error) {
      console.error('Logout failed:', error)
      window.location.href = '/auth'
    }
  }

  const toggleMultipleBookings = async () => {
    try {
      const newValue = !allowMultipleBookings
      const res = await fetch(`${API_BASE}/api/managers/settings`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ allow_multiple_bookings: newValue })
      })
      if (res.ok) {
        setAllowMultipleBookings(newValue)
      } else {
        alert('Failed to update setting')
      }
    } catch (error) {
      console.error('Failed to toggle setting:', error)
    }
  }

  if (loading) return <div className="text-center py-8">Loading...</div>

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      <div className="bg-background border rounded-xl p-6">
        <div className="flex items-center justify-between mb-2">
          <h1 className="text-2xl font-semibold text-white">Manager Dashboard 👨‍💼</h1>
          <button
            onClick={handleLogout}
            className="px-4 py-2 border border-white/20 text-white text-sm rounded-lg hover:bg-white/5 transition-colors"
          >
            Logout
          </button>
        </div>
        <p className="text-white/60">Manage your team and CapCut credentials</p>
      </div>

      {/* Subscription Status */}
      <div className={`border rounded-xl p-6 ${
        subscriptionStatus?.subscription_status === 'active' 
          ? 'bg-green-500/10 border-green-500/30' 
          : 'bg-yellow-500/10 border-yellow-500/30'
      }`}>
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-medium text-white mb-1">
              {subscriptionStatus?.subscription_status === 'active' ? '✅ Subscription Active' : '⚠️ No Active Subscription'}
            </h3>
            <p className="text-white/60 text-sm">
              {subscriptionStatus?.subscription_status === 'active' 
                ? 'Your team can book slots' 
                : 'Subscribe to enable team bookings'}
            </p>
          </div>
          {subscriptionStatus?.subscription_status !== 'active' && (
            <a 
              href="/manager/subscribe" 
              className="bg-primary text-background px-6 py-3 rounded-xl font-semibold hover:bg-primary/90"
            >
              Subscribe ₦5,000/month
            </a>
          )}
        </div>
      </div>

      {/* Team Settings */}
      <div className="bg-background border rounded-xl p-6">
        <h3 className="text-lg font-medium text-white mb-4">Team Settings ⚙️</h3>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-white">Allow Multiple Bookings Per Day</p>
            <p className="text-white/60 text-sm">When OFF, each team member can only book one slot per day</p>
          </div>
          <button
            onClick={toggleMultipleBookings}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
              allowMultipleBookings ? 'bg-primary' : 'bg-white/20'
            }`}
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                allowMultipleBookings ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        </div>
      </div>

      {/* CapCut Credentials */}
      <div className="bg-background border rounded-xl p-6">
        <h3 className="text-lg font-medium text-white mb-4">CapCut Pro Credentials</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <input
            type="email"
            placeholder="CapCut Email"
            value={credentials.capcut_email}
            onChange={(e) => setCredentials({...credentials, capcut_email: e.target.value})}
            className="p-3 bg-white/5 border border-white/20 rounded-xl text-white"
          />
          <input
            type="password"
            placeholder="CapCut Password"
            value={credentials.capcut_password}
            onChange={(e) => setCredentials({...credentials, capcut_password: e.target.value})}
            className="p-3 bg-white/5 border border-white/20 rounded-xl text-white"
          />
          <input
            type="email"
            placeholder="Gmail Email"
            value={credentials.gmail_email}
            onChange={(e) => setCredentials({...credentials, gmail_email: e.target.value})}
            className="p-3 bg-white/5 border border-white/20 rounded-xl text-white"
          />
          <input
            type="password"
            placeholder="Gmail App Password"
            value={credentials.gmail_password}
            onChange={(e) => setCredentials({...credentials, gmail_password: e.target.value})}
            className="p-3 bg-white/5 border border-white/20 rounded-xl text-white"
          />
        </div>
        <button
          onClick={saveCredentials}
          className="bg-primary text-background px-6 py-2 rounded-xl font-semibold hover:bg-primary/90"
        >
          Save Credentials
        </button>
      </div>

      {/* Team Stats */}
      <div className="bg-background border rounded-xl p-6">
        <h3 className="text-lg font-medium text-white mb-2">Team Members</h3>
        <p className="text-3xl font-bold text-primary">{teamMembers.length}/12</p>
      </div>

      {/* Add Team Member */}
      <div className="bg-background border rounded-xl p-6">
        <h3 className="text-lg font-medium text-white mb-4">Add Team Member</h3>
        <div className="flex gap-2">
          <input
            type="email"
            placeholder="member@example.com"
            value={newMemberEmail}
            onChange={(e) => setNewMemberEmail(e.target.value)}
            className="flex-1 p-3 bg-white/5 border border-white/20 rounded-xl text-white"
          />
          <button
            onClick={addMember}
            className="bg-primary text-background px-6 py-2 rounded-xl font-semibold hover:bg-primary/90"
          >
            Add
          </button>
        </div>
      </div>

      {/* Team Members List */}
      <div className="bg-background border rounded-xl p-6">
        <h3 className="text-lg font-medium text-white mb-4">Team</h3>
        {teamMembers.length === 0 ? (
          <p className="text-white/60">No team members yet.</p>
        ) : (
          <div className="space-y-3">
            {teamMembers.map((member) => (
              <div key={member.id} className="flex items-center justify-between p-4 bg-white/5 rounded-xl">
                <div>
                  <p className="text-white font-medium">{member.email}</p>
                  <p className="text-white/60 text-sm">
                    Added {new Date(member.added_at).toLocaleDateString()}
                  </p>
                </div>
                <button
                  onClick={() => removeMember(member.id)}
                  className="text-red-400 hover:text-red-300 px-4 py-2"
                >
                  Remove
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}