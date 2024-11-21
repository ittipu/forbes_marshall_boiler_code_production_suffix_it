from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
import time
import struct

# Define global Modbus server details
MODBUS_HOST = "192.168.2.10"  # Replace with your Modbus server IP
MODBUS_PORT = 502             # Default Modbus TCP port

# Define global Modbus addresses
STEAM_TOTAL = 130  # Replace with the register address for temperature
STEAM_PRESS = 5         # Replace with the register address for flow
STEAM_FLOW =  15
UNIT_ID = 1              # Modbus unit ID (commonly 1)


def hex_to_float(value):
    """Convert a 32-bit integer to a float."""
    try:
        return struct.unpack('>f', struct.pack('>I', int(value)))[0]
    except (TypeError, ValueError, struct.error) as e:
        print(f"Error converting value {value} to float: {e}")
        return 0.0  # Return a default value if conversion fails



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
                high, low = response.registers
                print("response registers: {}".format(response.registers))
                print("high: {}".format(high))
                print("low: {}".format(low))
                if address == STEAM_TOTAL:
                    value = (low << 16) | high  
                    float_value = hex_to_float(value)
                    float_value = round(float_value, 2)
                else:
                    value = (high << 16) | low  
                    float_value = hex_to_float(value)
                    float_value = round(float_value, 2)

                print(f"{name} value at address {address}: {float_value}")
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
        read_modbus_register(STEAM_FLOW, "Steam flow kg/h")
        time.sleep(1)  
        read_modbus_register(STEAM_TOTAL, "Total Steam kg")
        time.sleep(1)
        read_modbus_register(STEAM_PRESS, "Steam Press Bar(g)")
        time.sleep(5)

