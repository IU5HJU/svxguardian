# SVX Guardian

## Manuale del progetto

## 1. Visione

SVX Guardian è una piattaforma open source per il monitoraggio, la
supervisione e il controllo operativo di nodi radio basati su SvxLink.

L'obiettivo è offrire al Sysop una vista moderna, semplice e affidabile
dello stato del proprio nodo, mantenendo separate acquisizione,
monitoraggio, stato interno, presentazione e funzioni di controllo.

Il progetto è pensato per installazioni reali ed eterogenee e non deve
dipendere dalla particolare configurazione utilizzata durante lo
sviluppo.

SVX Guardian deve crescere in modo incrementale: una funzionalità viene
considerata disponibile soltanto quando è stata realmente implementata,
verificata e documentata.

---

## 2. Obiettivi

Gli obiettivi principali sono:

- monitorare lo stato del sistema Linux/Raspberry Pi;
- monitorare il servizio SvxLink;
- monitorare EchoLink;
- monitorare la connessione Reflector;
- fornire una dashboard web responsive;
- offrire una vista operativa adatta anche all'uso mobile;
- esporre API REST per lo stato e le funzioni previste;
- preservare e mostrare il RAW LOG SvxLink in modo efficiente;
- supportare autenticazione e controlli operativi riservati al Sysop;
- mantenere l'interfaccia multilingua;
- supportare installazioni SvxLink differenti;
- rendere in futuro l'installazione e il provisioning il più possibile
  guidati e ripetibili.

Funzioni future come notifiche, storico persistente, statistiche,
backup e recovery automatico restano obiettivi del progetto ma non
devono essere presentate come già implementate.

---

## 3. Principi

SVX Guardian deve rimanere:

- affidabile;
- semplice da comprendere;
- modulare;
- leggibile;
- verificabile;
- portabile;
- documentato;
- open source.

Una soluzione semplice e robusta è preferibile a una soluzione
inutilmente complessa.

Ogni componente deve avere una responsabilità chiaramente
identificabile.

Lo stato interno deve utilizzare valori tecnici canonici indipendenti
dalla lingua dell'interfaccia.

La traduzione appartiene ai livelli di presentazione.

---

## 4. Compatibilità

SVX Guardian è progettato per installazioni SvxLink eterogenee.

Il progetto non deve assumere:

- uno specifico modello di Raspberry Pi;
- una sola piattaforma hardware;
- una sola topologia radio;
- un Reflector necessariamente locale;
- una sola variante dei file di configurazione;
- che il nodo di sviluppo rappresenti il caso standard.

Gli ambienti di destinazione possono comprendere sistemi Linux su
Raspberry Pi e altre piattaforme compatibili con SvxLink.

Le topologie possono comprendere, in funzione dell'installazione:

- nodi simplex;
- ripetitori;
- hotspot;
- sistemi con Reflector remoto;
- sistemi con Reflector locale;
- configurazioni miste o distribuite.

Le compatibilità legacy già introdotte devono essere preservate salvo
una decisione esplicita e documentata.

---

## 5. Ambienti LAB e Legacy

Lo sviluppo utilizza due ambienti distinti.

### LAB

Il LAB è l'ambiente primario per:

- sviluppo;
- modifica dei file;
- test automatici;
- test funzionali;
- preparazione dei commit.

La sua configurazione può includere SvxLink e SvxReflector sulla stessa
macchina.

Questa topologia è un caso di prova e non costituisce il modello
standard del progetto.

### Legacy

Il Legacy è un nodo reale con traffico radio.

Viene utilizzato dopo la validazione sul LAB per verificare:

- comportamento con una installazione reale;
- compatibilità legacy;
- traffico EchoLink reale;
- traffico Reflector reale;
- regressioni non completamente riproducibili nel LAB.

Il Legacy non deve essere utilizzato come ambiente primario di
sviluppo.

---

## 6. Architettura

L'architettura operativa ruota attorno al Guardian Engine e allo stato
condiviso del nodo.

Vista semplificata:

