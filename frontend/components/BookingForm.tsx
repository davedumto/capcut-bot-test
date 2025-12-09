'use client'
import { useState } from 'react'
import { motion } from 'framer-motion'
import { ArrowRight } from 'lucide-react'

interface BookingFormProps {
  onSubmit: (data: { name: string; email: string }) => void
}

export default function BookingForm({ onSubmit }: BookingFormProps) {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    
    try {
      await onSubmit({ name, email })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <h2 className="text-2xl sm:text-3xl font-bold text-white mb-2 text-center">
        Book Your Session
      </h2>
      <p className="text-white/60 text-center mb-8">
        Enter your details to view available slots
      </p>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-white/80 mb-2">
            Name
          </label>
          <input
            type="text"
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full px-4 py-4 bg-white/5 border border-white/10 rounded-xl focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all text-white placeholder-white/40"
            placeholder="Your name"
            required
          />
        </div>
        
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-white/80 mb-2">
            Email
          </label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-4 py-4 bg-white/5 border border-white/10 rounded-xl focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all text-white placeholder-white/40"
            placeholder="your@email.com"
            required
          />
        </div>
        
        <motion.button
          type="submit"
          disabled={isLoading || !name.trim() || !email.trim()}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="w-full bg-primary text-background py-4 px-6 rounded-xl font-semibold hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-background disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center transition-all shadow-[0_0_20px_rgba(0,229,189,0.3)] hover:shadow-[0_0_30px_rgba(0,229,189,0.5)]"
        >
          {isLoading ? (
            <>
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-background" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Loading...
            </>
          ) : (
            <>
              Show Available Slots <ArrowRight className="w-5 h-5 ml-2" />
            </>
          )}
        </motion.button>
      </form>
    </motion.div>
  )
}