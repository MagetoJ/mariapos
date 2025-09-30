import type React from "react"
import type { Metadata } from "next"
import { Work_Sans } from "next/font/google"
import "./globals.css"
import { ThemeProvider } from "@/components/theme-provider"

const workSans = Work_Sans({
  subsets: ["latin"],
  variable: "--font-work-sans",
  weight: ["300", "400", "500", "600", "700"],
})

export const metadata: Metadata = {
  title: "Maria Havens POS",
  description: "Hotel & Restaurant Point of Sale System",
  manifest: "/manifest.json",
  themeColor: "#164e63",
  viewport: "width=device-width, initial-scale=1, maximum-scale=1",
    generator: 'v0.app'
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${workSans.variable} antialiased`} suppressHydrationWarning>
      <body className="font-sans">
        <ThemeProvider defaultTheme="light" storageKey="maria-havens-theme">
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}
