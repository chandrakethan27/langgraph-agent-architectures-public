'use client';

import React, { useEffect, useRef } from 'react';
import mermaid from 'mermaid';

mermaid.initialize({
  startOnLoad: false,
  theme: 'base',
  securityLevel: 'loose',
  fontFamily: '"Inter", "IBM Plex Mono", sans-serif',
  themeVariables: {
    // Background & surface
    primaryColor: '#e8eafc',
    primaryTextColor: '#0f172a',
    primaryBorderColor: '#050ef2',

    // Secondary nodes
    secondaryColor: '#f1f5f9',
    secondaryTextColor: '#0f172a',
    secondaryBorderColor: '#94a3b8',

    // Tertiary
    tertiaryColor: '#f8fafc',
    tertiaryTextColor: '#0f172a',
    tertiaryBorderColor: '#cbd5e1',

    // Lines & edges
    lineColor: '#475569',
    textColor: '#0f172a',

    // Main background
    mainBkg: '#e8eafc',
    nodeBorder: '#050ef2',
    clusterBkg: '#f1f5f9',
    clusterBorder: '#cbd5e1',
    titleColor: '#0f172a',

    // Edge label
    edgeLabelBackground: '#ffffff',

    // Font sizes
    fontSize: '14px',
  },
});

interface MermaidViewerProps {
  chart: string;
}

export default function MermaidViewer({ chart }: MermaidViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current && chart) {
      containerRef.current.removeAttribute('data-processed');
      const id = `mermaid-${Math.random().toString(36).substring(2, 9)}`;
      const processedChart = chart.replace(/\\n/g, '\n');
      
      try {
        mermaid.render(id, processedChart).then(({ svg }) => {
          if (containerRef.current) {
            containerRef.current.innerHTML = svg;
          }
        }).catch((err) => {
          console.error("Mermaid rendering error:", err);
        });
      } catch (e) {
        console.error("Mermaid render crash:", e);
      }
    }
  }, [chart]);

  return (
    <div className="mermaid-surface">
      <div ref={containerRef} style={{ display: 'flex', justifyContent: 'center', width: '100%' }} />
    </div>
  );
}
