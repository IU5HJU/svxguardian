<p align="center">
  <img src="docs/images/svxguardian-readme.png" alt="SVX Guardian Logo" width="420">
</p>

<h1 align="center">SVX Guardian</h1>

<p align="center">
<b>Creato da radioamatori, per radioamatori.</b>
</p>

<p align="center">
Piattaforma Open Source di monitoraggio per nodi radio SvxLink
</p>

<p align="center">
🇮🇹 <b>Italiano</b> · <a href="README.en.md">🇬🇧 English</a>
</p>

---

## Panoramica

**SVX Guardian** è una piattaforma open source progettata per il monitoraggio e la supervisione dei nodi radio basati su **SvxLink**.

L'obiettivo del progetto è fornire al Sysop una visione chiara e immediata dello stato dell'intero nodo attraverso una dashboard web moderna, responsive e utilizzabile sia da computer sia da dispositivi mobili.

Guardian monitora il sistema Linux/Raspberry Pi, il servizio SvxLink, EchoLink, Reflector e il log operativo, mantenendo separata la logica di acquisizione dei dati dalla loro presentazione.

Il progetto è sviluppato con particolare attenzione a:

- affidabilità;
- leggerezza;
- modularità;
- compatibilità con installazioni SvxLink reali;
- interfaccia responsive;
- supporto multilingua;
- facilità di manutenzione;
- possibilità di espansione futura.

---

## Funzionalità attuali

### Monitoraggio del sistema

- ✅ Stato del sistema Linux / Raspberry Pi
- ✅ Temperatura CPU
- ✅ Utilizzo CPU
- ✅ Utilizzo RAM
- ✅ Utilizzo disco
- ✅ Uptime del sistema
- ✅ Informazioni host e piattaforma

### Monitoraggio SvxLink

- ✅ Stato del servizio SvxLink
- ✅ PID del processo
- ✅ Uptime del servizio
- ✅ Lettura della configurazione SvxLink
- ✅ Rilevamento Logic e moduli configurati
- ✅ Informazioni RX e TX
- ✅ Lettura di `node_info.json`
- ✅ Compatibilità con configurazioni SvxLink legacy

### EchoLink

- ✅ Stato EchoLink
- ✅ Stato directory
- ✅ Stazioni connesse
- ✅ Stato della trasmissione
- ✅ Storico delle connessioni recenti
- ✅ Rilevamento delle connessioni instabili
- ✅ Informazioni operative delle stazioni

### Reflector

- ✅ Stato della connessione Reflector
- ✅ Host e porta
- ✅ TalkGroup predefinito
- ✅ TalkGroup attivo
- ✅ Stato Talker
- ✅ Monitoraggio dei nodi SvxLink connessi

> Il riconoscimento separato degli utenti collegati tramite client/applicazioni Reflector è attualmente in sviluppo.

### Dashboard Web

- ✅ Dashboard generale
- ✅ Vista operativa `/monitor`
- ✅ Pagina System
- ✅ Pagina SvxLink
- ✅ Pagina EchoLink
- ✅ Pagina Reflector
- ✅ Interfaccia responsive per desktop e dispositivi mobili
- ✅ Supporto multilingua

### RAW LOG realtime

SVX Guardian include un visualizzatore realtime del log originale di SvxLink.

Il contenuto rimane volutamente **RAW**, senza reinterpretazioni, per consentire al Sysop di verificare direttamente ciò che SvxLink sta realmente producendo.

Funzioni disponibili:

- ✅ Lettura incrementale del logfile
- ✅ Aggiornamento realtime
- ✅ LIVE / Pause / Play
- ✅ Recupero degli eventi prodotti durante la pausa
- ✅ Auto-scroll ON/OFF
- ✅ Clear della sola visualizzazione
- ✅ Buffer visuale limitato a 500 righe
- ✅ Gestione della rotazione e del troncamento del logfile
- ✅ Nessuna modifica al logfile originale `/var/log/svxlink`

### Controllo e autenticazione

- ✅ Autenticazione Sysop / Co-Sysop
- ✅ Sessioni web protette
- ✅ Protezione CSRF
- ✅ `SECRET_KEY` privata esterna al repository
- ✅ Credenziali e configurazione privata separate dal codice pubblico
- ✅ Funzioni di controllo del nodo protette da autenticazione

### REST API

- ✅ Esportazione dello stato corrente di Guardian
- ✅ Endpoint `/api/state`
- ✅ Endpoint incrementale `/api/logs`

---

## Architettura

SVX Guardian utilizza un'architettura modulare.

I monitor raccolgono le informazioni dalle diverse sorgenti e aggiornano uno stato interno comune. La dashboard, l'API e le future notifiche utilizzano questo stato senza duplicare la logica di monitoraggio.

Principali componenti:

```text
SystemMonitor
      │
SvxLinkMonitor
      │
EchoLinkMonitor
      │
ReflectorMonitor
      │
      ▼
 Guardian Engine
      │
      ▼
  Node State
      │
      ├── Web Dashboard
      ├── Operational Monitor
      └── REST API
```