```text
                    Guardian Engine
                           │
                ┌──────────┼──────────┐
                │          │          │
           Configurazione NodeState Node Info
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
 SystemMonitor       SvxLinkMonitor      EchoLinkMonitor
                                               │
                                        ReflectorMonitor
                           │
                           ▼
                    Stato canonico
                           │
                 ┌─────────┴─────────┐
                 │                   │
            Web Dashboard         REST API
```

I monitor non costituiscono una catena tra loro.

Ogni monitor aggiorna esclusivamente le parti di `NodeState` di propria
competenza.

La descrizione tecnica completa è mantenuta in `ARCHITECTURE.md`.

---

## 7. Modello dei dati

SVX Guardian mantiene distinti due concetti.

### NodeInfo

Rappresenta informazioni statiche e di configurazione del nodo.

Può comprendere:

- callsign;
- QTH;
- locator;
- Sysop;
- configurazione RX/TX;
- moduli;
- logiche;
- configurazione EchoLink;
- configurazione Reflector;
- versione SvxLink;
- percorsi dei file rilevati.

### NodeState

Rappresenta lo stato dinamico corrente.

Comprende informazioni relative a:

- sistema operativo;
- SvxLink;
- EchoLink;
- Reflector.

Questa separazione impedisce di confondere la configurazione del nodo
con il suo stato operativo.

---

## 8. Componenti implementati

Lo stato attuale comprende:

- Guardian Engine;
- `SystemMonitor`;
- `SvxLinkMonitor`;
- `EchoLinkMonitor`;
- `ReflectorMonitor`;
- `NodeState`;
- lettura della configurazione SvxLink;
- lettura di `node_info.json`;
- compatibilità con configurazioni legacy supportate;
- informazioni statiche del nodo;
- dashboard web;
- vista operativa `/monitor`;
- pagine tecniche dedicate;
- API `/api/state`;
- API incrementale `/api/logs`;
- RAW LOG;
- multilingua;
- Translation Manager;
- autenticazione Sysop/Co-Sysop;
- protezione CSRF delle operazioni riservate;
- restart controllato del servizio SvxLink.

La documentazione tecnica dei singoli componenti appartiene ai
documenti dedicati e al codice sorgente.

---

## 9. Dashboard

L'interfaccia web comprende:

```text
/                  Dashboard generale
/monitor           Vista operativa
/system            Sistema
/svxlink           SvxLink
/echolink          EchoLink
/reflector         Reflector
/logs              RAW LOG
/configuration     Configurazione e controllo
```

L'interfaccia supporta:

- responsive design;
- utilizzo desktop e mobile;
- temi Light e Dark;
- traduzione delle stringhe destinate all'utente.

La specifica completa è mantenuta in `DASHBOARD.md`.

---

## 10. EchoLink

Il monitoraggio EchoLink comprende lo stato operativo e le informazioni
sulle stazioni connesse.

Sono gestiti, tra gli altri:

- stato directory;
- stazioni connesse;
- nomi;
- tempi di connessione;
- stato di trasmissione;
- connessioni recenti;
- connessioni instabili.

Il monitoraggio operativo utilizza anche una integrazione locale
SvxLink basata su:

```text
/usr/share/svxlink/events.d/local/EchoLink.tcl
```

Gli eventi Guardian previsti sono:

```text
SVXGUARDIAN_ECHOLINK_RX_START
SVXGUARDIAN_ECHOLINK_RX_STOP
```

La futura installazione completa dovrà gestire automaticamente questa
dipendenza senza inserire configurazioni private nel repository.

---

## 11. Reflector

Il monitor Reflector gestisce:

- stato della connessione;
- host;
- porta;
- talkgroup;
- cifratura;
- nodi connessi;
- errori;
- motivo dell'ultima disconnessione.

I nodi SvxLink connessi e gli utenti/client applicativi sono concetti
distinti.

Gli utenti provenienti da client come LATRY non devono essere inseriti
artificialmente in `reflector_connected_nodes`.

Il modello degli utenti/client Reflector deve essere definito e
validato con traffico reale nella pagina `/reflector` prima di essere
esteso alla vista `/monitor`.

