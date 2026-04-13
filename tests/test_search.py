from truthgpt.search import gather_evidence

ev = gather_evidence("Eiffel Tower height 324 meters", per_source=2)
for e in ev:
    print(f"[{e.source}] {e.title}\n{e.url}\n{e.snippet}\n")