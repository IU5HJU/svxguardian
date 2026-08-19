# Sviluppo di SVX Guardian

## 1. Scopo

Questo documento descrive il metodo di sviluppo di SVX Guardian, gli
ambienti utilizzati per la validazione e le principali tappe tecniche
del progetto.

Non sostituisce:

- `ARCHITECTURE.md`, che descrive l'architettura;
- `CONTRIBUTING.md`, che definisce le regole di contribuzione;
- `ROADMAP.md`, che descrive le attività future;
- `DASHBOARD.md`, che documenta l'interfaccia web.

Le funzionalità riportate come completate devono corrispondere a
implementazioni realmente sviluppate e collaudate.

---

## 2. Ambienti di sviluppo

SVX Guardian utilizza due ambienti distinti.

### LAB

Il LAB è l'ambiente primario per:

- sviluppo;
- modifica dei file;
- test automatici;
- test funzionali;
- verifica della documentazione;
- preparazione dei commit.

### Legacy

Il Legacy è un nodo reale con traffico radio.

Viene utilizzato solo dopo la validazione sul LAB e la pubblicazione del
commit su GitHub.

Serve per verificare:

- compatibilità con una installazione SvxLink reale;
- comportamento con configurazioni legacy;
- eventi EchoLink e Reflector reali;
- traffico radio effettivo;
- regressioni non riproducibili completamente nel LAB.

Il Legacy non è l'ambiente primario di sviluppo.

---

## 3. Flusso operativo

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

Prima di modificare un file deve essere letta la sua versione reale
corrente.

Quando una modifica viene fornita manualmente per copia/incolla,
preferire il file completo pronto da copiare quando questo riduce il
rischio di errori.

---

## 4. Repository e commit

Il branch principale è:

```text
main
```

I commit destinati al repository di produzione devono essere firmati.

Sul Legacy l'aggiornamento deve preservare una storia lineare tramite:

```bash
git merge --ff-only
```

Non utilizzare `sudo` per modificare i file interni al repository.

Dopo ogni push e dopo ogni aggiornamento del Legacy deve essere
verificato lo stato del repository.

---

## 5. Stato tecnico consolidato

### Modello dati

La configurazione statica del nodo e lo stato dinamico sono mantenuti
separati.

`NodeInfo` rappresenta le informazioni statiche ricavate dalla
configurazione SvxLink e da `node_info.json`.

`NodeState` rappresenta lo stato operativo corrente.

Questa separazione evita di confondere configurazione e stato runtime.

### Monitor

Il Guardian Engine utilizza attualmente:

- `SystemMonitor`;
- `SvxLinkMonitor`;
- `EchoLinkMonitor`;
- `ReflectorMonitor`.

Ogni monitor aggiorna le parti di `NodeState` di propria competenza.

### Configurazione SvxLink

Guardian rileva e utilizza le informazioni provenienti da:

```text
/etc/svxlink/svxlink.conf
/etc/svxlink/node_info.json
/var/log/svxlink
```

È supportata anche la forma legacy:

```text
O_FILE=/etc/svxlink/node_info.json
```

all'interno di `[ReflectorLogic]`.

### Dashboard e API

Sono operative le pagine:

```text
/
/monitor
/system
/svxlink
/echolink
/reflector
/logs
/configuration
```

e le API:

```text
/api/state
/api/logs
```

### Multilingua

Lo stato interno utilizza valori tecnici canonici indipendenti dalla
lingua.

La traduzione viene applicata soltanto nei livelli di presentazione.

### Autenticazione

L'autenticazione Sysop/Co-Sysop utilizza configurazione privata
esterna al repository.

Il percorso attuale è:

```text
/etc/svxguardian
```

La chiave persistente delle sessioni Flask è:

```text
/etc/svxguardian/secret.key
```

Le operazioni protette utilizzano token CSRF.

### Controllo del nodo

È implementato il restart del servizio SvxLink per utenti autorizzati.

Altri controlli eventualmente visibili ma disabilitati
nell'interfaccia non devono essere considerati implementati.

---

## 6. RAW LOG

Il RAW LOG è stato implementato come funzione separata dal normale
ciclo di monitoraggio.

Caratteristiche consolidate:

- lettura incrementale;
- buffer in RAM;
- gestione di troncamento e rotazione;
- API separata da `guardian.run()`;
- stato LIVE;
- Pause/Play;
- recupero delle righe prodotte durante Pause;
- Auto-scroll ON/OFF;
- Clear limitato alla visualizzazione del browser;
- contatore righe;
- massimo 500 righe visualizzate;
- sorgente `/var/log/svxlink`.

Decisione vincolante:

**il RAW LOG resta RAW.**

Guardian non deve reinterpretare o classificare le righe mostrate nella
pagina `/logs`.

Il polling del RAW LOG non deve provocare l'esecuzione completa di
tutti i monitor.

---

## 7. EchoLink

Il monitor EchoLink gestisce attualmente:

- stato directory;
- stazioni connesse;
- nomi delle stazioni;
- durata delle connessioni;
- stato di trasmissione;
- connessioni recenti;
- rilevamento delle connessioni instabili.

Lo storico recente è stato ottimizzato per evitare scansioni complete e
ripetute del logfile ad ogni refresh.

Commit di riferimento:

```text
09394b44fc1e07236e629ccbe38b05ef65783db2
Optimize EchoLink recent connection history
```

La pagina EchoLink e la vista operativa mobile sono state adattate per
mostrare in modo leggibile nominativo, nome, tempi e stato della
connessione.

---

## 8. Reflector e LATRY

