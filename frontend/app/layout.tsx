import type { Metadata } from 'next'
import { Space_Grotesk } from 'next/font/google'
import '@/styles/globals.css'

const spaceGrotesk = Space_Grotesk({ 
  subsets: ['latin'],
  variable: '--font-space-grotesk'
})

export const metadata: Metadata = {
  title: 'CapCut Sharing - Book Your Editing Session',
  description: 'Share a CapCut Pro account through time-slot booking',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={spaceGrotesk.variable}>
      <body className="min-h-screen bg-background">
        {children}
      </body>
    </html>
  )
}