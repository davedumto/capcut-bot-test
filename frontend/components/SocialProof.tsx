'use client';

import { motion } from 'framer-motion';
import { Quote } from 'lucide-react';

export function SocialProof() {
  const testimonials = [
    {
      quote: "I was spending ₦15k monthly on CapCut Pro for my TikToks. Now I spend ₦2,000 max—and I edit MORE than before.",
      author: "Chioma A.",
      role: "Content Creator",
      location: "Lagos"
    },
    {
      quote: "My team of 5 editors used to need 5 subscriptions. Now we share slots for ₦5k/month total. That's ₦70,000 saved.",
      author: "Femi O.",
      role: "Agency Owner",
      location: "Abuja"
    },
    {
      quote: "I was skeptical about the 'instant access' thing. Paid at 2:34 AM, had credentials by 2:35. Wild.",
      author: "David M.",
      role: "YouTuber",
      location: "Port Harcourt"
    }
  ];

  return (
    <section id="social-proof" className="relative w-full py-24 px-4 overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-b from-background via-primary/5 to-background -z-10" />
      
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center space-y-4 mb-16"
        >
          <h2 className="font-display text-4xl md:text-5xl font-bold text-white">
            Why 200+ Nigerian Creators Switched to Slotio
          </h2>
        </motion.div>

        {/* Testimonials Grid */}
        <div className="grid md:grid-cols-3 gap-8">
          {testimonials.map((testimonial, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: index * 0.2 }}
              className="relative group"
            >
              <div className="relative bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 p-8 hover:bg-white/10 hover:border-primary/50 transition-all duration-300 h-full flex flex-col">
                {/* Quote Icon */}
                <div className="absolute -top-4 -left-4 w-12 h-12 bg-gradient-to-br from-primary to-accent rounded-full flex items-center justify-center">
                  <Quote className="w-6 h-6 text-background" />
                </div>

                {/* Quote */}
                <blockquote className="text-lg text-white/90 mb-6 leading-relaxed flex-grow">
                  "{testimonial.quote}"
                </blockquote>

                {/* Author */}
                <div className="flex items-center gap-3 border-t border-white/10 pt-4">
                  <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary/20 to-accent/20 flex items-center justify-center text-xl font-bold text-white">
                    {testimonial.author[0]}
                  </div>
                  <div>
                    <p className="font-semibold text-white">{testimonial.author}</p>
                    <p className="text-sm text-white/60">{testimonial.role}, {testimonial.location}</p>
                  </div>
                </div>

                {/* Hover Glow */}
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-primary/0 via-primary/0 to-accent/0 group-hover:from-primary/10 group-hover:to-accent/10 transition-all duration-300 -z-10" />
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
