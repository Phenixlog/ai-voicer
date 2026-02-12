---
name: frontend-design-saas
description: "High-end SaaS UI/UX redesign and implementation for landing pages and app UIs with a modern 2026 aesthetic. Use when the user asks to elevate UI/UX, redesign a landing page or SaaS app, create a design system or tokens, or implement a polished interface in Next.js/React/Tailwind; includes French triggers like 'refonte UI', 'landing page', 'app SaaS', 'design system'."
---

# Frontend Design (SaaS)

## Core workflow
1. Clarify context: product, audience, conversion goal, brand constraints, required sections, stack, existing code.
2. If brand direction is missing, propose 2 visual directions with name, mood, palette, type pairing, and UI characteristics. If the user does not choose, pick one and state it.
3. Define design tokens: color roles, typography scale, spacing, radius, shadows, borders, motion.
4. Design layout: grid, spacing rhythm, content density, emphasis hierarchy.
5. Build components and flows: nav, hero, CTA, cards, forms, tables, empty states, onboarding.
6. Implement in code: Next.js or React with Tailwind by default, accessible and responsive, with CSS variables.
7. Add purposeful motion: load, hover, focus, and state transitions that feel intentional.

## Output requirements
- Provide a concise summary of the visual direction and token choices.
- Apply changes directly to the codebase when files are present.
- Provide new components and styles when needed.
- Include responsive behavior notes for mobile, tablet, and desktop.
- Ensure accessibility basics: contrast, focus states, and keyboard navigation.
- Avoid generic UI patterns and avoid default component library styling.

## Aesthetic guardrails (2026 SaaS)
- No default fonts or color palettes. Pick a distinctive pairing.
- Avoid purple-first defaults and flat single-color backgrounds.
- Use layered backgrounds, gradients, or soft geometric shapes.
- Create clear depth with shadows and borders.
- Typography should be intentional: display for hero, clean text for body.
- Use iconography and illustrations only if consistent with the brand.
- Motion should feel deliberate, not decorative.

## Implementation guidance
- Prefer CSS variables for tokens and map Tailwind to variables.
- Use semantic HTML and accessible components.
- Keep layouts modular and composable.
- If the user does not specify a stack, default to Next.js + React + Tailwind.
- If the user asks for design only, provide tokens, structure, and component specs without full code.

## References
- For design dimensions, read `references/design-dimensions.md`.
- For landing pages, read `references/landing-checklist.md`.
- For app UIs, read `references/app-ui-checklist.md`.
- For Tailwind implementation patterns, read `references/tailwind-implementation.md`.
- For typography pairings, read `references/typography-pairs.md`.
