from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
import time
import struct
import paho.mqtt.client as mqtt
import ntplib
from datetime import datetime, timezone, timedelta


DEVICE_ID = "5018"
DEVICE_TYPE_ID = "103"

# MQTT broker details
MQTT_BROKER = "epiciotmqtt.suffixit.com"  # Replace with your MQTT broker address
MQTT_PORT = 1883
MQTT_USERNAME = "epiciot-mqtt-prod"    # Replace with your MQTT username
MQTT_PASSWORD = "Ep1cI0TMqtT@3125##"    # Replace with your MQTT password
MQTT_TOPIC = "epiciotmqttmreading" 


# Define global Modbus server details
MODBUS_HOST = "192.168.2.10"  # Replace with your Modbus server IP
MODBUS_PORT = 502             # Default Modbus TCP port

# Define global Modbus addresses
STEAM_TOTAL = 131  # Replace with the register address for temperature
STEAM_PRESS = 5         # Replace with the register address for flow
STEAM_FLOW =  15

REG_ADDRESSES = [STEAM_FLOW, STEAM_PRESS, STEAM_TOTAL]  # Replace with actual register addresses
TOTAL_OF_REG = len(REG_ADDRESSES)


modbus_client = ModbusTcpClient(MODBUS_HOST, port=MODBUS_PORT)
mqtt_client = mqtt.Client(client_id=DEVICE_ID, protocol=mqtt.MQTTv311)
mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

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
                value = (high << 16) | low  
                float_value = hex_to_float(value)
                float_value = round(float_value, 2)
                print(f"{name} value at address {address}: {float_value}")
                return float_value
        else:
            print(f"Failed to connect to Modbus server at {MODBUS_HOST}:{MODBUS_PORT}")

    except ModbusException as e:
        print(f"Modbus exception: {e}")

    finally:
        # Close the connection
        client.close()
        print("Connection closed.")


def get_ntp_datetime(ntp_server="time.google.com"):
    try:
        client = ntplib.NTPClient()
        response = client.request(ntp_server, version=3)
        ntp_time = datetime.fromtimestamp(response.tx_time, tz=timezone.utc)
        local_time = ntp_time + timedelta(hours=6)
        return local_time.strftime("%H:%M:%S %d-%m-%Y")
    
    except Exception as e:
        print(f"Error fetching NTP time: {e}")
        return None

# Publish data to MQTT
def publish_to_mqtt(client, topic, payload):
    try:
        result = client.publish(topic, payload)
        if result[0] == mqtt.MQTT_ERR_SUCCESS:
            print(f"Published to {topic}: {payload}")
        else:
            print(f"Failed to publish to {topic}")
    except Exception as e:
        print(f"MQTT exception: {e}")

def reconnect_mqtt(client, broker, port):
    """Reconnect to MQTT broker."""
    try:
        client.connect(broker, port)
        print(f"Reconnected to MQTT broker at {broker}:{port}")
    except Exception as e:
        print(f"Failed to reconnect to MQTT broker: {e}")
        time.sleep(5)  # Wait before trying to reconnect


# Main function
if __name__ == "__main__":
    while True:
        try:
            if not mqtt_client.is_connected():
                print("MQTT client is not connected. Attempting to connect...")
                reconnect_mqtt(mqtt_client, MQTT_BROKER, MQTT_PORT)
        
            values = []
            for reg_address in REG_ADDRESSES:
                value = read_modbus_register(modbus_client, reg_address)
                
                if value is not None:
                    values.append(value)  # Round to 2 decimal places
                else:
                    values.append(0)  # Placeholder for failed reads
            print(values)
            date_time = get_ntp_datetime()
            payload = f"{DEVICE_ID}|{DEVICE_TYPE_ID}|{date_time}|" + "|".join(map(str, values))
            publish_to_mqtt(mqtt_client, MQTT_TOPIC, payload)
            time.sleep(15)

        except KeyboardInterrupt:
            print("Program terminated by user.")

        except Exception as e:
            print(f"Unexpected error: {e}")

        finally:
            mqtt_client.disconnect()
            print("Connections closed.")
