# nlm-feeds

Feed automatici per NotebookLM — aggiornati ogni giorno via GitHub Actions.
Nessuna macchina locale richiesta. Zero intervento manuale.

## Come funziona

1. GitHub Actions esegue `scripts/update_feeds.py` ogni giorno alle 09:00 (IT)
2. Lo script legge RSS feeds da fonti autorevoli per dominio
3. Filtra per rilevanza e deduplicazione (registry.json)
4. Aggiorna i file `feeds/*/feed.md`
5. NotebookLM sincronizza automaticamente i file come sorgenti

## Notebook → Feed

| Notebook NLM | File feed | Fonti RSS |
|---|---|---|
| Security & Hacking | feeds/security-hacking/feed.md | PortSwigger, BleepingComputer, Krebs, HackerNews |
| Programming & Architecture | feeds/programming-architecture/feed.md | Martin Fowler, InfoQ, Clean Coder |
| Tecnologie Abilitanti IT | feeds/tecnologie-abilitanti-it/feed.md | Kubernetes, Docker, GitHub, CNCF |
| AI & System Design | feeds/ai-system-design/feed.md | Anthropic, HuggingFace, OpenAI, DeepMind |

## Setup (una tantum)

### 1. Pusha questo repo su GitHub
```bash
cd nlm-feeds
git init
git add .
git commit -m "Initial setup"
git remote add origin https://github.com/TUO_USERNAME/nlm-feeds.git
git push -u origin main
```

### 2. Aggiungi ogni feed.md come sorgente GitHub in NotebookLM

Per ogni notebook, apri NotebookLM → "+ Aggiungi fonte" → "GitHub" → incolla l'URL raw del file:

- Security: `https://raw.githubusercontent.com/TUO_USERNAME/nlm-feeds/main/feeds/security-hacking/feed.md`
- Programming: `https://raw.githubusercontent.com/TUO_USERNAME/nlm-feeds/main/feeds/programming-architecture/feed.md`
- DevOps: `https://raw.githubusercontent.com/TUO_USERNAME/nlm-feeds/main/feeds/tecnologie-abilitanti-it/feed.md`
- AI: `https://raw.githubusercontent.com/TUO_USERNAME/nlm-feeds/main/feeds/ai-system-design/feed.md`

Fatto. Da domani mattina tutto è automatico.

## Struttura repo

```
nlm-feeds/
├── .github/workflows/daily-feed.yml   # GitHub Action (cloud)
├── scripts/update_feeds.py            # logica discovery + filtro
├── feeds/
│   ├── security-hacking/feed.md
│   ├── programming-architecture/feed.md
│   ├── tecnologie-abilitanti-it/feed.md
│   └── ai-system-design/feed.md
├── registry.json                      # hash URL già processati
└── README.md
```
