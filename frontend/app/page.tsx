'use client'
import { Hero } from '@/components/Hero'
import { HowItWorks } from '@/components/HowItWorks'
import { SocialProof } from '@/components/SocialProof'
import { Pricing } from '@/components/Pricing'
import { FAQ } from '@/components/FAQ'
import { Footer } from '@/components/Footer'
import { useRouter } from 'next/navigation'

export default function Home() {
  const router = useRouter()

  const handleBookNow = () => {
    router.push('/auth')
  }

  return (
    <main className="min-h-screen w-full bg-background text-white selection:bg-primary selection:text-background">
      <Hero onBookNow={handleBookNow} />
      <HowItWorks onBookNow={handleBookNow} />
      <SocialProof />
      <Pricing />
      <FAQ onBookNow={handleBookNow} />
      <Footer onBookSlot={handleBookNow} />
    </main>
  )
}