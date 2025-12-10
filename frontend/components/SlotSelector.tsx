'use client'
import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Clock, RefreshCw, ChevronLeft } from 'lucide-react'
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
      
      let errorMessage = 'Failed to book slot. Please try again.'
      
      if (err instanceof Error) {
        const message = err.message.toLowerCase()
        
        if (message.includes('already booked') || message.includes('duplicate')) {
          errorMessage = 'You have already booked a slot today. Each email can only book one slot per day.'
        } else if (message.includes('not available') || message.includes('unavailable')) {
          errorMessage = 'This slot is no longer available. Please choose another slot.'
        } else if (message.includes('invalid slot')) {
          errorMessage = 'Invalid slot selected. Please refresh and try again.'
        } else {
          errorMessage = err.message
        }
      }
      
      setError(errorMessage)
    } finally {
      setIsBooking(false)
    }
  }

  const renderSlotCard = (slot: TimeSlot, index: number) => {
    const now = new Date()
    const slotStart = new Date(slot.start_time)
    const isPast = slotStart <= now
    
    let bgClass, borderClass, isClickable, statusBadge
    
    if (isPast) {
      bgClass = 'bg-white/5'
      borderClass = 'border-white/10'
      isClickable = false
      statusBadge = { bg: 'bg-white/10', text: 'text-white/40', label: 'Past' }
    } else if (slot.available) {
      bgClass = 'bg-white/5 hover:bg-white/10 hover:border-primary/50'
      borderClass = 'border-white/20'
      isClickable = true
      statusBadge = { bg: 'bg-primary/20', text: 'text-primary', label: 'Available' }
    } else {
      bgClass = 'bg-accent/10'
      borderClass = 'border-accent/30'
      isClickable = false
      statusBadge = { bg: 'bg-accent/20', text: 'text-accent', label: 'Booked' }
    }
    
    return (
      <motion.button
        key={slot.id}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: index * 0.03 }}
        onClick={isClickable ? () => handleSlotSelection(slot) : undefined}
        className={`p-3 text-center rounded-xl transition-all duration-200 border flex flex-col items-center justify-center gap-1 min-h-[120px] ${bgClass} ${borderClass} ${
          isClickable ? 'cursor-pointer group' : 'cursor-not-allowed opacity-60'
        }`}
        disabled={!isClickable}
        whileHover={isClickable ? { scale: 1.02 } : {}}
        whileTap={isClickable ? { scale: 0.98 } : {}}
      >
        <div className={`text-sm font-bold ${isPast ? 'text-white/40' : 'text-white'}`}>
          {formatTime(slot.start_time)} – {formatTime(slot.end_time)}
        </div>
        <div className={`inline-flex items-center justify-center px-2 py-0.5 rounded-full text-xs font-medium ${statusBadge.bg} ${statusBadge.text}`}>
          {statusBadge.label}
        </div>
      </motion.button>
    )
  }

  const groupedSlots = groupSlotsByPeriod(slots)
  
  if (isLoading) {
    return (
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-8"
      >
        <h2 className="text-xl font-semibold text-white mb-6">
          Loading Available Slots...
        </h2>
        <div className="animate-pulse space-y-4">
          <div className="h-16 bg-white/10 rounded-xl"></div>
          <div className="h-16 bg-white/10 rounded-xl"></div>
          <div className="h-16 bg-white/10 rounded-xl"></div>
        </div>
      </motion.div>
    )
  }

  if (showConfirmation && selectedSlot) {
    return (
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-8"
      >
        <h3 className="text-2xl font-bold text-white mb-6 text-center">
          Confirm Your Booking
        </h3>
        
        <div className="bg-primary/10 border border-primary/30 rounded-xl p-6 mb-6">
          <div className="text-center mb-4">
            <div className="text-3xl font-bold text-white mb-2">
              {formatTime(selectedSlot.start_time)} – {formatTime(selectedSlot.end_time)}
            </div>
            <div className="text-white/60">
              Duration: 1.5 hours • {formatDate(selectedSlot.start_time)}
            </div>
          </div>
          
          {error && (
            <div className="bg-red-500/20 border border-red-500/50 rounded-xl p-4 mt-4">
              <div className="text-red-400 text-sm font-medium">{error}</div>
            </div>
          )}
        </div>
        
        <div className="flex gap-3">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => {
              setShowConfirmation(false)
              setSelectedSlot(null)
              setError('')
            }}
            className="flex-1 border border-white/20 text-white py-4 px-4 rounded-xl hover:bg-white/5 transition-colors font-medium flex items-center justify-center gap-2"
          >
            <ChevronLeft className="w-4 h-4" /> Choose Different Slot
          </motion.button>
          
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleBooking}
            disabled={isBooking}
            className="flex-1 bg-primary text-background py-4 px-4 rounded-xl hover:bg-primary/90 transition-colors font-bold disabled:opacity-50 flex items-center justify-center shadow-[0_0_20px_rgba(0,229,189,0.3)]"
          >
            {isBooking ? (
              <>
                <svg className="animate-spin -ml-1 mr-2 h-5 w-5 text-background" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Booking...
              </>
            ) : (
              'Confirm & Book'
            )}
          </motion.button>
        </div>
      </motion.div>
    )
  }

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-6 sm:p-8"
    >
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-white">
          Available Slots
        </h2>
        <button 
          onClick={fetchSlots}
          className="text-primary hover:text-primary/80 transition-colors"
        >
          <RefreshCw className="w-5 h-5" />
        </button>
      </div>
      
      {error && (
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="bg-red-500/20 border border-red-500/40 rounded-xl p-4 mb-6"
        >
          <div className="flex items-start gap-3">
            <div className="text-red-400 text-lg">⚠️</div>
            <div>
              <div className="font-semibold text-red-400">Error</div>
              <div className="text-sm text-red-300 mt-1">{error}</div>
              <button
                onClick={() => {
                  setError('')
                  fetchSlots()
                }}
                className="bg-primary text-background px-4 py-2 rounded-lg text-sm font-medium mt-3 hover:bg-primary/90 transition-colors"
              >
                Retry
              </button>
            </div>
          </div>
        </motion.div>
      )}
      
      {slots.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-4xl mb-4">😔</div>
          <div className="text-lg font-semibold text-white mb-2">
            No available slots for today
          </div>
          <div className="text-white/60">
            Please check back later for new time slots.
          </div>
        </div>
      ) : (
        <div className="space-y-8">
          {timePeriods.map((period) => {
            const periodSlots = groupedSlots[period.key]
            if (periodSlots.length === 0) return null
            
            return (
              <div key={period.key} className="space-y-4">
                <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                  <span className="text-xl">{period.icon}</span>
                  {period.label} 
                  <span className="text-white/40 font-normal text-sm">({period.timeRange})</span>
                </h3>
                
                <div className="grid gap-3" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))' }}>
                  {periodSlots.map((slot, index) => renderSlotCard(slot, index))}
                </div>
              </div>
            )
          })}
          
          {/* Slot statistics */}
          <div className="text-center pt-6 border-t border-white/10">
            <p className="text-sm text-white/60">
              <span className="font-semibold text-primary">{slots.filter(s => s.available && new Date(s.start_time) > new Date()).length}</span> Available
              {' '} • <span className="font-semibold text-accent">{slots.filter(s => !s.available && new Date(s.start_time) > new Date()).length}</span> Booked
              {' '} • <span className="font-semibold text-white/40">{slots.filter(s => new Date(s.start_time) <= new Date()).length}</span> Past
            </p>
          </div>
        </div>
      )}
    </motion.div>
  )
}