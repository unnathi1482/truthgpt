# TruthGPT – Roadmap

## ✅ MVP v1 (Complete)
- [x] Groq LLM integration (answer generation)
- [x] Bullet-point factual prompt (reduces hallucination)
- [x] Claim extraction from LLM answer
- [x] Wikipedia evidence search (page extracts)
- [x] DuckDuckGo evidence search
- [x] Topic detection + relevance filtering
- [x] DeBERTa NLI fact verification (verified/contradicted/unverified)
- [x] Verified % score calculation
- [x] Basic Streamlit UI (answer + verification + sources)
- [x] Temperature strategy (stable by default, varied for random facts)
- [x] Clean answer formatting

## 🔄 MVP v2 (Planned)
- [ ] Better UI (colors, layout, cleaner sections)
- [ ] Color-coded claim verdicts (green/red/orange)
- [ ] Clickable source links with titles
- [ ] Hide raw verification details (show summary by default)
- [ ] Better verification summary (e.g., "3 of 6 claims verified")
- [ ] Show detected topic prominently
- [ ] Handle edge cases (no evidence found, API errors)
- [ ] Better wording for unverified/contradicted claims

## 🔄 MVP v3 (Planned)
- [ ] Parallel evidence searches (faster pipeline)
- [ ] Caching (don't re-verify same question twice)
- [ ] Better claim extraction (sentence-level)
- [ ] Chat history (multi-turn conversations)
- [ ] Loading indicators per pipeline stage
- [ ] More evidence sources
- [ ] Mobile-friendly UI
- [ ] Deploy to Hugging Face Spaces

## 💡 Future Ideas
- [ ] User feedback (thumbs up/down per claim)
- [ ] Export verified answer as PDF
- [ ] API endpoint for developers
- [ ] Browser extension