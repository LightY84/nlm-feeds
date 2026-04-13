"""
NLM Web Discovery — gira su GitHub Actions, trova contenuti freschi via DuckDuckGo.
Complementa i feed RSS cercando articoli, guide, paper che i feed non coprono.
Focus sui gap identificati nelle sintesi Socratiche.

Zero API key. Usa duckduckgo-search (gratuito).
"""

import json
import hashlib
import re
import time
import random
from datetime import datetime, timezone, timedelta
from pathlib import Path

from duckduckgo_search import DDGS

# ---------------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent.parent
FEEDS_DIR = ROOT / "feeds"
SYNTHESIS_DIR = ROOT / "synthesis"
REGISTRY_FILE = ROOT / "registry.json"

# ---------------------------------------------------------------------------
# CONFIG: query di ricerca per notebook, orientate ai gap
# ---------------------------------------------------------------------------
NOTEBOOKS = {
    "security-hacking": {
        "queries": [
            "IoT security vulnerability 2026",
            "smart contract audit exploit",
            "wireless hacking WPA3 bluetooth attack",
            "WebAssembly WASM security vulnerability",
            "post-quantum cryptography implementation",
            "bot detection evasion browser fingerprint",
            "OWASP LLM top 10 security",
        ],
        "keywords": ["security", "vulnerability", "exploit", "attack", "hacking",
                     "penetration", "CVE", "breach", "malware", "OWASP",
                     "authentication", "injection", "XSS", "CSRF", "IoT",
                     "smart contract", "bluetooth", "WASM", "quantum", "fingerprint"],
        "max_results": 3,
    },
    "programming-architecture": {
        "queries": [
            "frontend architecture React Next.js 2026",
            "NoSQL distributed database design pattern",
            "Infrastructure as Code Terraform Pulumi best practices",
            "OpenTelemetry observability microservices",
            "SOLID principles modern TypeScript",
            "event sourcing CQRS practical guide",
        ],
        "keywords": ["architecture", "design pattern", "clean code", "refactor",
                     "microservices", "DDD", "SOLID", "API", "frontend",
                     "NoSQL", "Terraform", "observability", "OpenTelemetry",
                     "TypeScript", "React", "Next.js"],
        "max_results": 3,
    },
    "tecnologie-abilitanti-it": {
        "queries": [
            "Kubernetes production best practices 2026",
            "Terraform Infrastructure as Code tutorial",
            "ArgoCD GitOps deployment guide",
            "OpenTelemetry Prometheus Grafana observability stack",
            "serverless AWS Lambda cloud functions patterns",
            "DevSecOps zero trust HashiCorp Vault",
        ],
        "keywords": ["kubernetes", "docker", "container", "CI/CD", "DevOps",
                     "deployment", "pipeline", "cloud", "terraform", "helm",
                     "GitOps", "ArgoCD", "observability", "Prometheus",
                     "serverless", "Lambda", "Vault", "zero trust"],
        "max_results": 3,
    },
    "ai-system-design": {
        "queries": [
            "LLMOps monitoring production deployment 2026",
            "RAG vector database embedding chunking re-ranking",
            "fine-tuning PEFT LoRA quantization local models",
            "multi-agent architecture tool calling orchestration",
            "AI agent memory long-term planning",
            "LLM evaluation benchmark hallucination detection",
        ],
        "keywords": ["LLM", "language model", "AI", "machine learning", "RAG",
                     "agent", "fine-tuning", "embedding", "transformer",
                     "vector database", "LLMOps", "PEFT", "LoRA",
                     "multi-agent", "tool calling", "hallucination"],
        "max_results": 3,
    },
}


def load_registry() -> dict:
    if REGISTRY_FILE.exists():
        return json.loads(REGISTRY_FILE.read_text())
    return {nb: [] for nb in NOTEBOOKS}


def save_registry(registry: dict):
    REGISTRY_FILE.write_text(json.dumps(registry, indent=2, ensure_ascii=False))


