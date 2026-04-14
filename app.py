import streamlit as st

from truthgpt.pipeline import run_pipeline
from truthgpt.format_answer import format_answer_for_display

st.set_page_config(page_title="TruthGPT", page_icon="✅", layout="centered")

st.title("TruthGPT")
st.caption("AI answers with claim-by-claim verification (MVP v1)")

with st.form("ask_form"):
    question = st.text_input(
        "Ask a question",
        placeholder="e.g., Tell me about the Eiffel Tower in 4–6 bullet points.",
    )
    submitted = st.form_submit_button("Get verified answer")

if submitted:
    if not question.strip():
        st.warning("Please enter a question.")
        st.stop()

    with st.spinner("Generating answer and verifying claims..."):
        try:
            out = run_pipeline(question, max_claims=6, evidence_per_source=3)
        except Exception as e:
            st.error(f"Unexpected error: {type(e).__name__}: {e}")
            st.stop()

    if getattr(out, "used_fallback", False):
        st.warning(
            "LLM is currently unavailable from this server. "
            "Showing an evidence-based answer (Wikipedia) instead."
        )

    st.subheader("Answer")
    st.markdown(format_answer_for_display(out.answer))

    st.subheader("Verification summary")
    percent = int(round(out.verified_ratio * 100))
    st.metric("Verified claims", f"{percent}%")
    st.progress(out.verified_ratio)

    if out.topic_title:
        st.caption(f"Detected topic: **{out.topic_title}**")

    st.subheader("Claim-by-claim verification")
    with st.expander("Show detailed verification", expanded=True):
        if not out.results:
            st.write("No claims extracted from the answer.")
        else:
            for r in out.results:
                if r.verdict == "verified":
                    label = "✅ VERIFIED"
                    color = "green"
                elif r.verdict == "contradicted":
                    label = "❌ CONTRADICTED"
                    color = "red"
                else:
                    label = "⚠️ UNVERIFIED"
                    color = "orange"

                st.markdown(
                    f"**<span style='color:{color}'>{label}</span>**",
                    unsafe_allow_html=True,
                )
                st.write(r.claim)
                st.caption(f"Confidence: `{r.confidence:.3f}`")

                if r.evidence:
                    st.markdown(f"**Source:** [{r.evidence.title}]({r.evidence.url})")
                    st.caption(r.evidence.snippet)
                else:
                    st.caption("No evidence found for this claim.")
                st.divider()

    st.subheader("Sources")
    if out.sources:
        for url in out.sources[:10]:
            st.write(url)
        if len(out.sources) > 10:
            st.caption(f"...and {len(out.sources) - 10} more.")
    else:
        st.write("No sources collected.")