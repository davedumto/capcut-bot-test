'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Eye, EyeOff } from 'lucide-react'

interface PasswordLoginProps {
  email: string
}

export default function PasswordLogin({ email }: PasswordLoginProps) {
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [forgotMode, setForgotMode] = useState(false)
  const [resetSent, setResetSent] = useState(false)
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ email, password })
      })
      
      const data = await response.json()
      
      if (data.success) {
        if (data.must_change_password) {
          router.push('/auth/change-password')
        } else if (data.user.user_type === 'manager') {
          router.push('/manager/dashboard')
        } else if (data.user.user_type === 'team_member') {
          router.push('/team-member/dashboard')
        } else {
          router.push('/dashboard')
        }
      } else {
        setError('Invalid email or password')
      }
    } catch (error) {
      setError('Login failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleForgotPassword = async () => {
    setLoading(true)
    setError('')
    
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${API_BASE_URL}/api/auth/forgot-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      })
      
      const data = await response.json()
      
      if (data.success) {
        setResetSent(true)
      } else {
        setError(data.message || 'Failed to send reset link')
      }
    } catch (error) {
      setError('Failed to send reset link. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  if (resetSent) {
    return (
      <div className="text-center space-y-4">
        <div className="text-green-400 text-xl">✓ Reset Link Sent!</div>
        <p className="text-white/60">
          Check your email for a password reset link. Click the link to sign in and set a new password.
        </p>
        <button
          onClick={() => { setResetSent(false); setForgotMode(false) }}
          className="text-primary hover:text-primary/80"
        >
          Back to Login
        </button>
      </div>
    )
  }

  if (forgotMode) {
    return (
      <div className="space-y-4">
        <div className="text-center">
          <h3 className="text-xl font-semibold text-white mb-2">Reset Password</h3>
          <p className="text-white/60 text-sm">We'll send a reset link to:</p>
          <p className="text-white">{email}</p>
        </div>
        
        {error && (
          <div className="text-red-400 text-sm text-center">{error}</div>
        )}
        
        <button
          onClick={handleForgotPassword}
          disabled={loading}
          className="w-full bg-primary text-background px-6 py-3 rounded-xl font-semibold hover:bg-primary/90 transition-colors disabled:opacity-50"
        >
          {loading ? 'Sending...' : 'Send Reset Link'}
        </button>
        
        <button
          onClick={() => setForgotMode(false)}
          className="w-full text-white/60 hover:text-white text-sm"
        >
          Back to Login
        </button>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <input
          type="email"
          value={email}
          disabled
          className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white/60"
        />
      </div>
      
      <div className="relative">
        <input
          type={showPassword ? "text" : "password"}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          className="w-full px-4 py-3 pr-12 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/60 focus:outline-none focus:border-primary"
          required
        />
        <button
          type="button"
          onClick={() => setShowPassword(!showPassword)}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-white/60 hover:text-white"
        >
          {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
        </button>
      </div>

      {error && (
        <div className="text-red-400 text-sm text-center">{error}</div>
      )}
      
      <button
        type="submit"
        disabled={loading || !password}
        className="w-full bg-primary text-background px-6 py-3 rounded-xl font-semibold hover:bg-primary/90 transition-colors disabled:opacity-50"
      >
        {loading ? 'Signing in...' : 'Sign In'}
      </button>
      
      <button
        type="button"
        onClick={() => setForgotMode(true)}
        className="w-full text-white/60 hover:text-white text-sm"
      >
        Forgot Password?
      </button>
    </form>
  )
}