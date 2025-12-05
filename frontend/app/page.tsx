'use client'
import { useState } from 'react'
import Header from '@/components/Header'
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

export default function Home() {
  const [step, setStep] = useState<'form' | 'slots' | 'confirmation'>('form')
  const [userDetails, setUserDetails] = useState<UserDetails | null>(null)
  const [bookingData, setBookingData] = useState<BookingData | null>(null)

  console.log('Home component state:', { step, userDetails, bookingData })

  const handleFormSubmit = (details: UserDetails) => {
    console.log('Form submitted with details:', details)
    setUserDetails(details)
    setStep('slots')
  }

  const handleBookingComplete = async (sessionId: string) => {
    // Fetch session details to get start and end times
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
      
      // Show confirmation with estimated times as fallback
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
    <div className="min-h-screen bg-pale">
      <Header />
      
      <main className="max-w-2xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
        <div className="text-center mb-6 sm:mb-8">
          <h1 className="text-2xl sm:text-3xl font-bold text-rough mb-2">
            CapCut Pro Account Sharing
          </h1>
          <p className="text-lg text-darknavy">
            Book your editing session (1 hour 30 minutes) - Available 24/7!
          </p>
        </div>

        {step === 'form' && (
          <div className="bg-pale rounded-lg border-2 border-gold/20 p-6 sm:p-8 shadow-warm">
            <BookingForm onSubmit={handleFormSubmit} />
          </div>
        )}
        
        {step === 'slots' && userDetails && (
          <div className="space-y-6">
            <div className="bg-pale rounded-lg border-2 border-gold p-4 sm:p-6 shadow-warm">
              <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3">
                <div>
                  <p className="text-lg font-semibold text-rough">{userDetails.name}</p>
                  <p className="text-sm text-darknavy">{userDetails.email}</p>
                </div>
                <button
                  onClick={handleStartOver}
                  className="text-sm text-gold hover:text-gold/80 font-medium underline self-start sm:self-center"
                >
                  Edit Details
                </button>
              </div>
            </div>
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
            <div className="text-center">
              <button
                onClick={handleStartOver}
                className="bg-gold text-pale px-6 py-3 rounded-md font-semibold hover:bg-gold/90 transition-colors"
              >
                Make Another Booking
              </button>
            </div>
          </div>
        )}
      </main>
      
      <footer className="bg-gold border-t-2 border-gold mt-16">
        <div className="max-w-4xl mx-auto px-4 py-6 sm:py-8">
          <div className="text-center text-sm text-pale">
            <p className="font-semibold">CapCut Sharing Platform • Built for Nigerian Creators</p>
            <p className="mt-2 text-pale/90">
              Share the cost, maximize the creativity • 1.5-hour sessions • 24/7 availability • Automatic rotation
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}