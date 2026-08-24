# dashboard/app.py
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from src.core.analytics import get_dashboard_data, parse_row_detail
from src.core.orchestrator import run_cycle

st.set_page_config(page_title="AURA — Autonomous Trading Terminal",
                   page_icon="◆", layout="wide")

# ── accent tokens used inside helper HTML ──────────────────────
AMBER  = "#ffb000"
UP     = "#12b981"
DOWN   = "#ff5257"
HOLD   = "#64708c"
CYAN   = "#3dd6d0"
VIOLET = "#9d8bff"

STATUS_COLOR = {"APPROVED": UP, "REJECTED": DOWN, "NO_TRADE": HOLD}


# ── helper: lamba text chhota karo ──
def _short(txt, n=60):
    return (txt[:n] + "…") if txt and len(txt) > n else (txt or "")


# ============================================================
#  GLOBAL CSS
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');

:root{
  --bg:#070a11; --panel:#0c111c; --panel2:#101725;
  --rule:#1b2436; --rule2:#2a3855;
  --tx1:#e2e8f4; --tx2:#7583a0; --tx3:#47536e;
  --amber:#ffb000; --up:#12b981; --down:#ff5257; --hold:#64708c;
}

html,body,[class*="css"]{ font-family:'IBM Plex Sans',sans-serif; }

[data-testid="stAppViewContainer"]{
  background:
    repeating-linear-gradient(0deg, rgba(255,255,255,0.010) 0px, rgba(255,255,255,0.010) 1px, transparent 1px, transparent 3px),
    radial-gradient(circle at 85% 0%, rgba(255,176,0,0.05), transparent 45%),
    var(--bg);
}
[data-testid="stHeader"]{ background:transparent; }
.block-container{ padding-top:1.4rem; padding-bottom:2.5rem; max-width:1240px; }

.mono{ font-family:'IBM Plex Mono',monospace; }

/* ── TERMINAL HEADER BAR ── */
.term-bar{
  display:flex; align-items:center; justify-content:space-between;
  border:1px solid var(--rule); border-bottom:2px solid var(--amber);
  background:linear-gradient(180deg,var(--panel2),var(--panel));
  padding:12px 18px; border-radius:4px;
}
.term-left{ display:flex; align-items:baseline; gap:16px; }
.wordmark{
  font-family:'IBM Plex Mono',monospace; font-weight:700; font-size:1.9rem;
  letter-spacing:0.12em; color:var(--tx1);
}
.wordmark b{ color:var(--amber); }
.term-meta{
  font-family:'IBM Plex Mono',monospace; font-size:0.68rem; letter-spacing:0.14em;
  text-transform:uppercase; color:var(--tx2);
}
.term-right{ display:flex; align-items:center; gap:22px; }
.stat-inline{ font-family:'IBM Plex Mono',monospace; font-size:0.7rem; letter-spacing:0.08em; color:var(--tx2); text-align:right; }
.stat-inline b{ color:var(--tx1); font-weight:600; }
.live-dot{ display:inline-block; width:6px; height:6px; border-radius:50%; background:var(--up);
  margin-right:5px; box-shadow:0 0 6px var(--up); animation:blink 1.6s steps(2) infinite; }
@keyframes blink{ 50%{ opacity:0.25; } }
.cursor{ display:inline-block; width:8px; height:1em; background:var(--amber); margin-left:2px;
  vertical-align:-2px; animation:blink 1s steps(2) infinite; }

/* ── SESSION TAPE ── */
.tape{
  border:1px solid var(--rule); border-radius:4px; margin-top:8px; overflow:hidden;
  background:var(--panel); white-space:nowrap;
}
.tape-inner{ display:inline-block; padding:7px 0; animation:tape 34s linear infinite; }
@keyframes tape{ 0%{ transform:translateX(0);} 100%{ transform:translateX(-50%);} }
.tape-item{ font-family:'IBM Plex Mono',monospace; font-size:0.72rem; letter-spacing:0.06em;
  color:var(--tx2); padding:0 22px; border-right:1px solid var(--rule); }
.tape-item b{ color:var(--tx1); }
@media (prefers-reduced-motion: reduce){ .tape-inner{ animation:none; } }

