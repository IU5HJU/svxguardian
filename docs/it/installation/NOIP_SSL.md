# SVX Guardian - Configurazione certificato SSL con No-IP

> 🇮🇹 **Documentazione italiana**  
> 🇬🇧 [English documentation](../../installation/NOIP_SSL.md)

## Scopo

Questo documento descrive la procedura SSL con No-IP collaudata durante lo sviluppo di SVX Guardian.

La procedura è stata verificata utilizzando:

- un hostname DDNS No-IP;
- un certificato DV emesso tramite No-IP;
- verifica DNS mediante record TXT;
- download della PEM Chain;
- Apache come reverse proxy HTTPS;
- Gunicorn in ascolto locale su `127.0.0.1:8080`.

La procedura è stata collaudata nell'agosto 2026.

No-IP può modificare nel tempo:

- la propria interfaccia web;
- i prodotti SSL disponibili;
- la procedura di validazione;
- la terminologia utilizzata;
- i formati di download dei certificati.

Per l'architettura HTTPS generale di SVX Guardian vedere:

```text
docs/it/installation/HTTPS.md
```

---

## Principio fondamentale

La procedura No-IP descritta in questo documento non richiede che la porta TCP pubblica 80 sia disponibile per SVX Guardian.

La validazione del certificato è stata eseguita tramite DNS TXT.

Questo è particolarmente utile nelle installazioni radioamatoriali domestiche, dove:

- la porta 80 può essere già utilizzata da un altro servizio;
- la porta 80 può essere bloccata;
- il router può imporre limitazioni;
- più servizi possono condividere lo stesso indirizzo IP pubblico;
- il radioamatore può non avere il pieno controllo delle porte standard.

SVX Guardian può quindi essere pubblicato in HTTPS senza dipendere dalla porta HTTP 80.

---

## Requisiti

Prima di iniziare sono necessari:

- un hostname No-IP funzionante;
- accesso all'account No-IP che gestisce l'hostname;
- SVX Guardian funzionante localmente;
- OpenSSL installato;
- Apache installato;
- Gunicorn configurato per SVX Guardian;
- accesso `root` o `sudo` al Raspberry Pi.

Negli esempi utilizzeremo:

```text
example.ddns.net
```

Sostituirlo sempre con l'hostname reale del nodo.

---

## Procedura guidata raccomandata

Il punto di ingresso consigliato è:

```bash
sudo ./install/ssl/setup-https.sh
```

Per iniziare una nuova configurazione scegliere:

```text
1) Start a new HTTPS certificate setup
```

La procedura guidata richiama automaticamente lo script di generazione CSR e prepara la directory SSL locale.

---

## Directory SSL

SVX Guardian utilizza:

```text
/etc/svxguardian/ssl
```

Permessi attesi:

```text
root:root
700
```

Chiave privata:

```text
/etc/svxguardian/ssl/example.ddns.net.key
```

Permessi raccomandati:

```text
root:root
600
```

CSR:

```text
/etc/svxguardian/ssl/example.ddns.net.csr
```

Permessi raccomandati:

```text
root:root
644
```

Certificato:

```text
/etc/svxguardian/ssl/example.ddns.net.pem
```

Permessi raccomandati:

```text
root:root
644
```

---

## Passaggio 1 - Generazione della chiave privata e del CSR

Eseguire:

```bash
sudo ./install/ssl/create-csr.sh
```

Lo script richiede:

```text
Hostname / FQDN
Codice paese
Stato / Regione
Località / Città
Organizzazione
Unità organizzativa
```

La chiave privata viene generata localmente sul Raspberry Pi e deve rimanere sul nodo.

Il CSR può invece essere fornito a No-IP.

---

## Requisiti CSR riscontrati durante il collaudo

Durante la procedura reale, un CSR contenente soltanto il Common Name non è stato accettato.

Sono stati riscontrati questi errori:

```text
Invalid two character ISO-3166 country code.
```

e:

```text
CSR must contain a State/Province
```

Per questo motivo lo script `create-csr.sh` di SVX Guardian richiede tutti i campi necessari alla procedura No-IP collaudata.

---

## Codice paese

Il paese deve essere indicato utilizzando un codice ISO di due caratteri.

Esempi:

```text
Italia:
IT

Germania:
DE

Francia:
FR

Spagna:
ES

Regno Unito:
GB

Stati Uniti:
US
```

Non inserire il nome completo del paese.

Errato:

```text
Italia
Italy
Germania
Germany
```

Corretto:

```text
IT
DE
```

---

## Stato / Regione

Il campo State / Province non deve essere lasciato vuoto.

Esempio:

```text
Toscana
```

Utilizzare la regione, stato o provincia appropriata per il titolare del certificato.

