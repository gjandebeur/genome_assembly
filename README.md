# genome_assembly library prep through SNP analyses

full pipeline for genome assembly (de novo &amp; reference-based)

library prep for assembly (fastQC, fastp/fastplong, minimap2/flye)

### First obtain .fastq file and run through fastQC for initial QC checks on the raw data

```
for loop to perform fastQC
for file in /example/directory/*.fastq.gz
do
    fastqc "$file" --threads 8 --outdir /example/output/fastQC/
done
```

### Run fastplong on long-read data (ONT) and fastp on short-read (Illumina)
```
for file in /example/directory/*.fastq.gz
do
    fname=$(basename "$file")
    
    fastplong \
          -i "$file" \
          -o "/example/output/$sample_trim.fastq.gz" \
          --disable_adapter_trimming \
          -q 15 -l 30 -n 0 \
          --cut_front --cut_tail -M 20 -W 4 \
          --trim_poly_x \
          --json "/output/${sample}_fastplong.json" \
          --html "/output/${sample}_fastplong.html" \
          --thread 8 

	echo "$sample finished"
done
```

### Run fastp for short-read data (complicated because PAIRED analysis)

```
for file in /example/rawdata/directory/*.fastq.gz
do
    fname=$(basename "$file")
    sample=${fname%_R1_001.fastq.gz}
    
    r1_file="/example/file/one.fastq.gz"
    r2_file="/example/file/two.fastq.gz"
    
    if [[ -f "$r1_file" && -f "$r2_file" ]]; then
        echo "Processing sample: $sample"    
        fastp \
              --in1 "$r1_file" \
              --in2 "$r2_file" \
              --out1 "/example/output/one_clean.fastq.gz" \
              --out2 "/example/output/two_clean.fastq.gz"  \
              --unpaired1 example/one.unpaired.fastq \
              --unpaired2 example/two.unpaired.fastq \
              --failed_out /example/failedreads/$sample.fastq \
              -q 30 -l 100 -n 2 -e 30 --cut_front --cut_tail -M 30 -W 1 \
              --trim_poly_g \
              --trim_poly_x \
              --dont_eval_duplication \
              --json "/example/report/${sample}_fastp.json" \
              --html "/example/report/${sample}_fastp.html" \
              --thread 8 \
    else
        echo "Warning: Missing R1 or R2 file for sample $sample"
    fi
done
```
