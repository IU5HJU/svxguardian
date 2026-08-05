# Contributing to SVX Guardian

Versione documento: 1.0

---

# 1. Scopo

Questo documento definisce le regole di sviluppo del progetto SVX Guardian.

L'obiettivo è mantenere il codice, la documentazione e l'architettura coerenti nel tempo, indipendentemente dal numero di sviluppatori o dalle sessioni di lavoro.

Tutte le modifiche al progetto devono rispettare queste linee guida.

---

# 2. Filosofia di sviluppo

SVX Guardian privilegia:

- semplicità;
- chiarezza;
- modularità;
- leggibilità;
- stabilità;
- compatibilità.

Una soluzione semplice e ben documentata è preferibile a una soluzione complessa.

---

# 3. Metodo di lavoro

Ogni attività deve seguire questo flusso:

1. analisi;
2. implementazione;
3. verifica;
4. documentazione;
5. commit;
6. push.

Nessuna milestone è considerata conclusa senza documentazione aggiornata.

---

# 4. Modalità operativa

Durante lo sviluppo si procede sempre:

- un passo alla volta;
- un comando alla volta;
- una verifica prima del passo successivo.

Questo metodo riduce gli errori e rende ogni modifica facilmente verificabile.

---

# 5. Modifica dei file

Le modifiche devono essere eseguite sull'intero file.

Non utilizzare modifiche parziali quando possono compromettere la struttura del documento o del codice.

Prima delle modifiche importanti è consigliato creare una copia di sicurezza.

---

# 6. Repository Git

Il repository deve rimanere sempre in uno stato coerente.

Prima di ogni commit verificare:

- documentazione aggiornata;
- test eseguiti;
- `git status`;
- assenza di file indesiderati;
- working tree pulito dopo il push.

Non utilizzare `sudo` per modificare file interni al repository.

---

# 7. Documentazione

La documentazione è parte integrante del progetto.

## PROJECT.md

Visione generale del progetto.

## ARCHITECTURE.md

Architettura software.

## DEVELOPMENT.md

Diario cronologico dello sviluppo.

## ROADMAP.md

Milestone future.

## DASHBOARD.md

Specifiche funzionali della dashboard.

---

# 8. Convenzioni di codice

## Python

- una responsabilità per modulo;
- codice leggibile;
- funzioni brevi;
- type hint quando opportuno;
- docstring per classi e funzioni pubbliche.

## HTML

Nessuna stringa visibile deve essere hardcoded.

Utilizzare sempre il Translation Manager.

## CSS

Preferire nomi descrittivi.

Evitare duplicazioni.

## JSON

Mantenere una struttura stabile e documentata.

---

# 9. Internazionalizzazione

Le stringhe visibili devono essere tradotte.

I termini tecnici internazionali possono rimanere invariati.

Esempi:

- SvxLink
- EchoLink
- Reflector
- RX
- TX
- TG
- CTCSS

Ogni modifica deve mantenere sincronizzati tutti i file presenti nella directory `locale/`.

---

# 10. Compatibilità

SVX Guardian deve funzionare su installazioni differenti.

Non assumere mai una configurazione hardware specifica.

Il nodo utilizzato per lo sviluppo rappresenta un ambiente di test, non un modello di riferimento.

---

# 11. Controlli qualità

Prima di considerare conclusa una milestone verificare:

- test automatici;
- strumenti di audit;
- documentazione;
- stato del repository.

Le verifiche devono essere ripetibili.

---

# 12. Obiettivo

Ogni modifica deve migliorare almeno uno dei seguenti aspetti:

- affidabilità;
- semplicità;
- leggibilità;
- documentazione;
- compatibilità;
- esperienza del sysop.

Una funzionalità non documentata non è considerata completa.
