# Development Journal

---

## 2026-08-04

### Obiettivo

Consolidamento dell'architettura di SVX Guardian e preparazione al supporto di installazioni eterogenee.

### Completato

#### Configurazione nodo

- Rifattorizzato `ConfigReader`.
- Introdotto `NodeInfoReader`.
- Separata la lettura di `svxlink.conf` da `node_info.json`.
- Integrati i dati statici del nodo.

#### Modello dati

- Separazione tra `NodeInfo` per la configurazione e `NodeState` per lo stato operativo.
- Estensione del modello dati con informazioni geografiche e radio.

#### Reflector

- Nuova architettura del Reflector.
- Supporto previsto per:
  - Reflector locale
  - Reflector remoto
  - Configurazioni miste
  - Reflector disabilitato

- Nuovi campi:
  - `reflector_configured`
  - `reflector_hosts`
  - `reflector_port`
  - `reflector_default_tg`
  - `reflector_mode`
  - `reflector_logic_name`

#### API

L'endpoint `/api/state` espone ora:

- dati del nodo;
- configurazione Reflector;
- configurazione radio;
- informazioni statiche.

#### Dashboard

- Pannello `Node Identity` collegato ai dati reali.
- Lettura corretta di `node_info.json`.
- Visualizzazione di nominativo, QTH, locator, Reflector e moduli caricati.

### Decisioni progettuali

#### Compatibilità SvxLink

`node_info.json` rimane compatibile con SvxLink.

SVX Guardian non dovrà modificarlo automaticamente senza conferma del sysop.

#### Configurazione SVX Guardian

La configurazione specifica del progetto sarà mantenuta in un file separato, ad esempio:

```text
config/svxguardian.json
```

#### Portabilità

SVX Guardian non deve essere progettato esclusivamente sulla configurazione del nodo di sviluppo.

Dovrà supportare:

- Raspberry Pi;
- VPS;
- Reflector locali;
- Reflector remoti;
- configurazioni miste;
- hotspot;
- ripetitori;
- nodi simplex;
- installazioni distribuite.

#### Topologia dell'ambiente di sviluppo

Nell'ambiente di sviluppo, il client SvxLink e SvxReflector convivono sullo stesso Raspberry Pi.

Questa configurazione è considerata un caso particolare di prova e non il modello standard del progetto.

---

## 2026-08-05

### Obiettivo

Completamento dell'internazionalizzazione della dashboard e consolidamento del repository.

### Completato

#### Internazionalizzazione

- Eliminata ogni stringa visibile hardcoded dalla dashboard principale.
- Tutte le etichette dell'interfaccia utilizzano il sistema di traduzione.
- Mantenuti in inglese i termini tecnici standard:
  - SvxLink
  - EchoLink
  - Reflector
  - RX
  - TX
  - CTCSS
  - TG

#### Traduzioni

Aggiornati e sincronizzati i file:

- `en.json`
- `it.json`
- `fr.json`
- `es.json`
- `de.json`
- `ru.json`

Tutte le lingue contengono lo stesso insieme di 40 chiavi.

#### Controllo qualità

Creato il nuovo strumento:

```text
tools/check_i18n.py
```

Funzioni implementate:

- verifica della validità dei file JSON;
- rilevamento delle chiavi duplicate;
- controllo delle chiavi mancanti;
- segnalazione delle chiavi inutilizzate;
- verifica delle stringhe visibili hardcoded nei template;
- controllo della coerenza fra i file di traduzione.

Risultato finale:

```text
I18N STATUS: PASSED
```

Le chiavi attualmente inutilizzate sono mantenute perché previste per condizioni operative e schermate future.

#### Documentazione

- Corretto il nome `docs/ROADMAP.mp` in `docs/ROADMAP.md`.
- Git ha riconosciuto la modifica come rinomina completa, mantenendo la cronologia del file.

#### Repository

- Uniformata la proprietà dei file del repository all'utente `iq5lv`.
- Stabilito che `sudo` non deve essere utilizzato per modificare file interni al repository.
- Repository sincronizzato con GitHub.
- Working tree verificato come pulito.

### Decisioni progettuali

Da questa milestone in avanti:

- ogni stringa visibile deve utilizzare il `TranslationManager`;
- i termini tecnici internazionali possono restare invariati, ma devono essere gestiti coerentemente;
- nessuna nuova funzione sarà considerata completa con stringhe visibili hardcoded;
- ogni milestone terminerà con:
  - aggiornamento della documentazione;
  - esecuzione dei test;
  - esecuzione degli strumenti di controllo;
  - verifica di Git;
  - commit;
  - push;
  - controllo finale del working tree.

### Metodo di lavoro

Durante le sessioni SSH:

- si procede con un passo alla volta;
- si modifica un file completo alla volta;
- prima delle modifiche importanti si crea un backup;
- non si utilizzano modifiche parziali quando possono compromettere la struttura del file;
- ogni risultato viene verificato prima del passaggio successivo.

### Stato del progetto

Il progetto dispone ora di:

- architettura modulare;
- separazione tra configurazione statica e stato operativo;
- lettura di `svxlink.conf` e `node_info.json`;
- supporto strutturato per Reflector locali, remoti e misti;
- API REST con informazioni del nodo;
- dashboard responsive;
- internazionalizzazione completa della dashboard;
- audit automatico delle traduzioni;
- documentazione organizzata;
- repository pulito e coerente.

### Prossime attività

- completamento del pannello `Node Identity`;
- rilevamento automatico della versione di SvxLink;
- rilevamento dell'hardware e del sistema operativo;
- Event Engine;
- storico delle metriche;
- modalità Control Room;
- configurazione HTTPS tramite reverse proxy;
- procedura guidata per gli altri sysop.
