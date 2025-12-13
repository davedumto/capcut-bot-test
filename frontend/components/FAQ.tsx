'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { ArrowRight, ChevronDown } from 'lucide-react';
import { useState } from 'react';

interface FAQProps {
  onBookNow: () => void;
}

const faqs = [
  {
    question: "How do I get my CapCut Pro credentials?",
    answer: "Once you book and pay for a slot, you'll receive login credentials via email the moment your session starts. Just copy the username and password, log into CapCut, and start editing."
  },
  {
    question: "What if I need more than 90 minutes?",
    answer: "You can book multiple back-to-back slots if you need more time. Each slot is 90 minutes (1.5 hours), so booking 2 slots gives you 3 hours of editing time."
  },
  {
    question: "What happens when my session ends?",
    answer: "Your access automatically ends after 90 minutes. The CapCut account password is reset for security, and the slot becomes available for the next user."
  },
  {
    question: "Is this secure and legal?",
    answer: "Yes. You're paying for timed access to a shared CapCut Pro account—similar to how coworking spaces rent desks by the hour. Each session uses a fresh password for security."
  }
];

export function FAQ({ onBookNow }: FAQProps) {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  const toggleFAQ = (index: number) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <section className="relative w-full py-24 px-4 overflow-hidden">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            FAQ
          </h2>
        </motion.div>

        {/* FAQ Accordion */}
        <div className="space-y-4">
          {faqs.map((faq, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 overflow-hidden hover:border-white/20 transition-colors"
            >
              {/* Question - Clickable */}
              <button
                onClick={() => toggleFAQ(index)}
                className="w-full flex items-center justify-between p-6 text-left transition-all"
              >
                <h3 className="text-lg font-semibold text-white pr-8">
                  {faq.question}
                </h3>
                <ChevronDown 
                  className={`w-5 h-5 text-primary flex-shrink-0 transition-transform duration-300 ${
                    openIndex === index ? 'rotate-180' : ''
                  }`}
                />
              </button>

              {/* Answer - Animated */}
              <AnimatePresence>
                {openIndex === index && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3, ease: 'easeInOut' }}
                  >
                    <div className="px-6 pb-6 pt-0">
                      <p className="text-white/70 leading-relaxed">
                        {faq.answer}
                      </p>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ))}
        </div>

        {/* Final CTA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="mt-16 text-center"
        >
          <h3 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Still Paying Full Price for Software You Barely Use?
          </h3>
          <p className="text-xl text-white/70 mb-2">
            Join 200+ Nigerian creators who stopped wasting money on unused subscriptions.
          </p>
          <p className="text-lg text-white/60 mb-8">
            Your first session: <span className="text-white font-semibold">₦500</span>. Your savings this year: <span className="text-white font-semibold">₦100,000+</span>
          </p>
          
          <button
            onClick={onBookNow}
            className="group inline-flex items-center gap-2 px-8 py-4 bg-primary text-background rounded-full font-semibold text-lg hover:bg-primary/90 hover:shadow-2xl hover:shadow-primary/50 transition-all duration-300"
          >
            Get CapCut Pro Access Now — ₦500
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </button>

          <p className="text-sm text-white/50 mt-4">
            No subscription. No commitment. No regrets.
          </p>
        </motion.div>
      </div>
    </section>
  );
}
