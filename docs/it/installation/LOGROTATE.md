# SVX Guardian - Rotazione del logfile SvxLink

> 🇮🇹 **Documentazione italiana**
> 🇬🇧 [English documentation](../../installation/LOGROTATE.md)

## Panoramica

`ReflectorMonitor` ed `EchoLinkMonitor` ricostruiscono lo stato
corrente del nodo scansionando il logfile di SvxLink all'indietro,
cercando l'ultima riga di stato (connessione, disconnessione,
snapshot dei nodi).

Senza `logrotate` configurato per il logfile di SvxLink
(tipicamente `/var/log/svxlink`), il file cresce senza limiti. Su un
nodo reale ha raggiunto 17 MB dopo 95 giorni di uptime, e ogni
richiesta della dashboard scansionava sempre più a ritroso in un file
in continua crescita, degradando l'intera dashboard.

SVX Guardian affronta il problema da due angolazioni complementari:

- `ReflectorMonitor.MAX_BACKWARD_SCAN_BYTES` limita quanto
  l'applicazione stessa può scansionare all'indietro (vedi
  `src/modules/reflector.py`), così che una rotazione mancante o
  fallita non riporti la dashboard a tempi di risposta di vari
  secondi;
- `install/logrotate/` permette al Sysop di configurare `logrotate`
  a livello di sistema operativo per il logfile di SvxLink, in modo
  che non continui a crescere sul disco.

Le due correzioni sono complementari e normalmente vanno applicate
insieme.

---

## Strumenti per la rotazione dei log

SVX Guardian mette a disposizione:

```text
install/logrotate/configure-logrotate.sh
install/logrotate/svxlink.logrotate.template
```

---

## svxlink.logrotate.template

Il template generico `logrotate` per il logfile di SvxLink.

Non contiene valori specifici del nodo.

Variabili del template:

```text
@SVXGUARDIAN_SVXLINK_LOG@
@SVXGUARDIAN_LOGROTATE_SIZE@
@SVXGUARDIAN_LOGROTATE_ROTATE@
```

La configurazione generata utilizza `copytruncate`: SvxLink continua
a scrivere sullo stesso inode già aperto, senza richiedere un
restart o un segnale di reopen del log dopo la rotazione.

---

## configure-logrotate.sh

Lo script di configurazione interattivo deve essere eseguito come
root:

```bash
sudo ./install/logrotate/configure-logrotate.sh
```

Esegue i seguenti passaggi:

1. rileva il logfile di SvxLink, con la stessa priorità usata da
   `ConfigManager._resolve_log_file`:
   - override tramite la variabile d'ambiente
     `SVXGUARDIAN_SVXLINK_LOG`;
   - `LOGFILE=` da un file di default systemd di SvxLink
     (`/etc/default/svxlink` o `/usr/local/etc/default/svxlink`);
   - percorsi di installazione noti
     (`/var/log/svxlink`, `/usr/local/var/log/svxlink`);
   - percorso storico Debian/Raspberry Pi OS come fallback;
2. richiede la dimensione massima prima della rotazione (default
   `10M`) e il numero di rotazioni da mantenere (default `14`),
   validando entrambi gli input;
3. crea un backup con timestamp dell'eventuale
   `/etc/logrotate.d/svxlink` esistente prima di sovrascriverlo;
4. renderizza il template e verifica che non resti alcun
   placeholder `@SVXGUARDIAN_*@` non risolto;
5. installa la configurazione e la valida con `logrotate -d`,
   ripristinando il backup (o rimuovendo il file se non esisteva una
   configurazione precedente) in caso di fallimento della
   validazione.

Un'esecuzione completata correttamente restituisce:

```text
LOGROTATE_CONFIG_STATUS=SUCCESS
```

---

## Verificare una configurazione preesistente

Se esiste già un `/etc/logrotate.d/svxlink` precedente, viene
salvato come:

```text
/etc/logrotate.d/svxlink.backup-<timestamp>
```

Per confrontarlo con la configurazione appena installata da SVX
Guardian:

```bash
diff /etc/logrotate.d/svxlink.backup-<timestamp> /etc/logrotate.d/svxlink
```

Nota: una direttiva `logrotate` che combina un intervallo temporale
(`daily`, `weekly`, `monthly`) con `size` non è un conflitto — per il
manuale di `logrotate`, quando è presente `size` l'intervallo
temporale viene ignorato e la rotazione è governata esclusivamente
dalla dimensione, controllata a ogni esecuzione del cron di
`logrotate`. Un eventuale `daily` preesistente insieme a `size` è
quindi ridondante, non un cambiamento di comportamento.

---

## Validare la configurazione installata

```bash
sudo logrotate -d /etc/logrotate.d/svxlink
```

Una simulazione (`-d`) non ruota mai il logfile: si limita a
segnalare cosa accadrebbe.

Per forzare una rotazione reale a scopo di test:

```bash
sudo logrotate -f /etc/logrotate.d/svxlink
```

---

## Documentazione collegata

Per il limite applicativo alla scansione all'indietro del log, vedere
`src/modules/reflector.py::MAX_BACKWARD_SCAN_BYTES` e il principio di
progettazione "Prestazioni" in:

```text
docs/ARCHITECTURE.md
```