---

## Località / Città

Inserire la città o località appropriata.

Esempio:

```text
Example City
```

---

## Common Name

Il Common Name deve corrispondere all'hostname completo utilizzato per raggiungere SVX Guardian.

Esempio:

```text
example.ddns.net
```

Non utilizzare:

```text
localhost
192.168.1.100
raspberrypi
```

salvo il caso in cui il certificato sia stato espressamente emesso per tali identificativi.

---

## Esempio di Subject del CSR

Un Subject completo può essere simile a:

```text
C=IT
ST=Toscana
L=Example City
O=SVX Guardian
OU=Amateur Radio
CN=example.ddns.net
```

I campi relativi all'organizzazione possono variare.

---

## Controllo del CSR

Per ispezionare il CSR:

```bash
sudo openssl req \
  -in /etc/svxguardian/ssl/example.ddns.net.csr \
  -noout \
  -subject \
  -text
```

Controllare che il Subject contenga:

- hostname corretto;
- paese;
- regione/stato;
- località;
- eventuali dati organizzativi.

---

## Visualizzazione del CSR

Per visualizzare il CSR da inviare a No-IP:

```bash
sudo cat /etc/svxguardian/ssl/example.ddns.net.csr
```

Copiare tutto il blocco:

```text
-----BEGIN CERTIFICATE REQUEST-----
...
-----END CERTIFICATE REQUEST-----
```

Il CSR può essere fornito al provider del certificato.

---

## La chiave privata non deve mai essere caricata

Non visualizzare, inviare o caricare:

```text
/etc/svxguardian/ssl/example.ddns.net.key
```

La chiave privata deve rimanere sul Raspberry Pi.

Non deve essere:

- incollata nel portale No-IP;
- allegata a email;
- inserita nella documentazione;
- caricata su GitHub;
- inviata tramite chat o messaggistica;
- copiata su servizi cloud non controllati.

---

## Passaggio 2 - Avvio della procedura su No-IP

Accedere all'account No-IP che gestisce l'hostname.

Aprire la sezione dedicata ai certificati SSL.

Durante il workflow collaudato è stato possibile creare o attivare il certificato direttamente dalla sezione SSL.

Quando No-IP richiede il CSR, incollare quello generato da SVX Guardian.

---

## Passaggio 3 - Verifica DNS TXT

Durante la procedura collaudata, No-IP ha generato un valore TXT di verifica.

Il record TXT era associato direttamente all'hostname DDNS.

Esempio:

```text
example.ddns.net. 300 IN TXT "<verification-token>"
```

Il token mostrato nell'esempio non è reale.

Utilizzare sempre il valore esatto mostrato dal portale No-IP.

---

## Nota importante sul nome del record TXT

Non assumere automaticamente che il record debba essere:

```text
_acme-challenge.example.ddns.net
```

Durante il workflow No-IP collaudato, il record TXT era associato direttamente all'hostname DDNS.

Utilizzare sempre:

- il nome indicato da No-IP;
- il valore indicato da No-IP.

---

## Verifica della propagazione TXT

Se `dig` è disponibile:

```bash
dig TXT example.ddns.net +short
```

È possibile interrogare anche resolver DNS pubblici.

Cloudflare:

```bash
dig @1.1.1.1 TXT example.ddns.net +short
```

Google:

```bash
dig @8.8.8.8 TXT example.ddns.net +short
```

Il valore restituito deve corrispondere a quello fornito da No-IP.

---

## Installazione di dig

Su versioni recenti di Raspberry Pi OS / Debian il pacchetto può essere:

```bash
sudo apt update
sudo apt install bind9-dnsutils
```

Su altri sistemi può essere disponibile anche:

```bash
sudo apt install dnsutils
```

I nomi dei pacchetti possono cambiare in base alla distribuzione e alla versione.

---

## Problemi con i mirror dei repository

Durante il collaudo, l'installazione degli strumenti DNS ha temporaneamente restituito errori:

```text
404 Not Found
```

relativi a pacchetti `bind9-*`.

La prima azione da eseguire è:

```bash
sudo apt update
```

e successivamente ripetere l'installazione.

Non modificare immediatamente la configurazione dei repository se il problema può dipendere da indici locali non aggiornati.

---

## Passaggio 4 - Verifica del certificato su No-IP

Quando il record TXT è visibile pubblicamente, tornare nel portale No-IP e completare la verifica.

Durante il collaudo, il certificato ha raggiunto lo stato:

```text
ACTIVE
```

Non procedere alla configurazione Apache prima che il certificato sia stato effettivamente emesso.

---

## Passaggio 5 - Download del certificato

Durante il collaudo No-IP offriva più formati di download.

