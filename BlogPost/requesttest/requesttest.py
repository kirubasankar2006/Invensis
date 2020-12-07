import requests 

def client():
    credentials = {"username" : "Admin_Invensis", "password" : "invensis123"}

    response = requests.post("http://127.0.0.1:8000/rest-auth/login/", data =credentials)
    print("status code:", response.status_code)
    print(response.json())

if __name__=="__main__":
    client()