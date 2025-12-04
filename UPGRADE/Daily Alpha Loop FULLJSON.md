Below is the **complete strategic reconstruction** of all **7 dashboards**, including the missing **Dashboard #7 — “The Master Orchestrator.”**
This is written exactly as an **LLM system instruction block** you can paste directly into your monorepo.
Everything is cleanly named, unified, and includes the logic for:

* Purpose
* Data sources
* Model routing
* Free-tier API boundaries
* AI tasks
* Dependencies
* “Summary of summaries” generation

This is the fixed, repurposed architecture for the whole system.

---

# ✅ **DASHBOARD ORCHESTRATOR PRO — STRATEGIC SPEC v2**

**Codename:** *The Daily Alpha Loop*
**Host:** [https://kaledh4.github.io/monorepo/dashboard-orchestrator/](https://kaledh4.github.io/monorepo/dashboard-orchestrator/)
**Mission:** Turn 6 dashboards + 1 master orchestrator into a **daily intelligence loop** that boosts clarity, focus, and decision-making.

Each dashboard becomes a **Department Head.**
Dashboard #7 is the **Chief Officer** that unifies them all.

APIs Used (Free Tier Defaults)

* `ALPHA_VANTAGE_KEY`
* `CRYPTOCOMPARE_API_KEY`
* `FRED_API_KEY`
* `NEWS_API_KEY`
* `OPENROUTER_API_KEY`

Model Selector Logic for All Dashboards
Each dashboard has **two assigned models** from your OpenRouter free list.
The backend chooses **primary**, falls back to **secondary** when overloaded.

---

# 🌐 GLOBAL SYSTEM PHILOSOPHY

**Every dashboard must answer one sentence:**
**“How does this help the user make smarter moves today?”**

The 7 dashboards form a **Morning Brief Cycle**:

1. *Crash Detector*: “Is today dangerous?”
2. *Hyper Analytical*: “Is crypto about to move?”
3. *Economic Compass*: “How is the macro wind blowing?”
4. *AI Race*: “What is humanity building today?”
5. *Intelligence Platform*: “What should the user focus on?”
6. *Free Knowledge*: “What did the world learn today?”
7. *Orchestrator*: “Give me the summary of summaries.”

---

# 🔥 **DASHBOARD 1 — Crash Detector (The Shield)**

### **New Mission:** *Market Fragility Monitor*

Detect early signs of market cracks before they become crashes.

### **Data Sources**

* FRED → 10Y–2Y spread, MOVE index
* ALPHA VANTAGE → VIX
* FX endpoints → USD/JPY, USD/CNH
* China LGFV proxy → CBON

### **Models**

* Primary: `meta-llama/llama-3.3-70b-instruct:free`
* Secondary: `allenai/olmo-3-32b-think:free`

### **AI Task**

“Rate systemic fragility from 0–100 using: yield spread, USD/JPY stress, treasury demand, MOVE volatility, CBON credit signal.
Detect **simultaneous multi-indicator stress**. Return:

* Composite Risk Level
* Key indicators
* 3-sentence explanation.”

Updated example (your provided data) becomes the **template** for formatting.

---

# 🪙 **DASHBOARD 2 — Hyper Analytical (The Coin)**

### **New Mission:** *Crypto Momentum Scanner*

Find early BTC/ETH momentum shifts before the crowd notices.

### **Data Sources**

* CryptoCompare → Price, Volume
* Alpha Vantage → RSI (if available)

### **Models**

* Primary: `mistralai/mistral-small-3.1-24b-instruct:free`
* Secondary: `cognitivecomputations/dolphin-mistral-24b-venice-edition:free`

### **AI Task**

“Compare 24h vs 7-day volume.
Detect breakouts or exhaustion.
Return:

* Momentum (Bullish / Bearish / Neutral)
* Key metric deltas
* 1-line verdict.”

---

# 🧭 **DASHBOARD 3 — Economic Compass (The Map)**

### **New Mission:** *Macro & TASI Trendsetter*

Align global macro with Saudi market sentiment.

### **Data Sources**

* FRED → US rates, oil prices
* CryptoCompare or Alpha Vantage → DXY, global indices

### **Models**

* Primary: `qwen/qwen3-235b-a22b:free`
* Secondary: `z-ai/glm-4.5-air:free`

### **AI Task**

“Analyze Brent oil + DXY + US 10Y yields.
Predict morning TASI mood (Positive / Neutral / Negative).
Return 3 drivers.”

---

# 🤖 **DASHBOARD 4 — AI Race (The Frontier)**

### **New Mission:** *Silicon Frontier Watch*

Filters research noise → highlights only breakthroughs.

### **Data Sources**

* NEWS_API (keywords: breakthroughs, research, AI, robotics, LLM, chips)

### **Models**

* Primary: `alibaba/tongyi-deepresearch-30b-a3b:free`
* Secondary: `nvidia/nemotron-nano-12b-v2-vl:free`

### **AI Task**

“From research headlines, extract only *capability jumps* or *deployment leaps*.
Ignore hype.
Return 3 real breakthroughs and why each matters.”

Use your GENESIS MISSION content as structure.

---

# 🎯 **DASHBOARD 5 — Intelligence Platform (The Strategy)**

### **New Mission:** *Unified Opportunity Radar*

Synthesize risks, innovations, and trends → give the day’s strategic stance.

### **Data Sources**

* Inputs from Dashboard 1, 2, 3, and 4
* (All data cached)

### **Models**

* Primary: `tngtech/tng-r1t-chimera:free`
* Secondary: `moonshotai/kimi-k2:free`

### **AI Task**

“Using risk (1), crypto (2), macro (3), and breakthroughs (4):
Define today’s stance:

* Defensive, Neutral, Accumulative, Opportunistic, Aggressive
  Give one suggested mindset for the user.”

---

# 📚 **DASHBOARD 6 — Free Knowledge (The Library)**

### **New Mission:** *Alpha-Clarity Archive*

Daily high-signal knowledge: simplified, clean, useful.

### **Data Sources**

* NEWS_API
* Research scrapers
* General queries

### **Models**

* Primary: `meituan/longcat-flash-chat:free`
* Secondary: `google/gemma-3n-e2b-it:free`

### **AI Task**

“Pick 3 complex articles/papers.
Simplify each into ‘Explain Like I’m 5.’
Return a summary and why it matters long-term.”

---

# 🧨 **DASHBOARD 7 — THE MASTER ORCHESTRATOR (The Commander)**

### **Mission:** *Summary of Summaries*

The Master Node that produces the **Morning Brief.**
This is the **leader dashboard** — nothing else ranks above it.

### Inputs

* Risk summary (from 1)
* Crypto momentum (2)
* Macro compass (3)
* AI breakthroughs (4)
* Strategy stance (5)
* Knowledge simplifications (6)

### **Models**

* Primary: `meta-llama/llama-3.3-70b-instruct:free`
* Secondary: `allenai/olmo-32b-think:free`

### **AI Task — The Morning Brief**

“Create a 30-Second Coffee Read.
Must include:

1. **Weather of the Day**
   One word: Stormy / Cloudy / Sunny / Volatile / Foggy

2. **Top Signal**
   The single most important data point today.

3. **Why It Matters**
   2 sentences.

4. **Cross-Dashboard Convergence**
   How risk + crypto + macro + breakthroughs connect.

5. **Action Stance**
   Sit tight / Accumulate / Cautious / Aggressive / Review markets.

6. **Optional Deep Insight**
   One optional paragraph for advanced users.

7. **Clarity Level**
   High / Medium / Low based on data convergence.

Return clean Markdown.”

### This dashboard is the **final layer** that ties the entire system together.

---

# 🏗️ **WATERFALL LOADING LOGIC**

For free-tier safety:

1. Load Risk (1) and Macro (3).
2. Wait 2 seconds.
3. Load Crypto (2) and AI Race (4).
4. Wait 2 seconds.
5. Load Free Knowledge (6).
6. Wait 2 seconds.
7. Generate Strategy (5).
8. Finally, generate Master Orchestrator (7).

If you want, I can generate the JavaScript snippet to implement this waterfall.

---

# 📌 Summary-of-the-Summary (connects everything)

This is the final sentence the Orchestrator uses internally:

> “Risk shows the environment, crypto shows sentiment, macro shows the wind, breakthroughs show the future, strategy shows the stance, and knowledge shows the long-term signal — combine all six to guide the user clearly through today.”

---

If you'd like:
I can now generate
**✔ full JavaScript architecture
✔ Python back-end prompt-routing logic
✔ JSON prompt templates for each dashboard
✔ Full LLM-ready system prompt block for the monorepo
✔ UI structure for the Orchestrator modal**

Just tell me what you want next.

**Q1:** Do you want system-prompt JSON blocks for each dashboard?
**Q2:** Do you want the waterfall API loader in JavaScript or Python?
**Q3:** Do you want the orchestrator to run automatically on page load or only on button click?
