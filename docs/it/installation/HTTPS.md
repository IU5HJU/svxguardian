# SVX Guardian - Configurazione HTTPS

> 🇮🇹 **Documentazione italiana**  
> 🇬🇧 [English documentation](../../installation/HTTPS.md)

## Panoramica

SVX Guardian può essere pubblicato in modo sicuro tramite HTTPS utilizzando:

- Apache come reverse proxy;
- Gunicorn come application server locale;
- un certificato SSL/TLS emesso per il nome host del nodo;
- un hostname DNS o DDNS;
- l'eventuale port forwarding del router.

L'architettura raccomandata è:

```text
Internet
   |
   | HTTPS
   v
Router / NAT
   |
   | porta TCP pubblica
   v
Apache HTTPS
   |
   | reverse proxy
   v
127.0.0.1:8080
   |
   v
Gunicorn
   |
   v
SVX Guardian
```

SVX Guardian non richiede che la porta del backend sia esposta direttamente a Internet.

Gunicorn deve normalmente essere in ascolto esclusivamente su:

```text
127.0.0.1:8080
```

Apache gestisce la connessione HTTPS e inoltra le richieste al backend Gunicorn locale.

---

## Principio fondamentale

SVX Guardian non deve dipendere dalla disponibilità pubblica della porta TCP 80.

Molte installazioni radioamatoriali utilizzano reti domestiche nelle quali:

- la porta 80 può essere già utilizzata da un altro servizio;
- la porta 80 può essere bloccata dal router o dal provider;
- l'utente può non avere la possibilità di riservare le porte standard;
- più servizi possono condividere lo stesso indirizzo IP pubblico.

Per questo motivo, quando disponibile, è preferibile utilizzare la validazione DNS del certificato.

La dashboard HTTPS può essere pubblicata sulla porta:

```text
443
```

oppure su una porta pubblica alternativa, ad esempio:

```text
8443
9443
10443
```

Il certificato identifica l'hostname e non la porta TCP.

---

## Porta pubblica e porta locale

La porta esposta dal router non deve necessariamente coincidere con quella utilizzata localmente da Apache.

Esempio 1:

```text
Internet TCP 443
        |
        v
Router
        |
        v
Raspberry Pi TCP 443
```

La dashboard sarà raggiungibile tramite:

```text
https://example.ddns.net
```

Esempio 2:

```text
Internet TCP 8443
        |
        v
Router
        |
        v
Raspberry Pi TCP 443
```

La dashboard sarà raggiungibile tramite:

```text
https://example.ddns.net:8443
```

Il certificato rimane valido perché viene emesso per:

```text
example.ddns.net
```

e non è legato alla porta TCP 443.

---

## Sicurezza del backend

SVX Guardian non deve esporre Gunicorn direttamente sulla rete pubblica.

Il binding Gunicorn raccomandato è:

```text
127.0.0.1:8080
```

Il router non deve inoltrare la porta TCP 8080 verso il Raspberry Pi.

Architettura corretta:

```text
Internet
   |
   v
Apache HTTPS
   |
   v
127.0.0.1:8080
   |
   v
Gunicorn
```

Architettura non raccomandata:

```text
Internet
   |
   v
TCP 8080
   |
   v
Gunicorn esposto direttamente
```

---

## Directory SSL

SVX Guardian conserva localmente il materiale SSL in:

```text
/etc/svxguardian/ssl
```

Permessi raccomandati per la directory:

```text
root:root
700
```

Chiave privata:

```text
/etc/svxguardian/ssl/<hostname>.key
root:root
600
```

Certificato / catena PEM:

```text
/etc/svxguardian/ssl/<hostname>.pem
root:root
644
```

CSR:

```text
/etc/svxguardian/ssl/<hostname>.csr
root:root
644
```

La chiave privata non deve mai essere pubblicata, inviata, caricata su servizi esterni o inserita in Git.

