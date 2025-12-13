'use client';

import { motion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';

interface PainSectionProps {
  onBookNow: () => void;
}

export function PainSection({ onBookNow }: PainSectionProps) {
  return (
    <section className="relative w-full py-24 px-4 overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-b from-background via-red-950/10 to-background -z-10" />
      
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center space-y-4 mb-16"
        >
          <h2 className="font-display text-4xl md:text-5xl font-bold text-white">
            You're Throwing Money Away Every Month
          </h2>
          <p className="text-xl text-white/70">
            The math doesn't lie:
          </p>
        </motion.div>

        {/* Cost Comparison Table */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="bg-white/5 backdrop-blur-xl rounded-3xl border border-white/10 overflow-hidden mb-12"
        >
          <div className="grid grid-cols-3 text-center">
            {/* Header Row */}
            <div className="p-6 bg-white/5 border-b border-r border-white/10">
              <p className="text-sm text-white/60 mb-2">What you pay</p>
            </div>
            <div className="p-6 bg-white/5 border-b border-r border-white/10">
              <p className="text-sm text-white/60 mb-2">What you use</p>
            </div>
            <div className="p-6 bg-white/5 border-b border-white/10">
              <p className="text-sm text-white/60 mb-2">What you waste</p>
            </div>

            {/* Data Row */}
            <div className="p-8 border-r border-white/10">
              <p className="text-3xl md:text-4xl font-bold text-primary">₦15,000</p>
              <p className="text-sm text-white/50 mt-2">/month</p>
            </div>
            <div className="p-8 border-r border-white/10">
              <p className="text-3xl md:text-4xl font-bold text-white">~3-4 hours</p>
              <p className="text-sm text-white/50 mt-2">of actual editing</p>
            </div>
            <div className="p-8">
              <p className="text-3xl md:text-4xl font-bold text-red-500">₦12,000+</p>
              <p className="text-sm text-white/50 mt-2">sitting unused</p>
            </div>
          </div>
        </motion.div>

        {/* Value Prop */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="text-center space-y-6"
        >
          <p className="text-xl md:text-2xl text-white/80 max-w-3xl mx-auto">
            You're paying for 720 hours of access. You use maybe 6.
          </p>
          
          <p className="text-2xl md:text-3xl font-bold text-white">
            That's ₦144,000 per year for software you barely touch.
          </p>

          <p className="text-lg text-white/60">
            What if you only paid for the hours you actually edit?
          </p>

          <div className="pt-4">
            <button
              onClick={onBookNow}
              className="group inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-primary to-accent rounded-full font-semibold text-lg hover:shadow-2xl hover:shadow-primary/50 transition-all duration-300"
            >
              Stop Overpaying — Try ₦500 Session
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </button>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
