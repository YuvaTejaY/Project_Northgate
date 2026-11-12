---
name: Institutional Compliance Workspace
colors:
  surface: '#f8f9ff'
  surface-dim: '#cbdbf5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d3e4fe'
  on-surface: '#0b1c30'
  on-surface-variant: '#44474d'
  inverse-surface: '#213145'
  inverse-on-surface: '#eaf1ff'
  outline: '#75777e'
  outline-variant: '#c5c6cd'
  surface-tint: '#515f78'
  primary: '#000000'
  on-primary: '#ffffff'
  primary-container: '#0d1c32'
  on-primary-container: '#76849f'
  inverse-primary: '#b9c7e4'
  secondary: '#0051d5'
  on-secondary: '#ffffff'
  secondary-container: '#316bf3'
  on-secondary-container: '#fefcff'
  tertiary: '#000000'
  on-tertiary: '#ffffff'
  tertiary-container: '#2f1500'
  on-tertiary-container: '#c76c00'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d6e3ff'
  primary-fixed-dim: '#b9c7e4'
  on-primary-fixed: '#0d1c32'
  on-primary-fixed-variant: '#39475f'
  secondary-fixed: '#dbe1ff'
  secondary-fixed-dim: '#b4c5ff'
  on-secondary-fixed: '#00174b'
  on-secondary-fixed-variant: '#003ea8'
  tertiary-fixed: '#ffdcc3'
  tertiary-fixed-dim: '#ffb77d'
  on-tertiary-fixed: '#2f1500'
  on-tertiary-fixed-variant: '#6e3900'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
typography:
  headline-xl:
    fontFamily: Plus Jakarta Sans
    fontSize: 2rem
    fontWeight: '700'
    lineHeight: 2.5rem
    letterSpacing: -0.025em
  headline-xl-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 1.5rem
    fontWeight: '700'
    lineHeight: 2rem
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 1.5rem
    fontWeight: '600'
    lineHeight: 2rem
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 1.25rem
    fontWeight: '600'
    lineHeight: 1.75rem
    letterSpacing: -0.015em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 1.125rem
    fontWeight: '600'
    lineHeight: 1.5rem
    letterSpacing: -0.015em
  title-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 0.875rem
    fontWeight: '600'
    lineHeight: 1.25rem
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Inter
    fontSize: 1rem
    fontWeight: '400'
    lineHeight: 1.5rem
  body-md:
    fontFamily: Inter
    fontSize: 0.875rem
    fontWeight: '400'
    lineHeight: 1.25rem
  body-sm:
    fontFamily: Inter
    fontSize: 0.75rem
    fontWeight: '400'
    lineHeight: 1rem
  label-md:
    fontFamily: Inter
    fontSize: 0.75rem
    fontWeight: '500'
    lineHeight: 1rem
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Inter
    fontSize: 0.6875rem
    fontWeight: '600'
    lineHeight: 0.875rem
    letterSpacing: 0.04em
  metric-tabular:
    fontFamily: Inter
    fontSize: 0.875rem
    fontWeight: '500'
    lineHeight: 1.25rem
    letterSpacing: -0.01em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-desktop: 1.5rem
  margin: 1rem
  margin-desktop: 2rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.75rem
  space-lg: 1rem
  space-xl: 1.5rem
---

## Brand & Style

This design system serves high-stakes institutional banking, specifically cross-border corporate KYC and document chasing. The audience consists of compliance officers, corporate treasurers, risk analysts, and institutional onboarding managers who process multi-layered ownership structures under strict regulatory deadlines.

The aesthetic blends **Modern Corporate Banking** with high-density **SaaS Precision**. The experience prioritizes clarity, precision, and unshakeable institutional trust over decorative novelty. Visual weight is communicated through architectural layouts, disciplined typography, and micro-elevation rather than heavy drop shadows.

