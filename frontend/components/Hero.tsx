'use client';

import { motion } from 'framer-motion';
import { ArrowRight, Lock, Zap, Check } from 'lucide-react';
import { useRouter } from 'next/navigation';
import dynamic from 'next/dynamic';

const GlassSurface = dynamic(() => import('./GlassSurface'), { ssr: false });

interface HeroProps {
  onBookNow: () => void;
}

export function Hero({ onBookNow }: HeroProps) {
  const router = useRouter();
  
  return (
    <section className="relative min-h-screen w-full flex flex-col items-center justify-center px-4 pt-24">
      {/* Sticky Glass Navbar */}
      <div className="fixed top-4 left-1/2 -translate-x-1/2 z-50 w-[90%] max-w-5xl">
        <GlassSurface
          width="100%"
          height={80}
          borderRadius={28}
          blur={16}
          saturation={1.5}
          className="px-2"
        >
          <nav className="flex items-center justify-between w-full pl-6">
            <span className="font-display text-4xl font-bold text-white tracking-tight">
              Slotio
            </span>
            <div className="flex items-center gap-3">
              <button 
                onClick={() => router.push('/auth')}
                className="text-white/70 hover:text-white transition-colors font-medium text-lg px-3 py-1.5"
              >
                Login
              </button>
              <button 
                onClick={() => router.push('/auth')}
                className="bg-primary text-background px-4 py-1.5 rounded-xl font-semibold text-lg hover:bg-primary/90 transition-colors"
              >
                Get Started
              </button>
            </div>
          </nav>
        </GlassSurface>
      </div>

      {/* Background Animated Gradient */}
      <motion.div
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full bg-gradient-radial from-primary/20 via-accent/10 to-transparent blur-3xl -z-10"
        animate={{
          opacity: [0.5, 0.8, 0.5],
          scale: [1, 1.1, 1]
        }}
        transition={{
          duration: 4,
          repeat: Infinity,
          ease: 'easeInOut'
        }}
      />

      {/* Hero Content */}
      <div className="relative z-10 max-w-5xl mx-auto text-center space-y-8">
        {/* Social Proof Badge */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 backdrop-blur-sm border border-white/10"
        >
          <span className="text-sm text-white/80">
            Join 200+ Nigerian creators saving ₦10,000+ monthly
          </span>
        </motion.div>

        {/* Main Headline */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="space-y-4"
        >
          <h1 className="font-display text-5xl md:text-7xl font-bold leading-tight tracking-tight text-white">
            CapCut Pro. ₦500. Not ₦17,000.
          </h1>
        </motion.div>

        {/* Subheadline */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="text-lg md:text-2xl text-white/80 max-w-3xl mx-auto leading-relaxed font-medium tracking-wide"
          style={{ fontFamily: "'Syne', sans-serif" }}
        >
          Why pay for 30 days when you only edit for 3 hours? Get instant CapCut Pro access for just <span className="text-primary font-bold">₦500</span> per session.
        </motion.p>

        {/* CTAs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          className="flex flex-col sm:flex-row items-center justify-center gap-4"
        >
          <button
            onClick={onBookNow}
            className="group relative px-8 py-4 bg-primary text-background rounded-full font-semibold text-lg hover:bg-primary/90 hover:shadow-2xl hover:shadow-primary/50 transition-all duration-300 flex items-center gap-2"
          >
            Use CapCut Pro for ₦500
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </button>
        </motion.div>


      </div>
    </section>
  );
}
