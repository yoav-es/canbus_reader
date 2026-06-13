# simulation class for sensor reading
import random

#Simulator sensor class
class simSensor:
    #
    def __init__(self, name, id, cur_val, min_v, max_v, max_step):
        self.name = name 
        self.id = id
        self.current_value = cur_val
        self.min_value = min_v
        self.max_value = max_v
        self.step = max_step


    #upating sensor val
    def update_sensor_val(self):
        step_change = random.uniform(-self.step, self.step)
        new_val = self.current_value + step_change
        if new_val > self.max_value:
            self.current_value = self.max_value
        elif new_val < self.min_value:
            self.current_value = self.min_value
        else:
            self.current_value = new_val
        
    #Print representation
    def __str__(self):
        return f"{self.name}->{self.__dict__}"
    


temp_sensor = simSensor('temp_sensor', 0x10A, 22.0, 40.0, 120.0, 0.2)
rpm_sensor = simSensor('rpm_sensor', 0x110, 1200.0, 800.0, 7200.0, 150.0)
speed_sensor = simSensor('speed_sensor', 0x120, 0.0, 0.0, 180.0, 1.5)
oil_pressure = simSensor('oil_pressure', 0x130, 2.5, 0.5, 5.0, 0.05)


all_sensors = [temp_sensor, rpm_sensor, speed_sensor, oil_pressure]
# print(test_sensor1)
# print(test_sensor2)
