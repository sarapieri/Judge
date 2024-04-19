import json 

def count_harmful_categories(entries):
    """
    Counts occurrences of harmful categories in a dataset.
    
    Args:
        data (list): A list of dictionaries, each representing an entry with 'harmful_category' key.
    
    Returns:
        dict: A dictionary with categories as keys and their counts as values.
    """
    # Initialize an empty dictionary to store counts of each combination
    counts = {}

    # Iterate over each entry in the list
    for entry in entries:
        # Extract the category and subcategory from the entry
        category = entry.get('harmful_category', 'Unknown Category')
        subcategory = entry.get('harmful_subcategory', 'Unknown Subcategory')
        
        # Create a unique key for each combination of category and subcategory
        key = (category, subcategory)
        
        # Increment the count for this combination in the dictionary
        if key not in counts:
            counts[key] = 1
        else:
            counts[key] += 1

    return counts

def print_formatted(counts):
    # Replace (None, None) key with ('unknown', 'unknown')
    updated_counts = {(('unknown', 'unknown') if k == (None, None) else k): v for k, v in counts.items()}

    # Sort the dictionary by keys (which are tuples)
    sorted_dict = {key: updated_counts[key] for key in sorted(updated_counts)}

    # Print all items in the sorted dictionary
    for k, v in sorted_dict.items():
        print(k, v)

# Load your JSON dataset
with open('/share/users/sara.pieri/Judge/dataset.json', 'r') as file:
    data = json.load(file)

# Initialize dictionaries to hold data for each type
data_vlguard = [entry for entry in data if 'VLGuard' in entry['id']]
data_rtvlm = [entry for entry in data if 'RTVLM' in entry['id']]
data_figstep = [entry for entry in data if 'FigStep' in entry['id']]

counts = count_harmful_categories(data)
counts_vlguard = count_harmful_categories(data_vlguard)
counts_rtvlm = count_harmful_categories(data_rtvlm)
counts_figstep = count_harmful_categories(data_figstep)

# Print the counts for each type
print("All counts:")
print_formatted(counts)
print("Counts of harmful categories for VLGuard:")
print_formatted(counts_vlguard)
print("Counts of harmful categories for RTVLM:")
print_formatted(counts_rtvlm)
print("Counts of harmful categories for FigStep:")
print_formatted(counts_figstep)