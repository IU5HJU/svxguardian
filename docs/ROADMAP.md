# SVX Guardian — Roadmap

🇮🇹 **Italiano** · [🇬🇧 English](ROADMAP.en.md)

**SVX Guardian** è una piattaforma open source per il monitoraggio e la supervisione di nodi radio **SvxLink**.

L'obiettivo è realizzare un sistema moderno, modulare, affidabile e facilmente installabile, capace di monitorare l'intero nodo: sistema operativo, SvxLink, EchoLink, Reflector e servizi associati.

---

# Obiettivi del progetto

- Monitoraggio professionale dei nodi SvxLink
- Dashboard web moderna e responsive
- Vista operativa ottimizzata per dispositivi mobili
- Interfaccia multilingua
- Monitoraggio EchoLink e Reflector
- LOG RAW realtime
- REST API
- Autenticazione Sysop / Co-Sysop
- Accesso HTTPS
- Notifiche Telegram ed e-mail
- Installazione e provisioning automatizzati
- Progetto Open Source rivolto alla comunità radioamatoriale

---

# Milestone storica

## v0.1.0 — Core Framework ✅

Completato:

- [x] Struttura iniziale del progetto
- [x] Guardian Engine
- [x] Modello `NodeState`
- [x] Interfaccia `BaseMonitor`
- [x] `SystemMonitor`
- [x] Repository Git
- [x] Ambiente virtuale Python
- [x] `requirements.txt`

Questa milestone ha costituito la base architetturale di SVX Guardian.

---

# Stato attuale dello sviluppo

> Le sezioni seguenti descrivono funzionalità implementate nel ramo di sviluppo corrente.
> La numerazione delle future release verrà assegnata al momento della loro formalizzazione e pubblicazione.

## System Monitor ✅

- [x] Stato del sistema
- [x] Temperatura CPU
- [x] Utilizzo CPU
- [x] Utilizzo RAM
- [x] Utilizzo disco
- [x] Uptime
- [x] Informazioni host e piattaforma

---

## SvxLink Monitor ✅

- [x] Stato del servizio SvxLink
- [x] PID
- [x] Uptime del servizio
- [x] Lettura configurazione SvxLink
- [x] Rilevamento Logic
- [x] Rilevamento moduli
- [x] Informazioni RX
- [x] Informazioni TX
- [x] Lettura `node_info.json`
- [x] Compatibilità con configurazioni SvxLink legacy
- [x] Integrazione nello stato Guardian

---

## EchoLink Monitor ✅

- [x] Stato EchoLink
- [x] Stato directory
- [x] Stazioni connesse
- [x] Stato RX / trasmissione
- [x] Connessioni recenti
- [x] Informazioni delle stazioni
- [x] Rilevamento delle connessioni instabili
- [x] Ottimizzazione della lettura dello storico
- [x] Integrazione dashboard
- [x] Integrazione nello stato Guardian

---

## Reflector Monitor 🚧

Implementato:

- [x] Stato connessione Reflector
- [x] Host e porta
- [x] TalkGroup predefinito
- [x] TalkGroup attivo
- [x] Stato Talker
- [x] Rilevamento nodi SvxLink connessi
- [x] Integrazione dashboard
- [x] Integrazione nello stato Guardian

In sviluppo:

- [ ] Distinzione tra nodi SvxLink e utenti/client applicativi
- [ ] Rilevamento corretto degli utenti collegati tramite applicazioni come LATRY
- [ ] Gestione degli eventi `Node joined` / `Node left`
- [ ] Verifica con traffico reale sul nodo Legacy
- [ ] Valutazione della futura integrazione degli utenti Reflector nella vista `/monitor`

---

## RAW LOG realtime ✅

- [x] Lettura incrementale di `/var/log/svxlink`
- [x] Visualizzazione RAW senza reinterpretazione
- [x] Aggiornamento realtime
- [x] LIVE
- [x] Pause / Play
- [x] Recupero degli eventi prodotti durante la pausa
- [x] Auto-scroll ON/OFF
- [x] Clear della sola visualizzazione
- [x] Contatore delle righe
- [x] Buffer visuale massimo di 500 righe
- [x] Gestione troncamento logfile
- [x] Gestione delle modifiche del logfile
- [x] Lettore separato dal ciclo `Guardian.run()`
- [x] Collaudo con traffico reale

Il LOG RAW rimane intenzionalmente non interpretato per fornire al Sysop una visione diretta degli eventi prodotti da SvxLink.

---

## REST API ✅

- [x] Esportazione JSON dello stato Guardian
- [x] Endpoint `/api/state`
- [x] Esportazione delle informazioni del nodo
- [x] Endpoint incrementale `/api/logs`
- [x] Snapshot isolato dello stato

Ulteriori endpoint potranno essere aggiunti in funzione delle future integrazioni.

---

## Web Dashboard ✅ / 🚧

Implementato:

