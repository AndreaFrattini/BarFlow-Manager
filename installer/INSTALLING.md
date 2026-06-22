# Installer e distribuzione di AccountFlow

Questo documento spiega come installare l'applicazione su Windows e su iPad/iOS per una demo.

## 1) Installazione su Windows

Per un PC Windows puoi usare gli installer già presenti nella cartella `installer`:

- `build_installer.bat`
- `build_installer.ps1`
- `post_install.ps1`

### Procedura consigliata
1. Esegui `build_installer.ps1` oppure `build_installer.bat` per generare il pacchetto.
2. Installa il file generato sul PC.
3. Avvia l'applicazione e verifica che il database e le risorse siano configurati correttamente.

## 2) Installazione su iPad / iOS (demo)

Un'app Qt/PySide distribuita con Briefcase non può essere installata su iPad come un semplice file `.exe` o `.msi`.
Per iOS il metodo pratico è uno di questi:

- **TestFlight** (consigliato per demo e feedback):
  - puoi inviare al cliente un link TestFlight;
  - sul suo iPad basta aprire il link e installare l'app.

### Nota importante
Se vuoi farla usare a un amico senza passare per gli store ufficiali, la soluzione più realistica è:
1. creare il build iOS con Xcode/Briefcase;
2. distribuire il build tramite TestFlight oppure con un provisioning ad hoc;
3. far aprire al cliente il link o il QR code sul suo iPad.

## 3) Demo per amico (workflow completo su Mac + TestFlight + iPad)

Questa sezione è pensata per il caso in cui vuoi far provare l'app a un amico senza usare un canale "ufficiale" come App Store.

### Passo 1 — Preparazione sul tuo Mac
1. Assicurati di avere un Mac con macOS aggiornato.
2. Installa Xcode e gli strumenti command line.
3. Installa UV, se non è già presente.
4. Apri il terminale nella cartella del progetto e esegui:
   - `uv sync`
   - `uv run briefcase create iOS`
   - `uv run briefcase build iOS`
5. Se necessario, apri Xcode e controlla che il progetto sia stato creato correttamente.

### Passo 2 — Preparare la distribuzione TestFlight
1. Accedi al tuo account Apple Developer.
2. Assicurati di avere configurato:
   - un identificativo bundle corretto;
   - un profilo di provisioning valido;
   - una firma del team Apple.
3. In Xcode, seleziona il target iOS e verifica che il build sia firmato correttamente.
4. Crea il build e caricalo su App Store Connect.
5. Nella sezione TestFlight aggiungi il build e crea un gruppo di tester.
6. Invia l'invito al tuo amico tramite email o link TestFlight.

### Passo 3 — Far installare l'app sul suo iPad
1. Sul suo iPad, l'amico deve aprire il link ricevuto.
2. Se richiesto, deve accedere con il suo ID Apple.
3. Dovrà confermare l'installazione e attendere il download.
4. Una volta installata, l'app appare sulla schermata Home.

### Passo 4 — Feedback e verifica
1. Chiedi all'amico di usare l'app per qualche minuto.
2. Fai raccogliere feedback su:
   - leggibilità dell'interfaccia;
   - velocità di caricamento;
   - eventuali errori o crash;
   - utilità delle funzioni principali.
3. Se serve, puoi aggiornare il build e inviare una nuova versione tramite TestFlight.

### Passo 5 — Come rimuovere l'app da iPad
1. Tieni premuta l'icona dell'app sulla schermata Home.
2. Seleziona **Rimuovi App**.
3. Conferma la rimozione.

> Nota: se la app è stata installata tramite TestFlight, puoi anche rimuoverla dalla sezione TestFlight o dalla schermata delle app installate.

## 4) Come rimuovere l'app da iPad

Per rimuovere l'app da iPad:
1. tieni premuta l'icona dell'app sulla schermata Home;
2. seleziona **Rimuovi App**;
3. conferma la rimozione.

Se hai distribuito l'app tramite TestFlight, puoi anche rimuoverla dalla sezione TestFlight o dall'elenco delle app installate.