---

## Protezione Git

Il repository deve ignorare il materiale crittografico reale.

Regole raccomandate nel `.gitignore`:

```gitignore
*.key
*.csr
*.pem
*.crt
*.cer
*.p12
*.pfx

/ssl/
/certs/
/certificates/
```

La `/` iniziale nelle regole delle directory è importante.

Per esempio:

```gitignore
/ssl/
```

ignora esclusivamente una directory `ssl` presente nella radice del repository.

Non nasconde:

```text
install/ssl/
```

che contiene gli script d'installazione di SVX Guardian e deve essere versionata.

---

## Strumenti per l'installazione HTTPS

SVX Guardian mette a disposizione:

```text
install/ssl/create-csr.sh
install/ssl/verify-certificate.sh
install/ssl/install-certificate.sh
install/ssl/setup-https.sh

install/apache/configure-apache.sh
install/apache/svxguardian.conf.template
```

---

## create-csr.sh

Questo script genera:

```text
/etc/svxguardian/ssl/<hostname>.key
/etc/svxguardian/ssl/<hostname>.csr
```

La chiave privata viene generata localmente.

Il CSR utilizza SHA-256 e contiene le informazioni richieste dal provider del certificato.

Lo script richiede:

```text
Hostname / FQDN
Codice paese
Stato / Regione
Località / Città
Organizzazione
Unità organizzativa
```

Il codice paese deve utilizzare il formato ISO a due caratteri.

Esempi:

```text
IT
DE
FR
ES
GB
US
```

La chiave privata non viene mostrata dallo script.

Il CSR generato può invece essere fornito al provider del certificato.

---

## verify-certificate.sh

Lo script di verifica controlla:

- corrispondenza dell'hostname;
- Subject Alternative Name;
- validità temporale del certificato;
- corrispondenza tra certificato e chiave privata;
- numero di certificati contenuti nel PEM;
- presenza della catena del certificato.

Una verifica conclusa correttamente restituisce:

```text
SSL_CERTIFICATE_STATUS=VALID
```

Questo risultato è leggibile sia dall'utente sia da future procedure automatiche.

---

## install-certificate.sh

Lo script di installazione:

1. controlla che l'hostname corrisponda;
2. verifica la validità del certificato;
3. verifica la corrispondenza certificato/chiave privata;
4. controlla il contenuto del PEM;
5. crea la directory SSL se necessario;
6. crea un backup dell'eventuale certificato esistente;
7. installa il nuovo file PEM;
8. applica i permessi corretti;
9. esegue una verifica finale.

La chiave privata non viene sostituita né modificata.

Una installazione conclusa correttamente restituisce:

```text
SSL_CERTIFICATE_INSTALL_STATUS=SUCCESS
```

---

## configure-apache.sh

Lo script di configurazione Apache:

1. verifica che Apache sia installato;
2. richiede l'hostname;
3. richiede la porta HTTPS locale;
4. verifica il backend Gunicorn;
5. verifica la presenza del certificato e della chiave privata;
6. abilita i moduli Apache necessari;
7. crea un backup della configurazione SVX Guardian esistente;
8. genera la configurazione Apache dal template;
9. aggiunge una direttiva `Listen` se viene utilizzata una porta locale non standard;
10. esegue `apache2ctl configtest`;
11. abilita il sito SVX Guardian;
12. ricarica Apache;
13. esegue un test HTTPS locale.

Una configurazione conclusa correttamente restituisce:

```text
APACHE_HTTPS_STATUS=SUCCESS
```

---

## setup-https.sh

È il punto di ingresso guidato raccomandato.

Eseguire:

```bash
sudo ./install/ssl/setup-https.sh
```

Il menu permette di:

```text
1) Avviare una nuova configurazione del certificato HTTPS
2) Continuare dopo aver ricevuto il certificato PEM
3) Verificare un certificato installato
4) Configurare / riparare Apache HTTPS
5) Mostrare i file SSL presenti
0) Uscire
```

