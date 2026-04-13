# AI & System Design — Sintesi Socratica #3
**Data:** 2026-04-13 | **Session:** 4019a1bc

## Punti di forza attuali
- Panoramica strategica AI
- Normativa (AI Act, GDPR)
- Business/adoption AI
- CI/CD tradizionale
- **Nuovo:** Pattern RAG domain-specific per dati tabellari+immagini, architetture agentiche multi-agente, monitoraggio LLM senza ground truth

## Gap identificati
- **LLMOps e Monitoraggio in Produzione** — parzialmente coperto: framework EVA, GroUSE, UMBRELA scoring documentati ma non ancora implementati
- **System Design RAG avanzato** — significativamente coperto: pattern Relational-Agentic RAG, Colpali multi-modal, JSON RAG, Graph RAG documentati
- **Fine-Tuning e Modelli Locali** — TRL v1.0 documentato ma non applicabile su HF Spaces free tier (no GPU)
- **Architetture Agentiche Multi-Agente** — parzialmente coperto: ALTK-Evolve on-the-job learning, "Delegate, Review and Own", orchestrazione specialistica
- **Evaluation Frameworks per RAG** — gap nuovo: come valutare sistematicamente la qualità del RAG Pokefinance

## Insight chiave
**Tre principi emergenti AI/ML/LLM 2025-2026:**
1. **Dall'Assistenza all'Autonomia Agentica (Goal-Oriented)** — shift da copilot passivi a sistemi agentici che perseguono obiettivi, osservano contesto, scelgono azioni e imparano dai risultati con intervento umano minimo
2. **Architettura come "Contesto" Leggibile dalle Macchine** — Enterprise Architecture diventa insieme di policy/vincoli/metadati consumabili programmaticamente dagli agenti, non blueprint statico
3. **Governance basata su Telemetria Operativa** — monitoraggio non cerca ground truth assoluta ma osservabilità real-time: log strutturati, metriche latenza, tracciamento tool, explainability

**Pattern concreti per Pokefinance RAG:**
- **Relational-Agentic RAG**: Text-to-SQL via Claude Tool-Use su vista materializzata unified_product_data, NO vector store massivo
- **Multi-modal via metadati**: non indicizzare pixel ma estrarre descrizioni testuali (rarità, colori, soggetti) come metadati nel DB
- **Embedding leggero**: sqlite-vss o similarità Numpy per ~5000 elementi, <100MB RAM
- **Streaming SSE**: risposta Widget+Testo inviata progressivamente, evitando buffer JSON grandi
- **On-the-job Learning**: logging successo risposte AI per affinare prompt/intenti senza ricaricare modelli

## Connessioni con Pokefinance
- Il pattern Relational-Agentic RAG è direttamente implementabile: Claude interroga il DB via MCP tool (16 tool read-only già operativi)
- L'espansione GenUI Tier 2 per query PSA/BGS è il prossimo step naturale
- Il backfill tcggo_id è prerequisito per arricchire metadati immagini
- Il framework GroUSE per meta-valutazione del giudice AI è applicabile per validare le risposte Claude su query finanziarie

## Domande per il prossimo ciclo
1. Come si implementa concretamente un **feedback loop per on-the-job learning** nel contesto MCP — come si cattura e si usa il feedback utente sulle risposte Claude per migliorare i prompt senza fine-tuning?
2. Quali sono i **pattern di evaluation sistematica** per un RAG Text-to-SQL su dati finanziari — come si costruisce un benchmark con query golden per Pokefinance (PSA pricing, trend analysis, gemme nascoste)?
3. Come si evolve il **paradigma "Delegate, Review and Own"** per un sistema multi-agente Pokefinance — quale architettura permette a un agente di monitoring prezzi, uno di analisi rischio e uno di alert di collaborare autonomamente?
