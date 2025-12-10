'use client'
import { Hero } from '@/components/Hero'
import { HowItWorks } from '@/components/HowItWorks'
import { Features } from '@/components/Features'
import { CTASection } from '@/components/CTASection'
import { Footer } from '@/components/Footer'
import { useRouter } from 'next/navigation'

export default function Home() {
  const router = useRouter()

  const handleBookNow = () => {
    router.push('/book-slot')
  }

  return (
    <main className="min-h-screen w-full bg-background text-white selection:bg-primary selection:text-background">
      <Hero onBookNow={handleBookNow} />
      <HowItWorks />
      <Features />
      <CTASection onViewSlots={handleBookNow} />
      <Footer onBookSlot={handleBookNow} />
    </main>
  )
}