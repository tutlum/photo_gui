from jinja2 import Template
import os


def list_images_in_folder(folder_path):
    # Initialize an empty list to store image paths
    image_paths = []

    # List all files in the folder
    for filename in os.listdir(folder_path):
        # Get the full file path
        file_path = os.path.join(folder_path, filename)
        # Check if the file is a regular file and has an image extension
        if os.path.isfile(file_path) and any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']):
            # Append the file path to the list
            image_paths.append(file_path)

    return image_paths

def fill_template(template="template/template.html", title="Fotos einer Veranstaltung"):
    # Read the template file
    with open(template) as file:
        template_str = file.read()

    # Create a Jinja2 template object
    template = Template(template_str)

    images=list_images_in_folder("gallery")
    # Data to fill in the template
    data = {
        'title': title,
        'images': images
    }

    # Render the template with the data
    filled_template = template.render(data)

    # Print or save the filled template
    # print(filled_template)

    if not os.path.isdir('static_site'):
        os.mkdir('static_site')

    # If you want to save it to a file
    with open('static_site/index.html', 'w') as file:
        file.write(filled_template)

if __name__=="__main__":
    fill_template()