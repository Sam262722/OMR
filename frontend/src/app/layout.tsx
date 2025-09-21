import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'

const inter = Inter({ 
  subsets: ['latin'],
  variable: '--font-inter',
})

export const metadata: Metadata = {
  title: 'OMR Evaluator - Advanced Optical Mark Recognition',
  description: 'Professional OMR evaluation system with AI-powered accuracy, real-time processing, and comprehensive analytics for educational institutions.',
  keywords: ['OMR', 'optical mark recognition', 'education', 'evaluation', 'assessment', 'automated grading'],
  authors: [{ name: 'OMR Evaluator Team' }],
  viewport: 'width=device-width, initial-scale=1',
  themeColor: '#2563eb',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={inter.variable} suppressHydrationWarning>
      <body className={`${inter.className} antialiased bg-gray-50 dark:bg-gray-900`} suppressHydrationWarning>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  )
}
