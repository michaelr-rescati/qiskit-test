"""Test dell'algoritmo di Deutsch-Jozsa sul simulatore."""

import pytest
from qiskit_aer import AerSimulator

from src.deutsch_jozsa import (
    balanced_oracle,
    constant_oracle,
    deutsch_jozsa_circuit,
    interpret_counts,
)

SIM = AerSimulator()


def _run(oracle, n, shots=1024):
    qc = deutsch_jozsa_circuit(oracle, n)
    counts = SIM.run(qc, shots=shots).result().get_counts()
    return interpret_counts(counts)


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5])
@pytest.mark.parametrize("output", [0, 1])
def test_constant_oracle(n, output):
    assert _run(constant_oracle(n, output), n) == "constant"


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5])
def test_balanced_oracle_full_mask(n):
    assert _run(balanced_oracle(n), n) == "balanced"


@pytest.mark.parametrize("mask", [1, 2, 3, 5, 7])
def test_balanced_oracle_various_masks(mask):
    n = 3
    assert _run(balanced_oracle(n, mask), n) == "balanced"


def test_constant_all_zeros_outcome():
    n = 3
    qc = deutsch_jozsa_circuit(constant_oracle(n), n)
    counts = SIM.run(qc, shots=1024).result().get_counts()
    # funzione costante -> deve misurare sempre "000"
    assert set(counts.keys()) == {"0" * n}


def test_oracle_qubit_mismatch():
    with pytest.raises(ValueError):
        deutsch_jozsa_circuit(constant_oracle(3), n=2)


def test_balanced_mask_must_be_nonzero():
    with pytest.raises(ValueError):
        balanced_oracle(3, mask=0)