---

## 12. RAW LOG

La pagina `/logs` fornisce accesso al log operativo SvxLink.

Decisione di progetto:

**il RAW LOG resta RAW.**

Guardian non deve reinterpretare o classificare le righe mostrate in
questa vista.

La lettura è incrementale e separata dal normale ciclo
`guardian.run()`.

La pagina offre controlli locali per:

- Pause/Play;
- Auto-scroll;
- Clear.

`Clear` non modifica il logfile originale.

Questa architettura evita scansioni complete e ripetute del log durante
il polling frequente.

---

## 13. Sicurezza e configurazione privata

Il monitoraggio pubblico deve poter funzionare anche senza
autenticazione configurata.

Le funzioni di controllo sono invece riservate agli utenti autorizzati
Sysop/Co-Sysop.

Segreti, password, chiavi e credenziali non devono essere inseriti nel
repository Git.

La configurazione privata attuale utilizza:

```text
/etc/svxguardian
```

La chiave persistente utilizzata per le sessioni Flask è:

```text
/etc/svxguardian/secret.key
```

Le operazioni protette utilizzano token CSRF.

---

## 14. HTTPS

L'accesso HTTPS tramite Apache reverse proxy fa parte
dell'infrastruttura prevista per una installazione completa.

La procedura collaudata con No-IP comprende:

- generazione chiave e CSR;
- requisiti del CSR;
- verifica DNS TXT;
- installazione della chain PEM;
- VirtualHost Apache;
- reload della configurazione.

Questa procedura deve essere preservata e resa automatizzabile nel
futuro installer.

Non deve essere descritta come provisioning automatico già completato.

---

## 15. Metodo di sviluppo

Il flusso di riferimento è:

```text
Design → LAB → pytest → test funzionale → commit GPG → GitHub
→ Legacy (merge --ff-only) → pytest → restart → traffico reale
```

Prima di ogni commit eseguire almeno:

```bash
git diff --check
pytest -q
git status --short
```

I commit destinati al repository di produzione devono essere firmati.

Prima di modificare un file deve essere letta la versione reale
corrente.

Le regole complete sono definite in `CONTRIBUTING.md` e
`DEVELOPMENT.md`.

---

## 16. Documentazione

La documentazione è parte integrante del progetto.

La struttura bilingue prevista comprende:

```text
README.md
README.en.md
docs/ROADMAP.md
docs/ROADMAP.en.md
docs/ARCHITECTURE.md
docs/ARCHITECTURE.en.md
docs/CONTRIBUTING.md
docs/CONTRIBUTING.en.md
docs/DASHBOARD.md
docs/DASHBOARD.en.md
docs/DEVELOPMENT.md
docs/DEVELOPMENT.en.md
docs/PROJECT.md
docs/PROJECT.en.md
```

Il README deve rimanere sintetico.

I dettagli tecnici appartengono ai documenti nella directory `docs/`.

Non devono essere inventati numeri di release o milestone non
formalizzati nel repository.

---

## 17. Funzionalità future

La direzione futura comprende, tra le altre:

- notifiche;
- storico persistente;
- statistiche avanzate;
- backup;
- recovery automatico;
- modello dedicato agli utenti/client Reflector;
- provisioning completo del nodo;
- installazione guidata;
- automazione HTTPS;
- configurazione automatica delle dipendenze Guardian;
- ulteriori ottimizzazioni delle prestazioni.

Queste voci rappresentano obiettivi e non funzionalità già disponibili.

La pianificazione dettagliata appartiene a `ROADMAP.md`.

---

## 18. Obiettivo a lungo termine

SVX Guardian vuole diventare una piattaforma open source affidabile e
facilmente installabile per il monitoraggio dei nodi SvxLink.

Il progetto deve poter essere utilizzato da radioamatori con
installazioni differenti senza richiedere che il loro sistema replichi
l'ambiente di sviluppo.

La qualità del codice, la verificabilità, la compatibilità e la
documentazione sono considerate parte integrante del prodotto.
