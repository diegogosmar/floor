# Come Funzionano le Fork e la Sincronizzazione

## Domanda: Cosa succede quando fai push al tuo repo originale?

Quando fai push/commit al tuo repository originale (`diegogosmar/floor`), la fork su `floor-implementations` **NON si aggiorna automaticamente**.

## Due Scenari Possibili

### Scenario 1: Fork con Link al Repository Originale (CONSIGLIATO)

Se aggiungi solo un **README con link** al tuo repository originale:

```markdown
## Python Implementation
- **Repository**: https://github.com/diegogosmar/floor
```

**Vantaggi**:
- ✅ **Nessuna sincronizzazione necessaria** - Il link punta sempre al repo originale aggiornato
- ✅ Quando fai push a `diegogosmar/floor`, gli utenti vedono sempre la versione più recente
- ✅ Nessun lavoro di manutenzione sulla fork
- ✅ Un'unica fonte di verità (il tuo repo)

**Come funziona**:
1. Fai fork di `floor-implementations`
2. Aggiungi README con link al tuo repo
3. Fai Pull Request
4. Dopo il merge, **non devi più toccare la fork**
5. Tutti i tuoi aggiornamenti a `diegogosmar/floor` sono automaticamente visibili tramite il link

### Scenario 2: Fork con Codice Copiato (NON CONSIGLIATO)

Se copi il codice nella fork:

```bash
# Nella fork
cp -r /path/to/your/floor implementations/python-diegogosmar/
```

**Problemi**:
- ❌ Devi mantenere sincronizzato manualmente
- ❌ Ogni push al repo originale richiede un push anche alla fork
- ❌ Duplicazione del codice
- ❌ Confusione su quale sia la versione "ufficiale"

**Se scegli questa opzione, devi sincronizzare manualmente**:

```bash
# 1. Aggiorna il tuo repo originale
cd /path/to/your/floor
git push origin main

# 2. Vai alla fork e aggiorna
cd /path/to/floor-implementations
cd implementations/python-diegogosmar
git pull origin main  # Se è un submodule
# O copia manualmente i file aggiornati
```

## Raccomandazione: Usa il Link

Per `floor-implementations`, la **migliore pratica** è aggiungere solo un **README con link** al tuo repository originale.

### Struttura Consigliata

```
floor-implementations/
├── README.md                    # Lista delle implementazioni
└── implementations/
    └── python-diegogosmar/
        └── README.md            # Descrizione + link al repo originale
```

### Contenuto del README nella Fork

```markdown
# Python Floor Manager Implementation

**Repository**: https://github.com/diegogosmar/floor  
**Author**: Diego Gosmar  
**OFP Version**: 1.0.1

## Overview

[Descrizione breve]

## Quick Start

Vedi il [repository principale](https://github.com/diegogosmar/floor) per la documentazione completa.

## Features

- ✅ Full OFP 1.0.1 compliance
- ✅ Floor Manager as Convener
- ...

## Documentation

- **Main Repository**: https://github.com/diegogosmar/floor
- **Quick Start**: https://github.com/diegogosmar/floor#quick-start
```

## Workflow Consigliato

### Step 1: Aggiungi il Progetto (Una Volta)

```bash
# 1. Fork floor-implementations
# 2. Clone la tua fork
git clone https://github.com/YOUR_USERNAME/floor-implementations.git
cd floor-implementations

# 3. Crea directory e README
mkdir -p implementations/python-diegogosmar
# Copia il contenuto di docs/FLOOR_IMPLEMENTATIONS_README.md

# 4. Aggiorna README principale
# Aggiungi entry nella lista

# 5. Commit e PR
git add .
git commit -m "Add Python Floor Manager implementation"
git push origin main
# Crea Pull Request
```

### Step 2: Dopo il Merge (Nessun Altro Lavoro)

✅ **Fatto!** Non devi più toccare la fork.

Quando fai push al tuo repo originale:
```bash
cd /path/to/your/floor
git push origin main  # Solo questo!
```

Gli utenti che visitano `floor-implementations` vedranno il link al tuo repo aggiornato.

## Alternativa: Git Submodule (Avanzato)

Se il repository `floor-implementations` supporta submodules:

```bash
# Nella fork
cd floor-implementations
git submodule add https://github.com/diegogosmar/floor.git implementations/python-diegogosmar
```

**Vantaggi**:
- Link diretto al commit specifico
- Puoi aggiornare il submodule quando vuoi

**Svantaggi**:
- Devi aggiornare manualmente il submodule nella fork quando fai nuove release
- Più complesso da gestire

## Conclusione

**Raccomandazione**: Usa il **link al repository originale** nel README.

- ✅ Zero manutenzione
- ✅ Sempre aggiornato automaticamente
- ✅ Un'unica fonte di verità
- ✅ Pratica standard per repository di implementazioni

Dopo aver fatto la Pull Request iniziale, non devi più preoccuparti della sincronizzazione!

