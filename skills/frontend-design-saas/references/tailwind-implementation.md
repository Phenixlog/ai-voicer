# Tailwind Implementation Patterns

Use CSS variables for design tokens and map Tailwind colors to them. Keep tokens semantic.

```css
:root {
  --bg: 210 25% 98%;
  --surface: 210 20% 96%;
  --fg: 222 47% 11%;
  --muted: 215 16% 47%;
  --primary: 222 89% 58%;
  --primary-foreground: 0 0% 100%;
  --accent: 164 80% 40%;
  --ring: 222 89% 58%;
  --radius: 16px;
}

@layer base {
  body {
    background-color: hsl(var(--bg));
    color: hsl(var(--fg));
  }
}
```

```js
// tailwind.config.js
export default {
  theme: {
    extend: {
      colors: {
        bg: "hsl(var(--bg))",
        surface: "hsl(var(--surface))",
        fg: "hsl(var(--fg))",
        muted: "hsl(var(--muted))",
        primary: "hsl(var(--primary))",
        accent: "hsl(var(--accent))",
      },
      borderRadius: {
        xl: "var(--radius)",
      },
    },
  },
};
```

Prefer `clamp()` for fluid typography when possible and keep type scales consistent.
