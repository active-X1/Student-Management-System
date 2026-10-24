"""CSS for the web interface. Colours come from the shared theme, so every interface matches."""

from __future__ import annotations

from campusdesk.theme import THEME, Theme

_STATIC = """
html, body, .q-layout, .q-page, .q-page-container { background: transparent !important; color: var(--text); font-family: var(--font); }
body { min-height: 100vh; background: linear-gradient(-45deg, var(--bg1), var(--bg2), var(--bg3), var(--bg4)) !important;
  background-size: 400% 400% !important; animation: cd-drift 26s ease infinite; }
body::before, body::after { content: ""; position: fixed; z-index: -1; border-radius: 50%; filter: blur(95px); pointer-events: none; opacity: .4; }
body::before { width: 48vmax; height: 48vmax; top: -16vmax; left: -14vmax; background: radial-gradient(circle, var(--orb1), transparent 65%); animation: cd-float-a 30s ease-in-out infinite; }
body::after { width: 44vmax; height: 44vmax; bottom: -18vmax; right: -14vmax; background: radial-gradient(circle, var(--orb2), transparent 65%); animation: cd-float-b 34s ease-in-out infinite; }
.nicegui-content { padding: 0 !important; align-items: center; }

.cd-shell { width: 100%; max-width: 1040px; margin: 0 auto; padding: 32px 20px 56px; display: flex; flex-direction: column; gap: 20px; box-sizing: border-box; }
.glass { background: var(--glass); border: 1px solid var(--glass-border); border-radius: 20px; backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px); box-shadow: 0 10px 40px rgba(0,0,0,.28); }

.cd-header { display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap; }
.cd-brand { display: flex; align-items: center; gap: 14px; }
.cd-brand img { width: 52px; height: 52px; filter: drop-shadow(0 6px 14px rgba(59,130,246,.45)); }
.cd-title { font-size: 1.9rem; font-weight: 800; letter-spacing: -.02em; line-height: 1.1;
  background: linear-gradient(90deg, #93c5fd, #a5b4fc, #6ee7b7); -webkit-background-clip: text; background-clip: text; color: transparent; }
.cd-sub { color: var(--muted); font-size: .95rem; margin-top: 2px; }

.cd-stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
.cd-stat { padding: 18px 18px 16px; position: relative; overflow: hidden; }
.cd-stat::after { content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 4px; background: var(--accent, var(--primary)); }
.cd-stat .num { font-size: 2rem; font-weight: 800; line-height: 1; font-variant-numeric: tabular-nums; }
.cd-stat .num.small { font-size: 1.15rem; line-height: 1.5; padding-top: 6px; }
.cd-stat .cap { margin-top: 8px; font-size: .72rem; letter-spacing: .14em; text-transform: uppercase; color: var(--muted); }

.cd-toolbar { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
.cd-search { flex: 1 1 260px; }
.cd-chips { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; color: var(--muted); font-size: .85rem; }
.cd-sort { cursor: pointer; padding: 6px 14px; border-radius: 999px; border: 1px solid var(--glass-border); color: var(--muted); background: transparent; font: inherit; transition: all .16s ease; }
.cd-sort:hover { color: var(--text); background: var(--glass); }
.cd-sort.active { color: #fff; background: var(--primary); border-color: transparent; }
.cd-export { color: var(--muted); text-decoration: none; padding: 6px 14px; border: 1px solid var(--glass-border); border-radius: 999px; transition: all .16s ease; }
.cd-export:hover { color: var(--text); background: var(--glass); }

.cd-main { display: grid; grid-template-columns: 1fr 300px; gap: 20px; align-items: start; }
.cd-list { padding: 8px; display: flex; flex-direction: column; gap: 2px; }
.cd-row { display: grid; grid-template-columns: 44px 1fr auto auto; align-items: center; gap: 14px; padding: 12px 14px; border-radius: 14px; transition: background .15s ease; animation: cd-rise .35s ease both; }
.cd-row:hover { background: rgba(255,255,255,.06); }
.cd-avatar { width: 44px; height: 44px; border-radius: 50%; display: grid; place-items: center; font-weight: 800; color: #0b1020; font-size: .95rem; }
.cd-name { font-weight: 700; }
.cd-meta { color: var(--muted); font-size: .82rem; display: flex; gap: 10px; align-items: center; margin-top: 3px; flex-wrap: wrap; }
.cd-chip { padding: 2px 10px; border-radius: 999px; font-size: .75rem; font-weight: 600; border: 1px solid; }
.cd-id { color: var(--muted); font-size: .8rem; font-variant-numeric: tabular-nums; }
.cd-actions { display: flex; gap: 4px; }
.cd-empty { padding: 52px 20px; text-align: center; color: var(--muted); display: flex; flex-direction: column; align-items: center; gap: 10px; }
.cd-empty img { width: 84px; opacity: .9; }
.cd-empty .big { color: var(--text); font-size: 1.15rem; font-weight: 700; }

.cd-chart { padding: 18px; display: flex; flex-direction: column; gap: 14px; }
.cd-chart-title { font-size: .72rem; letter-spacing: .14em; text-transform: uppercase; color: var(--muted); font-weight: 700; }
.cd-bar-row .top { display: flex; justify-content: space-between; font-size: .85rem; margin-bottom: 6px; gap: 8px; }
.cd-bar-row .top span:first-child { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.cd-bar { height: 8px; border-radius: 999px; background: rgba(255,255,255,.08); overflow: hidden; }
.cd-bar > div { height: 100%; border-radius: 999px; transition: width .5s ease; }

.cd-dialog { width: min(440px, 92vw); padding: 24px; background: var(--surface) !important; border: 1px solid var(--glass-border); border-radius: 22px !important; gap: 14px; color: var(--text); }
.cd-dialog h2 { margin: 0; font-size: 1.3rem; font-weight: 800; }
.cd-error { color: var(--danger-hover); font-size: .88rem; min-height: 1.2em; }
.cd-suggest { display: flex; flex-wrap: wrap; gap: 6px; }
.cd-suggest button { cursor: pointer; background: transparent; font: inherit; font-size: .78rem; padding: 3px 10px; border-radius: 999px; border: 1px solid var(--glass-border); color: var(--muted); }
.cd-suggest button:hover { color: var(--text); background: var(--glass); }
.cd-footer { text-align: center; color: var(--muted); font-size: .8rem; opacity: .8; }

@keyframes cd-drift { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
@keyframes cd-float-a { 0%,100% { transform: translate(0,0); } 50% { transform: translate(8vmax, 6vmax); } }
@keyframes cd-float-b { 0%,100% { transform: translate(0,0); } 50% { transform: translate(-7vmax, -8vmax); } }
@keyframes cd-rise { from { transform: translateY(8px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }

@media (max-width: 860px) { .cd-main { grid-template-columns: 1fr; } .cd-stats { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 520px) {
  .cd-row { grid-template-columns: 44px 1fr; row-gap: 4px; }
  .cd-id { display: none; }
  .cd-actions { grid-column: 2; justify-self: start; margin-left: -8px; }
  .cd-header .q-btn { width: 100%; }
}
@media (prefers-reduced-motion: reduce) { body, body::before, body::after, .cd-row { animation: none !important; } }
"""


def build_css(theme: Theme = THEME) -> str:
    bg = theme.background
    variables = f"""
:root {{
  --bg1: {bg[0]}; --bg2: {bg[1]}; --bg3: {bg[2]}; --bg4: {bg[3]};
  --orb1: {theme.orbs[0]}; --orb2: {theme.orbs[1]};
  --text: {theme.text}; --muted: {theme.muted}; --surface: {theme.surface};
  --primary: {theme.primary}; --success: {theme.success}; --warning: {theme.warning};
  --danger: {theme.danger}; --danger-hover: {theme.danger_hover};
  --glass: rgba(255,255,255,0.06); --glass-border: rgba(255,255,255,0.12);
  --font: Inter, "SF Pro Display", "Segoe UI Variable", "Segoe UI", system-ui, -apple-system, Roboto, "Helvetica Neue", sans-serif;
}}
"""
    return variables + _STATIC
