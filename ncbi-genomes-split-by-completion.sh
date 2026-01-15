#!/bin/bash
#command to run: source download-and-split.sh
set -e

conda activate ncbi-data

for dir in ./*/ ;
do
cd "$dir"

datasets download genome accession --inputfile related.txt --include cds,gbff,genome,gff3,gtf,protein,rna,seq-report

unzip ncbi_dataset.zip
mv ncbi_dataset/data ./ncbi
rm -rf ncbi_dataset 
rm ncbi_dataset.zip
mkdir fna fna-complete fna-incomplete

#copy genomic fnas to a single folder

cp ncbi/*/G*.fna fna/

#output the number of contigs in each file

for f in fna/*.fna
do
awk '{cmd=sprintf("basename %s",FILENAME);cmd | getline out; print FILENAME,out; exit}' "$f"
grep -o '>' "$f" | wc -l
done >>out.txt

#copy files with less than 7 contigs to a complete folder and the rest to incomplete
for f in fna/*.fna ;
do
base=$(basename "$f" .fna)
if [ "$( grep -c "complete genome" "$f" )" -gt 0 ]
then
cp "$f" fna-complete/"$base".fna
else
cp "$f" fna-incomplete/"$base".fna
fi
done

cd ..
done