Lo script può quindi essere interrotto durante l'attesa dell'emissione del certificato e ripreso successivamente.

Durante l'attesa restituisce:

```text
HTTPS_SETUP_STATUS=WAITING_FOR_CERTIFICATE
```

Al completamento:

```text
HTTPS_SETUP_STATUS=SUCCESS
```

---

## Template Apache

Il template generico si trova in:

```text
install/apache/svxguardian.conf.template
```

Non contiene valori specifici del nodo.

Le variabili previste comprendono:

```text
@SVXGUARDIAN_HOSTNAME@
@SVXGUARDIAN_HTTPS_PORT@
@SVXGUARDIAN_CERTIFICATE@
@SVXGUARDIAN_PRIVATE_KEY@
@SVXGUARDIAN_BACKEND_HOST@
@SVXGUARDIAN_BACKEND_PORT@
```

Una configurazione tipica utilizza:

```text
Backend host: 127.0.0.1
Backend port: 8080
Porta HTTPS:  443
```

---

## Moduli Apache

Il reverse proxy HTTPS richiede:

```text
ssl
proxy
proxy_http
headers
```

Possono essere abilitati manualmente con:

```bash
sudo a2enmod ssl
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod headers
```

Lo script automatico `configure-apache.sh` esegue autonomamente questa operazione.

---

## Test del backend locale

Prima di cercare un problema nella configurazione HTTPS, verificare che il backend locale funzioni:

```bash
curl -s http://127.0.0.1:8080/api/state
```

Una risposta JSON valida conferma che il percorso:

```text
Gunicorn -> SVX Guardian
```

è operativo.

---

## Test HTTPS locale

HTTPS può essere verificato localmente senza dipendere dal NAT del router o dal percorso DNS pubblico.

Esempio:

```bash
curl \
  --resolve example.ddns.net:443:127.0.0.1 \
  https://example.ddns.net/api/state
```

Questo test verifica:

```text
Apache
  |
  v
Certificato
  |
  v
Reverse proxy
  |
  v
Gunicorn
  |
  v
SVX Guardian
```

senza utilizzare il percorso attraverso Internet e il router.

È uno strumento particolarmente utile per la diagnostica.

---

## Verifica della configurazione Apache

Prima di ricaricare Apache eseguire sempre:

```bash
sudo apache2ctl configtest
```

Risultato atteso:

```text
Syntax OK
```

Per visualizzare i VirtualHost attivi:

```bash
sudo apache2ctl -S
```

Esempio:

```text
*:443 example.ddns.net
```

---

## Porte in ascolto

Controllare Apache:

```bash
sudo ss -lntp | grep ':443'
```

Controllare Gunicorn:

```bash
sudo ss -lntp | grep ':8080'
```

Configurazione raccomandata:

```text
Apache:
*:443

Gunicorn:
127.0.0.1:8080
```

In una installazione di produzione Gunicorn non dovrebbe normalmente essere in ascolto su:

```text
0.0.0.0:8080
```

---

## Router / NAT

Il router deve inoltrare verso il Raspberry Pi la porta HTTPS pubblica scelta.

Configurazione standard:

```text
WAN TCP 443
    ->
Raspberry Pi TCP 443
```

Configurazione alternativa:

```text
WAN TCP 8443
    ->
Raspberry Pi TCP 443
```

Non inoltrare:

```text
TCP 8080
```

verso Gunicorn.

Il backend deve rimanere privato.

---

## Collaudo sul campo

Il test finale deve essere effettuato da una rete esterna.

Un metodo semplice consiste nel:

1. disabilitare il Wi-Fi sullo smartphone;
2. utilizzare la rete mobile;
3. aprire l'indirizzo HTTPS pubblico.

Con la porta HTTPS standard:

```text
https://example.ddns.net
```

