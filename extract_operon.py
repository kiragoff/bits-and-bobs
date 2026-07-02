#!/usr/bin/env python3
import os
import sys
import argparse
import pandas as pd
from Bio import SeqIO

# First things first, make sure it's executable:
#   chmod +x extract_operon.py
# 1) Extract operon from single gene (default pulls entire operon, both .ffn and .faa):
#   ./extract_operon.py PBUTOS_00001
# 2) Process a batch list from a text file (one locus tag per line):
#   ./extract_operon.py my_genes.txt --type both --outdir ./extracted_operons/
# 3) Extract JUST the specific gene(s), skipping the rest of the operon:
#   ./extract_operon.py PBUTOS_00001 --mode gene
# 4) Other options:
#   --type [both/aa/na]; for selectioning output options
#

# File paths
CSV_PATH = "/mnt/work-drive/kira/peri-final-genomes/operons.csv"
FFN_PATH = "/mnt/work-drive/kira/peri-final-genomes/peri.polished.ffn"
FAA_PATH = "/mnt/work-drive/kira/peri-final-genomes/peri.polished.faa"

def parse_input_genes(input_arg):
    if os.path.isfile(input_arg):
        with open(input_arg, 'r') as f:
            genes = [line.strip() for line in f if line.strip()]
        print(f"Loaded {len(genes)} genes from file.")
        return genes, True
    return [input_arg.strip()], False

def get_operon_maps(target_genes, csv_path, is_file_input, input_filename, outdir, mode):
    if not os.path.exists(csv_path):
        sys.exit(f"File not found: {csv_path}")
        
    # delimiter variance, because who knows what LibreOffice/Excel did this time 
    with open(csv_path, 'r') as f:
        first_line = f.readline()
    sep = ',' if (',' in first_line and '\t' not in first_line) else r'\s+'
    
    df = pd.read_csv(csv_path, sep=sep, quotechar='"')
    df.columns = df.columns.str.strip().str.replace('"', '').str.replace("'", "")
    
    if 'locus_tag' not in df.columns or 'operon' not in df.columns:
        sys.exit(f"Error: Missing columns. Found: {list(df.columns)}")
        
    # clean quotes/whitespace from data strings
    for col in ['locus_tag', 'operon']:
        df[col] = df[col].astype(str).str.strip().str.replace('"', '').str.replace("'", "")
    
    operon_counts = df['operon'].value_counts().to_dict()
    gene_to_operon_map = dict(zip(df['locus_tag'], df['operon']))
    
    matched_df = df[df['locus_tag'].isin(target_genes)]
    if matched_df.empty:
        sys.exit("None of the input genes were found in the annotation mapping.")
        
    unique_operons = matched_df['operon'].unique()
    operon_dictionary = {}
    
    if mode == "gene":
        # isolate the target gene(s) without pulling the rest of the operon
        for gene in matched_df['locus_tag'].unique():
            operon_dictionary[gene] = {gene}
    else:
        # pull all genes sharing an operon ID with the target gene(s)
        for op in unique_operons:
            if op in ['-', 'NA', 'nan']:
                isolated = matched_df[matched_df['operon'] == op]['locus_tag'].tolist()
                for gene in isolated:
                    operon_dictionary[gene] = {gene}
            else:
                operon_dictionary[op] = set(df[df['operon'] == op]['locus_tag'].tolist())
            
    if is_file_input:
        base = os.path.splitext(os.path.basename(input_filename))[0]
        suffix = "_gene_summary.txt" if mode == "gene" else "_summary.txt"
        summary_path = os.path.join(outdir, f"{base}{suffix}")
        
        all_genes = set().union(*operon_dictionary.values())
        
        with open(summary_path, 'w') as sf:
            sf.write("locus_tag\toperon\tno_genes\n")
            for gene in target_genes:
                op = gene_to_operon_map.get(gene, "NOT_FOUND")
                count = operon_counts.get(op, 0) if op != "NOT_FOUND" else 0
                sf.write(f"{gene}\t{op}\t{count}\n")
            
            sf.write(f"\n\nno_genes_extracted: {len(all_genes)}\n")
            sf.write(f"no_groups_extracted: {len(operon_dictionary)}\n")
        print(f"Summary written to: {summary_path}")
        
    return operon_dictionary

def extract_sequences(fasta_path, operon_dict, ext, outdir):
    if not os.path.exists(fasta_path):
        return

    handles = {op: open(os.path.join(outdir, f"operon_{op}.{ext}"), "w") for op in operon_dict}
    counts = {op: 0 for op in operon_dict}

    with open(fasta_path, "r") as f:
        for record in SeqIO.parse(f, "fasta"):
            seq_id = record.id.split()[0]
            for op, allowed_tags in operon_dict.items():
                if seq_id in allowed_tags:
                    SeqIO.write(record, handles[op], "fasta")
                    counts[op] += 1

    for op, h in handles.items():
        h.close()
        if counts[op] > 0:
            print(f"Extracted {counts[op]} sequences to operon_{op}.{ext}")

def main():
    parser = argparse.ArgumentParser(description="Extract target genes/operon from genome files.")
    parser.add_argument("gene_input", help="Locus tag or text file with list of locus tags.")
    parser.add_argument("--mode", choices=["operon", "gene"], default="operon")
    parser.add_argument("--type", choices=["na", "aa", "both"], default="both")
    parser.add_argument("--outdir", default=".")
    args = parser.parse_args()
    
    os.makedirs(args.outdir, exist_ok=True)
    
    genes, is_file = parse_input_genes(args.gene_input)
    operon_dict = get_operon_maps(genes, CSV_PATH, is_file, args.gene_input, args.outdir, args.mode)
    
    if args.type in ["na", "both"]:
        extract_sequences(FFN_PATH, operon_dict, "ffn", args.outdir)
    if args.type in ["aa", "both"]:
        extract_sequences(FAA_PATH, operon_dict, "faa", args.outdir)

if __name__ == "__main__":
    main()