Key brand traits:
- **Rigorous & Authoritative:** Every pixel reinforces compliance rigor, audit readiness, and institutional-grade data security.
- **Urgent without Alarmism:** SLA timelines, document deficiencies, and escalation workflows leverage nuanced amber hues to highlight operational urgency without triggering visual chaos.
- **High-Density Efficiency:** Optimized for multi-column data views, tiered verification states, and continuous checklist execution with minimal wasted viewport space.

## Colors

The palette is engineered for institutional gravity, legibility, and high-stakes operational clarity. It relies on a deep midnight sapphire foundation balanced by crisp structural neutrals and functional semantic indicators.

### Palette Architecture
- **Primary (`#0A192F`):** Deep Midnight Navy. Anchors top navigation, primary visual hierarchies, high-level headers, and high-impact structural panels.
- **Secondary (`#2563EB`):** Precision Cobalt. Powers primary interactive controls, selected table rows, active document drill-downs, and focused states.
- **Tertiary / SLA Warning (`#D97706`):** Institutional Amber. Dedicated exclusively to operational deadlines, pending document outreach, follow-up alerts, and SLA expirations.
- **Success / Verified (`#059669`):** Audit Emerald. Applied to verified KYC artifacts, certified beneficial ownership (UBO) matches, and compliant risk ratings.
- **Neutral Foundation:** Built on cool slate tones:
  - Surface Canvas: `#F8FAFC`
  - Elevated Container / Paper: `#FFFFFF`
  - Subtle Surface Inset / Rail: `#F1F5F9`
  - Structural Border / Dividers: `#E2E8F0`
  - Muted Data / Label Text: `#64748B`
  - High-Contrast Data Text: `#0F172A`

### Application Guidelines
Avoid decorative color floods. Semantic colors (Emerald, Amber, Crimson) must be restricted strictly to operational status chips, timeline milestones, and data validation states. Primary interactive accents must maintain a minimum 4.5:1 contrast against light slate backgrounds.

## Typography

The type system pairs **Plus Jakarta Sans** for structural section headlines and card framing with **Inter** for data tables, form fields, and operational metadata.

### Tabular Figures & Numeric Alignment
All numerical figures—including turn-around times (TAT), document expiration counts, UBO percentages, and SLA countdowns—must enforce OpenType tabular alignment (`font-feature-settings: "tnum" 1, "cv05" 1`). This ensures strict vertical alignment across dense multi-row ledger tables.

### Hierarchy Rules
- **Structural Headers (`headline-xl`, `headline-lg`):** Reserved for client legal name, entity group overviews, and parent onboard tracking screens.
- **Section Dividers & Metric Labels (`title-sm`, `label-sm`):** Micro-labels utilize upper-case formatting with positive letter spacing (`0.04em`) when designating document classifications and audit states.
- **Body & Captions (`body-md`, `body-sm`):** Optimized for low eye-strain during extended verification sessions.

## Layout & Spacing

The workspace uses a dense, responsive fluid grid structured for dashboard cockpits, side-by-side document inspection panels, and deep tabular listings.

### Grid & Architecture
- **Desktop (>= 1280px):** 12-column layout with 24px (`1.5rem`) gutters and a fixed 280px left rail for entity hierarchy and onboarding pipelines.
- **Split Inspector Mode:** When checking a corporate document against its registry data, the layout locks into a 50/50 dual-pane viewport with synchronized scrolling.
- **Tablet / Laptop (1024px - 1279px):** 12-column layout with 16px (`1rem`) gutters; navigation collapses into an icon-rail.
- **Mobile / Compact (< 1024px):** Single-column stacked layout with 16px margins, prioritized strictly for SLA escalation approvals and rapid document review.

### Spacing Discipline
Maintain a tight 4px/8px rhythm. Component internal vertical padding is intentionally compressed (`space-sm` for table cells and button heights) to maximize visible data above the fold without sacrificing click/touch accuracy.

## Elevation & Depth

This system avoids dramatic shadows in favor of a crisp architectural plane model featuring subtle outlines and micro-shadows.