/* ── SECTION HEADERS ── */
.sec{ margin-top:30px; margin-bottom:14px; }
.sec-eyebrow{ font-family:'IBM Plex Mono',monospace; font-size:0.68rem; letter-spacing:0.18em;
  text-transform:uppercase; color:var(--amber); }
.sec-title{ font-family:'IBM Plex Sans',sans-serif; font-weight:600; font-size:1.15rem;
  color:var(--tx1); letter-spacing:-0.01em; margin-top:2px; }
.sec-sub{ color:var(--tx2); font-size:0.82rem; margin-top:2px; }

/* ── KPI PANELS ── */
.kpi{ border:1px solid var(--rule); border-radius:4px; background:var(--panel);
  padding:14px 16px; position:relative; }
.kpi::after{ content:""; position:absolute; left:0; top:0; bottom:0; width:2px; background:var(--kc); }
.kpi-l{ font-family:'IBM Plex Mono',monospace; font-size:0.64rem; letter-spacing:0.12em;
  text-transform:uppercase; color:var(--tx3); }
.kpi-v{ font-family:'IBM Plex Mono',monospace; font-size:1.85rem; font-weight:600;
  color:var(--tx1); margin-top:8px; font-variant-numeric:tabular-nums; }
.kpi-s{ font-size:0.7rem; color:var(--tx2); margin-top:3px; }

/* ── EXPOSURE STRIP ── */
.expo{ border:1px solid rgba(255,82,87,0.4); border-left:3px solid var(--down);
  background:linear-gradient(90deg, rgba(255,82,87,0.08), transparent);
  border-radius:4px; padding:12px 16px; color:var(--tx1); font-size:0.86rem; line-height:1.5;
  font-family:'IBM Plex Sans',sans-serif; }
.expo b{ color:var(--down); font-family:'IBM Plex Mono',monospace; }

/* ── SIGNAL CHAIN ── */
.chain{ display:grid; grid-template-columns:repeat(4,1fr); gap:1px; background:var(--rule);
  border:1px solid var(--rule); border-radius:4px; overflow:hidden; }
.node{ background:var(--panel); padding:16px 16px 14px; position:relative; }
.node-top{ display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; }
.node-role{ font-family:'IBM Plex Mono',monospace; font-size:0.64rem; letter-spacing:0.12em;
  text-transform:uppercase; color:var(--nc); }
.node-idx{ font-family:'IBM Plex Mono',monospace; font-size:0.62rem; color:var(--tx3); }
.node-val{ font-family:'IBM Plex Sans',sans-serif; font-weight:600; font-size:1.15rem;
  color:var(--tx1); text-transform:capitalize; }
.node-sub{ font-family:'IBM Plex Mono',monospace; font-size:0.66rem; color:var(--tx2);
  margin-top:5px; min-height:1.4em; }
.bar{ height:3px; background:rgba(255,255,255,0.05); border-radius:2px; margin-top:12px; overflow:hidden; }
.bar-f{ height:100%; background:var(--nc); }
.node-badge{ display:inline-block; font-family:'IBM Plex Mono',monospace; font-weight:700;
  font-size:0.78rem; letter-spacing:0.08em; color:var(--nc); border:1px solid var(--nc);
  border-radius:3px; padding:4px 10px; margin-top:11px; }

/* ── EXECUTION LOG (signature) ── */
.log{ border:1px solid var(--rule); border-radius:4px; background:#060910;
  padding:14px 16px; }
.log-row{ display:grid; grid-template-columns:34px 96px 74px 1fr; gap:14px;
  font-family:'IBM Plex Mono',monospace; font-size:0.8rem; padding:4px 0; align-items:start; }
.log-idx{ color:var(--tx3); }
.log-stage{ color:var(--sc); letter-spacing:0.06em; }
.log-tick{ color:var(--tx1); font-weight:600; }
.log-msg{ color:var(--tx2); white-space:normal; word-break:break-word; line-height:1.5; }
.log-msg b{ color:var(--tx1); font-weight:500; }
.log-verdict{ color:var(--sc); font-weight:700; }
.log-caret{ font-family:'IBM Plex Mono',monospace; font-size:0.8rem; color:var(--amber);
  padding-top:6px; }

/* ── VERDICT STAMP ── */
.stamp{ display:inline-block; font-family:'IBM Plex Mono',monospace; font-weight:700;
  font-size:0.95rem; letter-spacing:0.16em; text-transform:uppercase; color:var(--vc);
  border:2px solid var(--vc); border-radius:3px; padding:6px 16px; }
