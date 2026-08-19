# Dashboard di SVX Guardian

## 1. Scopo

La dashboard di SVX Guardian fornisce una vista web dello stato operativo
di un nodo SvxLink.

L'interfaccia è progettata per essere:

- leggibile rapidamente;
- responsive;
- utilizzabile da desktop e dispositivi mobili;
- multilingua;
- leggera;
- coerente con lo stato canonico mantenuto da Guardian.

La dashboard non deve presentare come disponibili funzioni che non sono
ancora implementate o collaudate.

---

## 2. Struttura generale

L'interfaccia web utilizza Flask, template Jinja, Bootstrap 5,
Font Awesome e gli stylesheet di SVX Guardian.

Le normali pagine tecniche condividono:

- header globale;
- contenuto responsive;
- sidebar di navigazione;
- sistema di traduzione;
- supporto ai temi Light e Dark.

Le pagine principali sono:

```text
/                  Dashboard generale
/monitor           Vista operativa
/system            Stato del sistema
/svxlink           Stato e configurazione SvxLink
/echolink          Stato EchoLink
/reflector         Stato Reflector
/logs              RAW LOG SvxLink
/configuration     Configurazione e controllo
```

---

## 3. Temi

Sono supportati due temi:

- Light;
- Dark.

La preferenza viene salvata nel browser con la chiave:

```text
svxguardian-theme
```

Se non esiste una preferenza salvata, l'interfaccia utilizza la
preferenza di sistema del browser quando disponibile.

Il tema viene applicato il prima possibile durante il caricamento della
pagina per evitare il lampeggio iniziale del tema errato.

La vista `/monitor` utilizza gli stessi stati Light/Dark, con una
presentazione specificamente ottimizzata per l'uso operativo.

---

## 4. Multilingua

Le stringhe dell'interfaccia utilizzano il Translation Manager.

Lo stato tecnico interno rimane canonico e indipendente dalla lingua.

La traduzione viene applicata solo durante la presentazione.

I termini tecnici internazionali, quando opportuno, possono rimanere
invariati.

Le lingue effettivamente disponibili devono essere determinate dai file
di localizzazione presenti nel progetto e non devono essere dichiarate
in questo documento sulla base di una lista teorica.

---

## 5. Dashboard generale

La pagina `/` fornisce il riepilogo principale del nodo.

### Stato generale

Un banner evidenzia lo stato complessivo:

- `HEALTHY`;
- `WARNING`;
- `CRITICAL`;
- stato sconosciuto.

Viene mostrata anche la motivazione associata allo stato.

### Identità del nodo

La dashboard mostra in forma compatta:

- callsign;
- locator;
- QTH.

### Riepilogo sistema

Una scheda collegata alla pagina `/system` mostra:

- utilizzo CPU;
- temperatura CPU;
- utilizzo RAM;
- utilizzo disco.

### Servizi radio

Tre schede permettono di raggiungere direttamente:

- SvxLink;
- EchoLink;
- Reflector.

Ogni scheda mostra lo stato corrente del relativo servizio utilizzando
badge coerenti con la severità dello stato.

La dashboard generale è una vista sintetica: i dettagli appartengono
alle pagine dedicate.

---

## 6. Vista operativa `/monitor`

La pagina `/monitor` è una vista operativa dedicata, progettata in
particolare per una consultazione rapida anche da smartphone.

Non replica l'intera dashboard tecnica.

Mostra principalmente lo stato EchoLink e l'attività delle stazioni.

La vista comprende:

- identità SVX Guardian;
- callsign del nodo;
- stato operativo EchoLink;
- numero di connessioni;
- ora dell'ultimo aggiornamento;
- elenco delle stazioni;
- nominativo della stazione;
- nome della stazione quando disponibile;
- stato della stazione;
- durata della connessione.

Le stazioni vengono rappresentate con stati visivi distinti:

- connessa;
- connessione instabile;
- in trasmissione.

