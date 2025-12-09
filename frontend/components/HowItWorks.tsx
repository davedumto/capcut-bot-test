'use client';

import { motion } from 'framer-motion';
import { Clock, Mail, RefreshCw } from 'lucide-react';

const steps = [
  {
    icon: Clock,
    title: 'Pick a Time',
    description: 'Choose a slot that works for your schedule.'
  },
  {
    icon: Mail,
    title: 'Get Access',
    description: 'Credentials arrive securely at your start time.'
  },
  {
    icon: RefreshCw,
    title: 'Session Ends',
    description: 'Access rotates automatically when done.'
  }
];

export function HowItWorks() {
  return (
    <section className="py-24 px-4 relative w-full">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-100px' }}
          transition={{ duration: 0.5 }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl md:text-5xl font-bold text-white mb-4">
            How Slotio Works
          </h2>
          <p className="text-white/60 text-lg">
            Simple, secure, and automated.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
          {/* Connecting line for desktop */}
          <div className="hidden md:block absolute top-12 left-[16%] right-[16%] h-[2px] bg-gradient-to-r from-white/5 via-white/10 to-white/5 -z-10" />

          {steps.map((step, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-50px' }}
              transition={{ duration: 0.5, delay: index * 0.2 }}
              className="flex flex-col items-center text-center group"
            >
              <div className="w-24 h-24 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-sm flex items-center justify-center mb-6 group-hover:border-primary/50 group-hover:shadow-[0_0_30px_rgba(0,229,189,0.15)] transition-all duration-300">
                <step.icon className="w-10 h-10 text-primary" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">
                {step.title}
              </h3>
              <p className="text-white/60 max-w-[250px] leading-relaxed">
                {step.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
