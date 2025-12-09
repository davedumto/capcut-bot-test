'use client';

import { motion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';

interface CTASectionProps {
  onViewSlots: () => void;
}

export function CTASection({ onViewSlots }: CTASectionProps) {
  return (
    <section className="py-24 px-4 w-full relative overflow-hidden">
      {/* Background Gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-background to-primary/5 z-0" />

      <div className="max-w-4xl mx-auto relative z-10 text-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="bg-white/5 border border-white/10 rounded-[2rem] p-12 md:p-20 backdrop-blur-xl overflow-hidden relative"
        >
          {/* Decorative glow */}
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full bg-gradient-radial from-primary/10 to-transparent opacity-50 pointer-events-none" />

          <h2 className="text-4xl md:text-6xl font-bold text-white mb-6">
            Ready to start editing?
          </h2>
          <p className="text-xl text-white/60 mb-10 max-w-xl mx-auto">
            Book your first slot in under 30 seconds. No subscription required.
          </p>

          <motion.button
            onClick={onViewSlots}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="px-10 py-5 bg-primary text-background rounded-full font-bold text-lg shadow-[0_0_20px_rgba(0,229,189,0.4)] hover:shadow-[0_0_40px_rgba(0,229,189,0.6)] transition-shadow inline-flex items-center gap-2"
          >
            View Available Slots <ArrowRight className="w-5 h-5" />
          </motion.button>
        </motion.div>
      </div>
    </section>
  );
}