La stazione in trasmissione riceve una evidenza visiva prioritaria.

L'elenco può adottare una rappresentazione più compatta quando il
numero di stazioni aumenta.

La vista aggiorna i timer locali ogni secondo e acquisisce il nuovo
stato operativo ogni 2 secondi.

Il modello della pagina `/monitor` deve rimanere stabile. Gli utenti di
client applicativi Reflector, come LATRY, non devono essere aggiunti a
questa vista finché il relativo modello di stato non sarà stato
definito e validato nella pagina `/reflector`.

---

## 7. Pagina System

La pagina `/system` mostra lo stato del sistema Linux/Raspberry Pi.

Comprende:

- hostname;
- uptime;
- temperatura CPU;
- utilizzo CPU;
- utilizzo RAM;
- utilizzo disco.

CPU, RAM e disco sono accompagnati da barre di avanzamento.

Le soglie visuali attuali sono:

```text
< 75%       verde
75% - 89%   warning
>= 90%      critical
```

La temperatura CPU viene mostrata quando disponibile.

---

## 8. Pagina SvxLink

La pagina `/svxlink` combina stato dinamico del servizio e informazioni
statiche ricavate dalla configurazione del nodo.

### Stato del servizio

Mostra:

- stato SvxLink;
- PID;
- uptime del servizio.

### Identità del nodo

Mostra, quando disponibili:

- callsign;
- QTH;
- locator;
- Sysop;
- classe del nodo;
- posizione geografica.

### Configurazione

La pagina espone inoltre informazioni quali:

- versione SvxLink;
- file di configurazione rilevato;
- file `node_info.json`;
- moduli;
- logiche;
- configurazione RX;
- configurazione TX;
- ulteriori parametri tecnici ricavati dalla configurazione.

La pagina deve mostrare `NOT_AVAILABLE` quando un dato non è
disponibile invece di inventare valori.

---

## 9. Pagina EchoLink

La pagina `/echolink` è la vista tecnica dedicata a EchoLink.

### Stato generale

Mostra:

- stato EchoLink;
- numero di connessioni;
- callsign del nodo;
- presenza del modulo EchoLink;
- ultimo errore, quando presente.

Gli stati principali vengono rappresentati con badge distinti, tra cui:

- `ONLINE`;
- `OFFLINE`;
- `DNS_ERROR`;
- `ERROR`;
- stato sconosciuto.

### Stazioni connesse

La pagina mostra le stazioni EchoLink attualmente connesse.

### Ultimi collegamenti

È presente una sezione dedicata agli eventi/collegamenti recenti.

Per ogni collegamento possono essere mostrati:

- callsign;
- nome della stazione;
- data/ora di connessione;
- durata;
- stato;
- data/ora di disconnessione.

Le connessioni riconosciute come instabili vengono evidenziate
esplicitamente.

La pagina aggiorna dinamicamente lo stato tramite `/api/state` ogni
2 secondi senza richiedere il reload completo della pagina.

---

## 10. Pagina Reflector

La pagina `/reflector` mostra lo stato tecnico della connessione al
Reflector.

Comprende:

- stato;
- host;
- porta;
- numero di connessioni;
- talkgroup;
- stato della cifratura;
- motivo dell'ultima disconnessione;
- ultimo errore;
- nodi SvxLink connessi.

Gli stati previsti dalla presentazione comprendono:

- `CONNECTING`;
- `CONNECTED`;
- `RECONNECTING`;
- `DISCONNECTED`;
- `AUTH_ERROR`;
- `TIMEOUT`;
- `ERROR`;
- stato sconosciuto.

La pagina aggiorna dinamicamente lo stato tramite `/api/state` ogni
2 secondi.

### Nodi e client applicativi

`reflector_connected_nodes` rappresenta i nodi SvxLink connessi.

Gli utenti provenienti da client applicativi, come LATRY, costituiscono
un concetto differente e non devono essere inseriti artificialmente in
questo elenco.