.vdetail{ border:1px solid var(--rule); border-radius:4px; background:var(--panel);
  padding:12px 16px; color:var(--tx1); font-size:0.85rem; line-height:1.7; margin-top:10px;
  font-family:'IBM Plex Mono',monospace; }
.vdetail b{ color:var(--amber); }
.vdetail ul{ margin:6px 0 0 0; padding-left:18px; }

/* ── streamlit widget overrides ── */
.stButton>button{
  font-family:'IBM Plex Mono',monospace; text-transform:uppercase; letter-spacing:0.1em;
  font-size:0.74rem; font-weight:600; border-radius:3px; padding:0.6rem 0.9rem;
  color:#070a11; background:var(--amber) !important; border:1px solid var(--amber) !important;
}
.stButton>button:hover{ box-shadow:0 0 18px rgba(255,176,0,0.4); }
[data-baseweb="select"]>div{ border-radius:3px !important; border-color:var(--rule) !important;
  background:var(--panel) !important; font-family:'IBM Plex Mono',monospace !important; }
div[data-testid="stExpander"]{ border:1px solid var(--rule) !important; border-radius:4px !important; }
div[data-testid="stExpander"] summary{ font-family:'IBM Plex Mono',monospace !important;
  font-size:0.78rem !important; color:var(--tx2) !important; }
div[data-testid="stAlert"]{ background:var(--panel) !important; border:1px solid var(--rule) !important;
  border-radius:4px !important; color:var(--tx1) !important; }

/* ── empty + footer ── */
.empty{ border:1px dashed var(--rule); border-radius:4px; padding:44px 24px; text-align:center;
  color:var(--tx2); font-family:'IBM Plex Mono',monospace; }
.empty b{ color:var(--tx1); display:block; font-size:1.05rem; margin-bottom:6px; }
.footer{ margin-top:34px; padding-top:14px; border-top:1px solid var(--rule);
  font-family:'IBM Plex Mono',monospace; font-size:0.66rem; color:var(--tx3);
  text-align:center; letter-spacing:0.08em; }
