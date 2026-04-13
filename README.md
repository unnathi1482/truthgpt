
# ✅ TruthGPT – AI Answers You Can Actually Trust

> An AI chatbot that verifies every claim against real sources before showing you the answer.

---

## 🧠 What is TruthGPT?

Regular AI (like ChatGPT) can confidently give wrong answers (hallucinations).

**TruthGPT solves this** by automatically:
1. Generating an answer using a free LLM (Groq)
2. Breaking the answer into individual claims
3. Searching Wikipedia + DuckDuckGo for evidence
4. Verifying each claim using a local AI model (DeBERTa NLI)
5. Showing you the answer **with sources and a verified % score**

---

## 🎯 Example

**User asks:** "Tell me about the Eiffel Tower"

**TruthGPT:**
- ✅ VERIFIED – "The Eiffel Tower is located in Paris, France." (conf: 0.999)
- ✅ VERIFIED – "It was built for the 1889 World's Fair." (conf: 0.986)
- ❌ CONTRADICTED – "It stands at 324m tall." (Wikipedia says 330m)
- ⚠️ UNVERIFIED – "It weighs approximately 10,000 tons."

**Verified: 50% | Sources: Wikipedia**

---

## 🏗️ How It Works

```text
User Question
     ↓
Groq LLM generates answer
     ↓
Claims extracted from answer
     ↓
Wikipedia + DuckDuckGo searched for evidence
     ↓
DeBERTa NLI model verifies each claim
     ↓
Answer shown with verified %, sources, claim details
```

---

## 💻 Tech Stack

| Component | Tool | Why |
|-----------|------|-----|
| UI | Streamlit | Simple, professional |
| LLM | Groq API (llama-3.1-8b-instant) | Free, fast |
| Evidence | Wikipedia + DuckDuckGo | Free, no API key |
| Verification | DeBERTa NLI (local) | Free, runs on CPU |
| Hosting | Hugging Face Spaces | Free |

**Total cost: $0**

---

## 🚀 Run Locally

### 1) Clone the repo
> Note: This assumes your GitHub repo name is **truthgpt**.

```bash
git clone https://github.com/unnathi1482/truthgpt.git
cd truthgpt
```

### 2) Create virtual environment (Windows)
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3) Install dependencies
```bash
pip install -r requirements.txt
```

### 4) Add your Groq API key
Create a `.env` file in the project root:

```env
GROQ_API_KEY="your-groq-api-key-here"
```

Get a free key at: https://console.groq.com/

### 5) Run the app
```bash
streamlit run app.py
```

---

## 📁 Project Structure

```text
truthgpt/
├── app.py                  # Streamlit UI
├── requirements.txt        # Dependencies
├── .gitignore              # Git ignore rules
├── .env.example            # API key template (do not put real keys here)
├── ROADMAP.md              # Project roadmap
├── LICENSE                 # MIT License
├── tests/                  # Development test scripts
└── truthgpt/               # Core package
    ├── __init__.py
    ├── llm.py              # Groq LLM integration
    ├── claims.py           # Claim extraction
    ├── search.py           # Wikipedia + DDG search
    ├── verify.py           # DeBERTa NLI verification
    ├── pipeline.py         # End-to-end orchestration
    └── format_answer.py    # Answer formatting
```

---

## 📊 Roadmap

See [ROADMAP.md](ROADMAP.md) for planned features (v2, v3).

---

## 🔑 API Keys Needed

| Key | Required | Where to get |
|-----|----------|--------------|
| `GROQ_API_KEY` | ✅ Yes | https://console.groq.com/ |

No other keys needed. Wikipedia and DuckDuckGo are free with no signup.

---

## ⚠️ Limitations (MVP v1)

- Verification works best for factual, specific claims
- Very subjective or vague claims may show as unverified
- Pipeline takes ~10–20 seconds per question (v3 will be faster)
- DuckDuckGo search may occasionally return no results

---

## 👩‍💻 Built By

**Unnathi Yamavaram**  
[GitHub](https://github.com/unnathi1482)

Built as a portfolio project to demonstrate:
- LLM integration + prompt engineering
- NLP / NLI fact verification
- Full-stack AI app development
- Real-world problem solving (AI hallucinations)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
```

