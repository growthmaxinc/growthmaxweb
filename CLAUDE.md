# GrowthMax Website — Project Instructions

## About This Project
GrowthMax Inc (growthmaxinc.com) is an AI consultancy that builds custom AI agents and offers AI training bootcamps. The website is a static HTML site hosted via GitHub Pages. The core brand message is **"Partnership. Not Replacement."** — AI augments human expertise rather than replacing it.

## Source Control
- **Repository:** GitHub — `growthmaxinc/growthmaxweb`
- All code lives in GitHub. Changes are committed and pushed to the `main` branch.

## Tech Stack & Architecture
- **Static HTML** — no framework, no build step, no bundler
- **Tailwind CSS via CDN** — loaded from `https://cdn.tailwindcss.com` on every page
- **Google Fonts** — Inter (weights: 300, 400, 500, 600)
- **Google Analytics** — GA4 tag `G-F7QYH5FFXD` on every page
- **ElevenLabs ConvAI widget** — embedded chatbot on the homepage
- **Hosting** — GitHub Pages with custom domain `growthmaxinc.com` (CNAME file in root)

## Use Existing Services — Don't Reinvent
When the site needs functionality like forms, authentication, payments, analytics, email collection, scheduling, or similar — use a free, established third-party service (e.g., Formspree, Calendly, Mailchimp, Typeform, Auth0, Stripe) rather than building custom code. Embed via script tag, iframe, or API. Only build something custom when no suitable free option exists. This keeps the site simple, maintainable, and static.

## File Structure
```
/                         → root
├── index.html            → homepage (single-page with anchored sections)
├── solutions/
│   ├── agent-development.html
│   ├── bootcamp.html
│   └── foundations.html
├── resources/
│   ├── blog.html         → blog index page
│   └── faq.html
├── resources.html        → legacy resources page (may be superseded by /resources/)
├── blog-*.html           → individual blog posts (root level)
├── favicon.svg           → SVG favicon (cyan rounded square with G logo)
├── growthMAX.PNG          → logo image
├── *_gemini_cartoon.png  → team member cartoon avatars
└── CNAME                 → GitHub Pages custom domain
```

## Design System

### Color Palette
Use the Tailwind cyan/sky/blue palette consistently:
- **Page backgrounds:** `bg-sky-50` (primary), `bg-gradient-to-br from-sky-50 to-cyan-50` (alternating sections)
- **Nav:** `bg-cyan-100/80 backdrop-blur-md`, border `border-cyan-200`
- **Cards:** `bg-white` with `border border-cyan-200`, `rounded-2xl`, `shadow-md`
- **Team cards:** `bg-white/80`, `rounded-3xl`, `shadow-lg`
- **Text — headings:** `text-cyan-900`
- **Text — body:** `text-cyan-800 font-light`
- **Text — secondary/links:** `text-cyan-700`, hover `text-cyan-900`
- **Accent/category labels:** `text-blue-600`
- **Primary CTA buttons:** `bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-full`
- **Secondary CTA buttons:** `border-2 border-cyan-700 text-cyan-800 rounded-full`, hover fills `bg-cyan-700 text-white`
- **Footer:** `bg-cyan-50` with `border-t border-cyan-200`

### Typography
- Font: Inter, always
- Headings: `font-light tracking-tight` — large and airy, not bold
- Body: `font-light leading-relaxed`
- Section headings: `text-3xl md:text-5xl`
- Hero heading: `text-6xl md:text-7xl`
- Small labels/categories: `text-xs font-medium uppercase tracking-wide`

### Layout Patterns
- Max content width: `max-w-6xl mx-auto px-6` (general), `max-w-4xl` (text-heavy sections)
- Section padding: `py-12 md:py-20 px-6`
- Grid cards: `grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8`
- Rounded corners: `rounded-2xl` for cards, `rounded-full` for buttons and avatars
- Hover effects on cards: `hover:shadow-lg transition-shadow`

### Navigation
Every page must include the **same navigation structure**: fixed top nav with desktop dropdowns for Solutions and Resources, plus a mobile hamburger menu with accordion sub-menus. Copy the nav from an existing page when creating new ones — do not reinvent it.

On subpages, nav links point back to the homepage with anchors (e.g., `/#about`, `/#process`). On the homepage itself, links use `#about`, `#process`, etc.

### Footer
Every page must include the **same footer** with three columns (brand description, Solutions links, Resources links) plus a copyright line and LinkedIn icon. Copy from an existing page.

## SEO & Meta Tags
Every page should include:
- `<link rel="canonical" href="...">` with the full URL
- `<title>` — descriptive, includes "GrowthMax" or "GrowthMax Inc"
- `<meta name="description">` — compelling, under 160 characters
- Open Graph tags: `og:title`, `og:description`, `og:url`, `og:type`
- `<meta name="twitter:card" content="summary_large_image">`
- Favicon link: `<link rel="icon" type="image/svg+xml" href="/favicon.svg" />`
- GA4 script block (copy from any existing page)

For blog posts, also include:
- JSON-LD `BlogPosting` schema markup
- `<meta name="keywords">` with relevant terms
- `<meta name="author" content="GrowthMax Inc">`
- `<meta name="article:published_time">` with ISO date

For solution pages, also include:
- JSON-LD `Service` schema markup

## Content & Brand Voice

### Core Messaging Pillars
1. **Partnership, not replacement** — AI augments human expertise; it doesn't replace people
2. **Clarity over hype** — speak plainly about what AI can and can't do; no buzzword overload
3. **Outcomes-focused** — emphasize real results, not technology for technology's sake
4. **Empathy for the human side** — acknowledge that AI adoption creates anxiety and disorientation; meet people where they are

### Writing Style
- Warm, confident, direct — like a knowledgeable colleague, not a sales brochure
- Short paragraphs, clear structure
- Avoid: jargon soup, fear-mongering, over-promising, "revolutionize," "disrupt," "game-changer"
- Preferred vocabulary: augment, amplify, partner, judgment, expertise, outcomes, coherence
- Contact email: `hi@growthmaxinc.com`

### Blog Posts
- Blog post files live at root level: `blog-[slug].html`
- Blog index page at `/resources/blog.html` lists all posts
- Each blog card on the homepage/blog index has: category label, title, short description
- Blog categories include: AI Strategy, People & Culture, Getting Started

## When Creating New Pages
1. Start by copying the `<head>`, nav, and footer from an existing page of the same type
2. Update the canonical URL, title, meta description, and OG tags for the new page
3. Maintain the same visual patterns — don't introduce new colors, fonts, or layout paradigms
4. Add the new page to navigation menus across all pages if it's a new solution or resource
5. Test that all internal links work (especially nav dropdowns and mobile menu)

## When Editing Existing Pages
- Preserve the existing Tailwind class patterns — don't swap to custom CSS or inline styles
- Keep the Inter font; don't introduce additional typefaces
- Maintain mobile responsiveness (`md:` breakpoints are used throughout)
- Don't remove the GA4 tracking script or ElevenLabs widget

## Deployment
- The site is deployed via GitHub Pages from the repo's main branch
- Changes pushed to main go live automatically
- The CNAME file must remain in the root for the custom domain to work
- No build step required — just push HTML files
