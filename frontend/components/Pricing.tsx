'use client'

import { motion } from 'framer-motion'
import { Check, Zap, Users } from 'lucide-react'
import { useRouter } from 'next/navigation'

export function Pricing() {
  const router = useRouter()

  const plans = [
    {
      name: 'Pay Per Edit',
      price: '₦500',
      period: 'per 1.5-hour session',
      description: 'For solo creators who edit when inspiration hits',
      icon: Zap,
      features: [
        'Full CapCut Pro access',
        'Instant credential delivery',
        'Fresh password every session',
        'All premium features unlocked',
        'Zero subscription needed'
      ],
      cta: 'Get Access Now',
      ctaAction: () => router.push('/auth'),
      popular: false,
      gradient: 'from-primary/20 to-accent/20',
      subtext: 'Perfect for: Content creators, students, freelancers'
    },
    {
      name: 'Team Plan',
      price: '₦5,000',
      period: 'per month',
      description: 'For agencies & teams sharing access intelligently',
      icon: Users,
      features: [
        'Up to 12 team members',
        'Unlimited booking',
        'Team dashboard & analytics',
        'Priority support',
        'Coordinate without chaos'
      ],
      cta: 'Start Team Plan',
      ctaAction: () => router.push('/auth'),
      popular: true,
      gradient: 'from-primary/30 to-accent/30',
      badge: 'BEST VALUE',
      subtext: 'Perfect for: Agencies, media companies, creative studios'
    }
  ]

  return (
    <section id="pricing" className="relative w-full py-20 px-4 overflow-hidden">
      {/* Background gradient */}
      <motion.div
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] rounded-full bg-gradient-radial from-primary/10 via-accent/5 to-transparent blur-3xl -z-10"
        animate={{
          opacity: [0.3, 0.5, 0.3],
          scale: [1, 1.1, 1]
        }}
        transition={{
          duration: 5,
          repeat: Infinity,
          ease: 'easeInOut'
        }}
      />

      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 mb-6 backdrop-blur-sm">
            <span className="w-2 h-2 rounded-full bg-primary animate-pulse"></span>
            <span className="text-sm text-white/80 font-medium">
              Simple, Transparent Pricing
            </span>
          </div>

          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Choose How You Want to Save
          </h2>
          <p className="text-lg text-white/60 max-w-2xl mx-auto">
            Pay only for what you use, or get your own account for your team
          </p>
        </motion.div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
          {plans.map((plan, index) => {
            const Icon = plan.icon
            
            return (
              <motion.div
                key={plan.name}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="relative"
              >
                {/* Popular badge */}
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 z-10">
                    <div className="px-4 py-1 rounded-full bg-gradient-to-r from-primary to-accent text-background text-xs font-bold shadow-lg">
                      {plan.badge || 'MOST POPULAR'}
                    </div>
                  </div>
                )}

                <motion.div
                  whileHover={{ scale: 1.02, y: -5 }}
                  transition={{ duration: 0.2 }}
                  className={`
                    relative p-8 rounded-2xl border backdrop-blur-sm h-full
                    ${plan.popular 
                      ? 'bg-white/10 border-primary/50 shadow-[0_0_30px_rgba(0,229,189,0.2)]' 
                      : 'bg-white/5 border-white/10 hover:border-white/20'
                    }
                  `}
                >
                  {/* Gradient overlay */}
                  <div className={`absolute inset-0 bg-gradient-to-br ${plan.gradient} rounded-2xl opacity-50 -z-10`} />

                  {/* Icon */}
                  <div className="mb-6">
                    <div className="inline-flex p-3 rounded-xl bg-primary/20 border border-primary/30">
                      <Icon className="w-6 h-6 text-primary" />
                    </div>
                  </div>

                  {/* Plan details */}
                  <h3 className="text-2xl font-bold text-white mb-2">{plan.name}</h3>
                  <p className="text-white/60 mb-6">{plan.description}</p>

                  {/* Price */}
                  <div className="mb-6">
                    <div className="flex items-baseline gap-2">
                      <span className="text-5xl font-bold text-white">{plan.price}</span>
                      <span className="text-white/60">{plan.period}</span>
                    </div>
                  </div>

                  {/* Features */}
                  <ul className="space-y-3 mb-8">
                    {plan.features.map((feature, idx) => (
                      <motion.li
                        key={idx}
                        initial={{ opacity: 0, x: -10 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.3 + idx * 0.05 }}
                        className="flex items-start gap-3"
                      >
                        <div className="mt-0.5 p-0.5 rounded-full bg-primary/20">
                          <Check className="w-4 h-4 text-primary" />
                        </div>
                        <span className="text-white/80 text-sm">{feature}</span>
                      </motion.li>
                    ))}
                  </ul>

                  {/* CTA Button */}
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={plan.ctaAction}
                    className={`
                      w-full py-4 px-6 rounded-xl font-bold text-base transition-all duration-200
                      ${plan.popular
                        ? 'bg-primary text-background shadow-[0_0_20px_rgba(0,229,189,0.3)] hover:shadow-[0_0_30px_rgba(0,229,189,0.5)]'
                        : 'bg-white/10 text-white border border-white/20 hover:bg-white/20'
                      }
                    `}
                  >
                    {plan.cta}
                  </motion.button>
                </motion.div>
              </motion.div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