Il RAW LOG utilizza invece un lettore incrementale dedicato, separato dal normale ciclo `Guardian.run()`, per evitare riletture complete del logfile e mantenere fluida l'interfaccia.

Per maggiori dettagli:

```text
docs/ARCHITECTURE.md
```

---

## Struttura del progetto

```text
svxguardian/
├── config/
├── docs/
│   ├── images/
│   ├── ARCHITECTURE.md
│   ├── CONTRIBUTING.md
│   ├── DASHBOARD.md
│   ├── DEVELOPMENT.md
│   ├── PROJECT.md
│   └── ROADMAP.md
├── locale/
├── src/
│   ├── core/
│   ├── modules/
│   ├── services/
│   └── web/
├── systemd/
├── tests/
└── requirements.txt
```

---

## Requisiti

Ambiente di sviluppo attuale:

- Linux / Raspberry Pi OS
- Python 3.13+
- SvxLink
- Git

Dipendenze Python principali:

- Flask
- psutil
- gunicorn

---

## Installazione per sviluppo

> L'installer automatico completo è ancora in sviluppo.
> Le istruzioni seguenti descrivono l'installazione dell'ambiente di sviluppo di Guardian e non sostituiscono ancora una procedura completa di provisioning SvxLink.

Clonare il repository:

```bash
git clone git@github.com:IU5HJU/svxguardian.git
cd svxguardian
```

Creare l'ambiente virtuale:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Installare le dipendenze:

```bash
pip install -r requirements.txt
```

Avviare Guardian nell'ambiente di sviluppo:

```bash
python src/main.py
```

---

## Test

Il progetto utilizza test automatici con `pytest`.

Con l'ambiente virtuale attivo:

```bash
pytest -q
```

Le nuove funzionalità vengono testate prima del commit e del trasferimento sulle installazioni operative.

---

## Sicurezza

Le informazioni sensibili non devono essere archiviate nel repository Git.

In particolare:

- credenziali Sysop / Co-Sysop;
- chiavi private;
- `SECRET_KEY`;
- configurazioni private dell'installazione;
- certificati e materiale crittografico sensibile.

Guardian è progettato affinché questi elementi possano risiedere all'esterno del repository con permessi appropriati.

---

## HTTPS

SVX Guardian può essere pubblicato tramite reverse proxy HTTPS.

Il progetto prevede la gestione di:

- Apache reverse proxy;
- certificati SSL/TLS;
- chiavi private esterne al repository;
- certificate chain;
- accesso sicuro alla dashboard.

L'automazione completa della configurazione HTTPS fa parte del lavoro di provisioning del progetto.

---

## Stato del progetto

SVX Guardian è **in sviluppo attivo**.

Le funzioni principali di monitoraggio sono già operative e vengono collaudate sia in ambiente LAB sia su un nodo SvxLink reale.

Alcune aree sono ancora in evoluzione, tra cui:

- riconoscimento separato degli utenti/client Reflector;
- notifiche Telegram;
- notifiche e-mail;
- installer automatico;
- provisioning completo SvxLink + Guardian;
- automazione HTTPS;
- ulteriori funzioni diagnostiche;
- ottimizzazione generale delle prestazioni per le future versioni.

---

## Roadmap

La roadmap del progetto è disponibile in:

```text
docs/ROADMAP.md
```

---

## Filosofia di sviluppo

Ogni nuova funzione segue un ciclo di sviluppo controllato:

1. progettazione;
2. implementazione in ambiente LAB;
3. test automatici;
4. verifica funzionale;
5. commit Git firmato;
6. push su GitHub;
7. aggiornamento controllato del nodo Legacy;
8. collaudo con traffico reale.

L'obiettivo è mantenere il ramo principale sempre in uno stato verificabile e stabile.

---

## Visione a lungo termine

SVX Guardian vuole diventare una piattaforma completa e facilmente installabile per la supervisione dei nodi SvxLink.

La visione futura comprende un installer capace di predisporre un nodo completo:

```text
Linux / Raspberry Pi OS
        +
     SvxLink
        +
   SVX Guardian
        +
EchoLink / Reflector
        +
   Apache HTTPS
        +
Autenticazione Sysop
        +
Configurazione e servizi
```

L'obiettivo è ridurre drasticamente la complessità necessaria per realizzare e mantenere un nodo moderno.

---

## Contribuire

Idee, segnalazioni di bug, test e pull request sono benvenuti.

SVX Guardian nasce dall'esperienza pratica su nodi radio reali e vuole crescere grazie al contributo della comunità radioamatoriale.

Consulta anche:

```text
docs/CONTRIBUTING.md
```

---

## Licenza

Distribuito sotto licenza MIT.

---

## Autore

**Michele Maccaoni – IU5HJU**

GitHub: `IU5HJU`

---

<p align="center">

**73!**

</p>
