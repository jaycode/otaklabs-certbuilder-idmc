import pandas as pd
import os
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from datetime import datetime

certificates_path = "certificates-page1"
certificates_extension = "png"
final_certificates_path = "certificates"
processed_muse_path = "Muse outputs - processed"
top_path = "top.png"
df1 = pd.read_csv("../2.prepare_data/session_data_cleaned.csv")[['ID', 'Name']]
cols ="ID,Name,Date".split(",")
df2 = pd.read_csv("../2.prepare_data/session_data_cleaned_and_name_corrected.csv")[cols]
df_images = pd.merge(df1, df2, left_on="ID", right_on="ID", suffixes=("_old", ""))
df_merged = pd.read_csv("../2.prepare_data/session_data_merged.csv")

def load_image(image_path):
    image = Image.open(image_path)
    if image is None:
        raise FileNotFoundError(f"Image at path {image_path} not found.")
    return image

# Function to calculate dimensions while retaining aspect ratio
def calculate_dimensions(img_width, img_height, max_width, max_height):
    aspect_ratio = img_width / img_height
    if img_width > max_width or img_height > max_height:
        if max_width / aspect_ratio <= max_height:
            return max_width, max_width / aspect_ratio
        else:
            return max_height * aspect_ratio, max_height
    return img_width, img_height

def create_certificate(row):
    name = row['Name'].replace(".", "").strip()
    cert_path = os.path.join(certificates_path, "{}.{}".format(name, certificates_extension))
    print("cert: {}".format(cert_path))

    # Try loading certificate image
    cert_img = None
    try:
        cert_img = load_image(cert_path)
    except:
        print("  Certificate not found")

    if cert_img:
        muse1_img = None
        muse2_img = None
        top_img = load_image(top_path)

        # Load old image
        if not df_images[df_images['ID'] == row['Old ID']].empty:
            old_name = df_images[df_images['ID'] == row['Old ID']]['Name_old'].values[0].replace(".", "")
            date_str = df_images[df_images['ID'] == row['Old ID']]['Date'].values[0]
            date_obj = datetime.strptime(date_str, "%m/%d/%Y")
            date = date_obj.strftime("%Y-%m-%d")
            muse1_path = os.path.join(processed_muse_path, "{} - {}.jpg".format(old_name, date))
            print("Old path: {}".format(muse1_path))
            muse1_img = load_image(muse1_path)

        # Load new image
        if not df_images[df_images['ID'] == row['New ID']].empty:
            old_name = df_images[df_images['ID'] == row['New ID']]['Name_old'].values[0].replace(".", "")
            date_str = df_images[df_images['ID'] == row['New ID']]['Date'].values[0]
            date_obj = datetime.strptime(date_str, "%m/%d/%Y")
            date = date_obj.strftime("%Y-%m-%d")
            muse2_path = os.path.join(processed_muse_path, "{} - {}.jpg".format(old_name, date))
            print("New path: {}".format(muse2_path))
            muse2_img = load_image(muse2_path)

        # Create a PDF
        output_pdf_path = os.path.join(final_certificates_path, "{}.pdf".format(name))
        pdf = canvas.Canvas(output_pdf_path)

        # PDF dimension notes:
        # - 0, 0 is bottom left of page.
        # - (max_width - scaled_width)/2 means centerize the image

        # Add first page (certificate)
        pdf.setPageSize(landscape(A4))

        max_width, max_height = landscape(A4)[0], landscape(A4)[1]
        img_width, img_height = cert_img.size
        scaled_width, scaled_height = calculate_dimensions(img_width, img_height, max_width, max_height)

        pdf.drawImage(cert_path, (max_width - scaled_width)/2, (max_height - scaled_height)/2, width=scaled_width, height=scaled_height)
        pdf.showPage()

        # Add second page
        second_page_max_height = A4[1]*2
        pdf.setPageSize((A4[0], second_page_max_height))

        # Top message
        max_width, max_height = A4[0], A4[1]/4
        img_width, img_height = top_img.size
        scaled_width, scaled_height = calculate_dimensions(img_width, img_height, max_width, max_height)
        pdf.drawImage(top_path, (max_width - scaled_width)/2, second_page_max_height-scaled_height, width=scaled_width, height=scaled_height)
        
        # Old Muse result
        max_width, max_height = A4[0]/2, second_page_max_height - A4[1]/4
        img_width, img_height = muse1_img.size
        scaled_width, scaled_height = calculate_dimensions(img_width, img_height, max_width, max_height)

        pdf.drawImage(muse1_path, 0, max_height-scaled_height, width=scaled_width, height=scaled_height)

        # New Muse result
        max_width, max_height = A4[0]/2, second_page_max_height - A4[1]/4
        img_width, img_height = muse2_img.size
        scaled_width, scaled_height = calculate_dimensions(img_width, img_height, max_width, max_height)

        pdf.drawImage(muse2_path, A4[0] - scaled_width, max_height-scaled_height, width=scaled_width, height=scaled_height)

        pdf.showPage()


        pdf.save()


    # print(row)
df_merged.apply(create_certificate, axis=1)