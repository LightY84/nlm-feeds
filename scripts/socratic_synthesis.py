"""
Socratic Synthesis Engine — gira su GitHub Actions (domenica sera).
Legge i feed.md di ogni notebook, analizza i contenuti,
genera una sintesi evoluta con gap analysis e domande per il ciclo successivo.
Sovrascrive synthesis-latest.md per mantenere URL NLM stabili.

Zero dipendenze esterne (solo stdlib). Nessun API key.
L'intelligenza viene dal contenuto accumulato nei feed + sintesi precedenti.
"""

import os
import re
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent.parent
FEEDS_DIR = ROOT / "feeds"
SYNTHESIS_DIR = ROOT / "synthesis"

# ---------------------------------------------------------------------------
# CONFIG: domini di conoscenza e meta-contesto per ogni notebook
# ---------------------------------------------------------------------------
NOTEBOOKS = {
    "security-hacking": {
        "title": "Security & Hacking",
        "core_topics": [
            "Web security (OWASP, CWE Top 25)",
            "LLM/AI Security (OWASP LLM Top 10)",
            "Penetration testing (Burp Suite, Metasploit)",
            "Cloud/API Security",
        ],
        "known_gaps": [
            "Hardware Security / IoT",
            "Wireless / RF / Bluetooth",
            "Blockchain / Web3 / Smart Contract",
            "WebAssembly (WASM) / Memory Corruption",
            "Crittografia Post-Quantistica",
            "Bot Evasion / Browser Fingerprinting",
        ],
        "pokefinance_link": "Bot evasion critico per scraping Cardmarket; smart contract per tokenizzazione RWA carte",
    },
    "programming-architecture": {
        "title": "Programming & Architecture",
        "core_topics": [
            "Design pattern GoF",
            "TypeScript avanzato",
            "CQRS ed Event Sourcing",
            "Twelve-Factor App, Docker multi-stage",
            "Ottimizzazione DB relazionale",
        ],
        "known_gaps": [
            "Architettura Frontend moderna (Redux, Zustand, Next.js)",
            "Database distribuiti / NoSQL",
            "Infrastructure as Code (Terraform, Ansible)",
            "Sicurezza applicativa (OWASP Top 10 codice)",
            "Osservabilità (OpenTelemetry, Prometheus)",
            "Sviluppo mobile/desktop",
        ],
        "pokefinance_link": "Pattern architetturali applicabili a SPA Vanilla JS come Pokefinance",
    },
    "tecnologie-abilitanti-it": {
        "title": "Tecnologie Abilitanti IT",
        "core_topics": [
            "System Design teorico (load balancing, replica, service discovery)",
            "Message brokering (Kafka, RabbitMQ)",
            "Scalabilità orizzontale",
        ],
        "known_gaps": [
            "Kubernetes operativo (Pod, Deployment, Ingress, Istio, Helm)",
            "Infrastructure as Code (Terraform, Ansible, Pulumi)",
            "CI/CD e GitOps (ArgoCD, Flux)",
            "Osservabilità moderna (OpenTelemetry, Prometheus, Grafana, ELK)",
            "Serverless e Cloud-Native (Lambda, Cloud Functions)",
            "DevSecOps (Vault, IAM, Zero Trust)",
        ],
        "pokefinance_link": "Strumenti compatibili con HuggingFace Spaces tier gratuito",
    },
    "ai-system-design": {
        "title": "AI & System Design",
        "core_topics": [
            "Panoramica strategica AI",
            "Normativa (AI Act, GDPR)",
            "Business/adoption AI",
            "CI/CD tradizionale",
        ],
        "known_gaps": [
            "LLMOps e Monitoraggio in Produzione",
            "System Design RAG avanzato (vector DB, embedding, chunking, re-ranking)",
            "Fine-Tuning e Modelli Locali (PEFT, quantizzazione)",
            "Architetture Agentiche Multi-Agente (Tool Calling, memoria, orchestratori)",
        ],
        "pokefinance_link": "RAG per dominio Pokémon TCG; LLM-as-a-judge per chatbot portfolio",
    },
}


def read_file_safe(path: Path) -> str:
    """Legge un file, ritorna stringa vuota se non esiste."""
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def extract_articles(feed_content: str) -> list[dict]:
    """Estrae titoli e sommari dagli articoli nel feed.md."""
    articles = []
    # Pattern: ### [Title](URL)\n*date*\n\nsummary
    blocks = re.split(r"(?=^### \[)", feed_content, flags=re.MULTILINE)
    for block in blocks:
        title_match = re.search(r"### \[(.+?)\]", block)
        date_match = re.search(r"\*(\d{4}-\d{2}-\d{2})\*", block)
        if title_match:
            # Il sommario è tutto dopo la data fino al ---
            summary = ""
            lines = block.split("\n")
            capture = False
            for line in lines:
                if line.startswith("---"):
                    break
                if capture and line.strip():
                    summary += line.strip() + " "
                if date_match and date_match.group() in line:
                    capture = True
            articles.append({
                "title": title_match.group(1),
                "date": date_match.group(1) if date_match else "N/A",
                "summary": summary.strip()[:200],
            })
    return articles


