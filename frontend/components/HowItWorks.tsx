'use client';

import { motion } from 'framer-motion';
import { Calendar, CreditCard, Mail, Sparkles, ArrowRight } from 'lucide-react';

interface HowItWorksProps {
  onBookNow?: () => void;
}

const steps = [
  {
    icon: Calendar,
    number: "1",
    title: 'Pick Your Slot',
    description: 'Choose any 1.5-hour window. 16 slots available daily.'
  },
  {
    icon: CreditCard,
    number: "2",
    title: 'Pay ₦500',
    description: 'One-time payment. No subscription. No auto-renewal.'
  },
  {
    icon: Mail,
    number: "3",
    title: 'Get Your Access',
    description: 'Credentials sent instantly when your slot starts.'
  },
  {
    icon: Sparkles,
    number: "4",
    title: 'Edit Like a Pro',
    description: 'Full CapCut Pro features. All templates and effects unlocked.'
  }
];

export function HowItWorks({ onBookNow }: HowItWorksProps) {
  return (
    <section id="how-it-works" className="py-24 px-4 relative w-full">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            From Payment to Editing in 90 Seconds
          </h2>
          <p className="text-white/60 text-lg max-w-2xl mx-auto">
            Simple, secure, and ridiculously fast.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 relative mb-12">
          {/* Connecting line for desktop */}
          <div className="hidden lg:block absolute top-12 left-[12%] right-[12%] h-[2px] bg-gradient-to-r from-transparent via-primary/30 to-transparent -z-10" />

          {steps.map((step, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.15 }}
              className="relative flex flex-col items-center text-center group"
            >
              {/* Step Number Badge */}
              <div className="absolute -top-4 left-1/2 -translate-x-1/2 w-8 h-8 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center text-background font-bold text-sm z-10">
                {step.number}
              </div>

              {/* Icon Container */}
              <div className="w-24 h-24 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-sm flex items-center justify-center mb-6 group-hover:border-primary/50 group-hover:shadow-[0_0_30px_rgba(0,229,189,0.15)] transition-all duration-300">
                <step.icon className="w-10 h-10 text-primary" />
              </div>

              {/* Content */}
              <h3 className="text-xl font-bold text-white mb-3">
                {step.title}
              </h3>
              <p className="text-white/60 leading-relaxed text-sm">
                {step.description}
              </p>
            </motion.div>
          ))}
        </div>

        {/* CTA */}
        {onBookNow && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.8 }}
            className="text-center pt-8"
          >
            <button
              onClick={onBookNow}
              className="group inline-flex items-center gap-2 px-8 py-4 bg-primary text-background rounded-full font-semibold text-lg hover:bg-primary/90 hover:shadow-2xl hover:shadow-primary/50 transition-all duration-300"
            >
              Book Your First Slot — ₦500
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </button>
          </motion.div>
        )}
      </div>
    </section>
  );
}
