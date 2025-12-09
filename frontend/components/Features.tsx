'use client';

import { motion } from 'framer-motion';
import { Lock, Zap, RotateCw } from 'lucide-react';

const features = [
  {
    icon: Lock,
    title: 'Secure Access',
    description: 'Credentials sent directly to you. No sharing, no interruptions.'
  },
  {
    icon: Zap,
    title: 'Instant Delivery',
    description: 'Email arrives the second your slot begins. Zero downtime.'
  },
  {
    icon: RotateCw,
    title: 'Auto-Rotate',
    description: 'Every session uses a fresh password for maximum security.'
  }
];

export function Features() {
  return (
    <section className="py-24 px-4 w-full bg-gradient-to-b from-transparent to-white/[0.02]">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl md:text-5xl font-bold text-white mb-4">
            Why creators choose Slotio
          </h2>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              whileHover={{ y: -5 }}
              className="p-8 rounded-3xl bg-white/5 border border-white/10 backdrop-blur-md hover:bg-white/[0.07] hover:border-white/20 transition-all duration-300"
            >
              <div className="w-12 h-12 rounded-xl bg-accent/20 flex items-center justify-center mb-6 text-accent">
                <feature.icon className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-white mb-3">
                {feature.title}
              </h3>
              <p className="text-white/60 leading-relaxed">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
