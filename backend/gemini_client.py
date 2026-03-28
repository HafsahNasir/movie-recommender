import sys
import os
import time
import requests

GROQ_URL = 'https://api.groq.com/openai/v1/chat/completions'
MODEL = 'llama-3.1-8b-instant'


def generate_blurbs(films, taste_summary, api_key=None):
    """
    Generate a personalised "why you'd like it" blurb for each film
    using the Groq API (free tier, fast inference).
    Returns dict keyed by film title.
    """
    api_key = api_key or os.environ.get('GROQ_API_KEY', '')

    film_list = '\n'.join(
        f"- {f['title']} ({f['year']}) directed by {f['director']}, genres: {', '.join(f.get('genres', []))}"
        for f in films
    )

    prompt = f"""You are a film critic writing personalised recommendations. The viewer's taste profile:
{taste_summary}

For each film below, write ONE sentence (max 25 words) explaining exactly why THIS viewer would enjoy it — be specific, mention films/directors from their profile by name where relevant. Do NOT write generic praise.

Reply with ONLY: film title, colon, sentence. One per line. No markdown, no numbering.

Films:
{film_list}"""

    for attempt in range(3):
        try:
            resp = requests.post(
                GROQ_URL,
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json',
                },
                json={
                    'model': MODEL,
                    'messages': [{'role': 'user', 'content': prompt}],
                    'max_tokens': 400,
                },
                timeout=30,
            )
            if resp.status_code == 429 and attempt < 2:
                print(f"[groq] rate limited, retrying in 10s...", file=sys.stderr)
                time.sleep(10)
                continue
            resp.raise_for_status()
            text = resp.json()['choices'][0]['message']['content']
            return _parse_response(text, films)
        except Exception as e:
            print(f"[groq] error: {e}", file=sys.stderr)
            break

    return {f['title']: f"A highly regarded {f.get('genres', [''])[0].lower()} film worth watching." for f in films}


def _parse_response(text, films):
    """Parse model response into a dict keyed by film title."""
    blurbs = {}
    for line in text.strip().split('\n'):
        line = line.strip()
        if ':' in line:
            title_part, _, blurb = line.partition(':')
            title = title_part.strip().strip('-').strip()
            blurbs[title] = blurb.strip()

    for film in films:
        if film['title'] not in blurbs:
            for key in blurbs:
                if key.lower() == film['title'].lower():
                    blurbs[film['title']] = blurbs[key]
                    break
            else:
                blurbs[film['title']] = f"A standout {film.get('genres', [''])[0].lower()} film."

    return blurbs
