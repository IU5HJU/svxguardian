# Contribuire a SVX Guardian

## 1. Scopo

Questo documento definisce le regole di sviluppo e contribuzione del
progetto SVX Guardian.

L'obiettivo è mantenere codice, documentazione e architettura coerenti,
verificabili e manutenibili nel tempo, indipendentemente dal numero di
sviluppatori o dalle sessioni di lavoro.

Tutte le modifiche al progetto devono rispettare queste linee guida.

---

## 2. Filosofia di sviluppo

SVX Guardian privilegia:

- semplicità;
- chiarezza;
- modularità;
- leggibilità;
- affidabilità;
- stabilità;
- compatibilità;
- verificabilità.

Una soluzione semplice, verificabile e ben documentata è preferibile
a una soluzione inutilmente complessa.

Non deve essere dichiarata implementata o completata una funzionalità
che è soltanto progettata o prevista.

---

## 3. Ambienti di lavoro

Lo sviluppo utilizza due ambienti distinti:

- **LAB**: sviluppo, modifica e test;
- **Legacy**: nodo reale con traffico radio, utilizzato dopo la
  validazione sul LAB e su GitHub.

Il Legacy non deve essere utilizzato come ambiente primario di
sviluppo.

Il suo scopo è verificare il comportamento di Guardian in una reale
installazione SvxLink e con traffico radio effettivo.

---

## 4. Flusso di sviluppo

Il flusso operativo di riferimento è:

```text
Design → LAB → pytest → test funzionale → commit GPG → GitHub
→ Legacy (merge --ff-only) → pytest → restart → traffico reale
```

Ogni passaggio deve essere verificato prima di procedere al successivo.

Le modifiche devono essere prima validate sul LAB.

Solo dopo la pubblicazione e la validazione del relativo commit si
procede all'aggiornamento del Legacy.

Una funzionalità che richiede traffico reale non deve essere
considerata definitivamente validata sulla sola base dei test LAB.

---

## 5. Metodo operativo

Durante lo sviluppo si procede preferibilmente:

- un passo alla volta;
- con modifiche chiaramente delimitate;
- con una verifica prima del passo successivo;
- leggendo sempre la versione reale corrente di un file prima di
  modificarlo.

Quando una modifica viene fornita manualmente per copia/incolla,
preferire il file completo pronto da copiare anziché patch parziali,
quando questo riduce il rischio di errori o perdita di contesto.

Non utilizzare `sudo` per modificare i file interni al repository.

---

## 6. Controlli prima del commit

Prima di ogni commit eseguire almeno:

```bash
git diff --check
pytest -q
git status --short
```

Verificare inoltre:

- che i test previsti siano superati;
- che la documentazione interessata sia aggiornata;
- che non siano presenti file temporanei o indesiderati;
- che non siano inclusi segreti, credenziali o configurazioni private;
- che il diff corrisponda esclusivamente alle modifiche previste.

I commit destinati al repository di produzione devono essere firmati.

---

## 7. Git e pubblicazione

Il branch principale è `main`.

Le modifiche validate vengono pubblicate su GitHub secondo il flusso
di progetto.

Sul Legacy, l'allineamento con il repository deve preservare una
storia lineare utilizzando, quando previsto dal flusso operativo:

```bash
git merge --ff-only
```

Dopo l'aggiornamento del Legacy devono essere ripetuti i test
automatici pertinenti prima del riavvio e del collaudo con traffico
reale.

Dopo il push verificare che il repository locale e remoto siano nello
stato previsto.

---

## 8. Documentazione

La documentazione è parte integrante del progetto.

La struttura principale comprende:

### `README.md` / `README.en.md`

Presentazione sintetica del progetto rispettivamente in italiano e
inglese.

### `docs/PROJECT.md` / `docs/PROJECT.en.md`

Visione generale e obiettivi del progetto.

### `docs/ARCHITECTURE.md` / `docs/ARCHITECTURE.en.md`

Architettura software e principi strutturali.

### `docs/DEVELOPMENT.md` / `docs/DEVELOPMENT.en.md`

Informazioni e procedure relative allo sviluppo.

### `docs/ROADMAP.md` / `docs/ROADMAP.en.md`

Direzione e attività future del progetto.

### `docs/DASHBOARD.md` / `docs/DASHBOARD.en.md`

Specifiche funzionali e organizzazione della dashboard.

La documentazione deve distinguere chiaramente tra:

- funzionalità implementate;
- funzionalità in sviluppo;
- funzionalità previste.

Non inventare numeri di release o milestone non formalizzati nel
repository.

---

## 9. Convenzioni Python

Il codice Python deve privilegiare:

