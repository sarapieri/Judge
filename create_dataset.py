import json
import os
import imghdr
import pandas as pd 

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

def verify_image_exists(image_path):
    # Check if the file exists
    # print(image_path)
    if not os.path.exists(image_path):
        return False
    return True

def save_to_json_file(content, file_path, mode):
    """
    Saves the given content to a JSON file.

    Parameters:
    content (list): A list of entries to be saved.
    file_path (str): The path to the file where the content will be saved.
    """
    with open(file_path, mode) as file:
        json.dump(content, file, indent=4)
    print(f"Saved {file_path}\nEntries {len(content)}")
    
def create_entry_VLGuard(ids, entry, safe_prompt, safe_comb, idx_response, prompt_type, data_type): 

    set_origin  = 'train' if 'train' in data_type else 'test'
    new_entry_safe = {}
    new_entry_safe['id'] = data_type + str(ids)
    new_entry_safe['old_id'] = entry['id']
    image_path = 'VLGuard/' + set_origin + '/' + entry['image'] 
    new_entry_safe['image'] = image_path
    assert verify_image_exists(image_path)
    new_entry_safe['safe_image'] = entry['safe']

    if entry['safe'] == True:
        assert 'harmful_category' not in entry, "Safe images should not have a harmful category."
    else:
        assert 'harmful_category' in entry, "Unsafe images must have a harmful category."

    # set category 
    new_entry_safe['harmful_category'] = entry['harmful_category'] if 'harmful_category' in entry else None

    # set subcategory and remove 'disinformation' for ads 
    if 'harmful_category' in entry and entry['harmful_subcategory']  == 'disinformation': 
        new_entry_safe['harmful_subcategory'] = 'ads'

    else: 
        new_entry_safe['harmful_subcategory'] = entry['harmful_subcategory'] if 'harmful_category' in entry else None

    new_entry_safe['safe_prompt'] = safe_prompt
    new_entry_safe['safe_in_combination'] = safe_comb

    new_entry_safe['prompt'] = entry['instr-resp'][idx_response][prompt_type] 
    new_entry_safe['safe_reply'] = entry['instr-resp'][idx_response]['response']

    new_entry_safe['unsafe_reply']= None
    new_entry_safe['text_in_image']= None

    return new_entry_safe

def create_entry_RTVLM(ids, old_id, image, safe, harmful_category, harmful_subcategory, safe_prompt, safe_comb, prompt, safe_reply, unsafe_reply, text_in_image, data_type): 
    # Safe text
    new_entry_safe = {}
    new_entry_safe['id'] = data_type + str(ids)
    new_entry_safe['old_id'] = old_id
    new_entry_safe['image'] = image 
    new_entry_safe['safe_image'] = safe 

    new_entry_safe['harmful_category'] = harmful_category 
    new_entry_safe['harmful_subcategory'] = harmful_subcategory 

    new_entry_safe['safe_prompt'] = safe_prompt
    new_entry_safe['safe_in_combination'] = safe_comb

    new_entry_safe['prompt'] = prompt 
    new_entry_safe['safe_reply'] = safe_reply 

    new_entry_safe['unsafe_reply']= unsafe_reply
    new_entry_safe['text_in_image']= text_in_image

    return new_entry_safe

def open_json(path):
    # Load the JSON file
    with open(path, 'r') as file:
        data = json.load(file)
    return data

def open_jsonl(path):
    import json

    # Initialize an empty dictionary to store the JSON objects
    data = []
    # Open the .jsonl file and read line by line
    with open(path, 'r') as file:
        for index, line in enumerate(file):
            json_obj = json.loads(line.strip())
            data.append(json_obj)
    return data

