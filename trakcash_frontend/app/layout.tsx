export const metadata = {
  title: 'TrackCash',
  description: 'Track your spending effortlessly',
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