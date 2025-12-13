'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import TeamMemberDashboard from '@/components/dashboard/TeamMemberDashboard'

export default function TeamMemberDashboardPage() {
  const router = useRouter()
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null)
  const [isAuthorized, setIsAuthorized] = useState<boolean | null>(null)

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
        const response = await fetch(`${API_BASE_URL}/api/users/profile`, {
          credentials: 'include'
        })
        
        if (response.ok) {
          const data = await response.json()
          setIsAuthenticated(true)
          
          // Check if user is a team member
          if (data.user_type === 'team_member') {
            setIsAuthorized(true)
          } else {
            // Not a team member, redirect to appropriate dashboard
            router.push('/dashboard')
          }
        } else {
          // Not authenticated, redirect to auth
          router.push('/auth')
        }
      } catch (error) {
        console.error('Auth check failed:', error)
        router.push('/auth')
      }
    }
    
    checkAuth()
  }, [router])

  // Show loading while checking
  if (isAuthenticated === null || isAuthorized === null) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-white text-center">
          <div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-white/60">Loading...</p>
        </div>
      </div>
    )
  }

  // Don't render if not authenticated/authorized
  if (!isAuthenticated || !isAuthorized) {
    return null
  }

  return <TeamMemberDashboard />
}