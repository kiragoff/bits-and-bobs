#!/bin/bash
# command to run: source download-and-split.sh
set -e

conda activate ncbi-data

for dir in ./*/ ; do
    # Skip if it's not a real directory
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

    # count contigs and log them to out.txt
    for f in fna/*.fna; do
        [ -f "$f" ] || continue
        basename "$f" >> out.txt
        grep -c '>' "$f" >> out.txt
    done

    # Separate genomes based on contig count (less than 8)
    for f in fna/*.fna ; do
        [ -f "$f" ] || continue
        base=$(basename "$f" .fna)
        
        # Get the total count of '>' headers
        contigs=$(grep -c '>' "$f")
        
        if [ "$contigs" -lt 8 ]; then
            cp "$f" fna-complete/"$base".fna
        else
            cp "$f" fna-incomplete/"$base".fna
        fi
    done

    # back up to parent directory
    cd ..
done