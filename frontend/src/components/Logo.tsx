import React from "react";

interface LogoProps {
  size?: number;
  color?: string;
  className?: string;
  style?: React.CSSProperties;
}

export default function Logo({
  size = 32,
  color = "var(--accent)",
  className = "",
  style = {},
}: LogoProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      style={{ display: "inline-block", verticalAlign: "middle", ...style }}
    >
      {/* Top slanted parallelogram */}
      <path
        d="M 27 21 L 66 21 L 77 37.5 L 38 37.5 Z"
        fill={color}
      />
      {/* Lower C body */}
      <path
        d="M 23 37.5 L 38 37.5 L 38 62.5 L 66 62.5 L 77 78.5 L 38 78.5 L 23 62.5 Z"
        fill={color}
      />
    </svg>
  );
}
