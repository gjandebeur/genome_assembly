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
in1 and in2 == input files
out1 and out2 == output files
unpaired 1/2 == reads that didn't fit both in1 and in2
failed == couldn't read 
-q (Phred q score) 
-l 100 == minimum length of read to be counted
-n 2 == at MAX 2 N reads (unknown nucleotide) per read without being disgarded
--cut_front / cut_tail == cut out first nucleotides/adapter 
-M 30 == cuts above only if phred score > 30.
-W 1 == reading window of one, reads one nucleotide at a time
--trim_poly_g / trim_poly_x == trim out polyG/polyX tails that may occur
--dont_eval_duplication == doesn't look for duplications to save memory (This was already done in fastQC/MultiQC steps)



### rerun FastQC on the fastp/fastplong files for post-filtered QC. 
*Same code as prior just change the input/outputs*

### Run MultiQC on both raw and filtered outputs (separate by ONT and Illumina) 

```
multiqc -n illumina_multiqc -d /example/fastQC/fastp_data/
multiqc -n nanopore_multiqc -d /example/fastQC/fastplong_data/
```

-n == the output files name
-d == the input directory


### The next part branches into two aspects: de novo assembly and reference-based assembly.

## To perform De Novo Assembly of Genome (must be on ONT data)
*use Flye program (install via conda/bioconda)*

```
for file in /example/fastplong/data/*.fastq.gz
do
    fname=$(basename "$file")
    
    flye --nano-hq "$file" \
        -g 12.3m \
        -o "/scratch/gjandebeur/Cglabrata/flye/postfilter/${fname%}_nanopore.fastq" \
        --threads 8
done
```
*Options for FLYE include:
-g == genome size expected (~12.3m for C. glabrata)
-o == output file
--threads (how many CPU you have listed)*

### Reference-Based Assembly (minimap2) 

*First for ONT data*

```
#for file in /example/rawdata/*fastq.gz
#do
#    if [ -f "$file" ]; then
#    fname=$(basename "$file" .fastq.gz)
#    echo "Processing $fname..."
#    
#    ./minimap2 -ax map-ont \
#    "/REFERENCE/FILE.fasta" \
#    "$file" > /output/ONT/${fname}.sam
#    fi
#      echo "minimap2 failed"
#done
```
for above; 
-ax map-ont == uses ONT mapping to genome 

Next minimap2 for Illumina paired reads (different syntax)

```
#for file1 in "/example/file2/illumina/*_R1_001*.fastq.gz
#do
#    if [ -f "$file1" ]; then
#        base="${file1%_R1_001*.fastq.gz}"
#        base=$(basename "$base")
#        file2="/example/file2/illumina/${base}_R2_001*.fastq.gz"
#        file2=$(ls $file2 2>/dev/null | head -1)
#        if [ -f "$file2" ]; then
#            echo "Processing paired files for sample: $base"
#            echo "R1: $(basename $file1)"
#            echo "R2: $(basename $file2)"
#            ./minimap -ax sr \
#            "/REFERENCE/FILE.fasta" \
#            "$file1" "$file2" > /output/illumina/${base}.sam
#            echo "Generated: ${base}.sam"
#        else
#            echo "Warning: R2 file not found for $file1"
#            echo "Expected: $file2"
#        fi
#        echo "---------------------------------------------"
#    fi
#done
```
for above;
-ax sr === mapping using paired reads (illumina)
both file1/file2 must be paired data (not just two similar files)

#### For both Illumina and ONT data, run the following on the output to convert to binary .BAM file and sort. Additionally, the following command will run samtools flagstat to get overall statistical data on how well mapping occurred.

```
for file in /example/input/from/minimap2/*.sam
do
    fname=$(basename "$file" .sam)
    bam="/example/output/filepath/bam/${fname}.bam"
    echo "Converting $file to sorted BAM..."
    
    # Add temp directory and memory limit
    samtools sort -T /example/temporarydirectory/forsorting/tmp/${fname} -m 2G -o "$bam" "$file" || { echo "Sort failed for $file"; continue; }
    
    samtools index "$bam"
    samtools flagstat "$bam"
    echo "Done with $fname."
    echo "---------------------------------------------"
done
for file in /example/alldata/postfilter/*.bam
do
  samtools flagstat
echo "----------------------------------------------------"

done
```

After obtaining output files with the flagstat data, as well as from the Flye assembly, you can run the code attached to this directory to pull out statistical data and place into a .xlsx file for further analyses. 
*THESE TWO FILES MENTIONED ABOVE MUST BE RUN AS PYTHON SCRIPTS* 

Now Run BCFtools to mpileup reads
```
ref_dir="/pathto/reference"
bam_dir="/path/to/postfilter/ONT/bam"
output_dir="/path/to/output/postfilter/bcfpileup/"  

echo "Starting bcf mpileup loop"

for bam_file in "$bam_dir"/*.bam
do
    if [ -f "$bam_file" ]; then
        sample=$(basename "$bam_file" .bam)
        output_file="$output_dir/${sample}.vcf.gz"
        
        # Skip if output file already exists
        if [ -f "$output_file" ]; then
            echo "Skipping $sample - output already exists: $output_file"
            continue
        fi
        
        echo "Processing sample: $sample"
        echo "BAM file: $bam_file"
        
        bcftools mpileup \
            --max-depth 1000000 \
            --threads 8 \
            -O z \
            -o "$output_file" \
            -f "$ref_dir/referencefile.fasta" \
            "$bam_file"
        
        echo "Generated: ${sample}.vcf.gz"
        echo "---------------------------------------------"
    fi
done
echo "bcftools mpileup loop completed."
```

Using the pileup files, run bcftools call for SNP analysis

