# Project: AMR Prediction from Raw Nanopore Squiggles

## Goal
Predict Antibiotic Resistance (AMR) directly from raw Oxford Nanopore Technologies (ONT) electrical signals ("squiggles") using a 1D Convolutional Neural Network (1D-CNN). This approach bypasses the traditional base-calling step, aiming for faster and more efficient diagnostics.

## Background & Rationale
Traditional AMR detection requires sequencing (base-calling), assembly/alignment, and gene identification. This is computationally expensive and introduces latency. By classifying raw signals directly, we can potentially identify resistant strains within seconds of the read beginning, enabling "Read-Until" sequencing where non-target or non-resistant reads are ejected from the pore.

## Directory Structure
```text
/project
├── Readme.md           <- Project overview and roadmap
├── data/               <- Raw and processed Nanopore signal data (.fast5, .pod5)
├── docs/               <- Research summaries, literature reviews, and links
│   └── resources.md    <- Key papers, datasets, and technical tools
├── notebooks/          <- Experimental analysis and prototyping
└── src/                <- Production-ready source code (1D-CNN implementation)
```

## Methodology (The Roadmap)
1.  **Data Acquisition:** Sourcing raw signal data (e.g., SquiggleNet dataset, PRJEB41335).
2.  **Preprocessing:** Normalization (MAD), windowing, and signal cleaning.
3.  **Architecture:** Implementation of a 1D-CNN (ResNet-like) using PyTorch.
4.  **Training:** Optimizing the model to recognize AMR-conferring patterns in signal motifs.
5.  **Validation:** Testing against base-called ground truth and clinical susceptibility labels.

---
*Note: This project is part of the 425282 - Deep Learning course (MSc). FCUL*
