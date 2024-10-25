import './globals.css'

export const metadata = {
  title: 'LORA Scraper',
  description: 'Web interface for LORA scraper',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
