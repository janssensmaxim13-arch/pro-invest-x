import type { Metadata } from 'next'
import { Inter, Poppins } from 'next/font/google'
import '@/styles/globals.css'
import { Providers } from './providers'

const inter = Inter({ 
  subsets: ['latin'],
  variable: '--font-inter',
})

const poppins = Poppins({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700'],
  variable: '--font-poppins',
})

export const metadata: Metadata = {
  title: {
    default: 'ProInvestiX Enterprise',
    template: '%s | ProInvestiX',
  },
  description: 'Enterprise Platform voor Marokkaans Voetbal - NTSP, TicketChain, Diaspora Wallet & meer',
  keywords: ['voetbal', 'Marokko', 'scouting', 'NTSP', 'transfers', 'tickets', 'WK 2030'],
  authors: [{ name: 'ProInvestiX' }],
  creator: 'ProInvestiX',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="nl" suppressHydrationWarning>
      <body className={`${inter.variable} ${poppins.variable} font-sans antialiased`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
