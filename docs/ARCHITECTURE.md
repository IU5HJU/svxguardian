# Architettura di SVX Guardian

## Scopo

SVX Guardian è una piattaforma open source di monitoraggio per nodi
SvxLink su Raspberry Pi/Linux.

L'architettura è progettata per mantenere separati:

- acquisizione e monitoraggio dello stato;
- rappresentazione dello stato corrente;
- configurazione del nodo;
- interfaccia web;
- API REST;
- autenticazione e controllo operativo;
- lettura del log operativo SvxLink;
- localizzazione dell'interfaccia.

Le funzionalità future, come notifiche, storico persistente,
statistiche avanzate, backup e meccanismi di recovery automatico,
non devono essere considerate parte dell'architettura implementata
finché non saranno effettivamente sviluppate e collaudate.

---

## Architettura generale

```text
                    SVX Guardian
                         │
                  Guardian Engine
                         │
          ┌──────────────┼──────────────┐
          │              │              │
     Configurazione   NodeState      Node Info
                         │
        ┌────────────────┼────────────────┐
        │                │                │
 SystemMonitor     SvxLinkMonitor   EchoLinkMonitor
                                         │
                                  ReflectorMonitor
                         │
                         ▼
                  Stato canonico
                         │
             ┌───────────┴───────────┐
             │                       │
        Web Dashboard             REST API
             │
       Presentazione
       multilingua
```

Il diagramma rappresenta una vista logica semplificata.

I monitor non costituiscono una catena tra loro: ciascun monitor
aggiorna le parti di `NodeState` di propria competenza.

---

## Guardian Engine

Il Guardian Engine coordina il ciclo di monitoraggio.

I monitor vengono registrati nel Guardian e operano sullo stato
condiviso del nodo.

Attualmente sono utilizzati:

- `SystemMonitor`;
- `SvxLinkMonitor`;
- `EchoLinkMonitor`;
- `ReflectorMonitor`.

Ogni monitor implementa l'interfaccia comune definita da
`BaseMonitor`.

Il contratto fondamentale è:

```python
check(state: NodeState) -> None
```

Il monitor riceve lo stato corrente e aggiorna esclusivamente
le informazioni di propria competenza.

---

## NodeState

`NodeState` rappresenta lo stato dinamico corrente del nodo.

Contiene informazioni relative a:

### Sistema operativo

- hostname;
- temperatura CPU;
- utilizzo CPU;
- utilizzo RAM;
- utilizzo disco;
- uptime.

### SvxLink

- stato del servizio;
- PID;
- uptime del servizio.

### EchoLink

- stato directory;
- ultimo errore;
- stazioni connesse;
- nomi delle stazioni;
- orario di inizio connessione;
- stazioni con connessione instabile;
- numero di connessioni;
- stato di trasmissione;
- stazione in trasmissione;
- connessioni recenti.

### Reflector

- stato della connessione;
- host;
- porta;
- talkgroup;
- stato della cifratura;
- nodi connessi;
- numero di connessioni;
- ultimo errore;
- motivo dell'ultima disconnessione.

Lo stato interno utilizza valori tecnici canonici indipendenti
dalla lingua dell'interfaccia.

La traduzione viene applicata esclusivamente nel livello di
presentazione.

---

## Informazioni statiche del nodo

Le informazioni statiche ricavate dalla configurazione SvxLink e
dal file `node_info.json` sono mantenute separate dallo stato
dinamico.

Comprendono, tra le altre:

- nominativo;
- descrizione;
- Sysop;
- QTH e locator;
- configurazione RX/TX;
- configurazione EchoLink;
- configurazione Reflector;
- logiche e moduli;
- versione SvxLink;
- percorsi dei file di configurazione rilevati.

Questa separazione evita di confondere la configurazione del nodo
con il suo stato operativo corrente.

---

## Applicazione Web

L'applicazione web è realizzata con Flask.

Le principali pagine operative sono:

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

Prima del rendering delle normali pagine di monitoraggio viene
eseguito il ciclo Guardian e viene creata una copia isolata dello
stato corrente.

Questo evita che il template lavori direttamente sull'oggetto
dinamico condiviso.

---

## REST API

SVX Guardian espone attualmente:

```text
/api/state
/api/logs
```

### `/api/state`

Esegue il ciclo di monitoraggio e restituisce uno snapshot JSON
dello stato corrente insieme alle informazioni del nodo.

