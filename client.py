import requests

def main():
    endpoint = "http://localhost:8000/get/"
    response = requests.get(endpoint)
    print(response.json())

if __name__ == "__main__":
    main()