def add_data_VLGuard(json_path, id_start = 0, data_type = 'VLGuard_train_'):
    data_out = []

    # Load the JSON file
    data = open_json(json_path)

    ids = 0 + id_start
    print(f"Id start", id_start)
    # Scan each entry
    for i, entry in enumerate(data):
        # No empty fields
        for key, value in entry.items():
            assert value != "" or value != None

        # unsafe
        if not entry['safe']:
            assert len(entry['instr-resp']) == 1
            # ids, entry, safe_prompt, safe_comb, idx_response, prompt_type, data_type)
            new_entry_unsafe_image = create_entry_VLGuard(ids, entry, None, False, 0, 'instruction', data_type)
            ids += 1 
            data_out.append(new_entry_unsafe_image)

        # safe   
        else:
            assert len(entry['instr-resp']) == 2
            # ids, entry, safe_prompt, safe_comb, idx_response, prompt_type, data_type)
            new_entry_unsafe_text = create_entry_VLGuard(ids, entry, False, False, 1, 'unsafe_instruction', data_type)
            ids += 1 
            data_out.append(new_entry_unsafe_text)

            new_entry_safe_text = create_entry_VLGuard(ids, entry, True, True, 0, 'safe_instruction', data_type)
            ids += 1
            data_out.append(new_entry_safe_text)

    return data_out

def add_data_RTVLM(id_start = 0, data_type = 'RTVLM_'):
    data_out = []
    json_paths = ['/share/users/sara.pieri/Judge/RedTeamingVLM/data/Captcha/captcha.jsonl', \
                '/share/users/sara.pieri/Judge/RedTeamingVLM/data/Jailbreak2/jailbreak.jsonl', \
                '/share/users/sara.pieri/Judge/RedTeamingVLM/data/Safety/Politics/politics.jsonl', \
                '/share/users/sara.pieri/Judge/RedTeamingVLM/data/Safety/Racial/racial.jsonl',\
                '/share/users/sara.pieri/Judge/RedTeamingVLM/data/Harmful/harmful.jsonl' ]
    
    ids = 0 + id_start
    print(f"Id start", id_start)
    
    for json_path in json_paths:
        data = open_jsonl(json_path)
        # Scan each entry
        for i, entry in enumerate(data):
            # No empty fields
            for key, value in entry.items():
                # print(key, value)
                assert value != "" or value != None

            if 'captcha' in json_path:
                image = 'RedTeamingVLM/data/Captcha/img/' + str(entry['id']) + '.jpg'
                assert verify_image_exists(image)
                old_id = 'Captcha_' + str(entry['id'])
                safe_image = True
                harmful_category= 'safety'
                harmful_subcategory= 'captcha'
                safe_prompt = False 
                safe_comb = False 
                prompt = entry['instruction']
                safe_reply = None
                unsafe_reply= entry['answer']
                text_in_image= True
                new_entry_unsafe_image = create_entry_RTVLM(ids, old_id, image, safe_image, harmful_category, harmful_subcategory, safe_prompt, safe_comb, prompt, safe_reply, unsafe_reply, text_in_image, data_type + 'Captcha_' )
                ids += 1 
                data_out.append(new_entry_unsafe_image)

            elif 'jailbreak' in json_path:
                image = 'RedTeamingVLM/data/Jailbreak/img/' + str(entry['index']) + '.jpg'
                assert verify_image_exists(image)
                old_id = 'Jailbreak_' + str(entry['index'])
                safe_image = False
                harmful_category= 'safety'
                harmful_subcategory= 'jailbreak'
                safe_prompt = True
                safe_comb = False 
                prompt = None
                safe_reply = None
                unsafe_reply= None
                text_in_image= True
                new_entry_unsafe_image = create_entry_RTVLM(ids, old_id, image, safe_image, harmful_category, harmful_subcategory, safe_prompt, safe_comb, prompt, safe_reply, unsafe_reply, text_in_image, data_type + 'Jailbreak_')
                ids += 1 
                data_out.append(new_entry_unsafe_image)

            elif 'politics' in json_path:
                image = 'RedTeamingVLM/data/Safety/Politics/img/' + str(entry['id'])
                assert verify_image_exists(image)
                old_id = 'Politics_' + str(entry['id'])
                safe_image = True
                harmful_category= 'risky behavior'
                harmful_subcategory= 'political'
                safe_prompt = True
                safe_comb = False 
                prompt = entry['prompt']
                safe_reply = None
                unsafe_reply= None
                text_in_image= None
                new_entry_unsafe_image = create_entry_RTVLM(ids, old_id, image, safe_image, harmful_category, harmful_subcategory, safe_prompt, safe_comb, prompt, safe_reply, unsafe_reply, text_in_image, data_type + 'Politics_')
                ids += 1 
                data_out.append(new_entry_unsafe_image)

            elif 'racial' in json_path:
                image = 'RedTeamingVLM/data/Safety/Racial/img/' + str(entry['id'])
                assert verify_image_exists(image)
                old_id = 'Racial_' + str(entry['id'])
                safe_image = True
                harmful_category= 'discrimination'
                harmful_subcategory= 'race'
                safe_prompt = True
                safe_comb = False 
                prompt = entry['prompt']
                safe_reply = None
                unsafe_reply= None
                text_in_image= None
                new_entry_unsafe_image = create_entry_RTVLM(ids, old_id, image, safe_image, harmful_category, harmful_subcategory, safe_prompt, safe_comb, prompt, safe_reply, unsafe_reply, text_in_image, data_type + 'Racial_')
                ids += 1 
                data_out.append(new_entry_unsafe_image)

            elif 'harmful' in json_path:
                prompts = entry['questions']
                for j, question in enumerate(prompts): 
                    
                    image = 'RedTeamingVLM/data/Harmful/img/' + str(entry['index']) + '.jpg'
                    assert verify_image_exists(image)
                    old_id = 'Harmful_' + str(entry['index'])
                    safe_image = True
                    harmful_category= 'deception'
                    harmful_subcategory= 'disinformation'
                    safe_prompt = True
                    safe_comb = False 
                    prompt = question
                    safe_reply = entry['answers'][j]
                    unsafe_reply= None
                    text_in_image= None
                    new_entry_unsafe_image = create_entry_RTVLM(ids, old_id, image, safe_image, harmful_category, harmful_subcategory, safe_prompt, safe_comb, prompt, safe_reply, unsafe_reply, text_in_image, data_type + 'Racial_')
                    ids += 1 
                    data_out.append(new_entry_unsafe_image)            

    return data_out

