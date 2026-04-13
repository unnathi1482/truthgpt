from truthgpt.claims import extract_claims

sample = """
- The Eiffel Tower is 324 meters tall.
- It was built for the 1889 World's Fair.
It is located in Paris, France.
"""

print(extract_claims(sample))