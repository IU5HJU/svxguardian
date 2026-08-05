# SVX Guardian

## Project Handbook

Versione documento: 1.0

---

# 1. Visione del progetto

SVX Guardian è una piattaforma open source per il monitoraggio, la supervisione e la gestione di sistemi radio basati su SvxLink.

L'obiettivo del progetto è realizzare una dashboard moderna, semplice e affidabile che permetta al sysop di conoscere in tempo reale lo stato del proprio nodo radio.

Il progetto deve essere indipendente dalla configurazione hardware utilizzata e funzionare su installazioni SvxLink eterogenee.

---

# 2. Principi del progetto

SVX Guardian deve essere:

- semplice;
- stabile;
- leggibile;
- modulare;
- facilmente estendibile;
- completamente documentato.

Ogni nuova funzionalità deve rispettare questi principi.

---

# 3. Compatibilità

SVX Guardian deve funzionare con installazioni SvxLink differenti.

Sono considerate configurazioni supportate:

- Raspberry Pi
- PC Linux
- Mini PC
- VPS
- macchine virtuali

e le seguenti tipologie radio:

- nodo simplex
- ripetitore
- hotspot
- bridge
- reflector remoto
- reflector locale

Il nodo di sviluppo NON rappresenta il caso standard.

---

# 4. Nodo di sviluppo

L'ambiente utilizzato durante lo sviluppo presenta una configurazione particolare.

Nello stesso Raspberry Pi convivono:

- SvxLink
- SvxReflector

Questa configurazione è utilizzata esclusivamente come ambiente di sviluppo.

Il software non dovrà mai assumere che questa architettura sia quella normalmente utilizzata dagli altri sysop.

---

# 5. Architettura

Le componenti principali sono:

Guardian

↓

ConfigReader

↓

NodeInfoReader

↓

System Reader

↓

Health Engine

↓

Exporter

↓

Dashboard

Ogni componente deve avere una responsabilità precisa.

---

# 6. Stato attuale

Componenti completati

- ConfigReader
- NodeInfoReader
- Reflector Reader
- Health Engine
- Exporter JSON
- Dashboard principale
- API REST
- Internationalization
- Translation Manager
- I18N Audit

---

# 7. Componenti in sviluppo

Bootstrap Engine

Hardware Reader

Version Reader

Event Engine

Historical Database

HTTPS

Control Room

Setup Wizard

---

# 8. Regole di sviluppo

Durante lo sviluppo valgono sempre le seguenti regole.

## File

Sempre file completi.

Mai modifiche parziali.

## Procedura

Un comando.

Una verifica.

Un comando successivo.

## Backup

Prima delle modifiche importanti creare sempre un backup.

## Git

Ogni milestone termina con:

- documentazione aggiornata;
- test;
- git status;
- commit;
- push;
- verifica finale.

---

# 9. Convenzioni

I termini tecnici internazionali rimangono invariati.

Esempi:

- SvxLink
- EchoLink
- Reflector
- RX
- TX
- TG
- CTCSS

Le stringhe visibili devono utilizzare sempre il Translation Manager.

---

# 10. Repository

Documentazione

ARCHITECTURE.md

Descrive l'architettura del software.

DEVELOPMENT.md

Diario cronologico dello sviluppo.

ROADMAP.md

Funzionalità future.

PROJECT.md

Documento principale del progetto.

---

# 11. Stato Git

Ogni commit sul branch main deve rappresentare una versione stabile del progetto.

Il repository deve terminare sempre con:

working tree clean

---

# 12. Obiettivo finale

SVX Guardian dovrà diventare il sistema di riferimento open source per il monitoraggio dei nodi SvxLink.

Il progetto dovrà poter essere installato facilmente da qualsiasi radioamatore, indipendentemente dall'architettura del proprio sistema.

La qualità del codice e della documentazione è considerata parte integrante del progetto.
