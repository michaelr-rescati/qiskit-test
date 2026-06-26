"""Esegue Deutsch-Jozsa sul simulatore locale (Qiskit Aer).

Esempi:
    python run_local.py                      # n=3, oracolo bilanciato
    python run_local.py --n 4 --oracle constant
    python run_local.py --n 5 --oracle balanced --shots 2048
"""

import argparse

from qiskit_aer import AerSimulator

from src.deutsch_jozsa import (
    balanced_oracle,
    constant_oracle,
    deutsch_jozsa_circuit,
    interpret_counts,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Deutsch-Jozsa su simulatore locale")
    parser.add_argument("--n", type=int, default=3, help="numero di qubit di input")
    parser.add_argument(
        "--oracle",
        choices=["constant", "balanced"],
        default="balanced",
        help="tipo di oracolo da testare",
    )
    parser.add_argument("--shots", type=int, default=1024)
    args = parser.parse_args()

    oracle = (
        constant_oracle(args.n)
        if args.oracle == "constant"
        else balanced_oracle(args.n)
    )
    qc = deutsch_jozsa_circuit(oracle, args.n)

    print(f"Oracolo reale: {args.oracle}  (n={args.n}, shots={args.shots})")
    print(qc.draw(output="text"))

    sim = AerSimulator()
    result = sim.run(qc, shots=args.shots).result()
    counts = result.get_counts()

    verdict = interpret_counts(counts)
    print(f"\nCounts: {counts}")
    print(f"Verdetto: {verdict.upper()}")
    print("✅ Corretto" if verdict == args.oracle else "❌ Errato")


if __name__ == "__main__":
    main()