Il formato utilizzato con successo è stato:

```text
PEM Chain
```

Questo formato conteneva:

- il certificato dell'hostname;
- i certificati intermedi;
- la catena necessaria ad Apache.

---

## Perché utilizzare PEM Chain

La PEM Chain può essere utilizzata direttamente da Apache come:

```text
SSLCertificateFile
```

Durante il collaudo, il file PEM conteneva tre certificati.

SVX Guardian può verificare automaticamente quanti certificati sono presenti nel file.

---

## Copia della PEM Chain sul Raspberry Pi

Copiare il file scaricato sul Raspberry Pi utilizzando, ad esempio:

- SFTP;
- SCP;
- FileZilla;
- un altro sistema sicuro di trasferimento file.

Una posizione temporanea può essere:

```text
/home/<user>/
```

Esempio:

```text
/home/<user>/example_ddns_net.pem
```

La chiave privata non deve essere trasferita dal Raspberry Pi.

---

## Passaggio 6 - Verifica del certificato scaricato

Eseguire:

```bash
sudo ./install/ssl/verify-certificate.sh
```

Inserire:

```text
Certificate PEM file:
<percorso del PEM scaricato>

Private key file:
/etc/svxguardian/ssl/example.ddns.net.key

Expected hostname / FQDN:
example.ddns.net
```

Lo script verifica:

- hostname del certificato;
- Subject Alternative Name;
- validità temporale;
- corrispondenza certificato/chiave privata;
- contenuto della PEM Chain.

Risultato atteso:

```text
SSL_CERTIFICATE_STATUS=VALID
```

---

## Esempio di verifica corretta

Una verifica conclusa con successo comprende:

```text
[OK] Certificate matches hostname
[OK] Certificate is currently valid
[OK] Certificate and private key match
[OK] PEM file contains a certificate chain
```

e termina con:

```text
SSL_CERTIFICATE_STATUS=VALID
```

---

## Certificato e chiave privata non corrispondono

Se il certificato non corrisponde alla chiave privata, non continuare.

Una possibile causa è la generazione di una nuova private key dopo aver già inviato il CSR al provider.

Il certificato viene emesso per la chiave utilizzata durante la generazione del CSR originale.

Non rigenerare:

```text
example.ddns.net.key
```

dopo l'emissione del certificato, salvo che si voglia intenzionalmente creare una nuova coppia chiave/certificato.

---

## Passaggio 7 - Installazione della PEM Chain

Eseguire:

```bash
sudo ./install/ssl/install-certificate.sh
```

Lo script:

- verifica il certificato;
- verifica la private key;
- controlla l'hostname;
- controlla il contenuto del PEM;
- crea un backup dell'eventuale certificato esistente;
- installa il nuovo PEM;
- applica i permessi corretti;
- esegue una verifica finale.

Risultato atteso:

```text
SSL_CERTIFICATE_INSTALL_STATUS=SUCCESS
```

La chiave privata non viene modificata.

---

## Passaggio 8 - Configurazione Apache

Eseguire:

```bash
sudo ./install/apache/configure-apache.sh
```

Esempio di risposte:

```text
Hostname / FQDN:
example.ddns.net

Local HTTPS port [443]:
<Invio>

Backend host [127.0.0.1]:
<Invio>

SVX Guardian backend port [8080]:
<Invio>
```

Lo script:

- verifica il certificato;
- verifica il backend locale;
- abilita i moduli Apache necessari;
- crea un backup della configurazione esistente;
- genera il VirtualHost dal template;
- esegue `apache2ctl configtest`;
- ricarica Apache;
- esegue un test HTTPS locale.

Risultato atteso:

```text
APACHE_HTTPS_STATUS=SUCCESS
```

---

## Architettura Apache

La configurazione collaudata è:

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
   |
   v
SVX Guardian
```

Gunicorn non viene esposto direttamente a Internet.

---

## Passaggio 9 - Configurazione del router

Configurazione standard:

```text
Internet TCP 443
        ->
Raspberry Pi TCP 443
```

Se la porta pubblica 443 non è disponibile:

```text
Internet TCP 8443
        ->
Raspberry Pi TCP 443
```

L'indirizzo pubblico diventerà:

```text
https://example.ddns.net:8443
```

Il certificato rimane valido perché identifica l'hostname e non la porta TCP.

---

## Non inoltrare la porta TCP 8080

Rimuovere eventuali vecchie regole del router che espongono:

```text
TCP 8080
```

La configurazione di produzione collaudata utilizza:

```text
127.0.0.1:8080
```

per Gunicorn.

Il backend deve rimanere accessibile soltanto localmente.

---

## Passaggio 10 - Test HTTPS locale

Prima di verificare l'accesso da Internet:

```bash
curl \
  --resolve example.ddns.net:443:127.0.0.1 \
  https://example.ddns.net/api/state
