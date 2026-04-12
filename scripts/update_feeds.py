"""
NLM Feed Updater — gira su GitHub Actions ogni giorno alle 09:00 IT.
Legge RSS feeds, filtra novità, aggiorna i feed.md per ogni notebook.
Nessuna API key richiesta. Zero dipendenze locali.
"""

import json
import os
import hashlib
from datetime import datetime, timezone, timedelta
from pathlib import Path

import feedparser
import requests

# ---------------------------------------------------------------------------
# CONFIG: RSS feeds per notebook
# ---------------------------------------------------------------------------
NOTEBOOKS = {
    "security-hacking": {
        "feeds": [
            "https://portswigger.net/daily-swig/rss",
            "https://www.bleepingcomputer.com/feed/",
            "https://securityboulevard.com/feed/",
            "https://feeds.feedburner.com/TheHackersNews",
            "https://krebsonsecurity.com/feed/",
        ],
        "keywords": ["vulnerability", "exploit", "CVE", "security", "attack",
                     "hacking", "OWASP", "penetration", "breach", "malware",
                     "authentication", "injection", "XSS", "CSRF"],
        "max_per_run": 3,
    },
    "programming-architecture": {
        "feeds": [
            "https://martinfowler.com/feed.atom",
            "https://www.infoq.com/architecture-design/rss",
            "https://feeds.feedburner.com/ProgrammableWeb",
            "https://blog.cleancoder.com/atom.xml",
            "https://newsletter.pragmaticengineer.com/feed",
        ],
        "keywords": ["architecture", "design pattern", "clean code", "refactor",
                     "microservices", "DDD", "SOLID", "API", "software design",
                     "abstraction", "coupling", "cohesion", "domain"],
        "max_per_run": 3,
    },
    "tecnologie-abilitanti-it": {
        "feeds": [
            "https://kubernetes.io/feed.xml",
            "https://www.docker.com/blog/feed/",
            "https://github.blog/feed/",
            "https://about.gitlab.com/atom.xml",
            "https://www.cncf.io/feed/",
        ],
        "keywords": ["kubernetes", "docker", "container", "CI/CD", "DevOps",
                     "deployment", "pipeline", "cloud", "infrastructure",
                     "terraform", "helm", "GitOps", "observability", "monitoring"],
        "max_per_run": 3,
    },
    "ai-system-design": {
        "feeds": [
            "https://www.anthropic.com/rss.xml",
            "https://huggingface.co/blog/feed.xml",
            "https://openai.com/blog/rss",
            "https://deepmind.google/blog/rss.xml",
            "https://bair.berkeley.edu/blog/feed.xml",
        ],
        "keywords": ["LLM", "language model", "AI", "machine learning", "RAG",
                     "agent", "fine-tuning", "embedding", "transformer",
                     "Claude", "GPT", "Gemini", "inference", "alignment"],
        "max_per_run": 3,
    },
}

# ---------------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent.parent
FEEDS_DIR = ROOT / "feeds"
REGISTRY_FILE = ROOT / "registry.json"
CUTOFF_DAYS = 60  # ignora articoli più vecchi di N giorni

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def load_registry() -> dict:
    if REGISTRY_FILE.exists():
        return json.loads(REGISTRY_FILE.read_text())
    return {nb: [] for nb in NOTEBOOKS}


def save_registry(registry: dict):
    REGISTRY_FILE.write_text(json.dumps(registry, indent=2, ensure_ascii=False))


