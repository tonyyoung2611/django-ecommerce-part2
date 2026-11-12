import requests


def get_reddit_posts(subreddit='python'):
    url = f"https://www.reddit.com/r/{subreddit}/.json"

    headers = {
        'User-Agent': 'ASU-eCommerce-Learning-App/1.0'
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        posts = []

        for item in data['data']['children'][:10]:
            post = item['data']

            posts.append({
                'title': post['title'],
                'author': post['author'],
                'url': 'https://www.reddit.com' + post['permalink']
            })

        return posts

    except (requests.RequestException, ValueError, KeyError):
        return []