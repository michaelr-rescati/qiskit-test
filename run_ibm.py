"""Esegue Deutsch-Jozsa su hardware quantistico reale IBM.

Richiede un token IBM Quantum in un file `.env` (vedi .env.example).

Esempi:
    python run_ibm.py                                  # n=3, bilanciato, backend least-busy
    python run_ibm.py --n 4 --oracle constant
    python run_ibm.py --backend ibm_brisbane --shots 2048
"""

import argparse
import os

from dotenv import load_dotenv
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

from src.deutsch_jozsa import (
    balanced_oracle,
    constant_oracle,
    deutsch_jozsa_circuit,
    interpret_counts,
)


def get_service() -> QiskitRuntimeService:
    """Crea il service IBM dal token nel file .env."""
    load_dotenv()
    token = os.getenv("IBM_QUANTUM_TOKEN")
    if not token or token == "your_token_here":
        raise SystemExit(
            "Token IBM mancante. Copia .env.example in .env e inserisci "
            "IBM_QUANTUM_TOKEN."
        )
    channel = os.getenv("IBM_CHANNEL", "ibm_quantum_platform")
    instance = os.getenv("IBM_INSTANCE") or None
    return QiskitRuntimeService(channel=channel, token=token, instance=instance)


def main() -> None:
    parser = argparse.ArgumentParser(description="Deutsch-Jozsa su hardware IBM")
    parser.add_argument("--n", type=int, default=3, help="numero di qubit di input")
    parser.add_argument(
        "--oracle", choices=["constant", "balanced"], default="balanced"
    )
    parser.add_argument("--shots", type=int, default=1024)
    parser.add_argument(
        "--backend",
        default=None,
        help="nome del backend; se omesso usa il least-busy disponibile",
    )
    args = parser.parse_args()

    service = get_service()

    if args.backend:
        backend = service.backend(args.backend)
    else:
        backend = service.least_busy(operational=True, simulator=False)
    print(f"Backend selezionato: {backend.name}")

    oracle = (
        constant_oracle(args.n)
        if args.oracle == "constant"
        else balanced_oracle(args.n)
    )
    qc = deutsch_jozsa_circuit(oracle, args.n)

    # Transpilazione per il backend reale
    pm = generate_preset_pass_manager(optimization_level=1, backend=backend)
    isa_circuit = pm.run(qc)

    sampler = Sampler(mode=backend)
    print(f"Invio job (oracolo reale: {args.oracle}, shots={args.shots})...")
    job = sampler.run([isa_circuit], shots=args.shots)
    print(f"Job ID: {job.job_id()}  -- in attesa dei risultati...")

    result = job.result()
    counts = result[0].data.c.get_counts()

    verdict = interpret_counts(counts)
    print(f"\nCounts: {counts}")
    print(f"Verdetto: {verdict.upper()}")
    print("✅ Corretto" if verdict == args.oracle else "❌ Errato (rumore hardware?)")


if __name__ == "__main__":
    main()
