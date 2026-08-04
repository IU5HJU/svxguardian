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
