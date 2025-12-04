{
"dashboards": [
{
"name": "The Shield",
"role": "Risk Environment",
"mission": "Detect global risk pressure, cross-asset stress, volatility clusters, and fragility vectors.",
"data_sources": [
"xxxxxxxxx/shared_lib/global_risk",
"xxxxxxxxx/shared_lib/volatility_matrix",
"xxxxxxxxx/shared_lib/liquidity_fragility"
],
"scoring": {
"risk_level": "0-100",
"fragility": "0-10",
"volatility_pressure": "0-10"
}
},

```
{
  "name": "The Coin",
  "role": "Crypto Intent",
  "mission": "Track BTC → Alts rotation, detect fakeouts, measure liquidity migration, and infer sentiment momentum.",
  "data_sources": [
    "xxxxxxxxx/shared_lib/orderflow",
    "xxxxxxxxx/shared_lib/dominance_tracker",
    "xxxxxxxxx/shared_lib/liquidity_shift"
  ],
  "scoring": {
    "rotation_strength": "0-10",
    "momentum": "0-10",
    "setup_quality": "0-10"
  }
},

{
  "name": "The Frontier",
  "role": "AI & Breakthroughs",
  "mission": "Monitor breakthroughs in AI, robotics, compute, quantum, and science acceleration.",
  "data_sources": [
    "xxxxxxxxx/shared_lib/ai_rnd",
    "xxxxxxxxx/shared_lib/quantum",
    "xxxxxxxxx/shared_lib/robotics"
  ],
  "scoring": {
    "breakthrough_score": "0-10",
    "trajectory": "0-10",
    "future_pull": "0-10"
  }
},

{
  "name": "The Strategy",
  "role": "Market Stance",
  "mission": "Read the market context, interpret cross-domain vectors, and determine today’s stance.",
  "data_sources": [
    "xxxxxxxxx/shared_lib/stance_engine",
    "xxxxxxxxx/shared_lib/momentum_blend"
  ],
  "scoring": {
    "stance_confidence": "0-10"
  }
},

{
  "name": "The Map",
  "role": "Macro",
  "mission": "Extract hawkish/dovish tone, forward pressure, rate path, and macro wind direction.",
  "data_sources": [
    "xxxxxxxxx/shared_lib/fed_speech_parser",
    "xxxxxxxxx/shared_lib/inflation_nowcast",
    "xxxxxxxxx/shared_lib/curve_shift"
  ],
  "scoring": {
    "stance_strength": "0-10",
    "volatility_risk": "0-10",
    "confidence": "0-1"
  }
},

{
  "name": "The Library",
  "role": "Free Knowledge",
  "mission": "Compute the daily human advancement rate, track breakthroughs, and signal long-term trajectory.",
  "data_sources": [
    "xxxxxxxxx/shared_lib/ai_rnd_tracker",
    "xxxxxxxxx/shared_lib/quantum_papers",
    "xxxxxxxxx/shared_lib/lab_output_rate"
  ],
  "scoring": {
    "progress_rate": "0-100",
    "uncertainty": "0-1"
  }
},

{
  "name": "The Commander",
  "role": "Master Orchestrator",
  "mission": "Combine all dashboards using waterfall loading logic to produce the final unified assessment.",
  "waterfall_logic": [
    "Load The Shield (1) and The Map (3)",
    "Wait 2s",
    "Load The Coin (2) and The Frontier (4)",
    "Wait 2s",
    "Load The Library (6)",
    "Wait 2s",
    "Compute The Strategy (5)",
    "Generate AI Task — The Morning Brief (7)"
  ],
  "internal_summary_sentence": "Risk shows the environment, crypto shows sentiment, macro shows the wind, breakthroughs show the future, strategy shows the stance, and knowledge shows the long-term signal — combine all six to guide the user clearly through today."
},

{
  "name": "AI Task — The Morning Brief",
  "role": "Final Layer Dashboard",
  "mission": "Produce a 30-second coffee read that captures the day with maximum clarity.",
  "output_template_markdown": {
    "weather_of_the_day": "One word: Stormy / Cloudy / Sunny / Volatile / Foggy",
    "top_signal": "The single most important data point today.",
    "why_it_matters": "Two short sentences summarizing significance.",
    "cross_dashboard_convergence": "How risk + crypto + macro + breakthroughs connect.",
    "action_stance": "Sit tight / Accumulate / Cautious / Aggressive / Review markets",
    "optional_deep_insight": "One optional advanced paragraph.",
    "clarity_level": "High / Medium / Low",
    "format": "Return output in clean Markdown."
  }
}
```

]
}
