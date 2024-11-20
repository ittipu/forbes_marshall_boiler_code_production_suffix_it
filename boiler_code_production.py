from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
import time

# Define global Modbus server details
MODBUS_HOST = "192.168.2.10"  # Replace with your Modbus server IP
MODBUS_PORT = 502             # Default Modbus TCP port

# Define global Modbus addresses
TEMPERATURE_ADDRESS = 4  # Replace with the register address for temperature
FLOW_ADDRESS = 5         # Replace with the register address for flow
UNIT_ID = 1              # Modbus unit ID (commonly 1)

def read_modbus_register(address, name):
    # Connect to the Modbus TCP server
    client = ModbusTcpClient(MODBUS_HOST, port=MODBUS_PORT)

    try:
        if client.connect():
            print(f"Connected to Modbus server at {MODBUS_HOST}:{MODBUS_PORT}")

            # Read a single register
            response = client.read_holding_registers(address, 2)
            if response.isError():
                print(f"Error reading {name} register at address {address}: {response}")
            else:
                # Display the register value
                print(f"{name} value at address {address}: {response.registers[0]}")
        else:
            print(f"Failed to connect to Modbus server at {MODBUS_HOST}:{MODBUS_PORT}")

    except ModbusException as e:
        print(f"Modbus exception: {e}")

    finally:
        # Close the connection
        client.close()
        print("Connection closed.")

# Main function
if __name__ == "__main__":
    # Read temperature and flow values
    while True:   
        read_modbus_register(TEMPERATURE_ADDRESS, "Steam flow kg/h")
        read_modbus_register(FLOW_ADDRESS, "Steam flow total Ton")
        time.sleep(5)

