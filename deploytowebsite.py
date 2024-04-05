import os
import subprocess
import requests
import logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)


    

def convert(config, filename):

    prefix = config['publish']['image_prefix']
    watermark = config['publish']['watermark']
    imagename=f"{prefix}_{os.path.basename(filename)}"
    script= os.path.join(os.getcwd(), 'convert_single.sh')
    target= os.path.join(os.getcwd(), 'upload')
    wm= os.path.join(os.getcwd(), watermark)
    command = ["bash", script, filename, "1920", target, imagename, wm]
    logging.info(command)
    result = subprocess.run(command, capture_output=True, text=True)
    logging.info("Output:", str(result.stdout))
    logging.info("Error:", str(result.stderr))
    return os.path.join(target, imagename)

def upload(config, file):
    ftp_server = config["ftp"]["server"]
    local_file_path = file
    remote_directory = config["ftp"]["folder"]
    remote = f"{ftp_server}/{remote_directory}"
    logging.info(remote)

    username = config["ftp"]["username"]
    password = config["ftp"]["password"]

    # Define the curl command for uploading the file via FTP
    curl_command = f"curl --user '{username}:{password}' --upload-file '{local_file_path}' '{remote}'"
    logging.info(curl_command)
    result = subprocess.run(curl_command, shell=True).returncode
    logging.info("upload: ", result)
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
    # logging.info(response.content)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        return 0
    else:
        return 1

def to_website(config, last_picture):
    logging.info("start deploy ...")
    filepath = convert(config, last_picture)
    if (os.path.exists(filepath)):
        result = upload(config, filepath)
        if result == 0:
            logging.info("File uploaded successfully.")
            result = publish(config)
            if result == 0:
                logging.info("Published successfully.")
            else:
                logging.error("Error publishing.")
        else:
            logging.error("Error uploading file.")
