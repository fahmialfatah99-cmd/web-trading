import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        bloomberg: {
          bg: "#0a0a0a",
          panel: "#111111",
          border: "#333333",
          text: "#e5e5e5",
          accent: "#f59e0b", // Amber for alerts
          bull: "#00c853",   // Bright Green
          bear: "#ff3d00",   // Bright Red
        },
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', "monospace"], // Ideal for terminals
      },
    },
  },
  plugins: [],
};
export default config;
