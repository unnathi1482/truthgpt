from truthgpt.search import wikipedia_search

q = "Tell me about the Eiffel Tower in 4-6 bullet points."
res = wikipedia_search(q, limit=5)

print("Top Wikipedia titles for question:")
for e in res:
    print("-", e.title)