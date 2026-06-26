"""Algoritmo di Deutsch-Jozsa.

Data una funzione booleana f: {0,1}^n -> {0,1} promessa essere o COSTANTE
(stesso output per ogni input) o BILANCIATA (output 0 per metà degli input,
1 per l'altra metà), l'algoritmo determina quale dei due casi vale con una
sola valutazione dell'oracolo.

Lettura del risultato: misurando i primi n qubit,
    - tutti 0  -> la funzione e' COSTANTE
    - qualsiasi altro risultato -> la funzione e' BILANCIATA
"""

from __future__ import annotations

from qiskit import QuantumCircuit


def constant_oracle(n: int, output: int = 0) -> QuantumCircuit:
    """Oracolo per una funzione costante f(x) = `output` per ogni x.

    Usa n qubit di input + 1 qubit ausiliario (l'ultimo).
    """
    if output not in (0, 1):
        raise ValueError("output deve essere 0 o 1")
    oracle = QuantumCircuit(n + 1, name=f"constant({output})")
    if output == 1:
        # f(x) = 1 -> flippa sempre il qubit ausiliario
        oracle.x(n)
    return oracle


def balanced_oracle(n: int, mask: int | None = None) -> QuantumCircuit:
    """Oracolo per una funzione bilanciata.

    Implementa f(x) = (mask . x) mod 2 (prodotto interno bit a bit) che e'
    bilanciata per qualsiasi `mask` != 0. Se `mask` non e' dato, usa tutti 1.
    """
    if mask is None:
        mask = (1 << n) - 1  # tutti i bit a 1
    if not (1 <= mask <= (1 << n) - 1):
        raise ValueError("mask deve essere in [1, 2^n - 1] per essere bilanciata")

    oracle = QuantumCircuit(n + 1, name=f"balanced(0b{mask:0{n}b})")
    for qubit in range(n):
        if (mask >> qubit) & 1:
            oracle.cx(qubit, n)
    return oracle


def deutsch_jozsa_circuit(oracle: QuantumCircuit, n: int) -> QuantumCircuit:
    """Costruisce il circuito completo di Deutsch-Jozsa attorno a un oracolo.

    `oracle` deve agire su n+1 qubit (n di input + 1 ausiliario).
    """
    if oracle.num_qubits != n + 1:
        raise ValueError(
            f"l'oracolo ha {oracle.num_qubits} qubit, attesi {n + 1} (n+1)"
        )

    qc = QuantumCircuit(n + 1, n)

    # Prepara il qubit ausiliario nello stato |-> = H X |0>
    qc.x(n)
    qc.h(n)

    # Sovrapposizione uniforme sui qubit di input
    qc.h(range(n))
    qc.barrier()

    # Applica l'oracolo
    qc.compose(oracle, inplace=True)
    qc.barrier()

    # Interferenza
    qc.h(range(n))

    # Misura i qubit di input
    qc.measure(range(n), range(n))
    return qc


def interpret_counts(counts: dict[str, int]) -> str:
    """Restituisce 'constant' o 'balanced' a partire dai counts misurati.

    Decisione a maggioranza: l'esito piu' frequente. Se la stringa di bit piu'
    frequente e' tutta '0' la funzione e' costante, altrimenti bilanciata.
    """
    if not counts:
        raise ValueError("counts vuoti")
    top = max(counts, key=counts.get)
    return "constant" if set(top) == {"0"} else "balanced"
