import pandas as pd
import glob
import json

# read in couch info from "data/couch_info.json"

df = pd.read_json("data/couch_info.json")

# Transpose the DataFrame to switch rows and columns
df = df.T

# Reset the index to turn the index into a column
df = df.reset_index(drop=True)

# Melt the DataFrame
df_melted = df.melt(var_name='variable', value_name='value')

# Create the final DataFrame
df_long = pd.DataFrame({
    'video_id': df_melted[df_melted['variable'] == 'video_id']['value'].values,
    'couch_detected': df_melted[df_melted['variable'] == 'couch_detected']['value'].values,
    'image_path': df_melted[df_melted['variable'] == 'image_path']['value'].values
})

# read in couch colour classifications from "data/couch_colour_classifications_2"
classification_files = glob.glob("data/couch_colour_classifications_2/*.json")

# Create an empty list to store the classification data
classification_data = []

# Loop through each file and read the JSON data
for file in classification_files:
    with open(file, 'r') as f:
        data = json.load(f)
        classification_data.append(data)

# Convert the list of dictionaries to a DataFrame
df_classifications = pd.DataFrame(classification_data)

# Merge the classification data with the original DataFrame
df_final = pd.merge(df_long, df_classifications, on='video_id', how='left')

print(df_final)

df_final.value_counts('couch_colour')

df_final['couch_colour'].unique()

# save the final DataFrame to a json file
df_final.to_json("data/couch_info_with_colour_classifications.json", orient='records', indent=4)

