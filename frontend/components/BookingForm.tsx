'use client'
import { useState } from 'react'

interface BookingFormProps {
  onSubmit: (data: { name: string; email: string }) => void
}

export default function BookingForm({ onSubmit }: BookingFormProps) {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  // Debug logging
  console.log('BookingForm state:', { name, email, nameValid: name.trim(), emailValid: email.trim(), isLoading })

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
    <div>
      <h2 className="text-xl sm:text-2xl font-bold text-rough mb-6 text-center">
        📝 Book Your Session
      </h2>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label htmlFor="name" className="block text-sm font-semibold text-rough mb-2">
            Name
          </label>
          <input
            type="text"
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full px-4 py-3 bg-pale border-2 border-gold/30 rounded-md focus:outline-none focus:border-gold transition-colors text-darknavy placeholder-darknavy/60"
            placeholder="Your Name"
            required
          />
        </div>
        
        <div>
          <label htmlFor="email" className="block text-sm font-semibold text-rough mb-2">
            Email
          </label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-4 py-3 bg-pale border-2 border-gold/30 rounded-md focus:outline-none focus:border-gold transition-colors text-darknavy placeholder-darknavy/60"
            placeholder="your@email.com"
            required
          />
        </div>
        
        <button
          type="submit"
          disabled={isLoading || !name.trim() || !email.trim()}
          className="w-full bg-gold text-pale py-3 px-6 rounded-md font-semibold hover:bg-gold/90 focus:outline-none focus:ring-2 focus:ring-gold focus:ring-offset-2 focus:ring-offset-pale disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center transition-colors min-h-[48px]"
        >
          {isLoading ? (
            <>
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-pale" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Processing...
            </>
          ) : (
            'Show Available Slots'
          )}
        </button>
      </form>
    </div>
  )
}