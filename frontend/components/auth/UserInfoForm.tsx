'use client'
import { useState } from 'react'

interface UserInfoFormProps {
  email: string
  onSubmit: (name: string, marketingConsent: boolean) => void
}

export default function UserInfoForm({ email, onSubmit }: UserInfoFormProps) {
  const [name, setName] = useState('')
  const [marketingConsent, setMarketingConsent] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (name.trim()) {
      onSubmit(name.trim(), marketingConsent)
    }
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-semibold text-white mb-2">Almost there!</h2>
        <p className="text-white/60">Tell us a bit about yourself</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-white/80 mb-2">Your Name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Enter your full name"
            className="w-full p-3 bg-white/5 border border-white/20 rounded-xl text-white placeholder-white/40 focus:outline-none focus:border-primary focus:bg-white/10 transition-all"
            required
          />
        </div>

        <div className="flex items-start gap-3">
          <input
            type="checkbox"
            id="marketing"
            checked={marketingConsent}
            onChange={(e) => setMarketingConsent(e.target.checked)}
            className="mt-1 w-4 h-4 accent-primary"
          />
          <label htmlFor="marketing" className="text-white/80 text-sm">
            Send me tips and offers about CapCut sessions
            <p className="text-white/40 text-xs mt-1">
              We respect your privacy and comply with NDPR regulations
            </p>
          </label>
        </div>

        <button
          type="submit"
          disabled={!name.trim()}
          className="w-full bg-primary text-background font-semibold py-3 rounded-xl hover:bg-primary/90 disabled:bg-white/20 disabled:text-white/40 transition-colors"
        >
          Continue
        </button>
      </form>
    </div>
  )
}