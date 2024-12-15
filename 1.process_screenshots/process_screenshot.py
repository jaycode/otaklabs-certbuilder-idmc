import cv2
import easyocr
from PIL import Image
import re
from datetime import datetime
import numpy as np
import pdb

# Load the image
image_path = "Screenshot_(meryati)2024-12-03-21-38-08-43.jpg"
image_path = "Screenshot_2024-12-03-21-42-44-79.jpg"
image_path = "Screenshot_2024-12-06-08-25-39-88.jpg"
image_path = "Screenshot_2024-12-03-21-47-40-07.jpg"

def load_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Image at path {image_path} not found.")
    return image

def crop_image(image):
    return image[100:, :]

def initialize_ocr_reader():
    return easyocr.Reader(['en'])

def define_regions(image):
    if image.shape[0] > 5000:
        # With powerbands
        return {
            # "Date": (50, 0, 1025, 900),
            # "Mind Score": (50, 925, 1025, 2700),
            # "Stillness Score": (50, 2675, 1025, 3250),
            # "Heart Rate": (50, 3420, 1025, 4000),
            # "Stats": (50, 4300, 1025, 5050),
            "Name": (0, 5050, 1025, -1),
        }
    else:
        # Without powerbands
        return {
            "Date": (50, 0, 1025, 900),
            "Mind Score": (50, 925, 1025, 1700),
            "Stillness Score": (50, 1675, 1025, 2250),
            "Heart Rate": (50, 2420, 1025, 3000),
            "Stats": (50, 3300, 1025, 4050),
            "Name": (0, 4050, 1025, -1),
        }

