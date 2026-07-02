# Bits and Bobs

A collection of lightweight miscellaneous scripts, workflows, and tools I’ve written in in Python/R/Bash that make day to day life a bit easier. This repository is where miscellania lives. Most was created as targeted material for beginners or personal cheatsheets. Nothing is intended as a comprehensive overview.

## Available Tools
* **[extract_operon.py](./extract_operon.py)**: Makes fasta (faa/fna) files from locus tags, plus or minus the operon. Handles messy LibreOffice/Excel formatting variance automatically.
* **[alluvial_plots_from_csv.Rmd](./alluvial_plots_from_csv.Rmd)**: What it says on the tin: makes alluvial plots from a specifically formatted csv.
* **[bubbles-and-bars.Rmd](./bubbles-and-bars.Rmd)**: Generates bubble plots and bar charts from a csv file, using paleteer for colour customization.
* **[bubbles-and-bars-custom-colours.Rmd](./bubbles-and-bars-custom-colours.Rmd]**: As above, but lets you define a custom colour scheme – for example, keeping a specific organism the same colour across multiple charts.
* **[ncbi-genomes-split-by-completion.sh](./ncbi-genomes-split-by-completion.sh)**: Batch downloads genomes from NCBI and splits them based on whether they’re complete.
* **[ncbi-genomes-split-by-num-contigs.sh](./ncbi-genomes-split-by-num-contigs.sh)**: Batch downloads genomes from NCBI and splits them based on the number of contigs.
