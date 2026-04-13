from truthgpt.search import gather_evidence
from truthgpt.verify import verify_claim

claim = "The Eiffel Tower is located in Paris, France."
evidence = gather_evidence("Eiffel Tower Paris France", per_source=3)

res = verify_claim(claim, evidence)

print("VERDICT:", res.verdict)
print("CONF:", round(res.confidence, 3))
print("SCORES:", {k: round(v, 3) for k, v in res.scores.items()})
if res.evidence:
    print("\nBEST EVIDENCE:")
    print(res.evidence.source, "-", res.evidence.title)
    print(res.evidence.url)
    print(res.evidence.snippet)