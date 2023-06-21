import requests
import pandas as pd

# Function to run the API call and return data
def get_data(api_key, org_id, timespan, api_path):
    url = f"https://api.meraki.com/api/v1/organizations/{org_id}/summary/{api_path}?timespan={timespan}"

    headers = {
        'X-Cisco-Meraki-API-Key': api_key,
        'Content-Type': 'application/json'
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception("Request failed: " + response.text)

    return response.json()

# Ask for user input
api_key = input("Enter your Meraki API key: ")
org_id = input("Enter your Meraki organization ID: ")
days = int(input("For how many past days would you like to run the report for? (31 days is a maximum) "))

# Convert days to seconds
timespan_var = days * 86400

# Get the appliance data
appliance_data = get_data(api_key, org_id, timespan_var, 'top/appliances/byUtilization')

# Prepare data for .csv
network_names = []
average_utilizations = []

for item in appliance_data:
    network_names.append(item['network']['name'])
    average_utilizations.append(item['utilization']['average']['percentage'])

df_appliances = pd.DataFrame({
    'Security appliance': network_names,
    'Average device utilization(%)': average_utilizations
})

# Save to .csv
df_appliances.to_csv('topappliancesbyutilization.csv', index=False)

print("Appliance data saved to 'topappliancesbyutilization.csv'")

# Get the device data
device_data = get_data(api_key, org_id, timespan_var, 'top/devices/byUsage')

# Prepare data for .csv
device_names = []
device_models = []
client_totals = []
usage_totals = []
usage_percentages = []

for item in device_data:
    device_name = item['name'] if item['name'] else item['mac']
    device_names.append(device_name)
    device_models.append(item['model'])
    client_totals.append(item['clients']['counts']['total'])
    usage_totals.append(item['usage']['total'])
    usage_percentages.append(item['usage']['percentage'])

df_devices = pd.DataFrame({
    'Name': device_names,
    'Model': device_models,
    '# Clients': client_totals,
    'Usage (kB)': usage_totals,
    '% Usage': usage_percentages
})

# Save to .csv
df_devices.to_csv('topdevices.csv', index=False)

print("Device data saved to 'topdevices.csv'")

# Get the device model data
model_data = get_data(api_key, org_id, timespan_var, 'top/devices/models/byUsage')

# Prepare data for .csv
model_names = []
model_counts = []
model_usage_totals = []

for item in model_data:
    model_names.append(item['model'])
    model_counts.append(item['count'])
    model_usage_totals.append(item['usage']['total'])

df_models = pd.DataFrame({
    'Model': model_names,
    '# Devices': model_counts,
    'Usage (MB)': model_usage_totals
})

# Save to .csv
df_models.to_csv('Topdevicemodelsbyusage.csv', index=False)

print("Device model data saved to 'Topdevicemodelsbyusage.csv'")

# Function to get client details
def get_client_details(api_key, org_id, mac_address):
    url = f"https://api.meraki.com/api/v1/organizations/{org_id}/clients/search?mac={mac_address}"

    headers = {
        'X-Cisco-Meraki-API-Key': api_key,
        'Content-Type': 'application/json'
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise Exception("Request failed: " + response.text)
    
    return response.json()

# Get the client data
client_data = get_data(api_key, org_id, timespan_var, 'top/clients/byUsage')

# Prepare data for .csv
client_names = []
data_received = []
data_sent = []
mac_addresses = []

for item in client_data:
    client_names.append(item['name'])
    data_received.append(item['usage']['downstream'])
    data_sent.append(item['usage']['upstream'])
    mac_addresses.append(item['mac'])

df_clients = pd.DataFrame({
    'Description': client_names,
    'Data Received (MB)': data_received,
    'Data Sent (MB)': data_sent,
    'Mac Address': mac_addresses
})

# Save to .csv
df_clients.to_csv('Topclientsbyusage.csv', index=False)

print("Client data saved to 'Topclientsbyusage.csv'")

# Load the data from CSV
df_clients = pd.read_csv('Topclientsbyusage.csv')

# Create new columns for manufacturer and os
df_clients['Device Manufacturer'] = ""
df_clients['Operating System'] = ""

# Iterate over the dataframe and enrich the data
for index, row in df_clients.iterrows():
    # Get detailed client information
    detailed_info = get_client_details(api_key, org_id, row['Mac Address'])
    
    # If there are records for this client
    if detailed_info['records']:
        record = detailed_info['records'][0] # let's use the first record for now

        # Update manufacturer and os
        df_clients.at[index, 'Device Manufacturer'] = detailed_info['manufacturer']
        df_clients.at[index, 'Operating System'] = record['os']

# Save to .csv again
df_clients.to_csv('Topclientsbyusage.csv', index=False)

print("Client data updated and saved again to 'Topclientsbyusage.csv'")

# Get the manufacturers data
manufacturers_data = get_data(api_key, org_id, timespan_var, 'top/clients/manufacturers/byUsage')

# Prepare data for .csv
manufacturer_names = []
client_counts = []
data_received_manu = []
data_sent_manu = []

for item in manufacturers_data:
    manufacturer_names.append(item['name'])
    client_counts.append(item['clients']['counts']['total'])
    data_received_manu.append(item['usage']['downstream'])
    data_sent_manu.append(item['usage']['upstream'])

df_manufacturers = pd.DataFrame({
    'Manufacturer': manufacturer_names,
    '# Clients': client_counts,
    'Data Received (MB)': data_received_manu,
    'Data Sent (MB)': data_sent_manu
})

# Save to .csv
df_manufacturers.to_csv('Topmanufacturersbyusage.csv', index=False)

print("Manufacturer data saved to 'Topmanufacturersbyusage.csv'")