Il modello definitivo degli utenti/client Reflector rimane oggetto di
analisi e deve essere validato con traffico reale prima di essere
esteso ad altre viste.

---

## 11. RAW LOG

La pagina `/logs` visualizza il log operativo SvxLink come sorgente RAW.

La pagina non deve reinterpretare, classificare o modificare
semanticamente le righe del logfile.

Il lettore è incrementale e utilizza `/api/logs`.

Il polling avviene ogni 2 secondi.

Sono disponibili controlli locali nel browser per:

- Pause/Play;
- Auto-scroll;
- Clear.

`Clear` pulisce soltanto la visualizzazione nel browser e non modifica
il logfile originale.

La vista mantiene un cursore di lettura e limita il numero di righe
mantenute nel browser per evitare una crescita indefinita della pagina.

Il polling del RAW LOG non deve eseguire l'intero ciclo
`guardian.run()`.

---

## 12. Configurazione e controllo

La pagina `/configuration` separa la consultazione della configurazione
dalle operazioni che modificano lo stato del nodo.

Il monitoraggio pubblico deve continuare a essere disponibile anche
quando l'autenticazione non è configurata.

Le operazioni di controllo sono riservate agli utenti autorizzati
Sysop/Co-Sysop.

Le operazioni protette utilizzano token CSRF.

Il controllo operativo attualmente disponibile comprende il restart
del servizio SvxLink.

I controlli futuri eventualmente presenti nell'interfaccia ma
disabilitati non devono essere documentati come funzionalità
implementate.

---

## 13. Aggiornamento dei dati

Non esiste una regola generale secondo cui l'intera dashboard si
aggiorna ogni secondo.

Le politiche di aggiornamento dipendono dalla pagina.

Attualmente:

```text
/monitor       stato: 2 s, timer locali: 1 s
/echolink      stato: 2 s
/reflector     stato: 2 s
/logs          nuove righe: 2 s
```

Le pagine che effettuano aggiornamenti dinamici utilizzano le API senza
ricaricare completamente la pagina.

Le pagine tecniche statiche rispetto al caricamento non devono
introdurre polling senza una necessità reale.

---

## 14. Responsive design

L'interfaccia deve rimanere utilizzabile sia su desktop sia su mobile.

La dashboard tecnica utilizza la griglia responsive di Bootstrap e gli
stili specifici di Guardian.

La vista `/monitor` utilizza un layout dedicato, con larghezza
contenuta, elementi grandi e informazioni operative prioritarie.

Le modifiche responsive devono essere verificate in entrambe le
condizioni e non devono alterare inutilmente lo stile visivo già
consolidato.

---

## 15. Funzionalità non implementate

Non devono essere descritte come funzionalità attuali della dashboard,
finché non saranno sviluppate e collaudate:

- grafici storici;
- storico persistente generale;
- statistiche avanzate;
- pannello generale degli eventi di sistema;
- controlli automatici di recovery;
- funzioni di backup;
- nuove viste Reflector basate su client applicativi non ancora
  modellati.

La documentazione deve essere aggiornata quando una di queste
funzionalità diventa realmente disponibile.

---

## 16. Principi di progettazione

La dashboard deve permettere di comprendere rapidamente:

- se il nodo è operativo;
- se SvxLink è in esecuzione;
- se EchoLink è disponibile;
- se il Reflector è connesso;
- se il sistema Linux/Raspberry Pi è in condizioni normali;
- quali stazioni EchoLink sono attualmente collegate;
- se una connessione EchoLink è instabile o in trasmissione.

Le informazioni sintetiche appartengono alla dashboard generale.

I dettagli appartengono alle pagine dedicate.

La vista operativa deve privilegiare leggibilità e immediatezza.

Il RAW LOG deve rimanere RAW.

La presentazione multilingua non deve modificare il significato dello
stato interno.
