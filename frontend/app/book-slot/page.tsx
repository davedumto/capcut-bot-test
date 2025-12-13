'use client'
import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { ArrowLeft, Calendar } from 'lucide-react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import BookingForm from '@/components/BookingForm'
import SlotSelector from '@/components/SlotSelector'
import ConfirmationModal from '@/components/ConfirmationModal'

interface UserDetails {
  name: string
  email: string
}

interface BookingData {
  sessionId: string
  startTime: string
  endTime: string
}

export default function BookSlotPage() {
  const router = useRouter()
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null)
  const [step, setStep] = useState<'form' | 'slots' | 'confirmation'>('form')
  const [userDetails, setUserDetails] = useState<UserDetails | null>(null)
  const [bookingData, setBookingData] = useState<BookingData | null>(null)

  // Check authentication on mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
        const response = await fetch(`${API_BASE_URL}/api/users/profile`, {
          credentials: 'include'
        })
        
        if (response.ok) {
          const userData = await response.json()
          setIsAuthenticated(true)
          // Auto-populate user details and skip to slot selection
          setUserDetails({
            name: userData.name,
            email: userData.email
          })
          setStep('slots') // Skip form, go straight to slots
        } else {
          // Not authenticated, redirect to auth page
          router.push('/auth')
        }
      } catch (error) {
        console.error('Auth check failed:', error)
        router.push('/auth')
      }
    }
    
    checkAuth()
  }, [router])

  // Show loading while checking auth
  if (isAuthenticated === null) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-white text-center">
          <div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-white/60">Loading...</p>
        </div>
      </div>
    )
  }

  // Don't render anything if not authenticated (will redirect)
  if (!isAuthenticated) {
    return null
  }

  const handleFormSubmit = (details: UserDetails) => {
    setUserDetails(details)
    setStep('slots')
  }

  const handleBookingComplete = async (sessionId: string) => {
    try {
      const { getSessionDetails } = await import('@/lib/api')
      const sessionData = await getSessionDetails(sessionId)
      
      if (sessionData && sessionData.start_time && sessionData.end_time) {
        setBookingData({
          sessionId,
          startTime: sessionData.start_time,
          endTime: sessionData.end_time
        })
        setStep('confirmation')
      } else {
        throw new Error('Invalid session data received')
      }
    } catch (error) {
      console.error('Failed to fetch session details:', error)
      
      const now = new Date()
      const nextSlot = new Date(now)
      nextSlot.setMinutes(now.getMinutes() < 30 ? 30 : 60, 0, 0)
      if (nextSlot <= now) {
        nextSlot.setHours(nextSlot.getHours() + 1, 0, 0, 0)
      }
      
      const endTime = new Date(nextSlot.getTime() + 90 * 60 * 1000)
      
      setBookingData({
        sessionId,
        startTime: nextSlot.toISOString(),
        endTime: endTime.toISOString()
      })
      setStep('confirmation')
    }
  }

  const handleStartOver = () => {
    setStep('form')
    setUserDetails(null)
    setBookingData(null)
  }

  return (
    <div className="min-h-screen bg-background text-white">
      {/* Minimal header with just logo and back button */}
      <motion.nav 
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="fixed top-0 left-0 right-0 z-50 px-6 py-4 bg-background border-b border-white/10"
      >
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <Link href="/dashboard">
            <motion.div 
              whileHover={{ x: -3 }}
              className="text-white/60 hover:text-white flex items-center gap-2 font-medium transition-colors cursor-pointer"
            >
              <ArrowLeft className="w-5 h-5" />
              <span className="hidden sm:inline">Back</span>
            </motion.div>
          </Link>
          
          <Link href="/">
            <span className="font-display text-2xl font-bold text-white tracking-tight cursor-pointer">
              Slotio
            </span>
          </Link>
          
          {/* Empty div for centering */}
          <div className="w-16"></div>
        </div>
      </motion.nav>

      {/* Background gradient effect */}
      <div className="fixed inset-0 -z-10">
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[600px] rounded-full bg-gradient-radial from-primary/10 via-accent/5 to-transparent blur-3xl opacity-50" />
      </div>
      
      <main className="min-h-screen flex flex-col justify-center max-w-2xl mx-auto px-4 sm:px-6 pt-20 pb-12">
        {/* Page title */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 mb-4">
            <Calendar className="w-4 h-4 text-primary" />
            <span className="text-sm text-white/80">Book a session</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-bold text-white mb-3">
            {step === 'form' && 'Enter Your Details'}
            {step === 'slots' && 'Choose a Time Slot'}
            {step === 'confirmation' && 'You\'re All Set!'}
          </h1>
          <p className="text-white/60">
            {step === 'form' && '1.5 hours of premium access • Available 24/7'}
            {step === 'slots' && 'Select an available slot that works for you'}
            {step === 'confirmation' && 'Your session has been booked successfully'}
          </p>
        </motion.div>

        {step === 'form' && (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-6 sm:p-8"
          >
            <BookingForm onSubmit={handleFormSubmit} />
          </motion.div>
        )}
        
        {step === 'slots' && userDetails && (
          <div className="space-y-6">
            {/* User info card */}
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 p-4"
            >
              <div>
                <p className="text-lg font-semibold text-white">{userDetails.name}</p>
                <p className="text-sm text-white/60">{userDetails.email}</p>
              </div>
            </motion.div>
            
            <SlotSelector 
              userDetails={userDetails} 
              onBookingComplete={handleBookingComplete} 
            />
          </div>
        )}
        
        {step === 'confirmation' && userDetails && bookingData && (
          <div className="space-y-6">
            <ConfirmationModal
              sessionId={bookingData.sessionId}
              userDetails={userDetails}
              startTime={bookingData.startTime}
              endTime={bookingData.endTime}
            />
            <div className="text-center space-y-4">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={handleStartOver}
                className="bg-primary text-background px-8 py-4 rounded-full font-semibold hover:bg-primary/90 transition-colors shadow-[0_0_20px_rgba(0,229,189,0.3)]"
              >
                Book Another Session
              </motion.button>
              <div>
                <Link 
                  href="/"
                  className="text-white/60 hover:text-white font-medium underline underline-offset-2 transition-colors"
                >
                  Return to Home
                </Link>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
