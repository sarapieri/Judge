import json 

def count_harmful_categories(entries):
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

# Load your JSON dataset
with open('/share/users/sara.pieri/Judge/dataset.json', 'r') as file:
    data = json.load(file)
counts = count_harmful_categories(data)

sorted_dict = {key: counts[key] for key in sorted(counts)}
for k, v in sorted_dict.items():
    print(k,v)