### Layering Model
1. **Canvas Surface (`#F8FAFC`):** Base workspace background. Zero elevation.
2. **Structural Panels & Data Tables (`#FFFFFF`):** Sits directly on the canvas, outlined by a 1px border (`#E2E8F0`). Flat elevation.
3. **Elevated Overlays & Flyouts:** Drawers and document preview modals use low-opacity dual ambient shadows:
   - `0 1px 3px 0 rgba(15, 23, 42, 0.08), 0 4px 6px -1px rgba(15, 23, 42, 0.04)`
   - Border: `1px solid #CBD5E1`
4. **Active Row / Hovered Item:** Indicated by a tint shift (`#F8FAFC` to `#F1F5F9`) combined with an inset or boundary line accent in `#2563EB`, eliminating heavy floating drop shadows.

Backdrop blurs (`backdrop-filter: blur(4px)`) are permitted only behind critical compliance warning dialogs and document redline viewports.

## Shapes

To project institutional authority and maximize internal data density, this design system specifies a crisp, soft geometry (`roundedness: 1`).

### Shape Metrics
- **Interactive Controls (Buttons, Inputs, Selects):** 4px (`0.25rem`) border radius. Conveys stability, structural discipline, and professional software reliability.
- **Cards, Table Shells, and Group Panels:** 6px to 8px (`0.375rem` - `0.5rem`) corner radius. Accented with razor-sharp 1px neutral borders.
- **Status Badges & Pill Indicators:** Fully rounded (`9999px`) to create an unmistakable functional distinction between structural containers and real-time status markers.

## Components

### Buttons
- **Primary:** Deep Sapphire background (`#0A192F`), white text, 4px radius, `h-9` (36px compact) or `h-8` (32px table action). Hover state shifts to `#1E293B`.
- **Secondary / Action:** Solid slate border (`#CBD5E1`), white background, text `#0F172A`. Hover shifts background to `#F8FAFC`.
- **Destructive / Escalation:** Deep Crimson outline or solid tint (`#BE123C`), used for rejecting fraudulent or mismatched documentation.

### KYC Status Pills & SLA Badges
- **Verified:** Background `#ECFDF5`, text `#065F46`, border `1px solid #A7F3D0`. Prepended with an audit-check icon.
- **Urgent / SLA Expiring:** Background `#FFFBEB`, text `#92400E`, border `1px solid #FDE68A`. Incorporates tabular countdown indicators (e.g., `2h 15m`).
- **Missing / Rejected:** Background `#FEF2F2`, text `#991B1B`, border `1px solid #FECACA`.
- **Pending Review:** Background `#EFF6FF`, text `#1E40AF`, border `1px solid #BFDBFE`.

### High-Density Data Tables
- Table headers feature an uppercase label (`label-sm`), background `#F8FAFC`, border-bottom `1px solid #E2E8F0`.
- Row height is constrained to 40px for standard density and 48px for complex record views.
- Alternating subtle row hover (`#F8FAFC`) with immediate keyboard navigation support.
- Numerical columns and status metrics enforce tabular figure alignment.

### Input Fields & Search Filters
- Input containers feature `#FFFFFF` background, `1px solid #CBD5E1` border, 4px border radius, and inset text padding `0.5rem 0.75rem`.
- Focus state: `1px solid #2563EB` with an external `2px` ring in `rgba(37, 99, 235, 0.15)`.

### Checkboxes & Verification Triggers
- Checkboxes use a 4px rounded corner with a 1.5px border (`#94A3B8`).
- Checked state fills with `#2563EB` or `#059669` depending on whether it represents a manual analyst confirmation or an automated legal clearance.

### Document Chasing & Audit Cards
- Document tracking items feature dual metadata rows: Document Name + Entity Identifier on top, with Jurisdictional Tag + SLA Clock beneath.
- Left-hand edge includes a 3px vertical color ribbon indicating document validity: Emerald (Verified), Amber (Follow-up Dispatched), Red (Deficient).