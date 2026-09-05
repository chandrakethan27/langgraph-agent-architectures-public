import type { Metadata } from "next";
import { Instrument_Serif, Inter, IBM_Plex_Mono } from "next/font/google";
import "./globals.css";

const instrumentSerif = Instrument_Serif({
  weight: "400",
  subsets: ["latin"],
  variable: "--font-display",
});

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-body",
});

const plexMono = IBM_Plex_Mono({
  weight: ["400", "500", "600"],
  subsets: ["latin"],
  variable: "--font-mono",
});

export const metadata: Metadata = {
  title: "LangGraph Agent Architectures | Chandra Kethan",
  description:
    "A comprehensive, production-grade interactive platform showcasing 14 core AI Agent Architectures implemented using LangGraph, LangChain, and Claude — paired with a modern Next.js interactive visualization interface.",
  keywords: [
    "LangGraph",
    "AI Agents",
    "Agent Architectures",
    "Multi-Agent Systems",
    "ReAct Agent",
    "RAG",
    "LangChain",
    "Claude",
    "FastAPI",
    "Next.js",
  ],
  icons: {
    icon: "https://www.chandrakethan.com/icon.svg",
  },
  openGraph: {
    title: "LangGraph Agent Architectures | Chandra Kethan",
    description: "A comprehensive interactive platform showcasing 14 core AI Agent Architectures implemented using LangGraph.",
    url: "https://www.chandrakethan.com/langraph-mastery",
    siteName: "Chandra Kethan",
    images: [
      {
        url: "https://www.chandrakethan.com/og-image.jpg",
        width: 600,
        height: 600,
        alt: "LangGraph Mastery - Chandra Kethan",
      },
    ],
  },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body
        className={`${instrumentSerif.variable} ${inter.variable} ${plexMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
