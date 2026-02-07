# 🎨 AskTennis AI – Frontend UI/UX Improvement Guide

Suggestions to improve the AskTennis AI web app frontend (excluding email login/verification). Prioritized by impact and effort.

---

## 1. **Query history in the UI**

**Why:** You already save history per user; exposing it improves reuse and trust.

**Ideas:**
- **“Recent questions”** – In the main view (or sidebar), show the last 5–10 queries. Click to re-run or copy into the search bar.
- **Dedicated “History”** – Page or drawer listing past queries with date; expand to see answer/SQL/data (reuse `AiResponseView`-style layout).
- **Search bar suggestions** – As the user types, suggest matching past queries (from `GET /api/query/history`), e.g. “Federer vs Nadal head to head”.

**Implementation:** Call `GET /api/query/history` on load or when opening a “History” section; store in state or a small cache; render as list/cards with optional filters (e.g. by date).

---

## 2. **Empty and first-time states**

**Why:** New users see Quick Insights only; a clear “first run” and empty states set expectations.

**Ideas:**
- **First visit (no query yet):**
  - Short one-liner: “Ask anything about 147 years of tennis—players, matches, rankings.”
  - Optional: 2–3 example questions with a tennis visual (ball/court icon).
- **After error or no results:**
  - “No results for this question. Try rephrasing or a different filter.”
  - One-tap “Try again” or “Try: [example question]”.
- **When switching to Stats view with “All Players”:**
  - “Select a player in the sidebar to see their stats and matches.”

Use simple illustrations or icons (e.g. Lucide) to keep the tone light and on-brand.

---

## 3. **AI response UX (answer card)**

**Why:** The answer is the main outcome; small tweaks make it easier to scan and trust.

**Ideas:**
- **“Copy answer”** – Button to copy the AI answer text (and optionally “Copy SQL”) for sharing or notes.
- **“Read out loud”** – When you add TTS (e.g. Kokoro), a speaker icon that plays the answer. Show a small “Playing…”/progress state.
- **Structured highlights** – If the answer contains numbers (e.g. “won 23 Grand Slams”), optionally style them (badge/pill or bold) so key stats pop.
- **Expand/collapse** – Keep “Technical Reasoning (SQL)” and “Query Results” as expanders; consider “Expand all” / “Collapse all” for power users.
- **Skeleton for answer** – While loading, show a 2–3 line skeleton instead of only the tennis loader, so the layout doesn’t jump.

---

## 4. **Search bar and Quick Insights**

**Why:** Search is the primary entry point; clarity and guidance improve usage.

**Ideas:**
- **Placeholder rotation** – Rotate placeholders: “e.g. Who won Wimbledon 2023?”, “e.g. Federer vs Nadal on clay”, “e.g. Top 10 in 2024”.
- **Quick Insights expansion** – More chips (e.g. by category: “Head to head”, “Grand Slams”, “Rankings”, “Records”). Optional: “Surprise me” that picks a random insight.
- **Recent query chips** – Below or beside Quick Insights, show 2–3 “You recently asked: …” (from history) as clickable chips.
- **Character/feedback** – Optional subtle hint: “Tip: You can use the mic to speak your question” (show only when speech is supported).

---

## 5. **Navigation and layout**

**Why:** Clear navigation and layout help users switch between “Ask AI” and “Stats” without getting lost.

**Ideas:**
- **Explicit “Ask” vs “Stats”** – Two clear modes/tabs: “Ask AI” (search + response) and “Stats / Analysis” (filters + dashboard). Header or tab bar so the current mode is obvious.
- **Logout placement** – Move “Logout (user)” into the header or a user menu (avatar/chevron) instead of a floating button; frees space and looks cleaner.
- **Breadcrumb or context** – When on Stats view, show “Stats → [Player name]” so users know where they are.
- **Sidebar on desktop** – Keep filters in sidebar; ensure “Apply” or auto-apply is obvious. Optional: “Clear filters” that resets to “All Players” etc.

---

## 6. **Loading and errors**

**Why:** Predictable loading and error handling reduce confusion and support retries.

**Ideas:**
- **Progressive loading** – If the API ever supports streaming, show the answer as it arrives; for now, keep a single loader but with a short message: “Analyzing tennis data…”.
- **Error recovery** – On “Analysis Error”, add “Retry” and “Edit question” (focus back to search bar with the last query pre-filled).
- **Rate limit** – When you get 429, show “You’ve hit the limit. Try again in X seconds” with a small countdown if the backend sends `Retry-After`.
- **Timeouts** – For long-running queries, consider a timeout message: “This is taking longer than usual. You can try a simpler question or retry.”

---

## 7. **Mobile and responsiveness**

**Why:** Many users will use phones; touch and small screens need explicit attention.

**Ideas:**
- **Touch targets** – Quick Insight chips and buttons at least 44px height; enough spacing so the mic and “Analyze” are easy to tap.
- **Search bar on mobile** – Full width; mic and Analyze always visible (e.g. mic icon, then primary button). Optional: sticky search on scroll so users can refine without scrolling up.
- **Sidebar on mobile** – Already a drawer; ensure overlay + close is obvious. After applying filters, auto-close so the user sees the stats.
- **Tables** – For AI result tables, horizontal scroll with a clear “scroll to see more” or sticky first column; avoid tiny text.
- **Charts** – Ensure Recharts/DataVisualizer are responsive (already using ResponsiveContainer); test on 320px width.

