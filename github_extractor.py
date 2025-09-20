import requests
import json

# Load your skills database from JSON
with open("skills_database.json", "r") as f:
    skills_db = json.load(f)

skills_db = set([s.lower() for s in skills_db])  # normalize to lowercase


def extract_github_skills(username: str, token: str | None = None):
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    repos_url = f"https://api.github.com/users/{username}/repos"
    repos_res = requests.get(repos_url, headers=headers)
    if repos_res.status_code != 200:
        return []

    repos = repos_res.json()
    detected = set()

    for repo in repos:
        repo_name = repo["name"]
        owner = repo["owner"]["login"]

        # Languages
        lang_url = f"https://api.github.com/repos/{owner}/{repo_name}/languages"
        langs_res = requests.get(lang_url, headers=headers).json()
        for lang in langs_res.keys():
            if lang.lower() in skills_db:
                detected.add(lang.lower())

        # Topics
        topics_url = f"https://api.github.com/repos/{owner}/{repo_name}/topics"
        topics_res = requests.get(
            topics_url,
            headers={**headers, "Accept": "application/vnd.github.mercy-preview+json"},
        ).json()
        for topic in topics_res.get("names", []):
            if topic.lower() in skills_db:
                detected.add(topic.lower())

        # README
        readme_url = f"https://api.github.com/repos/{owner}/{repo_name}/readme"
        readme_res = requests.get(readme_url, headers=headers)
        if readme_res.status_code == 200:
            readme_text = requests.get(readme_res.json()["download_url"]).text.lower()
            for word in skills_db:
                if word in readme_text:
                    detected.add(word)

    return list(detected)
