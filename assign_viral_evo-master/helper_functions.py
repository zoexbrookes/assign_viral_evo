import numpy as np
import matplotlib.pyplot as plt
import pandas as pd         
from Bio import SeqIO

def jukes_cantor(reference_sequence: str, distant_sequence: str) -> float:
    """The Jukes-Cantor correction for estimating genetic distances
    calculated with Hamming distance.
    Should return genetic distance with the same unit as if not corrected.

    Parameters
    ----------
    reference_sequence: str
        A string of nucleotides in a sequence used as a reference
        in an alignment with other (e.g. AGGT-GA)
    distant_sequence: str
        A string of nucleotides in a sequence after the alignment
        with a reference (e.g. AGC-AGA)

    Returns
    -------
    float
        The Jukes-Cantor corrected genetic distance using Hamming distance.
        For example 1.163.

    """
    mismatches = 0
    val_len = 0

    for c1, c2 in zip(reference_sequence, distant_sequence):
        if c1 != '-' and c2 != '-':
            val_len += 1
            if c1 != c2:
                mismatches += 1

    if val_len == 0:
        return 0.0

    p = mismatches / val_len

    if p >= 0.75:
        return float('inf')

    return -3 / 4 * np.log(1 - (4 / 3) * p)


def kimura_two_parameter(reference_sequence: str, distant_sequence: str) -> float:
    """The Kimura Two Parameter correction for estimating genetic distances
    calculated with Hamming distance.
    Should return genetic distance with the same unit as if not corrected.

    Parameters
    ----------
    reference_sequence: str
        A string of nucleotides in a sequence used as a reference
        in an alignment with other (e.g. AGGT-GA)
    distant_sequence: str
        A string of nucleotides in a sequence after the alignment
        with a reference (e.g. AGC-AGA)

    Returns
    -------
    float
        The Kimura corrected genetic distance using Hamming distance.
        For example 1.196.

    """
    raise NotImplementedError()

def plot_seqs(ref_seq: str, fasta_file: str):
    dates = []
    distances = []

    with open(fasta_file) as f:
        if "ebola" in fasta_file or "zika" in fasta_file:
            next(f)
            next(f)
        for record in SeqIO.parse(f, "fasta"):
            dates.append(record.description.split("|")[2])
            distances.append(jukes_cantor(ref_seq, str(record.seq).upper()))

    df = pd.DataFrame({"date": pd.to_datetime(dates, format = "mixed"), "dists": distances}) 
    earliest = df["date"].min()
    df["days"] = (df["date"] - earliest).dt.days

    slope, intercept = np.polyfit(df["days"], df["dists"], 1)
    gen_len = len(ref_seq)

    sars_cov_2_per_genome_per_day = slope * gen_len
    sars_cov_2_per_nt_per_day = slope
    print("gen:", sars_cov_2_per_genome_per_day, "nt:", sars_cov_2_per_nt_per_day)

    plt.scatter(df["days"], df["dists"], alpha = 0.6, label = "viral genomes")
    plt.plot(df["days"], slope * df["days"] + intercept, color = "red", label = "regression fit")
    plt.xlabel('days elapsed')
    plt.ylabel('genetic distance')
    plt.legend()

    return plt

def mismatch_helper(ref_seq: str, variants: list[str]):
    seqs = []
    with open("data/p1-sars-cov-2-variants.fasta") as f:
        for line_num, line in enumerate(f):
            for i in variants:
                if i in line:
                    seqs.append(next(f))
    
    index_mismatches = [0] * len(ref_seq)
    mismatches = 0
    for a in seqs:
        for index, (ref_nt, alt_nt) in enumerate(zip(ref_seq, a)):
            if alt_nt != ref_nt:
                mismatches += 1
                index_mismatches[index] += 1

    n = 0
    for i in index_mismatches:
        index_mismatches[n] = i / len(variants)
        n += 1

    return mismatches, index_mismatches