def url_hash(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()[:12]


def extract_gap_queries(notebook_id: str) -> list[str]:
    """Estrae query aggiuntive dai gap della sintesi più recente."""
    synthesis_path = SYNTHESIS_DIR / notebook_id / "synthesis-latest.md"
    if not synthesis_path.exists():
        return []

    content = synthesis_path.read_text(encoding="utf-8")
    extra_queries = []

    # Cerca gap con ⚠️ (nessuna copertura)
    for match in re.finditer(r"\*\*(.+?)\*\* — ⚠️", content):
        gap_name = match.group(1)
        # Crea query dalla descrizione del gap
        extra_queries.append(f"{gap_name} tutorial guide 2026")

    return extra_queries[:3]  # max 3 query extra dai gap


def is_relevant(title: str, body: str, keywords: list[str]) -> bool:
    """Controlla se il risultato è rilevante per il notebook."""
    text = (title + " " + body).lower()
    return any(kw.lower() in text for kw in keywords)


def search_web(query: str, max_results: int = 5, retries: int = 3) -> list[dict]:
    """Cerca su DuckDuckGo con retry e backoff esponenziale."""
    for attempt in range(retries):
        try:
            time.sleep(random.uniform(2, 5))  # delay umano tra query
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results, region="wt-wt"))
            return results
        except Exception as e:
            wait = 2 ** attempt * random.uniform(3, 7)
            if attempt < retries - 1:
                print(f"  ⏳ Retry {attempt + 1}/{retries} tra {wait:.0f}s — {e}")
                time.sleep(wait)
            else:
                print(f"  ⚠️  Ricerca fallita dopo {retries} tentativi: {query}")
    return []


def format_discovery(title: str, url: str, body: str) -> str:
    """Formatta un risultato come blocco markdown."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    # Pulisci HTML residuo
    body = re.sub(r"<[^>]+>", "", body).strip()
    if len(body) > 300:
        body = body[:297] + "..."

    return (
        f"### [{title}]({url})\n"
        f"*{today} — via Web Discovery*\n\n"
        f"{body}\n\n"
        f"---\n"
    )


def get_static_header(notebook_id: str) -> str:
    titles = {
        "security-hacking":         "# Security & Hacking — Feed Automatico NLM",
        "programming-architecture": "# Programming & Architecture — Feed Automatico NLM",
        "tecnologie-abilitanti-it": "# Tecnologie Abilitanti IT — Feed Automatico NLM",
        "ai-system-design":         "# AI & System Design — Feed Automatico NLM",
    }
    return titles.get(notebook_id, f"# {notebook_id} — Feed Automatico NLM") + "\n\n"


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(f"🔍 NLM Web Discovery — {today}")
    print("=" * 50)

    registry = load_registry()
    total_added = 0

    for notebook_id, config in NOTEBOOKS.items():
        print(f"\n📘 {notebook_id}")

        feed_file = FEEDS_DIR / notebook_id / "feed.md"
        feed_file.parent.mkdir(parents=True, exist_ok=True)
        existing_content = feed_file.read_text(encoding="utf-8") if feed_file.exists() else ""

        known_hashes = set(registry.get(notebook_id, []))
        new_discoveries = []

        # Query base + query dinamiche dai gap
        all_queries = config["queries"][:4]  # max 4 query base per run
        gap_queries = extract_gap_queries(notebook_id)
        all_queries.extend(gap_queries)

        for query in all_queries:
            if len(new_discoveries) >= config["max_results"]:
                break

            print(f"  🔎 \"{query}\"")
            results = search_web(query, max_results=5)

            for result in results:
                url = result.get("href", result.get("link", ""))
                title = result.get("title", "")
                body = result.get("body", "")

                if not url or not title:
                    continue

                h = url_hash(url)
                if h in known_hashes:
                    continue

                if not is_relevant(title, body, config["keywords"]):
                    continue

                new_discoveries.append({
                    "hash": h,
                    "title": title,
                    "url": url,
                    "body": body,
                })
                known_hashes.add(h)

                if len(new_discoveries) >= config["max_results"]:
                    break

        if not new_discoveries:
            print(f"  ✓  Nessuna novità dal web")
            continue

        # Costruisci blocco aggiornamento
        header = f"\n## Web Discovery {today}\n\n"
        blocks = header + "".join(
            format_discovery(d["title"], d["url"], d["body"])
            for d in new_discoveries
        )

        # Scrivi: novità in cima
        feed_file.write_text(
            get_static_header(notebook_id) + blocks +
            existing_content.replace(get_static_header(notebook_id), ""),
            encoding="utf-8"
        )

        # Aggiorna registry
        registry.setdefault(notebook_id, [])
        for d in new_discoveries:
            if d["hash"] not in registry[notebook_id]:
                registry[notebook_id].append(d["hash"])

        print(f"  ✅ +{len(new_discoveries)} scoperte")
        total_added += len(new_discoveries)

    save_registry(registry)
    print(f"\n🔍 Totale scoperte oggi: {total_added} su {len(NOTEBOOKS)} notebook")


if __name__ == "__main__":
    main()
