# Security & Hacking — Sintesi Socratica #3
**Data:** 2026-04-13 | **Session:** 2fd59de5

## Punti di forza attuali
- Web security (OWASP, CWE Top 25)
- LLM/AI Security (OWASP LLM Top 10)
- Penetration testing (Burp Suite, Metasploit)
- Cloud/API Security
- **Nuovo:** Attacchi compositi multi-vettore 2025-2026 (supply chain + zero-day weaponization, cloud identity hijacking, payroll pirate)

## Gap identificati
- **AI-Assisted Phishing + Automated Session Hijacking** — AI generativa integrata in tempo reale per superare controlli comportamentali durante session hijack
- **Supply Chain + Smart Contract Poisoning** — pacchetti npm malevoli che alterano logica di trasferimento fondi in smart contract
- **WASM-Based Bot Evasion in Browser Fingerprinting** — WebAssembly usato dai bot per nascondere pattern di fingerprinting ai sistemi anti-bot
- **Deepfake Vishing + MFA Reset Engineering** — audio clonato per forzare reset MFA tramite helpdesk
- **Hardware Bit-Flips + Cloud Escape** — GPUBreach (bit-flips GDDR6) incatenato per evasione container/hypervisor
- Wireless/RF/Bluetooth, Blockchain/Web3, Crittografia Post-Quantistica — gap persistenti dai cicli precedenti

## Insight chiave
**Tre principi emergenti cybersecurity 2025-2026:**
1. **Zero Trust Esteso agli Agenti Non Umani** — ogni bot deve avere identità verificabile, permessi minimi, monitoraggio anomalie in tempo reale
2. **Crypto-Agility Post-Quantistica** — migrazione verso ML-KEM/ML-DSA con capacità di aggiornare algoritmi senza riscrivere applicazioni
3. **Governance tramite Telemetria Operativa** — conformità dimostrata continuamente tramite monitoraggio real-time, non policy statiche

**Pattern di attacco compositi emergenti documentati:**
- PRISMEX/APT28: spear-phishing + zero-day weaponization pre-disclosure + steganografia + C2 via servizi cloud legittimi
- CVE-2026-20965: token WAC hijack + PoP token contraffatti per lateral movement cross-tenant Azure
- CPUID: API compromise + distribuzione malware via download legittimi (CPU-Z, HWMonitor)
- Storm-2755 Payroll Pirate: account hijack + modifica diretta parametri pagamento

## Connessioni con Pokefinance
- **Bot evasion critico** per scraping Cardmarket: il progetto evita il problema usando API ufficiali (Price Guide, CardTrader) invece di scraping aggressivo
- **Integrità dati finanziari**: sanitizzazione XSS con `esc()`, validatori puri pre-scrittura DB
- **Sicurezza billing Stripe**: HKDF per derivazione chiavi, verifica firma webhook obbligatoria
- **Hardening backend**: CSP nonce-based, revoca JWT via jti, rate limiting per endpoint pesanti

## Domande per il prossimo ciclo
1. Come si implementa concretamente un sistema di **identità verificabile per agenti AI** (bot di sync, scalping agent) in un'architettura FastAPI con JWT — quali standard emergono nel 2026?
2. Quali sono le **tecniche di detection per deepfake vishing** applicabili a un contesto di helpdesk/support — come si difende un sistema di reset MFA dall'audio clonato?
3. Come evolve il pattern **GPUBreach (bit-flips GDDR6)** verso attacchi reali di cloud escape — quali mitigazioni hardware/software esistono per container runtime?