</style>
""", unsafe_allow_html=True)


# ============================================================
#  HELPERS
# ============================================================
def kpi(label, value, color, sub=""):
    s = f'<div class="kpi-s">{sub}</div>' if sub else ""
    return (f'<div class="kpi" style="--kc:{color}">'
            f'<div class="kpi-l">{label}</div>'
            f'<div class="kpi-v">{value}</div>{s}</div>')


def node_meter(idx, role, color, val, sub, pct):
    pct = max(0, min(100, pct))
    return (f'<div class="node" style="--nc:{color}">'
            f'<div class="node-top"><span class="node-role">{role}</span>'
            f'<span class="node-idx">{idx}</span></div>'
            f'<div class="node-val">{val}</div>'
            f'<div class="node-sub">{sub}</div>'
            f'<div class="bar"><div class="bar-f" style="width:{pct}%"></div></div></div>')


def node_badge(idx, role, color, val, sub, badge):
    return (f'<div class="node" style="--nc:{color}">'
            f'<div class="node-top"><span class="node-role">{role}</span>'
            f'<span class="node-idx">{idx}</span></div>'
            f'<div class="node-val">{val}</div>'
            f'<div class="node-sub">{sub}</div>'
            f'<div class="node-badge">{badge}</div></div>')


def log_row(idx, stage, color, tick, msg, verdict=""):
    v = f'<span class="log-verdict" style="--sc:{color}">{verdict}</span>' if verdict else ""
    return (f'<div class="log-row" style="--sc:{color}">'
            f'<span class="log-idx">{idx}</span>'
            f'<span class="log-stage">{stage}</span>'
            f'<span class="log-tick">{tick}</span>'
            f'<span class="log-msg">{msg} {v}</span></div>')


# ============================================================
#  HEADER BAR
# ============================================================
now = datetime.now().strftime("%H:%M:%S")
data = get_dashboard_data()

hb_l, hb_r = st.columns([3, 1])
with hb_l:
    st.markdown(
        '<div class="term-bar"><div class="term-left">'
        '<span class="wordmark">AU<b>RA</b></span>'
        '<span class="term-meta"><span class="live-dot"></span>Autonomous Risk &amp; Alpha · Session Live</span>'
        '</div><div class="term-right">'
        f'<div class="stat-inline">DECISIONS<br><b>{data["total"]}</b></div>'
        f'<div class="stat-inline">APPROVED<br><b>{data["approved_count"]}</b></div>'
        f'<div class="stat-inline">BLOCKED<br><b>{data["rejected_count"]}</b></div>'
        f'<div class="stat-inline">CLOCK<br><b class="mono">{now}</b><span class="cursor"></span></div>'
        '</div></div>',
        unsafe_allow_html=True)
with hb_r:
    st.write("")
    if st.button("▸ Run New Cycle", use_container_width=True):
        with st.spinner("Scanning · reasoning · enforcing risk..."):
            run_cycle(execute=False)
        st.success("Cycle complete — ledger updated.")

# ── session tape ──
if data["total"] > 0:
    items = ""
    for r in data["rows"][:12]:
        c = STATUS_COLOR.get(r["risk_status"], HOLD)
        items += (f'<span class="tape-item">{r["symbol"]} '
                  f'<b style="color:{c}">{r["action"]} · {r["risk_status"]}</b></span>')
    st.markdown(f'<div class="tape"><div class="tape-inner">{items}{items}</div></div>',
                unsafe_allow_html=True)

# ============================================================
#  EMPTY STATE
# ============================================================
if data["total"] == 0:
    st.markdown('<div class="empty"><b>No decisions on the ledger</b>'
                'Run a cycle to let the agent chain analyze the market and log its first audited decision.'
                '</div>', unsafe_allow_html=True)
    st.stop()

# ============================================================
#  01 · OVERVIEW
# ============================================================
st.markdown('<div class="sec"><div class="sec-eyebrow">01 · Overview</div>'
            '<div class="sec-title">Ledger Summary</div>'
            '<div class="sec-sub">Every decision AURA has proposed and enforced.</div></div>',
            unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)
k1.markdown(kpi("Total Decisions", data["total"], CYAN), unsafe_allow_html=True)
k2.markdown(kpi("Approved", data["approved_count"], UP), unsafe_allow_html=True)
k3.markdown(kpi("Risk Blocks", data["rejected_count"], DOWN, "Refused by risk engine"),
            unsafe_allow_html=True)
k4.markdown(kpi("Risk Deployed", f"${data['total_risk_deployed']:,.0f}", AMBER),
            unsafe_allow_html=True)

if data["exposure_blocks"] > 0:
    st.write("")
    st.markdown(f'<div class="expo"><b>{data["exposure_blocks"]}</b> trade(s) refused to protect '
                f'portfolio exposure — the AI wanted in, the deterministic risk engine said no.</div>',
                unsafe_allow_html=True)

# ============================================================
#  02 · AGENT ROOM
# ============================================================
st.markdown('<div class="sec"><div class="sec-eyebrow">02 · Agent Room</div>'
            '<div class="sec-title">Signal Chain — Latest Decision</div>'
            '<div class="sec-sub">Market read → strategy → adversarial critique → risk enforcement.</div></div>',
            unsafe_allow_html=True)

latest = data["rows"][0]
d = parse_row_detail(latest)
mv, th, cr, dec = d.get("market_view", {}), d.get("thesis", {}), d.get("critic", {}), d.get("decision", {})
status = dec.get("status", "?")
sc = STATUS_COLOR.get(status, HOLD)

chain = '<div class="chain">'
chain += node_meter("01", "Market Agent", CYAN, mv.get("trend", "?"),
                    "price &amp; momentum", float(mv.get("confidence", 0)) * 100)
chain += node_meter("02", "Strategy Agent", VIOLET, th.get("action", "?"),
                    "trade thesis", float(th.get("confidence", 0)) * 100)
chain += node_meter("03", "Critic Agent", AMBER, cr.get("verdict", "?"),
                    f'stress test · {cr.get("critic_score", 0)}/100', float(cr.get("critic_score", 0)))
chain += node_badge("04", "Risk Engine", sc, latest.get("symbol", "?"),
                    "deterministic · final say", status)
chain += '</div>'
st.markdown(chain, unsafe_allow_html=True)

# ============================================================
#  03 · DECISION TRACE (execution log)
# ============================================================
st.markdown('<div class="sec"><div class="sec-eyebrow">03 · Audit Trail</div>'
            '<div class="sec-title">Decision Trace</div>'
            '<div class="sec-sub">Any logged decision, replayed as an execution log — reasoning to ruling.</div></div>',
            unsafe_allow_html=True)

options = {f'{r["symbol"]}  ·  {r["action"]}  ·  {r["risk_status"]}  ·  #{r["id"]}': r
           for r in data["rows"]}
choice = st.selectbox("Select a decision", list(options.keys()), label_visibility="collapsed")
row = options[choice]
d = parse_row_detail(row)
mv, th, cr, dec = d.get("market_view", {}), d.get("thesis", {}), d.get("critic", {}), d.get("decision", {})
status = dec.get("status", "?")
sc = STATUS_COLOR.get(status, HOLD)
ts = row.get("timestamp", "")
tick = row["symbol"]
ev = " · ".join(_short(e, 45) for e in mv.get("evidence", [])[:2]) or "no evidence logged"

log = f'<div class="log"><div class="log-row" style="--sc:{AMBER}"><span class="log-idx"></span>' \
      f'<span class="log-stage" style="color:{AMBER}">SESSION</span><span class="log-tick">{tick}</span>' \
      f'<span class="log-msg">trace opened · {ts}</span></div>'
log += log_row("001", "MARKET", CYAN, tick,
               f'{mv.get("trend","?")} · conf <b>{float(mv.get("confidence",0))*100:.0f}%</b> · {ev}')
log += log_row("002", "STRATEGY", VIOLET, tick,
               f'<b>{th.get("action","?")}</b> · conf <b>{float(th.get("confidence",0))*100:.0f}%</b> · {_short(th.get("entry_reason",""), 90)}')
log += log_row("003", "CRITIC", AMBER, tick,
               f'score <b>{cr.get("critic_score",0)}/100</b> · risk: {_short(cr.get("strongest_risk","none"), 80)}',
               cr.get("verdict", ""))
if status == "APPROVED":
    s = dec.get("sizing", {})
    log += log_row("004", "RISK", UP, tick,
                   f'{dec.get("action")} <b>{s.get("shares")}</b> sh · ${s.get("position_value",0):,.0f} · risk ${s.get("risk_amount",0):,.0f}',
                   "APPROVED")
elif status == "REJECTED":
    reasons = " · ".join(dec.get("rejections", [])) or "policy violation"
    log += log_row("004", "RISK", DOWN, tick, _short(reasons, 110), "REFUSED")
else:
    log += log_row("004", "RISK", HOLD, tick, "strategy chose to hold", "NO TRADE")
log += f'<div class="log-caret">▸ <span class="cursor"></span></div></div>'
st.markdown(log, unsafe_allow_html=True)

if cr.get("counter_arguments"):
    with st.expander("▸ Cross-examination — critic's counter-arguments"):
        for arg in cr["counter_arguments"]:
            st.markdown(f'`—` {arg}')

# verdict stamp
vc = sc
label = {"APPROVED": "Approved", "REJECTED": "Refused", "NO_TRADE": "No Trade"}.get(status, status)
st.write("")
if status == "APPROVED":
    s = dec.get("sizing", {})
    st.markdown(f'<span class="stamp" style="--vc:{vc}">{label}</span>'
                f'<div class="vdetail">{dec.get("action")} <b>{s.get("shares")}</b> shares · '
                f'position ≈ <b>${s.get("position_value",0):,.0f}</b> · '
                f'risk ≈ <b>${s.get("risk_amount",0):,.0f}</b></div>', unsafe_allow_html=True)
elif status == "REJECTED":
    lis = "".join(f"<li>{r}</li>" for r in dec.get("rejections", [])) or "<li>policy violation</li>"
    st.markdown(f'<span class="stamp" style="--vc:{vc}">{label}</span>'
                f'<div class="vdetail">Blocked by the risk engine:<ul>{lis}</ul></div>',
                unsafe_allow_html=True)
else:
    st.markdown(f'<span class="stamp" style="--vc:{vc}">{label}</span>'
                f'<div class="vdetail">Strategy Agent chose to hold — no position opened.</div>',
                unsafe_allow_html=True)

st.markdown('<div class="footer">AURA · every trade proposed by AI, enforced by a deterministic '
            'auditable risk engine · paper trading only · not investment advice</div>',
            unsafe_allow_html=True)