```

Una risposta JSON valida conferma il corretto funzionamento di:

```text
Apache HTTPS
Certificato
Reverse proxy
Gunicorn
SVX Guardian
```

senza coinvolgere il router.

---

## Passaggio 11 - Collaudo sul campo

Utilizzare uno smartphone.

Disabilitare il Wi-Fi.

Utilizzare la rete cellulare.

Aprire:

```text
https://example.ddns.net
```

Poi verificare:

```text
https://example.ddns.net/monitor
```

Controllare:

- assenza di avvisi SSL;
- caricamento completo della dashboard;
- caricamento della vista operativa;
- aggiornamento dei dati;
- aggiornamento EchoLink;
- selezione della lingua;
- comportamento corretto sul dispositivo mobile.

---

## Diagnostica

### Il certificato è ACTIVE ma HTTPS non funziona

Controllare:

```bash
sudo apache2ctl configtest
```

Poi:

```bash
sudo apache2ctl -S
```

Infine:

```bash
sudo ss -lntp | grep ':443'
```

---

## Il backend non risponde

Controllare:

```bash
curl -s http://127.0.0.1:8080/api/state
```

Se questo comando fallisce, correggere prima SVX Guardian/Gunicorn e successivamente Apache.

---

## HTTPS locale funziona ma l'accesso Internet no

Controllare:

- port forwarding del router;
- firewall;
- risoluzione DDNS;
- indirizzo IP pubblico;
- eventuali restrizioni del provider Internet;
- regole obsolete o duplicate.

---

## Comportamento anomalo dell'indirizzo pubblico

Controllare se nel router è ancora presente una vecchia regola di inoltro relativa a:

```text
8080
```

Durante lo sviluppo una regola obsoleta sulla porta 8080 ha generato un comportamento confuso, anche se Apache HTTPS era configurato correttamente.

---

## Warning globale ServerName di Apache

Apache può mostrare:

```text
Could not reliably determine the server's fully qualified domain name
```

pur restituendo:

```text
Syntax OK
```

Questo warning non significa necessariamente che il VirtualHost SVX Guardian sia errato.

Per controllare i VirtualHost attivi:

```bash
sudo apache2ctl -S
```

Il warning può essere eliminato successivamente configurando un `ServerName` globale appropriato.

---

## Rinnovo del certificato

La procedura di rinnovo dipende da No-IP e dal tipo di certificato utilizzato.

Non bisogna presumere che la procedura futura sia identica a quella descritta in questo documento.

Prima del rinnovo:

1. conservare la chiave privata esistente, salvo volontà di effettuare una key rotation;
2. generare il CSR secondo le richieste del provider;
3. completare la validazione DNS;
4. scaricare la nuova PEM Chain;
5. verificare il certificato;
6. installarlo tramite lo script SVX Guardian;
7. ricaricare Apache;
8. ripetere i test HTTPS.

Lo script di installazione crea automaticamente un backup quando sostituisce un certificato esistente.

---

## Checklist di sicurezza

Prima di considerare terminata l'installazione verificare:

```text
[ ] La private key rimane esclusivamente sul nodo
[ ] I permessi della private key sono 600
[ ] I permessi della directory SSL sono 700
[ ] Il certificato PEM è stato verificato
[ ] Il certificato corrisponde all'hostname
[ ] Il certificato corrisponde alla private key
[ ] apache2ctl configtest restituisce Syntax OK
[ ] Gunicorn ascolta soltanto su 127.0.0.1
[ ] Il router non espone TCP 8080
[ ] HTTPS funziona localmente
[ ] HTTPS funziona da una rete esterna
[ ] /monitor funziona da smartphone
```

---

## File che non devono mai essere inseriti nel repository

Non effettuare mai commit di materiale crittografico reale:

```text
*.key
*.csr
*.pem
*.crt
*.cer
*.p12
*.pfx
```

Il repository deve contenere esclusivamente:

- script;
- template;
- documentazione.

Certificati e chiavi private reali rimangono fuori dal repository.

---

## Stato del collaudo

La procedura descritta è stata utilizzata con successo per ottenere:

```text
https://<hostname-No-IP>
```

attraverso:

```text
Hostname No-IP
    ->
Validazione DNS del certificato
    ->
Apache HTTPS
    ->
Gunicorn
    ->
SVX Guardian
```

senza richiedere la disponibilità pubblica della porta TCP 80.

No-IP rappresenta il primo workflow SSL specifico per provider effettivamente collaudato con SVX Guardian.
