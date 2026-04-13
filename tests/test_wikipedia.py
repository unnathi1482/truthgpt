from truthgpt.search import wikipedia_search

ev = wikipedia_search("Eiffel Tower height 324 meters", limit=3)
print("count:", len(ev))

for e in ev:
    print(f"[{e.source}] {e.title}\n{e.url}\n{e.snippet}\n")