def extract_previous_gaps(synthesis_content: str) -> list[str]:
    """Estrae i gap dal ciclo precedente per tracking evoluzione."""
    gaps = []
    in_gap_section = False
    for line in synthesis_content.split("\n"):
        if "gap identificat" in line.lower() or "aree critiche" in line.lower():
            in_gap_section = True
            continue
        if in_gap_section:
            if line.startswith("## ") or line.startswith("# "):
                break
            match = re.match(r"\d+\.\s+\*\*(.+?)\*\*", line)
            if match:
                gaps.append(match.group(1))
    return gaps


def count_gap_coverage(articles: list[dict], gaps: list[str]) -> dict[str, int]:
    """Conta quanti articoli toccano ogni gap conosciuto."""
    coverage = {}
    for gap in gaps:
        gap_keywords = [w.lower() for w in gap.split() if len(w) > 3]
        count = 0
        for article in articles:
            text = (article["title"] + " " + article["summary"]).lower()
            if any(kw in text for kw in gap_keywords):
                count += 1
        coverage[gap] = count
    return coverage


def generate_synthesis(notebook_id: str, config: dict) -> str:
    """Genera la sintesi Socratica per un notebook."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Leggi feed corrente
    feed_content = read_file_safe(FEEDS_DIR / notebook_id / "feed.md")
    articles = extract_articles(feed_content)

    # Leggi sintesi precedente
    prev_synthesis = read_file_safe(SYNTHESIS_DIR / notebook_id / "synthesis-latest.md")
    previous_gaps = extract_previous_gaps(prev_synthesis)

    # Analisi copertura gap
    gap_coverage = count_gap_coverage(articles, previous_gaps) if previous_gaps else {}

    # Calcola ciclo
    cycle_match = re.search(r"Sintesi Socratica #(\d+)", prev_synthesis)
    cycle_num = int(cycle_match.group(1)) + 1 if cycle_match else 1

    # --- Costruisci sintesi ---
    lines = []
    lines.append(f"# {config['title']} — Sintesi Socratica #{cycle_num}")
    lines.append(f"**Data:** {today} | **Ciclo:** {cycle_num} | **Articoli analizzati:** {len(articles)}")
    lines.append("")

    # Sezione 1: Stato conoscenza
    lines.append("## Stato attuale della conoscenza")
    lines.append("")
    lines.append("**Punti di forza consolidati:**")
    for topic in config["core_topics"]:
        lines.append(f"- {topic}")
    lines.append("")

    # Sezione 2: Evoluzione gap
    lines.append("## Evoluzione dei gap")
    lines.append("")
    if gap_coverage:
        # Ordina: gap con più copertura prima (quelli che si stanno colmando)
        sorted_gaps = sorted(gap_coverage.items(), key=lambda x: x[1], reverse=True)
        for gap_name, count in sorted_gaps:
            if count > 0:
                lines.append(f"- **{gap_name}** — 📈 {count} articoli rilevanti trovati nei feed")
            else:
                lines.append(f"- **{gap_name}** — ⚠️ Nessuna copertura dai feed attuali")
    else:
        for gap in config["known_gaps"]:
            lines.append(f"- **{gap}** — baseline iniziale")
    lines.append("")

    # Sezione 3: Nuovi articoli rilevanti
    lines.append("## Articoli recenti dai feed")
    lines.append("")
    if articles:
        for article in articles[:8]:  # max 8 più recenti
            lines.append(f"- **{article['title']}** ({article['date']})")
            if article["summary"]:
                lines.append(f"  > {article['summary'][:150]}")
    else:
        lines.append("*Nessun articolo disponibile in questo ciclo.*")
    lines.append("")

    # Sezione 4: Connessioni Pokefinance
    lines.append("## Connessioni con Pokefinance")
    lines.append("")
    lines.append(config["pokefinance_link"])
    lines.append("")

    # Sezione 5: Domande per il prossimo ciclo
    lines.append("## Domande per il prossimo ciclo")
    lines.append("")
    # Genera domande basate sui gap meno coperti
    uncovered = [g for g, c in gap_coverage.items() if c == 0] if gap_coverage else config["known_gaps"][:3]
    for i, gap in enumerate(uncovered[:3], 1):
        lines.append(f"{i}. Come colmare il gap su **{gap}** con risorse open-source?")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(f"🧠 Socratic Synthesis Engine — {today}")
    print("=" * 50)

    for notebook_id, config in NOTEBOOKS.items():
        print(f"\n📘 Elaborazione: {notebook_id}")

        # Assicura directory
        synthesis_dir = SYNTHESIS_DIR / notebook_id
        synthesis_dir.mkdir(parents=True, exist_ok=True)

        # Genera sintesi
        synthesis = generate_synthesis(notebook_id, config)

        # Scrivi synthesis-latest.md (sovrascrittura — URL stabile)
        latest_path = synthesis_dir / "synthesis-latest.md"
        latest_path.write_text(synthesis, encoding="utf-8")
        print(f"  ✅ synthesis-latest.md aggiornato")

        # Archivio datato (per storico)
        archive_path = synthesis_dir / f"synthesis-{today}.md"
        archive_path.write_text(synthesis, encoding="utf-8")
        print(f"  📁 Archiviato: synthesis-{today}.md")

    print(f"\n🎓 Sintesi Socratica completata per {len(NOTEBOOKS)} notebook")


if __name__ == "__main__":
    main()
