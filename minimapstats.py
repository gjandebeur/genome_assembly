import re
import pandas as pd


# Read the log file
with open("/pathto/minimap2_output.txt", "r") as f:
    content = f.read()

# Stats we want to collect
stat_names = [
    'total_reads', 'secondary', 'supplementary', 'duplicates', 'mapped', 
    'paired_in_sequencing', 'read1', 'read2', 'properly_paired', 'mismatch_paired'
]

# Corresponding regex patterns for each stat
patterns = [
    r'(\d+) \+ \d+ in total',
    r'(\d+) \+ \d+ secondary',
    r'(\d+) \+ \d+ supplementary',
    r'(\d+) \+ \d+ duplicates',
    r'(\d+) \+ \d+ mapped',
    r'(\d+) \+ \d+ paired in sequencing',
    r'(\d+) \+ \d+ read1',
    r'(\d+) \+ \d+ read2',
    r'(\d+) \+ \d+ properly paired',
    r'(\d+) \+ \d+ with itself and mate mapped'
]

# these are both set but they will be used for diff purposes
all_data = [] #this will be the final data frame
current_block = [] #this is just to collect the lines for EACH sample running
###
lines = content.split("\n")  #splits into lines so it can search each line

#this extracts the sample id 
for line in lines:  # loops
    line = line.strip()  # removes any spaces at start/end for each line
    
    if line.startswith("Done with"):  # grabs if starts w done with.
        sample_id = line.split()[2].rstrip(".") 
        # splits each word (Done, with, $sample) and also removes the period after the sample name
        # using [2] here because in python index (0,1,2) we want 3rd word which is 2

        block_text = "\n".join(current_block)  # combines all lines but uses \n between each

        stats = []  # just another list placeholder for the search function, this for the data
        for pat in patterns:  # the variables we want to find
            m = re.search(pat, block_text)
            stats.append(int(m.group(1)) if m else "Not found")  # makes integer and takes first captured value

        # Store results
        all_data.append([sample_id] + stats)  # combines the headers w the found data into 1 place

        # Reset current block for next sample
        current_block = []

    else:
        current_block.append(line)  #

print(all_data)
# Save to CSV
df = pd.DataFrame(list(all_data), columns=["sample_id"] + stat_names)

csv_filename = "/outputfile/minimap2_stats_update.csv"
df.to_csv(csv_filename, index=False)

print("Data saved to minimap2_stats.csv")
