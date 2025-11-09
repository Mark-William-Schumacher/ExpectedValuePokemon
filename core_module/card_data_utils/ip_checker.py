import requests


def get_public_ip():
    try:
        # Fetch IPv6 address
        response_ipv6 = requests.get('https://api64.ipify.org?format=json')
        # Fetch IPv4 address
        response_ipv4 = requests.get('https://api.ipify.org?format=json')

        if response_ipv6.status_code == 200 and response_ipv4.status_code == 200:
            ipv6 = response_ipv6.json().get('ip')
            ipv4 = response_ipv4.json().get('ip')
            return ipv4, ipv6
        else:
            return (
                f"Error: Unable to fetch IPv4. Status Code: {response_ipv4.status_code}",
                f"Error: Unable to fetch IPv6. Status Code: {response_ipv6.status_code}",
            )
    except Exception as e:
        return f"Error: {e}", f"Error: {e}"


# Example Usage
ipv4, ipv6 = get_public_ip()
print(f"Your public IPv4 address is: {ipv4}")
print(f"Your public IPv6 address is: {ipv6}")
