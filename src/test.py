import os
import pandas as pd
import json

# Directory containing the files
directory = 'data/couch_colour_classifications'

# List to hold all data
data_list = []

# Iterate over all files in the directory
for filename in os.listdir(directory):
    if filename.endswith('.json'):  # Assuming the files are in JSON format
        with open(os.path.join(directory, filename), 'r') as file:
            data = json.load(file)
            data_list.append(data)

# Create a DataFrame from the list of dictionaries
df = pd.DataFrame(data_list)

# Display the DataFrame
print(df)

# make couch_colour column lowercase
df['couch_colour'] = df['couch_colour'].str.lower()

# replace gray with grey at any point in the string
df['couch_colour'] = df['couch_colour'].str.replace('gray', 'grey')


# count couch_colour, sort by count
print(df['couch_colour'].value_counts())


# distinct couch_colours
print(df['couch_colour'].unique())