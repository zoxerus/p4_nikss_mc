import json
import requests




def send_data(url, payload, headers={'Content-Type': 'application/json'}):
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print(response.text)


def send_delay(delay, url = "http://192.168.30.37:8080/Delay"):  # Sends delay/jitter measurements to the Telemetry Agent
    
    send_data(url, delay)

# Sends delay/jitter measurements to the Telemetry Agent


def send_traffic(traffic, url = "http://192.168.30.74:8080/Traffic"):  # Sends traffic to the Multi-Flow Agent
    # url = "http://192.168.30.74:8080/Traffic"

    send_data(url, traffic)


def main():
    choices = {'1': send_delay, '2': send_traffic}
    while True:
        print("\n+------------------------------+")
        print("|  1. Send Delay               |")
        print("|  2. Send Traffic             |")
        print("|  3. Exit                     |")
        print("+------------------------------+")
        choice = input("Enter your choice (1-3): ")
        print("\n")

        if choice in choices:
            choices[choice]()  # Call the function based on choice
        elif choice == "3":
            print("Exiting the program...")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 3.")


if __name__ == "__main__":
    main()