- [x] Dashboard generale
- [x] Vista System
- [x] Vista SvxLink
- [x] Vista EchoLink
- [x] Vista Reflector
- [x] Vista LOG RAW
- [x] Vista Configuration
- [x] Vista operativa `/monitor`
- [x] Layout responsive
- [x] Supporto desktop
- [x] Supporto mobile
- [x] Aggiornamenti dinamici
- [x] Indicatori di stato
- [x] Supporto multilingua

In evoluzione:

- [ ] Ulteriori ottimizzazioni delle prestazioni
- [ ] Ulteriori rifiniture responsive
- [ ] Integrazione delle future funzioni Reflector

---

## Autenticazione e controllo nodo ✅ / 🚧

Implementato:

- [x] Autenticazione Sysop
- [x] Autenticazione Co-Sysop
- [x] Sessioni web
- [x] Protezione CSRF
- [x] `SECRET_KEY` esterna al repository
- [x] Credenziali private separate dal repository
- [x] Controlli operativi protetti da autenticazione

Da completare nel provisioning:

- [ ] Creazione automatica dei file privati
- [ ] Generazione automatica della `SECRET_KEY`
- [ ] Configurazione automatica dei permessi
- [ ] Configurazione dell'utente del servizio

---

# Prossime aree di sviluppo

## Reflector / client applicativi 🚧

Priorità corrente:

- [ ] Analisi completa degli eventi reali SvxReflector
- [ ] Separazione nodi / utenti
- [ ] Supporto utenti LATRY
- [ ] Test sul Legacy
- [ ] Definizione del modello dati canonico
- [ ] Eventuale integrazione in `/monitor` solo dopo il collaudo

---

## Notifiche

Pianificato:

- [ ] Telegram
- [ ] E-mail
- [ ] Alert configurabili
- [ ] Definizione degli eventi notificabili
- [ ] Livelli di priorità
- [ ] Protezione da notifiche ripetitive

MQTT rimane una possibile estensione futura.

---

## HTTPS e sicurezza

Implementazione e automazione previste:

- [ ] Template Apache HTTPS
- [ ] Reverse proxy verso Guardian
- [ ] Generazione chiave privata e CSR
- [ ] Gestione verifica DNS
- [ ] Installazione certificate chain
- [ ] Configurazione VirtualHost
- [ ] Reload controllato di Apache
- [ ] Procedura portabile e documentata

---

## Installer e provisioning

Obiettivo: realizzare un'installazione riproducibile su Raspberry Pi / Linux moderno.

Il provisioning futuro dovrà poter gestire:

- [ ] Installazione SvxLink
- [ ] Installazione SVX Guardian
- [ ] Ambiente virtuale Python
- [ ] Dipendenze
- [ ] Configurazione SvxLink
- [ ] EchoLink
- [ ] Reflector
- [ ] Override eventi EchoLink
- [ ] Servizi systemd
- [ ] Autenticazione Sysop / Co-Sysop
- [ ] File privati e permessi
- [ ] Apache
- [ ] HTTPS
- [ ] Certificati
- [ ] Configurazione iniziale del nodo
- [ ] Aggiornamento controllato

L'obiettivo non è soltanto installare Guardian, ma rendere riproducibile la realizzazione di un **nodo SvxLink completo**.

---

# Verso la v1.0.0

La prima release stabile dovrà raggiungere almeno questi obiettivi:

- [ ] Monitoraggio completo e stabile
- [ ] Dashboard stabile e responsive
- [ ] EchoLink stabile
- [ ] Reflector stabile
- [ ] LOG RAW stabile
- [ ] Autenticazione stabile
- [ ] API documentata
- [ ] Internazionalizzazione completa
- [ ] Documentazione bilingue
- [ ] Installer affidabile
- [ ] Provisioning riproducibile
- [ ] HTTPS documentato e automatizzabile
- [ ] Test sufficienti per le funzioni critiche
- [ ] Procedura di aggiornamento documentata
- [ ] Release pronta per la comunità

---

# Metodo di sviluppo

Le modifiche vengono sviluppate e verificate progressivamente:

```text
Design
  ↓
LAB
  ↓
Test automatici
  ↓
Test funzionale
  ↓
Commit Git firmato
  ↓
GitHub
  ↓
Legacy
  ↓
Test con traffico reale
```

Questo approccio permette di mantenere separato lo sviluppo dal nodo operativo e di verificare le modifiche prima della loro introduzione in produzione.

---

# Visione a lungo termine

SVX Guardian vuole diventare una piattaforma di riferimento per il monitoraggio e la gestione dei nodi SvxLink.

La visione finale è quella di poter partire da un sistema Linux / Raspberry Pi OS moderno e ottenere, attraverso una procedura guidata e riproducibile:

```text
SvxLink
   +
SVX Guardian
   +
EchoLink
   +
Reflector
   +
Dashboard
   +
LOG realtime
   +
Autenticazione
   +
HTTPS
   +
Notifiche
```

mantenendo il sistema modulare, documentato, aggiornabile e completamente open source.

---

**73!**
