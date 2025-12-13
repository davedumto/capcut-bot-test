'use client'
import { useState } from 'react'
import Link from 'next/link'
import EmailCheck from '@/components/auth/EmailCheck'
import MagicLinkForm from '@/components/auth/MagicLinkForm'
import PasswordLogin from '@/components/auth/PasswordLogin'
import UserInfoForm from '@/components/auth/UserInfoForm'

export default function AuthPage() {
  const [step, setStep] = useState<'email' | 'magic_link' | 'password' | 'new_user' | 'user_info'>('email')
  const [routeData, setRouteData] = useState<any>(null)
  const [userInfo, setUserInfo] = useState<{name: string, marketingConsent: boolean} | null>(null)

  const handleRouteDetected = (route: string, data: any) => {
    setRouteData(data)
    
    if (route === 'manager_dashboard') {
      setStep('password')
    } else if (route === 'pay_per_edit') {
      if (data.is_new) {
        setStep('user_info')
      } else {
        setStep('magic_link')
      }
    } else if (route === 'team_member') {
      setStep('magic_link')
    }
  }

  return (
    <div className="min-h-screen bg-background text-white flex flex-col px-4">
      {/* Header - Back button left, Logo center */}
      <div className="w-full max-w-5xl mx-auto pt-6 flex items-center">
        <Link href="/" className="inline-flex items-center gap-2 text-white/60 hover:text-white transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          <span className="text-sm font-medium">Back</span>
        </Link>
        <h1 className="flex-1 text-center text-4xl font-bold text-white tracking-tight pr-16">Slotio</h1>
      </div>

      {/* Auth form container */}
      <div className="flex-1 flex items-center justify-center">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <p className="text-white/60">Enter Email to signin or signup</p>
          </div>

          <div className="bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-8">
          {step === 'email' && (
            <EmailCheck onRouteDetected={handleRouteDetected} />
          )}

          {step === 'magic_link' && routeData && (
            <MagicLinkForm 
              email={routeData.email}
              name={userInfo?.name}
              marketingConsent={userInfo?.marketingConsent}
              onSuccess={() => {}} 
            />
          )}

          {step === 'password' && routeData && (
            <PasswordLogin email={routeData.email} />
          )}

          {step === 'user_info' && routeData && (
            <UserInfoForm 
              email={routeData.email}
              onSubmit={(name, marketingConsent) => {
                setUserInfo({name, marketingConsent})
                setStep('magic_link')
              }}
            />
          )}

          {step === 'new_user' && routeData && (
            <div className="text-center space-y-4">
              <h3 className="text-xl font-semibold">Welcome!</h3>
              <p className="text-white/60">
                Ready to book your first CapCut session for ₦500?
              </p>
              <Link 
                href={`/book-slot?email=${routeData.email}&new=true`}
                className="block w-full bg-primary text-background px-6 py-3 rounded-xl font-semibold hover:bg-primary/90 transition-colors text-center"
              >
                Continue to Booking
              </Link>
            </div>
          )}
        </div>

        {step !== 'email' && (
          <div className="text-center mt-4">
            <button
              onClick={() => {
                setStep('email')
                setRouteData(null)
              }}
              className="text-white/60 hover:text-white text-sm"
            >
              ← Back to email
            </button>
          </div>
        )}
        </div>
      </div>
    </div>
  )
}