def add_data_FigStep(id_start = 0, data_type = 'FigStep_'):
    data_out = []
    img_path = 'FigStep/data/images/SafeBench-Tiny/'
    csv_path = '/share/users/sara.pieri/Judge/FigStep/data/question/SafeBench-Tiny.csv'
    data = pd.read_csv(csv_path)
    ids = 0 + id_start
    print(f"Id start", id_start)
    for index, row in data.iterrows():
        image = img_path + 'query_ForbidQI_' + str(row['category_id']) + '_' + str(row['task_id']) + '_6.png'
        assert verify_image_exists(image)
        old_id = 'FigStep_' + str(index)
        safe_image = False
        harmful_category= 'safety'
        harmful_subcategory= 'jailbreak'
        safe_prompt = None
        safe_comb = False 
        prompt = None
        safe_reply = None
        unsafe_reply= None
        text_in_image= True
        new_entry_unsafe_image = create_entry_RTVLM(ids, old_id, image, safe_image, harmful_category, harmful_subcategory, safe_prompt, safe_comb, prompt, safe_reply, unsafe_reply, text_in_image, data_type)
        
        ids += 1
        data_out.append(new_entry_unsafe_image)
        # Access fields using row['field_name']
        # print(f"Row {index}: ForbidQI={row['dataset']}, Category ID={row['category_id']}, Task ID={row['task_id']}, Instruction={row['instruction']}")
    return data_out

json_path_train = "/share/users/sara.pieri/Judge/VLGuard/train.json"
json_path_test = "/share/users/sara.pieri/Judge/VLGuard/test.json" 
out_json = "/share/users/sara.pieri/Judge/dataset.json"

data_train_VLGuard = add_data_VLGuard(json_path_train)
data_test_VLGuard = add_data_VLGuard(json_path_test, id_start = 0, data_type = 'VLGuard_test_') # len(data_train_VLGuard),
data_rtvlm = add_data_RTVLM(id_start = 0, data_type = 'RTVLM_') # len(data_train_VLGuard) + len(data_test_VLGuard) 
data_figstep = add_data_FigStep(id_start = len(data_train_VLGuard) + len(data_test_VLGuard) + len(data_rtvlm), data_type = 'FigStep_') 

combined = data_train_VLGuard + data_test_VLGuard + data_rtvlm + data_figstep
# combined = data_rtvlm 
counts = count_harmful_categories(combined) 
print(counts)
# sorted_dict = {key: counts[key] for key in sorted(counts)}
# for k, v in sorted_dict.items():
#     print(k,v)
    
save_to_json_file(combined, out_json, 'w')