def url_hash(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()[:12]


def is_recent(entry) -> bool:
    """Ritorna True se l'entry è entro CUTOFF_DAYS."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=CUTOFF_DAYS)
    for attr in ("published_parsed", "updated_parsed"):
        t = getattr(entry, attr, None)
        if t:
            try:
                dt = datetime(*t[:6], tzinfo=timezone.utc)
                return dt >= cutoff
            except Exception:
                pass
    return True  # se non c'è data, includi per sicurezza


def is_relevant(entry, keywords: list[str]) -> bool:
    """Controlla se titolo o summary contengono almeno 1 keyword."""
    text = (
        getattr(entry, "title", "") + " " +
        getattr(entry, "summary", "")
    ).lower()
    return any(kw.lower() in text for kw in keywords)


def fetch_feed(url: str) -> list:
    """Scarica e parsifica un feed RSS/Atom. Ritorna lista di entry."""
    try:
        headers = {"User-Agent": "NLM-Feed-Bot/1.0 (github.com/nlm-feeds)"}
        resp = requests.get(url, timeout=15, headers=headers)
        resp.raise_for_status()
        parsed = feedparser.parse(resp.content)
        return parsed.entries or []
    except Exception as e:
        print(f"  ⚠️  Feed non raggiungibile: {url} — {e}")
        return []


def format_entry(entry) -> str:
    """Formatta un'entry come blocco markdown per il feed.md."""
    title = getattr(entry, "title", "Titolo non disponibile").strip()
    link  = getattr(entry, "link",  "#").strip()
    date  = ""
    for attr in ("published", "updated"):
        d = getattr(entry, attr, "")
        if d:
            date = d[:10]
            break
    summary = getattr(entry, "summary", "").strip()
    # tronca summary a 300 char
    if len(summary) > 300:
        summary = summary[:297] + "..."
    # rimuovi tag HTML elementari
    import re
    summary = re.sub(r"<[^>]+>", "", summary).strip()

    return (
        f"### [{title}]({link})\n"
        f"*{date}*\n\n"
        f"{summary}\n\n"
        f"---\n"
    )


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    registry = load_registry()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    total_added = 0

    for notebook_id, config in NOTEBOOKS.items():
        feed_file = FEEDS_DIR / notebook_id / "feed.md"
        feed_file.parent.mkdir(parents=True, exist_ok=True)

        # Leggi feed esistente (append in cima)
        existing_content = feed_file.read_text(encoding="utf-8") if feed_file.exists() else ""

        known_hashes = set(registry.get(notebook_id, []))
        new_entries = []

        for feed_url in config["feeds"]:
            print(f"  📡 {notebook_id} ← {feed_url}")
            entries = fetch_feed(feed_url)

            for entry in entries:
                link = getattr(entry, "link", "")
                if not link:
                    continue
                h = url_hash(link)
                if h in known_hashes:
                    continue
                if not is_recent(entry):
                    continue
                if not is_relevant(entry, config["keywords"]):
                    continue
                new_entries.append((h, entry))

            if len(new_entries) >= config["max_per_run"]:
                break

        # Limita al max per run
        new_entries = new_entries[: config["max_per_run"]]

        if not new_entries:
            print(f"  ✓  {notebook_id}: nessuna novità")
            continue

        # Costruisci header aggiornamento
        header = f"\n## Aggiornamento {today}\n\n"
        blocks = header + "".join(format_entry(e) for _, e in new_entries)

        # Scrivi: novità in cima, storico sotto
        feed_file.write_text(
            get_static_header(notebook_id) + blocks + existing_content.replace(get_static_header(notebook_id), ""),
            encoding="utf-8"
        )

        # Aggiorna registry
        registry.setdefault(notebook_id, [])
        for h, _ in new_entries:
            if h not in registry[notebook_id]:
                registry[notebook_id].append(h)

        print(f"  ✅ {notebook_id}: +{len(new_entries)} fonti")
        total_added += len(new_entries)

    save_registry(registry)
    print(f"\n🎓 Totale aggiunto oggi: {total_added} fonti su {len(NOTEBOOKS)} notebook")


def get_static_header(notebook_id: str) -> str:
    titles = {
        "security-hacking":         "# Security & Hacking — Feed Automatico NLM",
        "programming-architecture": "# Programming & Architecture — Feed Automatico NLM",
        "tecnologie-abilitanti-it": "# Tecnologie Abilitanti IT — Feed Automatico NLM",
        "ai-system-design":         "# AI & System Design — Feed Automatico NLM",
    }
    return titles.get(notebook_id, f"# {notebook_id} — Feed Automatico NLM") + "\n\n"


if __name__ == "__main__":
    main()
