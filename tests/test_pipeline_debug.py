from truthgpt.pipeline import run_pipeline

out = run_pipeline("Tell me about the Eiffel Tower in 4-6 bullet points.", max_claims=6)
print("TOPIC_QUERY:", out.topic_query)
print("TOPIC_TITLE:", out.topic_title, "\n")

print("ANSWER:\n", out.answer, "\n")
print("VERIFIED:", round(out.verified_ratio * 100, 1), "%\n")

for i, r in enumerate(out.results, start=1):
    print(f"#{i} {r.verdict.upper()} (conf={r.confidence:.3f})")
    print("CLAIM:", r.claim)
    print("SCORES:", {k: round(v, 3) for k, v in r.scores.items()})

    if r.evidence:
        print("EVIDENCE SOURCE:", r.evidence.source)
        print("EVIDENCE TITLE :", r.evidence.title)
        print("EVIDENCE URL   :", r.evidence.url)
        print("EVIDENCE SNIP  :", r.evidence.snippet)
    else:
        print("EVIDENCE: None")

    print("-" * 80)