import re
import pandas as pd

filepath = "/pathto/flye_assembly_26168635_4294967294_debug.txt" #or wherever the output is with the needed statistics 

# Read the file
with open(filepath, 'r') as f:
    content = f.read()

print("Extracting assembly statistics...")

# Find all assembly statistics blocks (with tabs!)
#this findall is ai but its meant to find the YYYY-MM-DD that happens right after the block of stats we want.
stats_blocks = re.findall(r'Assembly statistics:(.*?)(?=\[\d{4}-\d{2}-\d{2}|\Z)', content, re.DOTALL)
print(f"Found {len(stats_blocks)} assembly statistics blocks")

assembly_paths = re.findall(r'Final assembly:\s+(.+?/postfilter/(2Q7TWN_\d+_mCLA4_\d+)[^/]*?/assembly\.fasta)', content)

results = []

if stats_blocks:
    for i, block in enumerate(stats_blocks):
        print(f"\n=== Sample {i+1} ===")
        print("-" * 30)
        
        # Extract stats from this block using \t for tabs
        total_length = re.search(r'Total length:\s*(\d+)', block)
        fragments = re.search(r'Fragments:\s*(\d+)', block)
        fragments_n50 = re.search(r'Fragments N50:\s*(\d+)', block)
        largest_frg = re.search(r'Largest frg:\s*(\d+)', block)
        scaffolds = re.search(r'Scaffolds:\s*(\d+)', block)
        mean_coverage = re.search(r'Mean coverage:\s*(\d+)', block)
        
      # Also get the final assembly path to identify the sample
        # final_assembly = re.search(r'postfilter/(2Q7TWN_\d+_mCLA4_\d+)[^/]*?/assembly.fasta', block)
        # sample_name = final_assembly.group(1) if final_assembly else "Unknown"
        sample_name = assembly_paths[i][1] if i < len(assembly_paths) else "Unknown"

    

        # Extract just the sample identifier (like 2Q7TWN_1_mCLA4_1)
        if sample_name.startswith('2Q7TWN'):
            sample_match = re.search(r'(2Q7TWN_\d+_mCLA4_\d+)', sample_name)
            if sample_match:
                sample_name = sample_match.group(1)
      
        print(f"Sample: {sample_name}")
        print(f"Total length: {int(total_length.group(1)):,}" if total_length else "Total length: Not found")
        print(f"Fragments: {fragments.group(1)}" if fragments else "Fragments: Not found")
        print(f"Fragments N50: {int(fragments_n50.group(1)):,}" if fragments_n50 else "Fragments N50: Not found")
        print(f"Largest frg: {int(largest_frg.group(1)):,}" if largest_frg else "Largest frg: Not found")
        print(f"Scaffolds: {scaffolds.group(1)}" if scaffolds else "Scaffolds: Not found")
        print(f"Mean coverage: {mean_coverage.group(1)}" if mean_coverage else "Mean coverage: Not found")

else:
    print("No assembly statistics found in file")



#####
results.append({
  "Sample": sample_name,
  "Total length": int(total_length.group(1)),
    "Fragments": int(fragments.group(1)),
    "Fragments N50": int(fragments_n50.group(1)),
    "Largest fragment": int(largest_frg.group(1)),
    "Scaffolds": int(scaffolds.group(1)),
    "Mean coverage": int(mean_coverage.group(1))})

###
df = pd.DataFrame(results)

csv_path = "/path/to/flye_assembly_stats.csv"
df.to_csv(csv_path, index=False)
print(f"Saved {len(df)} samples to {csv_path}")
