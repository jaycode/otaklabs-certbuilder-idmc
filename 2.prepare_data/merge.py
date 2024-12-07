import pandas as pd

# Load the dataset
file_path = 'session_data_cleaned_and_name_corrected.csv'
df = pd.read_csv(file_path)

# Correct the filtering to match the date format in the dataset
old_data = df[df['Date'] == '11/3/2024'].copy()
new_data = df[df['Date'] == '11/24/2024'].copy()

# Rename columns to add "Old" or "New" prefix
old_data = old_data.add_prefix('Old ')
new_data = new_data.add_prefix('New ')

# Rename 'Old Name' and 'New Name' to just 'Name' for merging
old_data = old_data.rename(columns={'Old Name': 'Name'})
new_data = new_data.rename(columns={'New Name': 'Name'})

# Set 'Name' as the index for both dataframes
old_data.set_index('Name', inplace=True)
new_data.set_index('Name', inplace=True)

# Join the old and new data on 'Name'
combined_df = old_data.join(new_data, how='outer')

# Reorder the columns to group by feature ("Old ...", "New ...")
columns_order = ['Old ID', 'New ID', 'Old Date', 'Old Start Time', 'Old End Time',
                 'New Date', 'New Start Time', 'New End Time']

# Extract unique feature names excluding the "Old " or "New " prefix
features = ['ID', 'Duration', 'Mind', 'Stillness', 
            'HR (avg bpm)', 'Muse Points', 'Recoveries', 'Birds']

# Append the columns in the desired order: "Old feature", "New feature"
for feature in features:
    columns_order.append(f'Old {feature}')
    columns_order.append(f'New {feature}')

# Reorder the DataFrame
combined_df = combined_df[columns_order]

# Rename columns
combined_df.rename(columns={'Old Mind': 'Old Mind Score', 'New Mind': 'New Mind Score',
                            'Old Stillness': 'Old Stillness Score', 'New Stillness': 'New Stillness Score',
                           }, inplace=True)

# Save to CSV
combined_df.to_csv("session_data_merged.csv", index=True)
