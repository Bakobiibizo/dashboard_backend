import os
import shutil
import zipfile
import base64

def zip_directory(path, zip_file):
    for root, dirs, files in os.walk(path):
        for file in files:
            zip_file.write(os.path.join(root, file), 
                           os.path.relpath(os.path.join(root, file), 
                                           os.path.join(path, '..')))

def create_self_extracting_script(zip_filename):
    with open(zip_filename, "rb") as zip_file:
        encoded_zip = base64.b64encode(zip_file.read()).decode()

    script = f"""
import base64
import zipfile
import os
import subprocess
import sys

def extract_and_run():
    # Decode and extract the zip file
    zip_data = base64.b64decode('{encoded_zip}')
    with open('temp.zip', 'wb') as f:
        f.write(zip_data)
    
    with zipfile.ZipFile('temp.zip', 'r') as zip_ref:
        zip_ref.extractall('app')
    
    os.remove('temp.zip')
    
    # Install dependencies
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'app/requirements.txt'])
    
    # Run the FastAPI app
    os.chdir('app')
    subprocess.check_call([sys.executable, 'api.py'])

if __name__ == '__main__':
    extract_and_run()
"""
    
    with open("run_app.py", "w") as f:
        f.write(script)

def main():
    # Create a temporary directory for bundling
    if os.path.exists("temp_bundle"):
        shutil.rmtree("temp_bundle")
    os.mkdir("temp_bundle")

    # Copy necessary files and directories
    dirs_to_copy = ['build', 'data', 'keystore', 'routes', 'static', 'templates']
    files_to_copy = ['api.py', 'requirements.txt']

    for dir_name in dirs_to_copy:
        shutil.copytree(dir_name, f"temp_bundle/{dir_name}")

    for file_name in files_to_copy:
        shutil.copy(file_name, f"temp_bundle/{file_name}")

    # Create a zip file
    with zipfile.ZipFile("app_bundle.zip", "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_directory("temp_bundle", zip_file)

    # Create the self-extracting script
    create_self_extracting_script("app_bundle.zip")

    # Clean up
    shutil.rmtree("temp_bundle")
    os.remove("app_bundle.zip")

    print("Self-extracting package created: run_app.py")

if __name__ == "__main__":
    main()