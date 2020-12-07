# Invensis
Invensis Search Engine Project

Prerequisit for the project 
  - Install python using (https://www.python.org/downloads/). 
  - Check the python installation using the command: python --version
  - Installing PIP. 
    PIP should be availabe by default. Check the pip availability using the command: pip --version
    If not then:
            a)download it using ---> curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
            b)Run it using ----> py get-pip.py
  
  - Download git 
  
All the below commands can be executed from git bash. 
Project set up:
  - create a folder Invensis_dir
  - Git bash to the project   
  - Git clone the project using command: git pull git@github.com:kirubasankar2006/Invensis.git
  
Activate the virtual environemnt
  - Go to Invensis_dir
  - Type --> python -m venv invensisvenv
    Now virtual environemnt is created
        - For windows --> .\invensisvenv\Scripts\activate
        - For linux -->  /invensisvenv/bin/acitvate

Install the packages
    - Navigate to the BlogPost folder inside the Invensis_dir
    - Type : pip install -r requirements.txt
    - If you dont see any error then all the packages are installed. 

Start the development server:
  - python manage.py runserver
    
  
  
   
 
   
   
  
