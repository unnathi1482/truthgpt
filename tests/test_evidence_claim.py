from truthgpt.search import wikipedia_search, gather_evidence

claim = "The Eiffel Tower is an iconic iron lattice tower located in Paris, France."

print("=== Wikipedia search results (titles) ===")
wiki = wikipedia_search(claim, limit=5)
print([e.title for e in wiki])

print("\n=== Gather evidence (source + title) ===")
ev = gather_evidence(claim, per_source=3)
for e in ev:
    print(f"[{e.source}] {e.title} -> {e.url}")