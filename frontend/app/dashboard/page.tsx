'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import UserDashboard from '@/components/dashboard/UserDashboard'
import ManagerDashboard from '@/components/dashboard/ManagerDashboard'
import TeamMemberDashboard from '@/components/dashboard/TeamMemberDashboard'

export default function DashboardPage() {
  const router = useRouter()
  const [userType, setUserType] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchUserType()
  }, [])

  const fetchUserType = async () => {
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${API_BASE_URL}/api/users/profile`, {
        credentials: 'include'
      })
      if (response.ok) {
        const data = await response.json()
        setUserType(data.user_type)
      } else {
        // Not authenticated, redirect to auth
        router.push('/auth')
      }
    } catch (error) {
      console.error('Failed to fetch user type:', error)
      router.push('/auth')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="text-center py-8">Loading...</div>
  }

  if (userType === 'manager') {
    return <ManagerDashboard />
  } else if (userType === 'team_member') {
    return <TeamMemberDashboard />
  } else {
    return <UserDashboard />
  }
}