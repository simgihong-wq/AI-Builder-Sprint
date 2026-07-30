/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "var(--color-bg)",
        surface: "var(--color-surface)",
        ink: "var(--color-ink)",
        "text-secondary": "var(--color-text-secondary)",
        "text-tertiary": "var(--color-text-tertiary)",
        border: "var(--color-border)",
        "border-soft": "var(--color-border-soft)",
        primary: "var(--color-primary)",
        "primary-active": "var(--color-primary-active)",
        "primary-soft": "var(--color-primary-soft-bg)",
        "primary-soft-active": "var(--color-primary-soft-bg-active)",
        confirmed: "var(--color-confirmed)",
        "confirmed-text": "var(--color-confirmed-text)",
        "confirmed-bg": "var(--color-confirmed-bg)",
        "warning-bg-soft": "var(--color-warning-bg-soft)",
        "warning-bg": "var(--color-warning-bg)",
        "warning-text": "var(--color-warning-text)",
        "warning-text-2": "var(--color-warning-text-2)",
        danger: "var(--color-danger)",
        "danger-bg": "var(--color-danger-bg)",
      },
      fontFamily: {
        sans: ["Pretendard", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
