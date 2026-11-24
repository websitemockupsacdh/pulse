/** Warm paper palette. Borders instead of shadows. Terracotta is reserved for primary actions and active states. */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: { paper: "#F7F5F0", stone: "#EFECE6", rule: "#D8D2C5", ink: "#1C1B18", muted: "#6B665B", clay: "#C85A32", "clay-dark": "#A94A27" },
      fontFamily: {
        serif: ['"Newsreader Variable"', "Georgia", "serif"],
        sans: ['"Plus Jakarta Sans Variable"', "system-ui", "sans-serif"],
        mono: ['"JetBrains Mono Variable"', "ui-monospace", "monospace"],
      },
      letterSpacing: { tightest: "-0.03em" },
    },
  },
  plugins: [],
};
