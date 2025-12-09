'use client';

import { motion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';
import Link from 'next/link';

interface HeroProps {
  onBookNow: () => void;
}

export function Hero({ onBookNow }: HeroProps) {
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
            onClick={onBookNow}
            className="hidden sm:block text-white/70 hover:text-white transition-colors font-medium text-sm"
          >
            View Slots
          </button>
          <button 
            onClick={onBookNow}
            className="bg-primary text-background px-5 py-2 rounded-full font-semibold text-sm hover:bg-primary/90 transition-colors"
          >
            Book Now
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

      {/* Content */}
      <div className="max-w-4xl mx-auto text-center z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 mb-8 backdrop-blur-sm">
            <span className="w-2 h-2 rounded-full bg-primary animate-pulse"></span>
            <span className="text-sm text-white/80 font-medium">
              Trusted by 200+ creators
            </span>
          </div>

          <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-[1.1] tracking-tight">
            Book a slot. <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent">
              Get access when it starts.
            </span>
          </h1>

          <p className="text-lg md:text-xl text-white/60 max-w-xl mx-auto mb-10 leading-relaxed">
            Scheduled access to premium tools—automatically. No waiting, no
            shared passwords, just pure creative flow.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <motion.button
              onClick={onBookNow}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full sm:w-auto px-8 py-4 bg-primary text-background rounded-full font-bold text-base shadow-[0_0_20px_rgba(0,229,189,0.3)] hover:shadow-[0_0_30px_rgba(0,229,189,0.5)] transition-shadow flex items-center justify-center gap-2"
            >
              Get Started <ArrowRight className="w-4 h-4" />
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.02, backgroundColor: 'rgba(255,255,255,0.05)' }}
              whileTap={{ scale: 0.98 }}
              className="w-full sm:w-auto px-8 py-4 border border-white/20 text-white rounded-full font-semibold text-base hover:border-white/40 transition-colors"
            >
              See How It Works
            </motion.button>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