- una responsabilità chiaramente identificabile per componente;
- codice leggibile;
- funzioni di dimensione ragionevole;
- type hints quando opportuno;
- docstring per classi e funzioni pubbliche;
- logging al posto di output diagnostico non strutturato;
- separazione tra acquisizione, stato e presentazione.

I monitor devono operare attraverso le interfacce e gli oggetti di
stato previsti dall'architettura.

Non introdurre dipendenze dirette tra monitor quando la comunicazione
può avvenire attraverso lo stato condiviso.

---

## 10. HTML e presentazione

Le stringhe visibili destinate all'interfaccia devono utilizzare il
sistema di traduzione previsto dal progetto.

Non spostare logica tecnica o interpretazione dello stato nei template
quando appartiene al livello applicativo.

Le modifiche all'interfaccia devono essere verificate sia su desktop
sia su mobile.

Lo stile visivo e i colori consolidati di Guardian devono essere
preservati salvo una decisione esplicita di progetto.

---

## 11. CSS

Preferire nomi descrittivi e regole facilmente manutenibili.

Evitare duplicazioni quando una regola comune può essere riutilizzata.

Le modifiche responsive non devono risolvere un problema desktop
creandone uno mobile, o viceversa.

---

## 12. JSON e dati strutturati

Mantenere strutture stabili, documentate e coerenti con il modello
interno.

I valori di stato interni devono essere tecnici e canonici.

La rappresentazione localizzata appartiene al livello di
presentazione e non deve modificare il significato dei dati interni.

---

## 13. Internazionalizzazione

Lo stato interno di Guardian è indipendente dalla lingua.

La traduzione viene applicata nei livelli di presentazione, come
dashboard, console e output descrittivi destinati all'utente.

I termini tecnici internazionali possono rimanere invariati, ad
esempio:

- SvxLink;
- EchoLink;
- Reflector;
- RX;
- TX;
- TG;
- CTCSS.

Quando viene aggiunta o modificata una stringa traducibile, mantenere
sincronizzati i file di localizzazione pertinenti nella directory
`locale/`.

---

## 14. Segreti e configurazione privata

Credenziali, password, chiavi, token e altri segreti non devono essere
inseriti nel repository Git.

La configurazione privata di Guardian deve essere mantenuta fuori dal
repository.

L'installazione attuale utilizza:

```text
/etc/svxguardian
```

La chiave persistente delle sessioni Flask è mantenuta in:

```text
/etc/svxguardian/secret.key
```

Le future procedure di installazione e provisioning devono creare e
configurare i file privati con proprietario e permessi appropriati,
senza segreti hardcoded.

---

## 15. Log e prestazioni

Il RAW LOG SvxLink deve restare RAW.

La pagina e l'API dedicate al RAW LOG non devono reinterpretare o
classificare le righe mostrate.

Le funzioni eseguite frequentemente devono evitare scansioni complete
e ripetute dei logfile quando è possibile utilizzare una strategia
incrementale o equivalente.

Ottimizzazioni che modificano il comportamento osservabile devono
essere testate prima sul LAB e successivamente, quando necessario, sul
Legacy.

---

## 16. Compatibilità

SVX Guardian deve poter funzionare su installazioni SvxLink differenti.

Non assumere una configurazione hardware specifica o una sola variante
dei file di configurazione.

Le compatibilità legacy già supportate devono essere preservate salvo
una decisione esplicita e documentata.

Il nodo utilizzato per lo sviluppo è un ambiente di test, non un
modello universale di installazione.

---

## 17. Reflector e client applicativi

I nodi SvxLink connessi al Reflector e gli utenti/client applicativi
sono concetti distinti.

Non inserire artificialmente utenti provenienti da client applicativi,
come LATRY, in `reflector_connected_nodes`.

Eventuali nuovi modelli di stato per gli utenti Reflector devono essere
prima analizzati e collaudati con traffico reale.

La vista `/monitor` non deve essere modificata per integrare questi
utenti finché il relativo modello non è stabile e validato nella pagina
`/reflector`.

---

## 18. Controlli qualità

Prima di considerare conclusa un'attività verificare, secondo la sua
natura:

- test automatici;
- test funzionali;
- comportamento desktop e mobile;
- eventuale collaudo con traffico reale;
- documentazione;
- stato del repository;
- assenza di errori di formattazione rilevati da `git diff --check`.

Le verifiche devono essere ripetibili.

---

## 19. Obiettivo delle modifiche

Ogni modifica deve migliorare almeno uno dei seguenti aspetti:

- affidabilità;
- semplicità;
- leggibilità;
- manutenibilità;
- documentazione;
- compatibilità;
- prestazioni;
- esperienza del Sysop.

Una funzionalità non sufficientemente verificata e documentata non deve
essere considerata completa.
