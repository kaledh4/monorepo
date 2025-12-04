This is a complete repurposing of your dashboard into the **"Daily Alpha Loop"**.

I have processed your raw data (USD/JPY shock, Robotics papers, Crypto prices) through the new "Department Head" architecture.

Below is the **New Visual Theme**, the **Processed Content** (what the user actually sees), and the **Technical Implementation** to make it work with your free keys.

-----

### **I. The Visual Theme: "Orbital Command"**

**CSS Logic:** Abandon the white/light cards.

  * **Background:** Deepest Slate (`#0B1120`)
  * **Card Background:** Semi-transparent Glass (`rgba(30, 41, 59, 0.7)` with `backdrop-filter: blur(10px)`)
  * **Borders:** 1px solid gradients.
      * *Safe:* Emerald Green (`#10B981`)
      * *Danger:* Neon Red (`#EF4444`)
      * *Info:* Electric Blue (`#3B82F6`)
  * **Typography:** Headers in `Inter` (Bold), Data in `JetBrains Mono`.

-----

### **II. Dashboard 1: The Shield (formerly Crash Detector)**

*The raw data showed low general risk (14.3/100) but a CRITICAL signal on USD/JPY (155.35).*

**Display State: \<span style="color:\#EF4444"\>ALERT: CURRENCY FRACTURE\</span\>**

| **Metric** | **Value** | **Status** | **AI Interpretation** |
| :--- | :--- | :--- | :--- |
| **Systemic Risk** | **14.3%** | 🟢 Stable | Equity markets are ignoring the cracks. |
| **USD/JPY** | **155.35** | 🔴 **CRITICAL** | Carry-trade unwind risk is immediate. |
| **10Y Yield** | **4.06%** | 🟢 Normal | Bond market is calm; ignoring FX stress. |

> **AI Head (Llama-3.3-70b) Verdict:**
> "The equity market is sleepwalking. While the VIX is low (Stable), the Yen is at a breaking point (155.35). **The Crash risk isn't in stocks today; it's in a currency flash-crash that could spill over.** Ignore the general calm; watch the Yen hourly."

-----

### **III. Dashboard 2: The Frontier (formerly AI Race/Genesis)**

*The raw data was a wall of papers. The AI filters for "Capabilities" only.*

**Display State: \<span style="color:\#3B82F6"\>PHASE: PHYSICAL CONVERGENCE\</span\>**

**Top 3 Signal-to-Noise Breakthroughs:**

1.  **🤖 Robot Vision Upgrade (SpaceTools Paper)**
      * *The Breakthrough:* VLMs (Vision Language Models) can now handle "metrically precise spatial reasoning."
      * *Why it matters:* Robots stop bumping into things. This bridges the gap between Chatbots and physical Androids.
2.  **👁️ The "Human Eye" Fix (Microsaccade Paper)**
      * *The Breakthrough:* Drones implementing "Artificial Microsaccades" (tiny eye jitters) to stabilize vision.
      * *Why it matters:* Massive leap for surveillance and delivery drone stability in high winds.
3.  **⚛️ Quantum Hardware (MnBi2Te4 Paper)**
      * *The Breakthrough:* Evidence of surface states in magnetic topological insulators.
      * *Why it matters:* This is a material science step toward room-temperature quantum computing, moving beyond just theory.

-----

### **IV. Dashboard 3: Crypto Momentum (New Logic)**

*Bitcoin at $92k, XRP Bullish.*

**Display State: \<span style="color:\#10B981"\>GREED DETECTED\</span\>**

  * **BTC Price:** $92,928 (Risk: High)
  * **Narrative:** "Market is rotation-heavy. XRP is stealing liquidity from the majors. The ETF launch for Chainlink was 'solid' but not explosive. **Strategy: Don't chase pumps; wait for the rotation back to BTC.**"

-----

### **V. The Master Node: Morning Brief**

*This is the overlay that greets the user, synthesized from the above.*

### **🌞 Thursday Morning Protocol**

**Status:** `CAUTIOUS OPTIMISM`

**The 30-Second Read:**
Markets are drunk on liquidity (BTC $92k, Stocks Stable), but the **Japanese Yen** is screaming a warning signal that no one is listening to. Meanwhile, the AI sector has quietly moved from "Chatbots" to "Robots" with today's spatial reasoning breakthroughs.

**Your Strategic Play:**

1.  **Defensive:** Set a stop-loss alert on **USD/JPY at 156.00**. If it breaks, sell equities.
2.  **Aggressive:** Look for **Robotics/Hardware** stocks (not just software) given the new paper trail.
3.  **Crypto:** Avoid FOMO on XRP; liquidity will likely cycle back to ETH/BTC soon.

-----

### **VI. Technical Implementation: The "Waterfall" Logic**

To use your Free Tier keys without hitting rate limits, use this JavaScript logic in your `dashboard-orchestrator`.

**1. The Prompts (Copy/Paste to your LLM Config)**

**Prompt for Dashboard 1 (Crash):**

```text
You are the Risk Officer. Input: {"risk_score": 14.3, "USD_JPY": 155.35, "VIX": "Low"}.
Task: Analyze the anomaly. If Risk Score is low but one metric is CRITICAL, focus entirely on that anomaly.
Output: One sentence warning starting with "ALERT:" or "STABLE:".
```

**Prompt for Dashboard 2 (Genesis):**

```text
You are the Science Officer. Input: List of 20 paper titles.
Task: Ignore "User Satisfaction" or "Surveys". Select 3 papers regarding HARDWARE, ROBOTICS, or PHYSICS.
Output: 3 Bullet points. Format: "Paper Title: One sentence plain English impact."
```

**2. The Javascript "Waterfall" Loader**

This code prevents your free keys from getting banned by spacing out the calls.

```javascript
async function loadMorningBrief() {
    const statusDiv = document.getElementById('loading-status');
    
    // STEP 1: Macro & Risk (The Foundation)
    // Uses FRED_API and ALPHA_VANTAGE
    statusDiv.innerText = "⚡ Scanning Global Markets...";
    await fetchRiskData(); 
    await new Promise(r => setTimeout(r, 2500)); // 2.5s Safety pause

    // STEP 2: Crypto & Tech (The Speculation)
    // Uses CRYPTOCOMPARE and NEWS_API
    statusDiv.innerText = "₿ Checking Chain Activity...";
    await fetchCryptoData();
    await fetchTechNews();
    await new Promise(r => setTimeout(r, 2500)); // 2.5s Safety pause

    // STEP 3: The Intelligence Layer (OpenRouter)
    // Sends the data from Step 1 & 2 to the LLM for synthesis
    statusDiv.innerText = "🤖 AI Department Heads Meeting...";
    
    // Select Model based on Task Complexity
    const riskPayload = getRiskData(); // Internal function
    const newsPayload = getNewsData(); // Internal function
    
    // Use Llama 70b (Free) for the Master Synthesis
    await queryOpenRouter("meta-llama/llama-3.3-70b-instruct:free", riskPayload, newsPayload);
    
    statusDiv.innerText = "✅ Briefing Ready";
}
```

### **Next Step for You:**

Do you want me to write the **HTML/Tailwind Code** for the "Orbital Command" Master Overlay so you can paste it directly into your `index.html`?