Il monitor Reflector gestisce attualmente:

- stato della connessione;
- host;
- porta;
- talkgroup;
- cifratura;
- nodi connessi;
- errori;
- motivo dell'ultima disconnessione.

La gestione dei client applicativi Reflector è ancora oggetto di
analisi.

Il traffico reale ha mostrato eventi del tipo:

```text
ReflectorLogic: Node joined:
IU5HJU

ReflectorLogic: Talker start on TG #2225: IU5HJU
```

mentre la pagina `/reflector` può mostrare soltanto i nodi ricostruiti
attraverso la logica attuale di `reflector_connected_nodes`.

Decisione consolidata:

- non forzare gli utenti LATRY dentro `reflector_connected_nodes`;
- mantenere distinti nodi SvxLink e utenti/client applicativi;
- validare il nuovo modello prima nella pagina `/reflector`;
- non modificare `/monitor` finché il modello LATRY/Reflector non è
  stabile e collaudato con traffico reale.

Gli eventi da analizzare sul Legacy comprendono:

```text
Node joined
Node left
Connected nodes
Talker start
Talker stop
```

---

## 9. Compatibilità Legacy

La compatibilità con installazioni SvxLink esistenti è un requisito
del progetto.

È stata aggiunta compatibilità con la configurazione legacy di
`node_info.json`.

Commit di riferimento:

```text
e056000b935b01fbe693e320fc0cc9afa45e2971
Support legacy SvxLink node info configuration
```

Guardian non deve essere progettato esclusivamente attorno alla
configurazione del nodo LAB.

---

## 10. HTTPS e configurazione privata

L'accesso HTTPS tramite Apache reverse proxy fa parte
dell'infrastruttura prevista per l'installazione completa.

La procedura collaudata con No-IP deve essere preservata e resa
automatizzabile.

Comprende:

- generazione chiave e CSR;
- requisiti del CSR;
- verifica DNS TXT;
- installazione della chain PEM;
- configurazione VirtualHost Apache;
- reload;
- segreti fuori dal repository.

Queste procedure non devono essere descritte come provisioning
automatico già completato finché il relativo installer non sarà
implementato.

---

## 11. EchoLink override

Il monitoraggio operativo EchoLink utilizza una integrazione locale
SvxLink basata su:

```text
/usr/share/svxlink/events.d/local/EchoLink.tcl
```

Gli eventi richiesti da Guardian sono:

```text
SVXGUARDIAN_ECHOLINK_RX_START
SVXGUARDIAN_ECHOLINK_RX_STOP
```

Il provisioning futuro dovrà gestire:

- backup del file esistente;
- installazione dell'override;
- proprietario;
- permessi;
- compatibilità con l'installazione SvxLink presente.

---

## 12. Cronologia di sviluppo

### 4 agosto 2026

Attività principali:

- rifattorizzazione della lettura della configurazione;
- introduzione della separazione tra configurazione statica e stato
  operativo;
- integrazione dei dati del nodo;
- estensione delle informazioni Reflector;
- ampliamento di `/api/state`;
- aggiornamento della dashboard con dati reali del nodo.

Decisione progettuale importante:

SVX Guardian deve supportare installazioni eterogenee e non deve
assumere che la topologia del LAB rappresenti il modello standard.

### 5 agosto 2026

Attività principali:

- consolidamento dell'internazionalizzazione;
- utilizzo del sistema di traduzione nelle stringhe visibili;
- sincronizzazione dei file di localizzazione;
- introduzione dello strumento `tools/check_i18n.py`;
- controllo della coerenza dei file JSON e delle chiavi;
- consolidamento del repository e delle regole di lavoro.

Da questo punto il progetto adotta il principio:

**stato canonico interno, traduzione nel livello di presentazione.**

### 18 agosto 2026

Sono stati consolidati diversi aspetti della vista operativa e del RAW
LOG.

Commit verificati:

```text
7115ab5 Refine operational log controls
4d64c04 Refine raw log mobile controls
```

Il RAW LOG è stato collaudato anche sul Legacy ed è risultato fluido.

### 19 agosto 2026

È stato completato il primo checkpoint della documentazione bilingue.

Commit firmato:

```text
b2b55a2 Update bilingual project documentation
```

Il repository LAB risultava allineato a `origin/main`.

Sono state quindi avviate la revisione e la creazione bilingue dei
documenti tecnici rimanenti.

---

## 13. Test

L'ultimo stato test riportato nel checkpoint operativo è:

```text
22 passed
```

Questo valore rappresenta uno stato verificato in quel checkpoint e non
deve essere considerato un numero permanente.

Il numero dei test può cambiare con l'evoluzione del progetto.

La regola resta:

```bash
pytest -q
```

deve essere eseguito prima dei commit previsti dal flusso di sviluppo.

---

## 14. Documentazione bilingue

La struttura documentale prevista è:

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

---

## 15. Principi da preservare

Durante lo sviluppo non devono essere perse queste decisioni:

1. il RAW LOG resta RAW;
2. LAB prima, Legacy dopo;
3. i commit di produzione sono firmati;
4. lo stato interno è canonico e indipendente dalla lingua;
5. i segreti restano fuori Git;
6. evitare scansioni complete dei logfile nei refresh frequenti;
7. mobile è importante quanto desktop;
8. leggere sempre il file reale prima di modificarlo;
9. non dichiarare completato ciò che è solo progettato;
10. non inventare numeri di release;
11. nodi SvxLink e client applicativi Reflector sono concetti distinti;
12. `/monitor` resta congelata rispetto a LATRY finché il modello non è
    stabile e validato.
