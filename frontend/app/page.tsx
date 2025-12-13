'use client'
import { Hero } from '@/components/Hero'
import { HowItWorks } from '@/components/HowItWorks'
import { SocialProof } from '@/components/SocialProof'
import { Pricing } from '@/components/Pricing'
import { FAQ } from '@/components/FAQ'
import { Footer } from '@/components/Footer'
import { useRouter } from 'next/navigation'
import dynamic from 'next/dynamic'

// Dynamic import to avoid SSR issues with WebGL
const Particles = dynamic(() => import('@/components/Particles'), { ssr: false })

export default function Home() {
  const router = useRouter()

  const handleBookNow = () => {
    router.push('/auth')
  }

  return (
    <main className="min-h-screen w-full bg-background text-white selection:bg-primary selection:text-background relative">
      {/* Particles Background */}
      <div className="fixed inset-0 z-0">
        <Particles
          particleColors={['#00FFB2', '#00FFB2', '#ffffff']}
          particleCount={150}
          particleSpread={10}
          speed={0.05}
          particleBaseSize={80}
          moveParticlesOnHover={true}
          particleHoverFactor={2}
          alphaParticles={true}
          disableRotation={false}
        />
      </div>
      
      {/* Content */}
      <div className="relative z-10">
        <Hero onBookNow={handleBookNow} />
        <HowItWorks onBookNow={handleBookNow} />
        <SocialProof />
        <Pricing />
        <FAQ onBookNow={handleBookNow} />
        <Footer onBookSlot={handleBookNow} />
      </div>
    </main>
  )
}