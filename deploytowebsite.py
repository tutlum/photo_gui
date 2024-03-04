import os
import subprocess
import requests


    

def convert(config, filename):

    prefix = config['publish']['image_prefix']
    watermark = config['publish']['watermark']
    imagename=f"{prefix}_{filename}.jpg"
    command = ["convert_single.sh", filename, "1920", "upload", imagename, watermark]
    subprocess.run(command, shell=True).returncode
    return imagename

def upload(config, file):
    ftp_server = config["ftp"]["server"]
    local_file_path = file
    remote_directory = config["ftp"]["folder"]

    username = config["ftp"]["username"]
    password = config["ftp"]["password"]

    # Define the curl command for uploading the file via FTP
    curl_command = f"curl --user {username}:{password} --upload-file {local_file_path} {ftp_server}/{remote_directory}"
    print(curl_command)
    result = subprocess.run(curl_command, shell=True).returncode
    return 0 #result



def publish(config):
    # Define the URL of the PHP script
    url = config["publish"]["url"]

    # Define the parameters to be sent via POST
    params = config["publish"]["params"]

    # Define the username and password for basic authentication
    username = config["publish"]["username"]
    password = config["publish"]["password"]

    # Make a POST request to the PHP script with authentication
    response = requests.post(url, data=params, auth=(username, password))

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        return 0
    else:
        return 1

def to_website(config, last_picture):
    filepath = convert(config, last_picture)

    if (os.path.exists(filepath)):
        result = upload(config, filepath)
        if result == 0:
            print("File uploaded successfully.")
            result = publish()
            if result == 0:
                print("Published successfully.")
            else:
                print("Error publishing.")
        else:
            print("Error uploading file.")