import requests
import json

def get_problem_data(title_slug):
    url = "https://leetcode.com/graphql"
    query = """
    query questionData($titleSlug: String!) {
      question(titleSlug: $titleSlug) {
        questionId
        title
        titleSlug
        content
        difficulty
        topicTags {
          name
        }
        codeSnippets {
          lang
          langSlug
          code
        }
        sampleTestCase
      }
    }
    """
    variables = {"titleSlug": title_slug}
    
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    get_problem_data("two-sum")
