# canbus simulator
import logging
import asyncio
import socket
from simulator_sensor import all_sensors
from encoder import encode_can_frame
DT = 10  #samplig rate

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S'
)

async def sim_loop():
    sensor_names = ", ".join(sensor.name for sensor in all_sensors)
    logging.info(f"Starting sensor simulation, with the following sensors: {sensor_names}")    
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as can_bus:       
        while True:
            # update sensor val
            for sensor in all_sensors:
                sensor.update_sensor_val()
                logging.info(f"ID: {hex(sensor.id)} | {sensor.name}: {sensor.current_value:.2f}") # תיקון ה-typo והגבלה ל-2 ספרות אחרי הנקודה
                try:
                    frame = encode_can_frame(sensor.id, sensor.current_value)
                except Exception as e:
                    logging.error("Failed to encode message, corrupted or missing data")
                    continue
                try: 
                    can_bus.sendto(frame,("127.0.0.1", 5005))
                    logging.info(f"frame {frame} sent to bus")
                except Exception as e:
                    logging.error(f"Failed to broadcast from sensor {sensor.id}")
            await asyncio.sleep(DT)



if __name__ == "__main__":
    try:
        asyncio.run(sim_loop())
    except KeyboardInterrupt:
        logging.info("Simulator stopped.")


