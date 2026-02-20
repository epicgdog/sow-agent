import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SOW Agent — Clean, approachable B2B SaaS",
  description: "Statement of Work agent dashboard",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-[#F9FAFB] text-slate-900 antialiased">
        {children}
      </body>
    </html>
  );
}