### `/api/logs`

Fornisce in modo incrementale le nuove righe del logfile SvxLink.

L'endpoint utilizza un cursore client e non esegue
`guardian.run()`.

Questa separazione è intenzionale: il polling frequente del RAW LOG
non deve provocare continuamente l'esecuzione completa dei monitor.

---

## RAW LOG

Il RAW LOG utilizza un lettore incrementale dedicato.

Il log operativo SvxLink rimane una sorgente RAW:

- Guardian non deve reinterpretarne il contenuto nella pagina RAW LOG;
- il refresh del log non deve eseguire l'intero ciclo Guardian;
- il browser mantiene la propria gestione di Pause, Auto-scroll e Clear;
- Clear non modifica mai il logfile originale.

La lettura incrementale evita scansioni complete e ripetute del
logfile durante il refresh.

---

## Autenticazione e controllo operativo

Il monitoraggio pubblico deve continuare a funzionare anche quando
l'infrastruttura di autenticazione non è configurata.

Le operazioni di controllo sono invece riservate agli utenti
autorizzati Sysop/Co-Sysop.

La configurazione privata è mantenuta fuori dal repository.

Percorso previsto:

```text
/etc/svxguardian
```

La chiave persistente utilizzata per firmare le sessioni Flask è:

```text
/etc/svxguardian/secret.key
```

Se la chiave o il file di autenticazione non sono disponibili,
Guardian non genera automaticamente credenziali temporanee:
l'autenticazione rimane indisponibile.

Le operazioni protette utilizzano inoltre token CSRF.

Attualmente il livello di controllo comprende il riavvio del
servizio SvxLink tramite `NodeControl`.

---

## Multilingua

Le traduzioni sono gestite nel livello di presentazione.

I monitor e `NodeState` utilizzano valori tecnici canonici.

La lingua selezionata influenza dashboard e testi destinati
all'utente, non il significato dello stato interno.

I file di localizzazione sono mantenuti separati dal codice
applicativo.

---

## Bootstrap

`BootstrapEngine` gestisce la sequenza iniziale di avvio.

Attualmente:

1. inizializza la configurazione;
2. configura il logging;
3. registra nel log il banner di avvio.

Il bootstrap deve rimanere distinto dal ciclo operativo dei
monitor.

---

## Principi di progettazione

### Responsabilità separate

Ogni componente deve avere una responsabilità chiaramente
identificabile.

### Monitor indipendenti

I monitor non devono dipendere direttamente gli uni dagli altri.

La comunicazione dello stato avviene attraverso `NodeState`.

### Stato canonico

Lo stato interno non deve dipendere dalla lingua della UI.

### Presentazione separata

Traduzione e formattazione appartengono ai livelli di
presentazione.

### Log operativo preservato

Il RAW LOG deve restare RAW e non deve essere trasformato in una
rappresentazione interpretata.

### Configurazione privata fuori dal repository

Credenziali, chiavi e altri segreti non devono essere inseriti
nel repository Git.

### Prestazioni

Le funzioni eseguite frequentemente non devono provocare scansioni
complete e ripetitive dei logfile quando può essere utilizzata una
lettura incrementale.

### Compatibilità

Guardian deve poter funzionare con installazioni SvxLink reali,
comprese configurazioni legacy supportate esplicitamente.

---

## Reflector e client applicativi

La gestione Reflector deve mantenere distinti concetti differenti:

```text
Nodi SvxLink connessi
Utenti/client applicativi connessi
```

Gli utenti provenienti da client applicativi, come LATRY, non
devono essere inseriti artificialmente in
`reflector_connected_nodes`.

Il modello definitivo per gli utenti/client Reflector è ancora in
fase di analisi e deve essere validato con traffico reale prima di
essere esteso alla vista `/monitor`.

---

## Funzionalità future

Sono previste, ma non devono essere considerate implementate fino
al relativo sviluppo e collaudo:

- notifiche;
- storico persistente;
- statistiche avanzate;
- backup;
- recovery automatico;
- provisioning/installazione completa;
- automazione della configurazione HTTPS;
- ulteriori ottimizzazioni delle prestazioni.

---

## Filosofia del progetto

SVX Guardian deve rimanere:

- affidabile;
- semplice da comprendere;
- modulare;
- portabile;
- verificabile;
- open source;
- adatto all'utilizzo reale sui nodi radioamatoriali SvxLink.
