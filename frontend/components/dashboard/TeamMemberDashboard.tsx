'use client'
import { useEffect, useState } from 'react'

interface AvailableSlot {
  id: string
  start_time: string
  end_time: string
  available: boolean
}

interface ManagerInfo {
  name: string
  email: string
  company: string
}

interface Session {
  id: number
  start_time: string
  end_time: string
  status: string
  slot_id: string
}

export default function TeamMemberDashboard() {
  const [availableSlots, setAvailableSlots] = useState<AvailableSlot[]>([])
  const [managerInfo, setManagerInfo] = useState<ManagerInfo | null>(null)
  const [sessions, setSessions] = useState<Session[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchTeamMemberData()
  }, [])

  const fetchTeamMemberData = async () => {
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${API_BASE_URL}/api/users/team-member-data`, {
        credentials: 'include'
      })
      if (response.ok) {
        const data = await response.json()
        setAvailableSlots(data.available_slots || [])
        setManagerInfo(data.manager_info)
        setSessions(data.sessions || [])
      }
    } catch (error) {
      console.error('Failed to fetch team member data:', error)
    } finally {
      setLoading(false)
    }
  }

  const bookSlot = async (slotId: string) => {
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${API_BASE_URL}/api/team-bookings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ slot_id: slotId })
      })
      if (response.ok) {
        alert('Slot booked successfully!')
        fetchTeamMemberData() // Refresh data
      } else {
        const error = await response.json()
        alert(error.detail || 'Failed to book slot')
      }
    } catch (error) {
      console.error('Failed to book slot:', error)
      alert('Failed to book slot')
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
      window.location.href = '/auth'
    }
  }

  if (loading) {
    return <div className="text-center py-8">Loading...</div>
  }

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="bg-background border rounded-xl p-6">
        <div className="flex items-center justify-between mb-2">
          <h1 className="text-2xl font-semibold text-white">Team Member Dashboard 👥</h1>
          <button
            onClick={handleLogout}
            className="px-4 py-2 border border-white/20 text-white text-sm rounded-lg hover:bg-white/5 transition-colors"
          >
            Logout
          </button>
        </div>
        <p className="text-white/60">Book slots from your team's allocation</p>
      </div>

      {/* Manager Info */}
      {managerInfo && (
        <div className="bg-background border rounded-xl p-6">
          <h3 className="text-lg font-medium text-white mb-4">Your Manager</h3>
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-primary/20 rounded-xl flex items-center justify-center">
              <span className="text-primary font-semibold text-xl">
                {managerInfo.name.charAt(0).toUpperCase()}
              </span>
            </div>
            <div>
              <h4 className="text-white font-medium">{managerInfo.name}</h4>
              <p className="text-white/60 text-sm">{managerInfo.email}</p>
              {managerInfo.company && (
                <p className="text-white/60 text-sm">{managerInfo.company}</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Available Slots */}
      <div className="bg-background border rounded-xl p-6">
        <h3 className="text-lg font-medium text-white mb-4">Available Slots</h3>
        {availableSlots.length === 0 ? (
          <p className="text-white/60">No available slots. Contact your manager for more slots.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {availableSlots.map((slot) => (
              <div key={slot.id} className="p-4 bg-white/5 rounded-xl">
                <h4 className="text-white font-medium mb-2">
                  {new Date(slot.start_time).toLocaleDateString()}
                </h4>
                <p className="text-white/60 text-sm mb-3">
                  {new Date(slot.start_time).toLocaleTimeString()} - {new Date(slot.end_time).toLocaleTimeString()}
                </p>
                <button
                  onClick={() => bookSlot(slot.id)}
                  disabled={!slot.available}
                  className="w-full bg-primary text-background px-4 py-2 rounded-xl font-semibold hover:bg-primary/90 disabled:bg-white/20 disabled:text-white/40 transition-colors"
                >
                  {slot.available ? 'Book Slot' : 'Unavailable'}
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Usage History */}
      <div className="bg-background border rounded-xl p-6">
        <h3 className="text-lg font-medium text-white mb-4">Your Usage History</h3>
        {sessions.length === 0 ? (
          <p className="text-white/60">No sessions yet. Book your first slot to get started!</p>
        ) : (
          <div className="space-y-4">
            {sessions.map((session) => (
              <div key={session.id} className="flex items-center justify-between p-4 bg-white/5 rounded-xl">
                <div>
                  <h4 className="text-white font-medium">
                    {new Date(session.start_time).toLocaleDateString()}
                  </h4>
                  <p className="text-white/60 text-sm">
                    {new Date(session.start_time).toLocaleTimeString()} - {new Date(session.end_time).toLocaleTimeString()}
                  </p>
                </div>
                <div className="text-right">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                    session.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                    session.status === 'active' ? 'bg-blue-500/20 text-blue-400' :
                    'bg-white/20 text-white/60'
                  }`}>
                    {session.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}