---

## 8. **Accessibility (a11y)**

**Why:** Better a11y helps everyone and improves SEO and compliance.

**Ideas:**
- **Landmarks** – Use `<main>`, `<nav>`, `<header>`, `<aside>` (sidebar) so screen readers can jump by region.
- **Focus management** – After submit, move focus to the answer card or an “Answer” heading so keyboard users don’t stay in the search bar.
- **Live region for answer** – `aria-live="polite"` on the answer container so new content is announced.
- **Error announcements** – Ensure error message is in a live region and associated with `aria-describedby` where relevant.
- **Color contrast** – Check placeholder and secondary text (e.g. `text-slate-400`) against background; ensure 4.5:1 for normal text.
- **Skip link** – “Skip to main content” at the top for keyboard users.

---

## 9. **Visual polish and branding**

**Why:** A consistent, “premium” feel reinforces trust in the AI and the product.

**Ideas:**
- **Tennis accent** – Use your existing theme (emerald/green, blue) consistently: e.g. primary actions = emerald, links/ secondary = blue; optional subtle court-line or ball motif in empty states or header.
- **Micro-interactions** – Quick Insight chips: light scale on hover; answer card: soft fade-in (you have some already); “Analyze” button: brief loading state (spinner + “Analyzing…”).
- **Typography** – Keep Inter (or current font); ensure answer prose has a comfortable line height and max-width (e.g. 65ch) for long answers.
- **Version / status** – Header already has “Live System” and version; keep it subtle so it doesn’t distract.

---

## 10. **Keyboard and power users**

**Why:** Power users and a11y benefit from shortcuts.

**Ideas:**
- **Shortcuts** – `Ctrl/Cmd + K` or `/` to focus search bar; `Escape` to clear search or close modals/drawers.
- **Submit on Enter** – Already in place; keep it and avoid double-submit.
- **Optional command palette** – “Quick actions”: Focus search, Clear filters, Open history, Switch to Stats. Can be a later phase.

---

## 11. **Data tables and charts**

**Why:** AI often returns tables; making them scannable and trustworthy matters.

**Ideas:**
- **Table enhancements** – Sticky header on scroll; optional column sort if not already; row hover; optional “Export CSV” for the current result set.
- **Chart labels** – Clear axis labels and units; tooltips with full value and context (e.g. “Wimbledon 2023 – Winner: Djokovic”).
- **Empty table** – If `aiData` is empty but the answer exists, show “No tabular data for this question” instead of a blank block.

---

## 12. **Performance and perceived speed**

**Why:** Faster perceived performance improves satisfaction.

**Ideas:**
- **Optimistic UI** – After clicking a Quick Insight, immediately show the query in the search bar and a loading state (no need to wait for a round-trip).
- **Cache recent response** – In session, if the user re-submits the same query, show last result immediately (optional; backend cache may already help).
- **Lazy load below fold** – Conversation flow or heavy charts below the fold can be lazy-rendered or collapsed by default.
- **Image/asset optimization** – If you add images (e.g. player photos, illustrations), use responsive images and lazy loading.

---

## Priority matrix (suggested order)

| Priority | Area                    | Impact | Effort | Suggested order |
|----------|-------------------------|--------|--------|------------------|
| High     | Query history in UI     | High   | Medium | 1                |
| High     | Empty / first-time      | High   | Low    | 2                |
| High     | AI response UX (copy, etc.) | High | Low    | 3                |
| Medium   | Search & Quick Insights | Medium | Low    | 4                |
| Medium   | Navigation & layout     | Medium | Medium | 5                |
| Medium   | Loading & errors        | Medium | Low    | 6                |
| Medium   | Mobile & responsive    | High   | Medium | 7                |
| Medium   | Accessibility           | High   | Medium | 8                |
| Low      | Visual polish           | Medium | Low    | 9                |
| Low      | Keyboard / shortcuts    | Medium | Low    | 10               |
| Low      | Tables & charts         | Medium | Low    | 11               |
| Low      | Performance             | Medium | Low–Med| 12               |

---

## Quick wins (do first)

1. **Copy answer** button on the AI Insight card.  
2. **Retry** and **Edit question** on error state.  
3. **Empty state** when “All Players” and Stats view: “Select a player to see stats.”  
4. **First-time line** above Quick Insights: “Ask anything about 147 years of tennis.”  
5. **Logout** in header/user menu instead of floating button.  
6. **aria-live** on answer container and focus move after submit.

---

## Summary

Focus first on **surfacing query history**, **clear empty/first-time states**, and **AI response UX** (copy, retry, focus). Then tighten **navigation** (Ask vs Stats), **mobile**, and **accessibility**. Use the quick wins above for fast impact with limited effort. All of this stays independent of email login/verification and fits the AskTennis AI “tennis + AI” positioning.
