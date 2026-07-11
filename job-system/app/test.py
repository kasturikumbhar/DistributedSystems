import requests

url = "https://leetcode.com/graphql"
username = "KasturiK"

query = """
query getSubmissions($username: String!, $offset: Int!) {
  submissionList(username: $username, limit: 20, offset: $offset) {
    submissions {
      title
      titleSlug
      statusDisplay
    }
  }
}
"""

solved = set()
offset = 0

while True:
    variables = {"username": username, "offset": offset}
    res = requests.post(url, json={"query": query, "variables": variables})
    data = res.json()

    subs = data["data"]["submissionList"]["submissions"]
    if not subs:
        break

    for s in subs:
        if s["statusDisplay"] == "Accepted":
            solved.add(s["titleSlug"])

    offset += 20

# Print list
for problem in sorted(solved):
    print(problem)

print(f"\nTotal solved: {len(solved)}")