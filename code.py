import json
import pandas as pd
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
import time

SOURCE_1_SENSOR_ADDRESS = 17  
SOURCE_2_SENSOR_ADDRESS = 18  

def read_input(address):
    try:
        result = client.read_holding_registers(address, 1)
        return result.registers[0]
    except ModbusException as e:
        print(f"Error reading input at address {address}: {e}")
        return None

def write_output(address, value):
    try:
        result = client.write_register(address, value)
        print(f"Successfully wrote {value} to address {address}")
    except ModbusException as e:
        print(f"Error writing output at address {address}: {e}")

def detect_generated_source():
    source_1_status = read_input(SOURCE_1_SENSOR_ADDRESS)
    source_2_status = read_input(SOURCE_2_SENSOR_ADDRESS)

    if source_1_status == 1:
        print("Detected item generated at Source 1...")
        return 1
    #elif source_2_status == 1:
    #    print("Detected item generated at Source 2...")
    #    return 2
    else:
        return None
    
def move_crane(x, y):
    write_output(1, x)  
    write_output(2, y) 
    print(f"Moving crane to position X: {x}, Y: {y}")

def execute_commands_from_json(json_file):
    try:
        source = detect_generated_source()
        
        if source is None:
            print("No item detected at either source.")
            return  
        
        with open(json_file, 'r') as file:
            data = json.load(file)

        for action in data['actions']:
            if 'setX' in action and 'setY' in action:
                move_crane(action['setX'], action['setY'])
                wait_for_crane_to_arrive(action['setX'], action['setY'])

            if 'vacuum' in action:
                control_vacuum(action['vacuum'])
                time.sleep(1)  

        print("All JSON commands executed.")
    
    except Exception as e:
        print(f"Error during JSON command execution: {e}")

def wait_for_crane_to_arrive(target_x, target_y):
    while True:
        crane_atX = read_input(15)  
        crane_atY = read_input(16)  
        if crane_atX == target_x and crane_atY == target_y:
            print(f"Crane arrived at X: {target_x}, Y: {target_y}")
            break
        else:
            print(f"Crane is moving... Current X: {crane_atX}, Y: {crane_atY}")
        time.sleep(0.5)  

def control_vacuum(state):
    write_output(3, state)
    if state == 1:
        vacuum_state = "ON" 
    else:
        vacuum_state = "OFF"
    print(f"Vacuum is now {vacuum_state}")

if __name__ == "__main__":
    try:
        client = ModbusTcpClient('127.0.0.1')
        client.connect()
        json_file = r"C:\Users\nkill\Desktop\Mohmmad Hammoud's Work\Programming for Automation\Project\crane_commands.json"
        execute_commands_from_json(json_file)

    except ModbusException as e:
        print(f"Modbus error: {e}")
    finally:
        client.close()
        print("Modbus client closed.")