def extract_text_from_regions(cropped_image, reader, regions):
    extracted_text = ""
    for region_name, (x1, y1, x2, y2) in regions.items():
        # Adjust y2 if set to -1 to use the full image height
        if y2 == -1:
            y2 = cropped_image.shape[0]

        try:
            # Save each region image for debugging purposes
            region_path = f"debug_regions/debug_{region_name.replace(' ', '_').lower()}.jpg"
            region = cropped_image[y1:y2, x1:x2]
            region = cv2.resize(region, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
            cv2.imwrite(region_path, region)
            region_text_details = reader.readtext(region, detail=1)  # Extract text using EasyOCR with details
        except:
            region_text_details = ""

        # Combine text fragments that are close in proximity to create complete lines
        lines = []
        current_line = []
        current_y = None
        line_threshold = 15*4  # Maximum vertical distance to consider text on the same line

        for bbox, text, _ in region_text_details:
            _, (_, top_left_y), _, _ = bbox  # Get the y-coordinate of the top left of the bounding box

            if current_y is None:
                current_y = top_left_y
                current_line.append(text)
            else:
                if abs(top_left_y - current_y) <= line_threshold:
                    current_line.append(text)
                else:
                    lines.append(" ".join(current_line))
                    current_line = [text]
                    current_y = top_left_y

        # Add the last line if any
        if current_line:
            lines.append(" ".join(current_line))

        # Combine all detected lines for this region
        region_text = "\n".join(lines)
        extracted_text += f"\n{region_name} Region:\n{region_text}\n"

    return extracted_text

def find_percent(line):
    index = line.find("%")
    score_str = line[max(0, index-3):index]
    score_numeric = re.sub(r'\D', '', score_str.replace('Z', '7').replace('O', '0').replace('I', '1'))
    return int(score_numeric)/100

def extract_information(text):
    print(text)
    lines = text.split('\n')
    data = {
        "Mind Score": None,
        "Stillness Score": None,
        "Heart Rate": None,
        "Muse Points": None,
        "Recoveries": None,
        "Birds": None,
        "Name": None,
        "Date": None,
        "Start Time": None,
        "End Time": None,
        "Session Duration": None
    }

    # Extract time and duration using regex
    time_pattern = re.compile(r'\b([0-9ZOI]{1,2}[:.][0-9ZOI]{2}(?:am|pm)?)\b', re.IGNORECASE)
    duration_pattern = re.compile(r'\b([0-9ZOI]+m(?: \d+s)?)\b', re.IGNORECASE)
    times = time_pattern.findall(text)
    durations = duration_pattern.findall(text)
    date_pattern = re.compile(r'([A-Za-z]+\s*\d{1,2},\s*\d{4})', re.IGNORECASE)
    name_pattern = re.compile(r'\b(?:AM|PM)\s+(.+)', re.IGNORECASE)
    heart_rate_pattern = re.compile(r'Heart Rate\s*@*\s*(\d+)\s*bpm', re.IGNORECASE)
    stats_pattern = re.compile(r'muse points.*?recoveries.*?birds', re.IGNORECASE)

    if len(times) >= 2:
        data["Start Time"] = times[0].replace('Z', '7').replace('O', '0').replace('I', '1').replace('.', ':')
        data["End Time"] = times[1].replace('Z', '7').replace('O', '0').replace('I', '1').replace('.', ':')
    if durations:
        corrected_duration = durations[0]
        # Replace common OCR mistakes
        corrected_duration = corrected_duration.replace('Z', '7').replace('O', '0').replace('I', '1')
        data["Session Duration"] = corrected_duration

    # Extract other values
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if "%" in line and "Mind" in line:
            data["Mind Score"] = find_percent(line)
        elif "%" in line and "Still" in line:
            data["Stillness Score"] = find_percent(line)
        elif re.search(heart_rate_pattern, line):
            match = re.search(heart_rate_pattern, line)
            if match:
                data["Heart Rate"] = match.group(1)
        elif re.search(stats_pattern, line):
            previous_line_index = lines.index(line) - 1
            while previous_line_index >= 0:
                previous_line = lines[previous_line_index].strip()
                if previous_line:
                    numbers = re.findall(r'\d+', previous_line)
                    if len(numbers) >= 3:
                        data["Muse Points"] = numbers[0].replace('Z', '7').replace('O', '0').replace('I', '1')
                        data["Recoveries"] = numbers[1].replace('Z', '7').replace('O', '0').replace('I', '1')
                        data["Birds"] = numbers[2].replace('Z', '7').replace('O', '0').replace('I', '1')
                    break
                previous_line_index -= 1
        elif re.search(date_pattern, line):
            date_str = line.strip().replace(',', ', ')
            date_obj = datetime.strptime(date_str, '%b %d, %Y')
            data["Date"] = date_obj.strftime('%Y-%m-%d')
        elif re.search(name_pattern, line):
            name_match = name_pattern.search(line)
            if name_match:
                data["Name"] = name_match.group(1).strip()

    return data

def overlay_image(base_cv2_image, top_cv2_image, position=(0, 0)):
    # Convert OpenCV images (BGR) to PIL (RGB)
    base_pil = Image.fromarray(cv2.cvtColor(base_cv2_image, cv2.COLOR_BGR2RGB)).convert("RGBA")
    top_pil = Image.fromarray(cv2.cvtColor(top_cv2_image, cv2.COLOR_BGR2RGB)).convert("RGBA")

    # Paste top image onto base image at specified position
    base_pil.paste(top_pil, position, top_pil)

    # Convert to CV2 compatible image
    processed_image = cv2.cvtColor(np.array(base_pil.convert("RGB")), cv2.COLOR_RGB2BGR)

    return processed_image

def add_gamma(image):
    if image.shape[0] > 5000:
        # w/ powerbands
        return overlay_image(image, cv2.imread('gamma.png'), (215, 1355))
    else:
        # w/o powerbands
        return image

def process_screenshot(image, reader):
    regions = define_regions(image)
    cropped_image = crop_image(image)
    processed_image = add_gamma(cropped_image)
    extracted_text = extract_text_from_regions(processed_image, reader, regions)
    session_data = extract_information(extracted_text)
    return processed_image, session_data

# Extract and print the data
reader = initialize_ocr_reader()
image = load_image(image_path)
processed_image, session_data = process_screenshot(image, reader)
cv2.imwrite('processed_sample.jpg', processed_image)

for key, value in session_data.items():
    print(f"{key}: {value}")

# This script will save the cropped image, extract text using OCR, and parse the required information.
