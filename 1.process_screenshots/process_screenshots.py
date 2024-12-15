import cv2
import os
import pandas as pd
from process_screenshot import initialize_ocr_reader, load_image, process_screenshot



def process_images(input_dir, output_dir, csv_path='session_data.csv'):
    # Create output directories if they do not exist
    original_dir = os.path.join(output_dir, 'original')
    processed_dir = os.path.join(output_dir, 'processed')
    os.makedirs(original_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)

    reader = initialize_ocr_reader()
    csv_full_path = os.path.join(output_dir, csv_path)
    # Create DataFrame if CSV already exists, otherwise start with an empty DataFrame
    if os.path.exists(csv_full_path):
        df = pd.read_csv(csv_full_path)
    else:
        df = pd.DataFrame(columns=["Name", "Date", "Start Time", "End Time", "Duration", "Mind", "Stillness", "HR (avg bpm)", "Muse Points", "Recoveries", "Birds"])
    data_records = df.to_dict('records')

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(input_dir, filename)
            try:
                image = load_image(image_path)
                processed_image, session_data = process_screenshot(image, reader)

                # Rename and save the images with the format [Name] - [Date]
                name = session_data.get("Name", "Unknown")
                date = session_data.get("Date", "Unknown")
                new_filename = f"{name} - {date}.jpg"

                original_save_path = os.path.join(original_dir, new_filename)
                processed_save_path = os.path.join(processed_dir, new_filename)

                cv2.imwrite(original_save_path, image)
                cv2.imwrite(processed_save_path, processed_image)

                # Add data to records
                data_records.append({
                    "Name": name,
                    "Date": date,
                    "Start Time": session_data.get("Start Time"),
                    "End Time": session_data.get("End Time"),
                    "Duration": session_data.get("Session Duration"),
                    "Mind": session_data.get("Mind Score"),
                    "Stillness": session_data.get("Stillness Score"),
                    "HR (avg bpm)": session_data.get("Heart Rate"),
                    "Muse Points": session_data.get("Muse Points"),
                    "Recoveries": session_data.get("Recoveries"),
                    "Birds": session_data.get("Birds")
                })
                # Update CSV as each image is processed
                df = pd.DataFrame(data_records)
                df.to_csv(csv_full_path, index=False)
                print(f"Updated CSV with {filename}")
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    # Create DataFrame and save to CSV
    df = pd.DataFrame(data_records)
    csv_path = os.path.join(output_dir, 'session_data.csv')
    df.to_csv(csv_path, index=False)
    print(f"Data saved to {csv_full_path}")

input_directory = "Muse results - raw"
output_directory = "Muse results - output"
process_images(input_directory, output_directory)