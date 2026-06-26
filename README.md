# Deutsch-Jozsa con Qiskit + IBM Quantum

Implementazione, test e esecuzione dell'algoritmo di **Deutsch-Jozsa** sia su
simulatore locale (Qiskit Aer) sia su hardware quantistico reale tramite le API
IBM Quantum (`qiskit-ibm-runtime`).

## Cos'è Deutsch-Jozsa

Data una funzione `f: {0,1}^n -> {0,1}` promessa essere **costante** oppure
**bilanciata**, l'algoritmo determina quale dei due casi vale con **una sola**
valutazione dell'oracolo (classicamente servirebbero fino a `2^(n-1)+1`
valutazioni nel caso peggiore).

Lettura del risultato — misurando gli `n` qubit di input:
- tutti `0` → funzione **costante**
- qualsiasi altro esito → funzione **bilanciata**

## Struttura

```
.
├── src/deutsch_jozsa.py   # oracoli + costruzione circuito + interpretazione
├── run_local.py           # esecuzione su simulatore Aer
├── run_ibm.py             # esecuzione su hardware IBM reale
├── tests/                 # test con pytest
├── requirements.txt
└── .env.example           # template per il token IBM
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Esecuzione sul simulatore locale

```bash
python run_local.py                       # n=3, oracolo bilanciato
python run_local.py --n 4 --oracle constant
python run_local.py --n 5 --oracle balanced --shots 2048
```

## Test

```bash
pytest -q
```

## Esecuzione su hardware IBM reale

1. Crea un account su <https://quantum.ibm.com> e copia il tuo **API token**.
2. Configura le credenziali:
   ```bash
   cp .env.example .env
   # apri .env e incolla il token in IBM_QUANTUM_TOKEN
   ```
3. Lancia:
   ```bash
   python run_ibm.py                         # backend least-busy automatico
   python run_ibm.py --n 4 --oracle constant
   python run_ibm.py --backend ibm_brisbane --shots 2048
   ```

> Su hardware reale il rumore può produrre esiti diversi da `000` anche per
> funzioni costanti: per questo `interpret_counts` usa una decisione a
> maggioranza sull'esito più frequente.

## Note

- `.env` è in `.gitignore`: **il token non viene mai committato**.
- Qiskit 1.x con primitive `SamplerV2`; transpilazione automatica per il
  backend target.
