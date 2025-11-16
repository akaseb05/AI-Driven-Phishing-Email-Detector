import re
from typing import List, Dict

# Very simple list of sketchy words for now.
# Later this can be replaced with something smarter / AI-based.
SUSPICIOUS_WORDS = [
    "password", "verify", "verification", "urgent", "immediately",
    "click here", "account locked", "security alert", "invoice",
    "wire transfer", "bank", "gift card", "confidential",
    "login", "reset", "update your info"
]


def extract_links(text: str) -> List[str]:
    """Find all URLs in the text (very basic)."""
    pattern = r"https?://\S+"
    return re.findall(pattern, text)


def get_domain(email: str) -> str:
    """Return the part after @ in an email."""
    parts = email.split("@")
    if len(parts) != 2:
        # not a great email format, but don't crash
        return email.lower().strip()
    return parts[-1].lower().strip()


def sender_score(from_address: str, to_addresses: List[str]) -> float:
    """
    Basic sender check.

    Idea:
    - If sender and receivers share the same company domain -> less suspicious.
    - If sender is free mail (gmail, yahoo, etc.) and sending to a company -> more suspicious.
    - Otherwise just medium for now.
    """
    sender_domain = get_domain(from_address)
    to_domains = {get_domain(a) for a in to_addresses}

    if len(to_domains) == 1 and sender_domain in to_domains:
        return 0.2  # looks like same org

    free_providers = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com"}
    if sender_domain in free_providers:
        return 0.7  # kind of sketchy if pretending to be “security” or “IT”

    return 0.5  # default / unknown


def link_score(text: str) -> float:
    """
    Look at links in the email body.

    For now:
    - No links => lowish score.
    - IP links, @ tricks, super long paths => bump score.
    """
    links = extract_links(text)
    if not links:
        return 0.25

    suspicious_count = 0

    for url in links:
        # IP address in URL
        if re.search(r"\d+\.\d+\.\d+\.\d+", url):
            suspicious_count += 1

        # user@host trick inside URL
        if "@" in url.split("//")[-1]:
            suspicious_count += 1

        # super long path
        if url.count("/") > 5:
            suspicious_count += 1

    base = 0.4
    bonus = min(0.4, suspicious_count * 0.15)
    score = base + bonus

    if score > 1.0:
        score = 1.0

    return score


def cc_score(from_address: str, to_addresses: List[str], cc_addresses: List[str]) -> float:
    """
    Try to see if the CC list is weird.

    Super simple:
    - No CC => kind of neutral.
    - If a bunch of different domains show up => more suspicious.
    - If CC domains don't match sender or to_domains => more suspicious.
    """
    if not cc_addresses:
        return 0.3

    sender_domain = get_domain(from_address)
    to_domains = {get_domain(a) for a in to_addresses}
    cc_domains = {get_domain(a) for a in cc_addresses}

    all_domains = to_domains.union(cc_domains)
    domain_spread = len(all_domains)

    score = 0.3
    if domain_spread > 1:
        score += 0.1 * (domain_spread - 1)

    # if CC is not “in the same circle”
    if sender_domain not in cc_domains and not cc_domains.issubset(to_domains):
        score += 0.2

    if score > 1.0:
        score = 1.0

    return score


def content_score(subject: str, body: str) -> float:
    """
    Very naive content check.

    - looks for suspicious words
    - checks if there's too much ALL CAPS
    - checks for too many exclamation marks
    """
    text = (subject + " " + body).lower()
    score = 0.2

    # suspicious words
    hits = 0
    for w in SUSPICIOUS_WORDS:
        if w in text:
            hits += 1
    if hits > 0:
        score += min(0.4, hits * 0.08)

    # ALL CAPS words
    words = re.findall(r"[A-Za-z]+", subject + " " + body)
    long_words = [w for w in words if len(w) > 3]
    caps_words = [w for w in long_words if w.isupper()]

    if long_words:
        caps_ratio = len(caps_words) / len(long_words)
        if caps_ratio > 0.2:
            score += 0.2

    # too many exclamation marks
    if body.count("!") > 3:
        score += 0.1

    if score > 1.0:
        score = 1.0

    return score


def combine_scores(sender: float, links: float, cc: float, content: float) -> float:
    """
    Combine everything into one final number between 0 and 1.

    TODO: later this should be replaced with a trained model.
    """
    # weights are just guessed for now
    s_w = 0.25
    l_w = 0.30
    c_w = 0.20
    t_w = 0.25

    total = sender * s_w + links * l_w + cc * c_w + content * t_w
    return round(total, 3)


def build_explanation(sender: float, links: float, cc: float, content: float, prob: float) -> str:
    """
    Make a short explanation string a normal user could read.
    """
    reasons = []

    if sender > 0.6:
        reasons.append("Sender email/domain looks a bit off.")
    else:
        reasons.append("Sender email/domain seems somewhat normal.")

    if links > 0.6:
        reasons.append("Links in the email look unusual or risky.")
    elif links > 0.3:
        reasons.append("Email contains links, but they are not extremely suspicious.")
    else:
        reasons.append("Links do not look very risky.")

    if cc > 0.6:
        reasons.append("CC list includes people or domains that don't really match.")
    elif cc > 0.3:
        reasons.append("CC list is a little unusual.")
    else:
        reasons.append("CC list looks simple and expected.")

    if content > 0.6:
        reasons.append("Email language feels urgent or scam-like.")
    elif content > 0.3:
        reasons.append("Some of the language looks a bit pushy or suspicious.")
    else:
        reasons.append("Email text seems fairly normal.")

    reasons.append(f"Overall estimated phishing chance: {int(prob * 100)}%.")

    return " ".join(reasons)


def score_email(payload: Dict) -> Dict:
    """
    Main function the API will call.
    Takes a dict with email info and returns scores + explanation.
    """
    subject = payload.get("subject", "")
    body = payload.get("body", "")
    from_address = payload.get("from_address", "")
    to_addresses = payload.get("to_addresses", []) or []
    cc_addresses = payload.get("cc_addresses", []) or []

    s_score = sender_score(from_address, to_addresses)
    l_score = link_score(subject + "\n" + body)
    cc_sc = cc_score(from_address, to_addresses, cc_addresses)
    cont_score = content_score(subject, body)

    final_prob = combine_scores(s_score, l_score, cc_sc, cont_score)
    explanation = build_explanation(s_score, l_score, cc_sc, cont_score, final_prob)

    return {
        "phishing_probability": final_prob,
        "scores": {
            "sender_score": round(s_score, 3),
            "link_score": round(l_score, 3),
            "cc_score": round(cc_sc, 3),
            "content_score": round(cont_score, 3),
        },
        "explanation": explanation,
    }
