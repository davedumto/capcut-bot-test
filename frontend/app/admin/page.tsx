"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export default function AdminDashboard() {
  const router = useRouter()
  const [stats, setStats] = useState<any>(null)
  const [analytics, setAnalytics] = useState<any>(null)
  const [activeTab, setActiveTab] = useState("overview")
  const [managers, setManagers] = useState<any[]>([])
  const [slotioAccounts, setSlotioAccounts] = useState<any[]>([])
  const [botJobs, setBotJobs] = useState<any[]>([])
  const [botWorkerStatus, setBotWorkerStatus] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    try {
      const response = await fetch(`${API_URL}/api/admin/check-auth`, {
        credentials: 'include'
      })
      
      if (!response.ok) {
        router.push('/admin/login')
        return
      }

      // If authenticated, load data
      fetchStats()
      fetchAnalytics()
      fetchManagers()
      fetchSlotioAccounts()
      fetchBotJobs()
      fetchBotWorkerStatus()
      
      // Refresh bot status every 30 seconds
      const interval = setInterval(fetchBotWorkerStatus, 30000)
      return () => clearInterval(interval)
    } catch (err) {
      router.push('/admin/login')
    }
  }

  const handleLogout = async () => {
    try {
      await fetch(`${API_URL}/api/admin/logout`, {
        method: 'POST',
        credentials: 'include'
      })
      router.push('/admin/login')
    } catch (err) {
      console.error('Logout failed:', err)
    }
  }

  const fetchStats = async () => {
    try {
      const res = await fetch(`${API_URL}/api/admin/stats`)
      const data = await res.json()
      setStats(data)
    } catch (err) {
      console.error("Failed to fetch stats:", err)
    }
    setLoading(false)
  }

  const fetchAnalytics = async () => {
    const res = await fetch(`${API_URL}/api/admin/analytics`)
    setAnalytics(await res.json())
  }

  const fetchManagers = async () => {
    const res = await fetch(`${API_URL}/api/admin/managers`)
    setManagers(await res.json())
  }

  const fetchSlotioAccounts = async () => {
    const res = await fetch(`${API_URL}/api/admin/slotio-accounts`)
    setSlotioAccounts(await res.json())
  }

  const fetchBotJobs = async () => {
    const res = await fetch(`${API_URL}/api/admin/bot-jobs?status=failed`)
    setBotJobs(await res.json())
  }

  const fetchBotWorkerStatus = async () => {
    try {
      const res = await fetch(`${API_URL}/api/admin/bot-worker/status`)
      setBotWorkerStatus(await res.json())
    } catch (err) {
      console.error("Failed to fetch bot worker status:", err)
      setBotWorkerStatus({ status: "error", healthy: false })
    }
  }

  const addManager = async (e: any) => {
    e.preventDefault()
    const formData = new FormData(e.target)
    const res = await fetch(`${API_URL}/api/admin/managers`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: formData.get("email"),
        name: formData.get("name")
      })
    })
    const data = await res.json()
    if (data.success) {
      alert(`Manager added! Temp password: ${data.temp_password}`)
      fetchManagers()
      e.target.reset()
    }
  }

  const addSlotioAccount = async (e: any) => {
    e.preventDefault()
    const formData = new FormData(e.target)
    await fetch(`${API_URL}/api/admin/slotio-accounts`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: formData.get("name"),
        capcut_email: formData.get("capcut_email"),
        gmail_email: formData.get("gmail_email"),
        gmail_app_password: formData.get("gmail_app_password")
      })
    })
    fetchSlotioAccounts()
    e.target.reset()
  }

  const retryJob = async (jobId: number) => {
    await fetch(`${API_URL}/api/admin/bot-jobs/${jobId}/retry`, { method: "POST" })
    fetchBotJobs()
  }

  const removeManager = async (managerId: number) => {
    if (!confirm('Are you sure you want to remove this manager? They and their team members will become regular users.')) return
    try {
      const res = await fetch(`${API_URL}/api/admin/managers/${managerId}`, { method: "DELETE" })
      const data = await res.json()
      if (!res.ok) {
        alert(data.detail || 'Failed to remove manager')
        return
      }
      fetchManagers()
      fetchStats()
    } catch (error) {
      alert('Failed to remove manager')
    }
  }

  const deleteSlotioAccount = async (tenantId: number) => {
    if (!confirm('Are you sure you want to delete this Slotio account?')) return
    try {
      const res = await fetch(`${API_URL}/api/admin/slotio-accounts/${tenantId}`, { method: "DELETE" })
      const data = await res.json()
      if (!res.ok) {
        alert(data.detail || 'Failed to delete account')
        return
      }
      fetchSlotioAccounts()
    } catch (error) {
      alert('Failed to delete account')
    }
  }

  const resetManagerPassword = async (managerId: number) => {
    if (!confirm('Reset this manager\'s password?')) return
    try {
      const res = await fetch(`${API_URL}/api/admin/managers/${managerId}/reset-password`, { method: "POST" })
      const data = await res.json()
      if (!res.ok) {
        alert(data.detail || 'Failed to reset password')
        return
      }
      alert(`New temporary password: ${data.temp_password}\n\nPlease share this with the manager securely.`)
    } catch (error) {
      alert('Failed to reset password')
    }
  }

  if (loading) return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <div className="text-white text-2xl">Loading...</div>
    </div>
  )

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-4xl font-bold text-white">Admin Dashboard</h1>
          <button
            onClick={handleLogout}
            className="bg-white/5 hover:bg-white/10 border border-white/20 text-white px-6 py-2 rounded-xl font-semibold transition-colors"
          >
            Logout
          </button>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-5 gap-4 mb-8">
            <div className="bg-white/5 border border-white/20 p-6 rounded-xl">
              <div className="text-white/60 text-sm">Managers</div>
              <div className="text-4xl font-bold text-white">{stats.total_managers}</div>
            </div>
            <div className="bg-white/5 border border-white/20 p-6 rounded-xl">
              <div className="text-white/60 text-sm">Pay-per-edit Users</div>
              <div className="text-4xl font-bold text-white">{stats.total_pay_per_edit_users}</div>
            </div>
            <div className="bg-white/5 border border-white/20 p-6 rounded-xl">
              <div className="text-white/60 text-sm">Today's Sessions</div>
              <div className="text-4xl font-bold text-white">{stats.today_sessions}</div>
            </div>
            <div className="bg-white/5 border border-white/20 p-6 rounded-xl">
              <div className="text-white/60 text-sm">Revenue</div>
              <div className="text-4xl font-bold text-primary">₦{stats.total_revenue.toLocaleString()}</div>
            </div>
            <div className={`bg-white/5 border p-6 rounded-xl ${
              botWorkerStatus?.healthy ? 'border-green-500/50' : 'border-red-500/50'
            }`}>
              <div className="text-white/60 text-sm mb-2">Bot Worker</div>
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${
                  botWorkerStatus?.healthy ? 'bg-green-500 animate-pulse' : 'bg-red-500'
                }`}></div>
                <div className={`text-sm font-semibold ${
                  botWorkerStatus?.healthy ? 'text-green-400' : 'text-red-400'
                }`}>
                  {botWorkerStatus?.healthy ? 'Healthy' : 'Offline'}
                </div>
              </div>
              {botWorkerStatus?.seconds_since_heartbeat !== undefined && (
                <div className="text-xs text-white/40 mt-1">
                  Last ping: {botWorkerStatus.seconds_since_heartbeat}s ago
                </div>
              )}
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="border-b border-white/20 mb-6">
          {["overview", "managers", "slotio", "bot-jobs"].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-6 py-3 text-white ${
                activeTab === tab 
                  ? "border-b-2 border-primary font-semibold" 
                  : "hover:bg-white/5"
              }`}
            >
              {tab.split("-").map(w => w[0].toUpperCase() + w.slice(1)).join(" ")}
            </button>
          ))}
        </div>

        {/* Overview Tab */}
        {activeTab === "overview" && analytics && (
          <div className="space-y-6">
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-white/5 border border-white/20 p-6 rounded-xl">
                <div className="text-white/60 text-sm mb-2">Total Platform Revenue</div>
                <div className="text-3xl font-bold text-primary">₦{analytics.total_revenue.toLocaleString()}</div>
              </div>
              <div className="bg-white/5 border border-white/20 p-6 rounded-xl">
                <div className="text-white/60 text-sm mb-2">Total Sessions</div>
                <div className="text-3xl font-bold text-white">{analytics.total_sessions}</div>
              </div>
              <div className="bg-white/5 border border-white/20 p-6 rounded-xl">
                <div className="text-white/60 text-sm mb-2">Total Hours</div>
                <div className="text-3xl font-bold text-white">{analytics.total_hours.toFixed(1)}</div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-6">
              <div className="bg-background border border-white/20 p-6 rounded-xl">
                <h3 className="text-lg font-medium text-white mb-4">Last 7 Days Revenue</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={analytics.last_7_days}>
                    <XAxis dataKey="date" stroke="#fff" opacity={0.5} />
                    <YAxis stroke="#fff" opacity={0.5} />
                    <Tooltip contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #333' }} />
                    <Line type="monotone" dataKey="revenue" stroke="#00f0ff" strokeWidth={2} name="Revenue (₦)" />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              <div className="bg-background border border-white/20 p-6 rounded-xl">
                <h3 className="text-lg font-medium text-white mb-4">Last 7 Days Sessions</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={analytics.last_7_days}>
                    <XAxis dataKey="date" stroke="#fff" opacity={0.5} />
                    <YAxis stroke="#fff" opacity={0.5} />
                    <Tooltip contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #333' }} />
                    <Line type="monotone" dataKey="sessions" stroke="#00f0ff" strokeWidth={2} name="Sessions" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="bg-background border border-white/20 p-6 rounded-xl">
              <h3 className="text-lg font-medium text-white mb-4">Peak Usage Hours</h3>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={analytics.peak_hours}>
                  <XAxis dataKey="hour" stroke="#fff" opacity={0.5} />
                  <YAxis stroke="#fff" opacity={0.5} />
                  <Tooltip contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #333' }} />
                  <Bar dataKey="sessions" fill="#00f0ff" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {/* Managers Tab */}
        {activeTab === "managers" && (
          <div className="bg-background border border-white/20 p-6 rounded-xl">
            <h2 className="text-2xl font-semibold text-white mb-4">Add Manager</h2>
            <form onSubmit={addManager} className="mb-8 space-y-4">
              <input name="email" type="email" placeholder="Email" required className="p-3 bg-white/5 border border-white/20 rounded-xl text-white w-full" />
              <input name="name" placeholder="Name" required className="p-3 bg-white/5 border border-white/20 rounded-xl text-white w-full" />
              <button type="submit" className="bg-primary text-background px-6 py-3 rounded-xl font-semibold hover:bg-primary/90">Add Manager</button>
            </form>

            <h3 className="text-lg font-medium text-white mb-4">All Managers ({managers.length})</h3>
            <table className="w-full">
              <thead>
                <tr className="border-b border-white/20">
                  <th className="text-left py-3 text-white/60">Name</th>
                  <th className="text-left py-3 text-white/60">Email</th>
                  <th className="text-left py-3 text-white/60">Created</th>
                  <th className="text-left py-3 text-white/60">Actions</th>
                </tr>
              </thead>
              <tbody>
                {managers.map(m => (
                  <tr key={m.id} className="border-b border-white/10">
                    <td className="py-3 text-white">{m.name}</td>
                    <td className="py-3 text-white/80">{m.email}</td>
                    <td className="py-3 text-white/60">{new Date(m.created_at).toLocaleDateString()}</td>
                    <td className="py-3 flex gap-2">
                      <button 
                        onClick={() => resetManagerPassword(m.id)} 
                        className="text-primary hover:text-primary/80 text-sm"
                      >
                        Reset Password
                      </button>
                      <button 
                        onClick={() => removeManager(m.id)} 
                        className="text-red-400 hover:text-red-300 text-sm"
                      >
                        Remove
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Slotio Accounts Tab */}
        {activeTab === "slotio" && (
          <div className="bg-background border border-white/20 p-6 rounded-xl">
            <h2 className="text-2xl font-semibold text-white mb-4">Add Slotio Account</h2>
            <form onSubmit={addSlotioAccount} className="mb-8 space-y-4">
              <input name="name" placeholder="Account Name" required className="p-3 bg-white/5 border border-white/20 rounded-xl text-white w-full" />
              <input name="capcut_email" type="email" placeholder="CapCut Email" required className="p-3 bg-white/5 border border-white/20 rounded-xl text-white w-full" />
              <input name="gmail_email" type="email" placeholder="Gmail Email" required className="p-3 bg-white/5 border border-white/20 rounded-xl text-white w-full" />
              <input name="gmail_app_password" placeholder="Gmail App Password" required className="p-3 bg-white/5 border border-white/20 rounded-xl text-white w-full" />
              <button type="submit" className="bg-primary text-background px-6 py-3 rounded-xl font-semibold hover:bg-primary/90">Add Account</button>
            </form>

            <h3 className="text-lg font-medium text-white mb-4">Slotio Accounts ({slotioAccounts.length})</h3>
            <table className="w-full">
              <thead>
                <tr className="border-b border-white/20">
                  <th className="text-left py-3 text-white/60">Name</th>
                  <th className="text-left py-3 text-white/60">Email</th>
                  <th className="text-left py-3 text-white/60">Sessions</th>
                  <th className="text-left py-3 text-white/60">Hours</th>
                  <th className="text-left py-3 text-white/60">Actions</th>
                </tr>
              </thead>
              <tbody>
                {slotioAccounts.map(a => (
                  <tr key={a.id} className="border-b border-white/10">
                    <td className="py-3 text-white">{a.name}</td>
                    <td className="py-3 text-white/80">{a.capcut_email}</td>
                    <td className="py-3 text-white/60">{a.total_sessions}</td>
                    <td className="py-3 text-white/60">{a.total_hours}</td>
                    <td className="py-3">
                      <button 
                        onClick={() => deleteSlotioAccount(a.id)} 
                        className="text-red-400 hover:text-red-300 text-sm"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Bot Jobs Tab */}
        {activeTab === "bot-jobs" && (
          <div className="bg-background border border-white/20 p-6 rounded-xl">
            <h2 className="text-2xl font-semibold text-white mb-4">Failed Bot Jobs</h2>
            <table className="w-full">
              <thead>
                <tr className="border-b border-white/20">
                  <th className="text-left py-3 text-white/60">Job ID</th>
                  <th className="text-left py-3 text-white/60">Session</th>
                  <th className="text-left py-3 text-white/60">Error</th>
                  <th className="text-left py-3 text-white/60">Actions</th>
                </tr>
              </thead>
              <tbody>
                {botJobs.map(job => (
                  <tr key={job.id} className="border-b border-white/10">
                    <td className="py-3 text-white">#{job.id}</td>
                    <td className="py-3 text-white">#{job.session_id}</td>
                    <td className="py-3 text-red-400">{job.error_message || "Unknown error"}</td>
                    <td className="py-3">
                      <button onClick={() => retryJob(job.id)} className="text-primary hover:text-primary/80">Retry</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