Con una porta pubblica alternativa:

```text
https://example.ddns.net:8443
```

Verificare quindi anche la dashboard operativa:

```text
https://example.ddns.net/monitor
```

Controllare:

- assenza di avvisi relativi al certificato;
- caricamento completo della dashboard;
- aggiornamento dei dati;
- aggiornamento delle informazioni EchoLink;
- funzionamento della vista operativa;
- selezione della lingua;
- corretto comportamento sul browser mobile.

---

## Procedura di diagnostica

Seguire questo ordine permette di individuare più rapidamente il punto del problema.

### 1. Controllare SVX Guardian

```bash
curl -s http://127.0.0.1:8080/api/state
```

Se il comando fallisce, il problema si trova prima di Apache.

### 2. Controllare Gunicorn

```bash
sudo systemctl status svxguardian
```

Poi:

```bash
sudo ss -lntp | grep ':8080'
```

Risultato atteso:

```text
127.0.0.1:8080
```

### 3. Controllare Apache

```bash
sudo apache2ctl configtest
```

Poi:

```bash
sudo apache2ctl -S
```

### 4. Controllare HTTPS localmente

```bash
curl \
  --resolve example.ddns.net:443:127.0.0.1 \
  https://example.ddns.net/api/state
```

Se questo test funziona, Apache, TLS e SVX Guardian funzionano localmente.

### 5. Controllare router e NAT

Se il test HTTPS locale funziona ma l'indirizzo pubblico non è raggiungibile, verificare:

- port forwarding;
- firewall;
- indirizzo IP pubblico;
- risoluzione DDNS;
- eventuali restrizioni del provider Internet;
- regole di inoltro obsolete o duplicate.

---

## Errore comune durante l'installazione

Nel router può essere rimasta una vecchia regola che espone:

```text
TCP 8080
```

anche dopo la configurazione di Apache HTTPS.

Le vecchie regole di accesso diretto al backend devono essere rimosse.

Il percorso pubblico previsto è:

```text
Internet
   |
   v
Apache HTTPS
   |
   v
Gunicorn
```

e non:

```text
Internet
   |
   v
Gunicorn
```

---

## Rinnovo del certificato

La procedura di rinnovo dipende dal provider del certificato.

SVX Guardian non deve presumere che tutti i provider:

- utilizzino la stessa procedura di rinnovo;
- mettano a disposizione una API DNS;
- utilizzino la stessa durata dei certificati;
- forniscano lo stesso formato PEM.

Le procedure specifiche dei singoli provider devono essere documentate separatamente.

Per No-IP vedere:

```text
docs/it/installation/NOIP_SSL.md
```

---

## Regole di sicurezza

Non:

```text
pubblicare una chiave privata
inserire una chiave privata in Git
caricare una chiave privata su GitHub
inviare una chiave privata tramite email
inserire una chiave privata nella documentazione
```

Non esporre direttamente il backend Gunicorn a Internet salvo una necessità specifica e consapevole.

È invece necessario:

- utilizzare HTTPS per l'accesso pubblico;
- proteggere `/etc/svxguardian/ssl`;
- effettuare il backup della configurazione Apache esistente;
- verificare la corrispondenza certificato/chiave privata;
- eseguire `apache2ctl configtest` prima del reload;
- effettuare il test locale prima di intervenire sul router;
- mantenere la configurazione specifica del provider separata dal codice dell'applicazione.

---

## Stato di compatibilità attuale

L'architettura HTTPS e gli script sono stati collaudati con:

```text
Apache
Gunicorn
SVX Guardian
hostname DNS/DDNS
validazione DNS del certificato
```

Il primo workflow specifico per un provider verificato durante lo sviluppo di SVX Guardian è stato No-IP.

Le istruzioni specifiche del provider sono mantenute in una documentazione separata affinché l'architettura HTTPS principale di SVX Guardian rimanga indipendente dal singolo fornitore.
