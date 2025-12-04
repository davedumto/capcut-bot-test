'use client'
import { useState, useEffect } from 'react'
import { formatTime, formatDate } from '@/lib/utils'
import { getSlots, createBooking } from '@/lib/api'

interface TimeSlot {
  id: string
  start_time: string
  end_time: string
  available: boolean
}

interface SlotSelectorProps {
  userDetails: { name: string; email: string }
  onBookingComplete: (sessionId: string) => void
}

interface GroupedSlots {
  lateNight: TimeSlot[]
  morning: TimeSlot[]
  afternoon: TimeSlot[]
  evening: TimeSlot[]
}

interface TimePeriod {
  key: keyof GroupedSlots
  label: string
  icon: string
  timeRange: string
}

export default function SlotSelector({ userDetails, onBookingComplete }: SlotSelectorProps) {
  const [slots, setSlots] = useState<TimeSlot[]>([])
  const [selectedSlot, setSelectedSlot] = useState<TimeSlot | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isBooking, setIsBooking] = useState(false)
  const [error, setError] = useState('')
  const [showConfirmation, setShowConfirmation] = useState(false)

  const timePeriods: TimePeriod[] = [
    { key: 'lateNight', label: 'Late Night', icon: '🌜', timeRange: '12 AM - 6 AM' },
    { key: 'morning', label: 'Morning', icon: '☀️', timeRange: '6 AM - 12 PM' },
    { key: 'afternoon', label: 'Afternoon', icon: '🌤️', timeRange: '12 PM - 6 PM' },
    { key: 'evening', label: 'Evening', icon: '🌙', timeRange: '6 PM - 12 AM' }
  ]

  useEffect(() => {
    fetchSlots()
  }, [])

  const fetchSlots = async () => {
    try {
      const data = await getSlots()
      
      setSlots(data.slots)
      if (data.slots.length === 0) {
        setError('No available slots for today. Please check back later.')
      }
    } catch (err) {
      console.error('Failed to fetch slots:', err)
      setError(
        err instanceof Error 
          ? err.message
          : 'Could not load available slots. Please try again.'
      )
    } finally {
      setIsLoading(false)
    }
  }

  const groupSlotsByPeriod = (slots: TimeSlot[]): GroupedSlots => {
    // Now we support full 24-hour coverage
    return slots.reduce((groups: GroupedSlots, slot) => {
      const startTime = new Date(slot.start_time)
      const hour = startTime.getHours()
      
      if (hour >= 0 && hour < 6) {
        groups.lateNight.push(slot)
      } else if (hour >= 6 && hour < 12) {
        groups.morning.push(slot)
      } else if (hour >= 12 && hour < 18) {
        groups.afternoon.push(slot)
      } else if (hour >= 18) {
        groups.evening.push(slot)
      }
      
      return groups
    }, { lateNight: [], morning: [], afternoon: [], evening: [] })
  }


  const handleSlotSelection = (slot: TimeSlot) => {
    setSelectedSlot(slot)
    setShowConfirmation(true)
    setError('')
  }

  const handleBooking = async () => {
    if (!selectedSlot) return
    
    setIsBooking(true)
    setError('')
    
    try {
      const data = await createBooking({
        name: userDetails.name,
        email: userDetails.email,
        slot_id: selectedSlot.id,
      })
      
      if (data.success && data.session_id) {
        onBookingComplete(data.session_id)
      } else {
        throw new Error('Invalid booking response')
      }
    } catch (err) {
      console.error('Booking error:', err)
      
      // Handle specific error cases with user-friendly messages
      let errorMessage = 'Failed to book slot. Please try again.'
      
      if (err instanceof Error) {
        const message = err.message.toLowerCase()
        
        if (message.includes('already booked') || message.includes('duplicate')) {
          errorMessage = '⚠️ You have already booked a slot today. Each email can only book one slot per day.'
        } else if (message.includes('not available') || message.includes('unavailable')) {
          errorMessage = '❌ This slot is no longer available. Please choose another slot.'
        } else if (message.includes('invalid slot')) {
          errorMessage = '❌ Invalid slot selected. Please refresh and try again.'
        } else {
          errorMessage = err.message
        }
      }
      
      setError(errorMessage)
    } finally {
      setIsBooking(false)
    }
  }

  const renderSlotCard = (slot: TimeSlot) => {
    const now = new Date()
    const slotStart = new Date(slot.start_time)
    const isPast = slotStart <= now
    
    // Determine slot status: available, booked, or past
    let status, bgClass, borderClass, statusBadge, isClickable
    
    if (isPast) {
      status = 'Past'
      bgClass = 'bg-rough/10'
      borderClass = 'border-rough/30'
      statusBadge = { bg: 'bg-rough/20', text: 'text-rough', label: 'Past' }
      isClickable = false
    } else if (slot.available) {
      status = 'Available'
      bgClass = 'bg-pale hover:shadow-warm hover:scale-105'
      borderClass = 'border-gold/30 hover:border-gold'
      statusBadge = { bg: 'bg-gold', text: 'text-pale', label: '✓' }
      isClickable = true
    } else {
      status = 'Booked'
      bgClass = 'bg-bookedslot'
      borderClass = 'border-bookedslot'
      statusBadge = { bg: 'bg-bookedslot', text: 'text-rough', label: '✗' }
      isClickable = false
    }
    
    return (
      <button
        key={slot.id}
        onClick={isClickable ? () => handleSlotSelection(slot) : undefined}
        className={`p-3 text-center rounded-lg transition-all duration-200 border-2 min-h-[100px] flex flex-col justify-between ${bgClass} ${borderClass} ${
          isClickable ? 'cursor-pointer' : 'cursor-not-allowed opacity-60'
        }`}
        disabled={!isClickable}
      >
        <div className={`text-sm font-bold ${isPast ? 'text-rough/60' : 'text-rough'}`}>
          {formatTime(slot.start_time)}
        </div>
        <div className={`text-xs ${isPast ? 'text-rough/40' : 'text-darknavy'}`}>
          to
        </div>
        <div className={`text-sm font-bold ${isPast ? 'text-rough/60' : 'text-rough'}`}>
          {formatTime(slot.end_time)}
        </div>
        <div className={`inline-flex items-center justify-center px-2 py-1 rounded-full text-xs font-medium mt-2 ${statusBadge.bg} ${statusBadge.text}`}>
          {statusBadge.label}
        </div>
      </button>
    )
  }

  const groupedSlots = groupSlotsByPeriod(slots)
  const today = new Date()
  
  if (isLoading) {
    return (
      <div className="bg-pale rounded-lg border-2 border-gold/20 p-6 shadow-warm">
        <h2 className="text-xl font-semibold text-rough mb-6">
          Loading Available Slots...
        </h2>
        <div className="animate-pulse space-y-4">
          <div className="h-16 bg-gold/20 rounded-lg"></div>
          <div className="h-16 bg-gold/20 rounded-lg"></div>
          <div className="h-16 bg-gold/20 rounded-lg"></div>
        </div>
      </div>
    )
  }

  if (showConfirmation && selectedSlot) {
    return (
      <div className="bg-pale rounded-lg border-2 border-gold p-6 shadow-warm">
        <h3 className="text-xl font-bold text-rough mb-4 text-center">
          Confirm Your Booking
        </h3>
        
        <div className="bg-gold/10 border-2 border-gold rounded-lg p-6 mb-6">
          <div className="text-center mb-4">
            <div className="text-2xl font-bold text-rough">
              {formatTime(selectedSlot.start_time)} - {formatTime(selectedSlot.end_time)}
            </div>
            <div className="text-sm text-darknavy mt-1">
              Duration: 1.5 hours
            </div>
            <div className="text-sm text-darknavy">
              Date: {formatDate(selectedSlot.start_time)}
            </div>
          </div>
          
          {error && (
            <div className="bg-rough/10 border-2 border-rough rounded-lg p-4 mb-4">
              <div className="text-rough text-sm font-medium">{error}</div>
            </div>
          )}
        </div>
        
        <div className="flex gap-3">
          <button
            onClick={() => {
              setShowConfirmation(false)
              setSelectedSlot(null)
              setError('')
            }}
            className="flex-1 bg-pale border-2 border-gold text-rough py-3 px-4 rounded-md hover:bg-gold/10 transition-colors font-medium"
          >
            Choose Different Slot
          </button>
          
          <button
            onClick={handleBooking}
            disabled={isBooking}
            className="flex-1 bg-gold text-pale py-3 px-4 rounded-md hover:bg-gold/90 transition-colors font-semibold disabled:opacity-50 flex items-center justify-center min-h-[48px]"
          >
            {isBooking ? (
              <>
                <svg className="animate-spin -ml-1 mr-2 h-5 w-5 text-pale" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Booking...
              </>
            ) : (
              'Confirm & Book'
            )}
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-pale rounded-lg border-2 border-gold/20 p-6 shadow-warm">
      <h2 className="text-xl font-semibold text-rough mb-6">
        AVAILABLE SLOTS
      </h2>
      
      {error && (
        <div className="bg-rough/10 border-2 border-rough rounded-lg p-4 mb-6">
          <div className="flex items-start gap-3">
            <div className="text-rough text-lg">⚠️</div>
            <div>
              <div className="font-semibold text-rough">Error</div>
              <div className="text-sm text-rough mt-1">{error}</div>
              <button
                onClick={() => {
                  setError('')
                  fetchSlots()
                }}
                className="bg-gold text-pale px-4 py-2 rounded-md text-sm font-medium mt-3 hover:bg-gold/90 transition-colors"
              >
                Retry
              </button>
            </div>
          </div>
        </div>
      )}
      
      {slots.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-4xl mb-4">😔</div>
          <div className="text-lg font-semibold text-rough mb-2">
            No available slots for today
          </div>
          <div className="text-darknavy">
            Please check back later for new time slots.
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          {timePeriods.map((period) => {
            const periodSlots = groupedSlots[period.key]
            if (periodSlots.length === 0) return null
            
            return (
              <div key={period.key} className="space-y-4">
                <h3 className="text-lg font-semibold text-rough flex items-center gap-2">
                  <span className="text-xl">{period.icon}</span>
                  {period.label} ({period.timeRange})
                </h3>
                
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
                  {periodSlots.map(renderSlotCard)}
                </div>
              </div>
            )
          })}
          
          {/* Show slot statistics */}
          <div className="text-center pt-4 border-t-2 border-gold/30">
            <p className="text-sm text-darknavy">
              <span className="font-semibold text-gold">{slots.filter(s => s.available && new Date(s.start_time) > new Date()).length}</span> Available
              {' '} • <span className="font-semibold text-bookedslot">{slots.filter(s => !s.available && new Date(s.start_time) > new Date()).length}</span> Booked
              {' '} • <span className="font-semibold text-rough">{slots.filter(s => new Date(s.start_time) <= new Date()).length}</span> Past
              {' '} • <span className="font-semibold text-darknavy">{slots.length}</span> Total
            </p>
          </div>
        </div>
      )}
    </div>
  )
}