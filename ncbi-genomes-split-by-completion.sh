#!/bin/bash
# command to run: source download-and-split.sh
set -e

conda activate ncbi-data

for dir in ./*/ ; do
    # skip if it's not actually a directory
    [ -d "$dir" ] || continue
    
    cd "$dir"

    # download datasets
    datasets download genome accession --inputfile related.txt --include cds,gbff,genome,gff3,gtf,protein,rna,seq-report

    # unzip and clean up
    unzip -q ncbi_dataset.zip
    mv ncbi_dataset/data ./ncbi
    rm -rf ncbi_dataset ncbi_dataset.zip
    
    # create output folders
    mkdir -p fna fna-complete fna-incomplete

    # copy genomic fnas to a single folder
    cp ncbi/*/G*.fna fna/ 2>/dev/null || true

    # count contigs and log them
    for f in fna/*.fna; do
        [ -f "$f" ] || continue
        basename "$f" >> out.txt
        grep -c '>' "$f" >> out.txt
    done

    # Separate complete from incomplete genomes
    for f in fna/*.fna ; do
        [ -f "$f" ] || continue
        base=$(basename "$f" .fna)
        
        if grep -q "complete genome" "$f"; then
            cp "$f" fna-complete/"$base".fna
        else
            cp "$f" fna-incomplete/"$base".fna
        fi
    done

    # back up to parent directory
    cd ..
done