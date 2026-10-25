# 0004 — Content-first library workspace

Date: 2026-10-24. Status: implemented, awaiting user feedback.

The user rejected the previous UI/UX and requested an expert redesign, then supplied the UI UX Pro Max skill. Its accessibility and interaction guidance informed this revision; its marketing-oriented generated page patterns were unsuitable for the existing app.

Use a neutral green workspace with one search field, progressively disclosed filters, a joined conversation-list/reader surface, scannable titles and excerpts, and a dedicated reading state on narrow screens with explicit back navigation. Preserve source details in disclosures. Render basic Markdown using text nodes and safe HTTP(S) links; source HTML remains inert. Full Markdown syntax is not claimed.

Verified live at desktop and 375px widths: search, conversation selection, mobile back and restoring search. Browser startup regression, 13 API tests, JavaScript syntax and whitespace checks passed. Screen-reader, full accessibility conformance and all browser/device combinations remain unverified.

Reference: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill

## Visible option groups

User prefers options inside a shared rounded rectangle over dropdown menus. Native select values remain the underlying form contract; short lists present segmented buttons with explicit pressed states, and longer lists present searchable option panels. Dynamically loaded project/conversation options and multiselect assignment retain their original values and events. Verified source switching and its pressed state in the live UI; startup regression passed.

## Collapsed navigation

User requested a closed-by-default left panel with icons following the supplied ChatGPT reference. The app now starts with a 64px icon rail. A labeled toggle reveals navigation text; each destination retains an accessible name and native tooltip. On mobile the expanded panel overlays the content rather than compressing it. Verified desktop and mobile expand/collapse behavior; startup regression passed.

## Control treatment

The user explicitly rejects large boxed clickable controls throughout the app. Actions now use text-style buttons, navigation uses a thin active indicator, search options have no enclosing panel, and notices use a minimal side rule. Keyboard focus outlines remain visible. The compact rounded search input is retained as requested separately. Live browser inspection verified the resulting header, navigation and expanded options.

## Interaction revision — minimal information and progressive disclosure

User direction: "i prefer minimal, slick information. i heavily favor progressive disclosure". This supersedes the always-visible card grid and search tools. Default browsing now uses compact title/source/date rows. Search method, filters, assistant review and an optional matching-passage toggle sit under Search options. Active filters and Smart search remain indicated in its collapsed summary. A selected conversation opens a native dialog reader with explicit close/Escape handling and unsaved-change protection. Source provenance and annotations remain available inside disclosures. Live checks verified detail toggling and mobile dialog open/close; JavaScript startup regression passed.

## Visual revision — October 24

The user rejected the soft green/editorial direction and requested a slick, modern interface. The current visual system uses graphite surfaces, a restrained blue accent, compact sans-serif typography, tighter result rows and a simpler empty state. This supersedes the neutral green visual choices above while retaining progressive filters and mobile reading/back navigation. Desktop search/selection and 375px mobile navigation/setup were inspected in the live app. User acceptance remains unconfirmed.

The search composer keeps a small icon segment for each search method and a
current-method label. Opening that label reveals a rounded chooser with icons,
short descriptions and the selected state. Extra filters and passage previews
remain behind the plus control. Both ways of choosing a method share the same
search state and request path.

## Filter chooser refinement

Filters now open directly from a labeled slider icon into one rounded menu,
with source rows and selection marks, a project disclosure with searchable
choices, and switches for archived-only results and matching passages. Reset
clears these controls together; active filters appear on the trigger. The menu
scrolls within small viewports and supports outside-click and Escape dismissal.
This replaces the nested filter popover and plus trigger described above.
