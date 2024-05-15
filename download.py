import os
import csv
import logging
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import zipfile

def setup_logging(log_file):
    logging.basicConfig(filename=log_file, level=logging.ERROR,
                        format='%(asctime)s - %(levelname)s - %(message)s')

def extract_zip(zip_file, extract_to):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def download_from_drive(drive, file_id, filename):
    file_obj = drive.CreateFile({'id': file_id})
    file_obj.GetContentFile(filename)

def extract_drive_links(csv_file, download_dir, extract_dir, log_file):
    setup_logging(log_file)
    
    # Authenticate and create GoogleDrive instance
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)

    with open(csv_file, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row_number, row in enumerate(csv_reader, start=1):
            nim = row['NIM']
            nama = row['Nama']
            drive_link = row['Drive']
            try:
                # Extract file ID from Google Drive link
                file_id = drive_link.split('=')[-1]
                
                # Construct filename
                filename = os.path.join(download_dir, f"{nim}_{nama.replace(' ', '_')}.zip")
                
                # Download the file from Google Drive
                download_from_drive(drive, file_id, filename)
                print(f"Downloaded: {filename}")
                
                # Create directory for extraction
                extract_folder = os.path.join(extract_dir, os.path.splitext(os.path.basename(filename))[0])
                os.makedirs(extract_folder, exist_ok=True)
                
                # Extract ZIP file into the created folder
                extract_zip(filename, extract_folder)
                print(f"Extracted: {filename} to {extract_folder}")
            except Exception as e:
                error_message = f"Error occurred in CSV line {row_number}: {e}"
                print(error_message)
                logging.error(error_message)

# Define directories for downloading and extracting files
download_directory = 'downloads'
extract_directory = 'extracted'
log_file = 'error.log'

# Create directories if they don't exist
os.makedirs(download_directory, exist_ok=True)
os.makedirs(extract_directory, exist_ok=True)

# Replace 'input.csv' with the path to your CSV file
extract_drive_links('input.csv', download_directory, extract_directory, log_file)

