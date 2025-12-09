'use client'
import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { CheckCircle, Clock, Mail, LogOut, HelpCircle } from 'lucide-react'
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

  const steps = [
    {
      icon: Mail,
      title: 'Email Delivery',
      description: `At ${formatTime(startTime)}, you'll receive your CapCut login credentials`
    },
    {
      icon: Clock,
      title: 'Login & Edit',
      description: 'Use the credentials to login at capcut.com and start editing'
    },
    {
      icon: LogOut,
      title: 'Complete & Logout',
      description: `Finish your work and logout before ${formatTime(endTime)}`
    }
  ]

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
      className="bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-6 sm:p-8"
    >
      {/* Success Icon and Title */}
      <div className="text-center mb-8">
        <motion.div 
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: "spring", delay: 0.2 }}
          className="w-20 h-20 bg-primary rounded-full flex items-center justify-center mx-auto mb-4 shadow-[0_0_40px_rgba(0,229,189,0.4)]"
        >
          <CheckCircle className="w-10 h-10 text-background" />
        </motion.div>
        <h2 className="text-2xl sm:text-3xl font-bold text-white mb-3">
          Booking Confirmed!
        </h2>
        <p className="text-lg text-white/60">
          Credentials will be sent to <strong className="text-primary">{userDetails.email}</strong>
        </p>
      </div>

      {/* Countdown Timer */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="bg-gradient-to-br from-primary/20 to-accent/10 border border-primary/30 rounded-2xl p-6 mb-6 text-center"
      >
        <div className="text-lg font-medium text-white/80 mb-2">
          Session starts in
        </div>
        <div className="text-4xl sm:text-5xl font-bold text-primary mb-2">
          {timeUntilStart}
        </div>
        <div className="text-sm text-white/60">
          {formatDateTime(startTime)}
        </div>
      </motion.div>

      {/* Session Details */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-white/5 border border-white/10 rounded-xl p-6 mb-6"
      >
        <h3 className="text-lg font-bold text-white mb-4 text-center">Session Details</h3>
        <div className="space-y-3 text-sm">
          <div className="flex justify-between items-center py-2 border-b border-white/5">
            <span className="text-white/60">Name</span>
            <span className="text-white font-medium">{userDetails.name}</span>
          </div>
          <div className="flex justify-between items-center py-2 border-b border-white/5">
            <span className="text-white/60">Email</span>
            <span className="text-white font-medium">{userDetails.email}</span>
          </div>
          <div className="flex justify-between items-center py-2 border-b border-white/5">
            <span className="text-white/60">Time</span>
            <span className="text-white font-medium">{formatTime(startTime)} – {formatTime(endTime)}</span>
          </div>
          <div className="flex justify-between items-center py-2 border-b border-white/5">
            <span className="text-white/60">Duration</span>
            <span className="text-white font-medium">1.5 hours</span>
          </div>
          <div className="flex justify-between items-center py-2">
            <span className="text-white/60">Session ID</span>
            <span className="text-white/80 font-mono text-xs">{sessionId.slice(0, 8)}...</span>
          </div>
        </div>
      </motion.div>

      {/* Important Warning */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="bg-orange-500/10 border border-orange-500/30 rounded-xl p-5 mb-6"
      >
        <h4 className="text-base font-semibold text-orange-400 mb-3 flex items-center gap-2">
          <span>⚠️</span> Important
        </h4>
        <div className="text-sm text-orange-200/80 space-y-1.5">
          <p>• You will be logged out automatically at <strong>{formatTime(endTime)}</strong></p>
          <p>• Check your email at session start for login details</p>
          <p>• Only one person can use the account at a time</p>
        </div>
      </motion.div>

      {/* What happens next */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="bg-white/5 border border-white/10 rounded-xl p-6 mb-6"
      >
        <h4 className="text-lg font-semibold text-white mb-5">What happens next?</h4>
        <div className="space-y-5">
          {steps.map((step, index) => (
            <div key={index} className="flex items-start gap-4">
              <div className="w-10 h-10 bg-primary/20 text-primary rounded-xl flex items-center justify-center flex-shrink-0">
                <step.icon className="w-5 h-5" />
              </div>
              <div>
                <div className="font-medium text-white">{step.title}</div>
                <div className="text-sm text-white/60 mt-0.5">{step.description}</div>
              </div>
            </div>
          ))}
        </div>
      </motion.div>

      {/* Support Contact */}
      <div className="text-center pt-4 border-t border-white/10">
        <p className="text-sm text-white/50 flex items-center justify-center gap-2">
          <HelpCircle className="w-4 h-4" />
          Questions? <span className="text-primary font-medium">help@slotio.io</span>
        </p>
      </div>
    </motion.div>
  )
}