'use client'
import { useState, useEffect } from 'react'
import { formatDateTime, formatTime } from '@/lib/utils'

interface ConfirmationModalProps {
  sessionId: string
  userDetails: { name: string; email: string }
  startTime: string
  endTime: string
}

export default function ConfirmationModal({ 
  sessionId, 
  userDetails, 
  startTime, 
  endTime 
}: ConfirmationModalProps) {
  const [timeUntilStart, setTimeUntilStart] = useState<string>('')

  useEffect(() => {
    const updateCountdown = () => {
      const now = new Date()
      const start = new Date(startTime)
      const diffMs = start.getTime() - now.getTime()
      
      if (diffMs <= 0) {
        setTimeUntilStart('Session started!')
        return
      }
      
      const hours = Math.floor(diffMs / (1000 * 60 * 60))
      const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60))
      const seconds = Math.floor((diffMs % (1000 * 60)) / 1000)
      
      if (hours > 0) {
        setTimeUntilStart(`${hours}h ${minutes}m ${seconds}s`)
      } else if (minutes > 0) {
        setTimeUntilStart(`${minutes}m ${seconds}s`)
      } else {
        setTimeUntilStart(`${seconds}s`)
      }
    }

    updateCountdown()
    const interval = setInterval(updateCountdown, 1000)
    
    return () => clearInterval(interval)
  }, [startTime])

  return (
    <div className="bg-pale rounded-lg border-2 border-gold shadow-warm p-6 sm:p-8">
      {/* Success Icon and Title */}
      <div className="text-center mb-8">
        <div className="w-20 h-20 bg-gold rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-10 h-10 text-pale" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h2 className="text-2xl sm:text-3xl font-bold text-rough mb-3">
          Booking Confirmed!
        </h2>
        <p className="text-lg text-darknavy">
          Your credentials will be sent to <strong>{userDetails.email}</strong> at <strong>{formatTime(startTime)}</strong>
        </p>
      </div>

      {/* Countdown Timer */}
      <div className="bg-gold/10 border-2 border-gold rounded-lg p-6 mb-6 text-center">
        <div className="text-lg font-semibold text-rough mb-2">
          Session starts in
        </div>
        <div className="text-3xl sm:text-4xl font-bold text-gold mb-2">
          {timeUntilStart}
        </div>
        <div className="text-sm text-darknavy">
          {formatDateTime(startTime)}
        </div>
      </div>

      {/* Session Details */}
      <div className="bg-pale border-2 border-gold/30 rounded-lg p-6 mb-6">
        <h3 className="text-lg font-bold text-rough mb-4 text-center">Session Details</h3>
        <div className="space-y-3">
          <div className="flex flex-col sm:flex-row sm:justify-between gap-1">
            <span className="text-sm font-semibold text-rough">Name:</span>
            <span className="text-darknavy">{userDetails.name}</span>
          </div>
          <div className="flex flex-col sm:flex-row sm:justify-between gap-1">
            <span className="text-sm font-semibold text-rough">Email:</span>
            <span className="text-darknavy">{userDetails.email}</span>
          </div>
          <div className="flex flex-col sm:flex-row sm:justify-between gap-1">
            <span className="text-sm font-semibold text-rough">Time:</span>
            <span className="text-darknavy">{formatTime(startTime)} - {formatTime(endTime)}</span>
          </div>
          <div className="flex flex-col sm:flex-row sm:justify-between gap-1">
            <span className="text-sm font-semibold text-rough">Duration:</span>
            <span className="text-darknavy">1.5 hours</span>
          </div>
          <div className="flex flex-col sm:flex-row sm:justify-between gap-1">
            <span className="text-sm font-semibold text-rough">Session ID:</span>
            <span className="text-darknavy font-mono text-xs">{sessionId}</span>
          </div>
        </div>
      </div>

      {/* Important Warning */}
      <div className="bg-rough/10 border-2 border-rough rounded-lg p-6 mb-6">
        <h4 className="text-lg font-semibold text-rough mb-3 flex items-center">
          <span className="text-xl mr-2">⚠️</span>
          Important Information
        </h4>
        <div className="text-sm text-rough space-y-2">
          <p>• <strong>You will be logged out automatically at {formatTime(endTime)}</strong></p>
          <p>• Check your email at session start for login details</p>
          <p>• Only one person can use the account at a time</p>
          <p>• Please logout before your session expires to avoid interruption</p>
        </div>
      </div>

      {/* Instructions */}
      <div className="bg-gold/5 border border-gold/30 rounded-lg p-6 mb-6">
        <h4 className="text-lg font-semibold text-rough mb-4">What happens next?</h4>
        <div className="space-y-4">
          <div className="flex items-start gap-4">
            <div className="w-8 h-8 bg-gold text-pale rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0">
              1
            </div>
            <div>
              <div className="font-medium text-rough">Email Delivery</div>
              <div className="text-sm text-darknavy">
                At <strong>{formatTime(startTime)}</strong>, you'll receive an email with your CapCut login credentials
              </div>
            </div>
          </div>
          
          <div className="flex items-start gap-4">
            <div className="w-8 h-8 bg-gold text-pale rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0">
              2
            </div>
            <div>
              <div className="font-medium text-rough">Login & Edit</div>
              <div className="text-sm text-darknavy">
                Use the credentials to login at <strong>capcut.com</strong> and start your editing session
              </div>
            </div>
          </div>
          
          <div className="flex items-start gap-4">
            <div className="w-8 h-8 bg-gold text-pale rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0">
              3
            </div>
            <div>
              <div className="font-medium text-rough">Complete & Logout</div>
              <div className="text-sm text-darknavy">
                Finish your editing and logout before <strong>{formatTime(endTime)}</strong>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Support Contact */}
      <div className="text-center pt-4 border-t-2 border-gold/30">
        <p className="text-sm text-darknavy">
          Questions? Contact us at{' '}
          <span className="text-gold font-semibold">support@capcut-sharing.com</span>
        </p>
      </div>
    </div>
  )
}