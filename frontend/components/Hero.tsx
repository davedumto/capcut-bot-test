'use client';

import { motion } from 'framer-motion';
import { ArrowRight, Lock, Zap, Check } from 'lucide-react';
import { useRouter } from 'next/navigation';

interface HeroProps {
  onBookNow: () => void;
}

export function Hero({ onBookNow }: HeroProps) {
  const router = useRouter();
  
  return (
    <section className="relative min-h-screen w-full flex flex-col items-center justify-center overflow-hidden px-4 pt-20">
      {/* Navbar */}
      <nav className="absolute top-0 left-0 right-0 flex items-center justify-between px-6 py-6 max-w-7xl mx-auto w-full z-50">
        <div className="flex items-center">
          <span className="font-display text-2xl font-bold text-white tracking-tight">
            Slotio
          </span>
        </div>
        <div className="flex items-center gap-4">
          <button 
            onClick={() => router.push('/auth')}
            className="text-white/70 hover:text-white transition-colors font-medium text-sm"
          >
            Login
          </button>
          <button 
            onClick={() => router.push('/auth')}
            className="bg-primary text-background px-5 py-2 rounded-full font-semibold text-sm hover:bg-primary/90 transition-colors"
          >
            Get Started
          </button>
        </div>
      </nav>

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
            Stop Paying ₦15,000/month for CapCut Pro.
            <br />
            Pay ₦500 when you actually need it.
          </h1>
        </motion.div>

        {/* Subheadline */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="text-lg md:text-xl text-white/70 max-w-3xl mx-auto leading-relaxed"
        >
          Why pay for 30 days when you only edit for 3 hours? Get instant CapCut Pro access for just ₦500 per session.
          Your credentials arrive in 60 seconds.
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

        {/* Trust Badges */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.8 }}
          className="flex flex-wrap items-center justify-center gap-6 text-sm text-white/60 pt-4"
        >
          <div className="flex items-center gap-2">
            <Lock className="w-4 h-4 text-primary" />
            <span>Secure payment via Paystack</span>
          </div>
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-accent" />
            <span>Access in under 60 seconds</span>
          </div>
          <div className="flex items-center gap-2">
            <Check className="w-4 h-4 text-green-500" />
            <span>No subscription trap</span>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
