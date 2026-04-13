from truthgpt.pipeline import run_pipeline

out = run_pipeline("Tell me about the Eiffel Tower in 4-5 sentences.", max_claims=6)

print("ANSWER:\n", out.answer, "\n")
print("VERIFIED:", round(out.verified_ratio * 100, 1), "%")
print("\nCLAIM RESULTS:")
for r in out.results:
    print("-", r.verdict.upper(), f"({r.confidence:.3f})", r.claim)

print("\nSOURCES (top 5):")
for u in out.sources[:5]:
    print("-", u)