import google.generativeai as genai


def generate_blurbs(films, taste_summary, api_key):
    """
    Generate a personalised "why you'd like it" blurb for each film.
    Returns dict keyed by film title. Falls back to generic strings on error.
    """
    film_list = '\n'.join(
        f"- {f['title']} ({f['year']}) directed by {f['director']}, genres: {', '.join(f.get('genres', []))}"
        for f in films
    )

    prompt = f"""You are recommending films to someone with this taste profile:
{taste_summary}

For each of the following films, write ONE sentence (max 20 words) explaining why this specific person would enjoy it. Reference films or directors from their taste profile where relevant. Reply with ONLY the film title followed by a colon and the sentence, one per line.

Films:
{film_list}"""

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return _parse_response(response.text, films)
    except Exception:
        return {f['title']: f"A highly regarded {f.get('genres', [''])[0].lower()} film worth watching." for f in films}


def _parse_response(text, films):
    """Parse Gemini response into a dict keyed by film title."""
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
