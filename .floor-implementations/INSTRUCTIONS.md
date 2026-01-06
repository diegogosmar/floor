# Istruzioni per Aggiungere il Progetto a floor-implementations

## File Preparati

Ho preparato tutti i file necessari nella directory `.floor-implementations/`:

```
.floor-implementations/
├── implementations/
│   └── python-diegogosmar/
│       └── README.md          # README da copiare nella fork
├── README_UPDATE.md            # Sezione da aggiungere al README principale
└── INSTRUCTIONS.md            # Questo file
```

## Procedura Step-by-Step

### 1. Fork del Repository

Vai su GitHub e fai fork di:
```
https://github.com/open-voice-interoperability/floor-implementations
```

### 2. Clone della Tua Fork

```bash
git clone https://github.com/YOUR_USERNAME/floor-implementations.git
cd floor-implementations
```

### 3. Crea la Directory

```bash
mkdir -p implementations/python-diegogosmar
```

### 4. Copia il README

```bash
# Dalla directory del progetto floor
cp .floor-implementations/implementations/python-diegogosmar/README.md \
   /path/to/floor-implementations/implementations/python-diegogosmar/README.md
```

Oppure copia manualmente il contenuto del file.

### 5. Aggiorna il README Principale

Apri `README.md` del repository `floor-implementations` e aggiungi la sezione contenuta in `.floor-implementations/README_UPDATE.md`.

### 6. Commit e Push

```bash
cd /path/to/floor-implementations
git add implementations/python-diegogosmar/
git add README.md
git commit -m "Add Python Floor Manager implementation by Diego Gosmar"
git push origin main
```

### 7. Crea Pull Request

Vai su GitHub e crea una Pull Request dalla tua fork al repository originale.

## Note Importanti

- ✅ **NON copiare il codice sorgente** - Solo il README con link
- ✅ Dopo la PR iniziale, **non devi più toccare la fork**
- ✅ I tuoi aggiornamenti a `diegogosmar/floor` sono automaticamente visibili tramite il link
- ✅ Vedi `docs/FORK_SYNC_EXPLANATION.md` per dettagli sulla sincronizzazione

## Verifica

Dopo il merge della PR, verifica che:
1. Il link al repository funzioni
2. Il README sia leggibile
3. La sezione nel README principale sia presente

## Aiuto

Se hai problemi, consulta:
- `docs/ADD_TO_FLOOR_IMPLEMENTATIONS.md` - Guida completa
- `docs/FORK_SYNC_EXPLANATION.md` - Spiegazione sincronizzazione fork

