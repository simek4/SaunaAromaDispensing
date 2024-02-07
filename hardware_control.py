from config_gpio import ConfigGPIO
from config_manager import ConfigManager
import time
from gevent import spawn
import datetime


class HardwareControl:
    def __init__(self):
        self.running = False
        self.config_manager = ConfigManager()
        self.config_gpio = ConfigGPIO()
        self.loop_pause = 5


    def get_hardware_state(self):
        return self.running
    

    def set_hardware_state(self, state):
        self.running = state


    def valve_control(self):
        valves_pins = self.config_manager.get_valves_gpio_pins_values()
        for _, pin in valves_pins.items():
            print("ZAWÓR OTWARTY")
            self.config_gpio.set_output_state(True, pin)
        valve_open_time = self.config_manager.get_settings_values()[1]
        print("OPRÓŻNIAM BUFOR")
        time.sleep(valve_open_time)
        for _, pin in valves_pins.items():
            print("ZAWÓR ZAMKNIĘTY")
            self.config_gpio.set_output_state(False, pin)
        

    def check_scheduler(self):
        settings = self.config_manager.get_settings_values()
        start_time = datetime.datetime.strptime(settings[3], '%H%M').time()
        stop_time = datetime.datetime.strptime(settings[4], '%H%M').time()
        current_time = datetime.datetime.now().time()
        if start_time <= current_time < stop_time:
            print("Włączony według harmonogramu")
            return True
        else:
            print("Wyłączony według harmonogramu")
            return False


    def fill_reservoir(self, sensor, pump):
        start_work_time = time.time()
        work_time = self.config_manager.get_settings_values()[0]
        while (time.time() - start_work_time) < work_time:
            if not self.read_sensor(sensor):
                print("NAPEŁNIANIE BUFORA")
                self.config_gpio.set_output_state(True, pump)
            else:
                print("NISKI POZIOM CIECZY")
                break
            time.sleep(1)
        print("KONIEC NAPEŁNIANIA BUFORA")
        self.config_gpio.set_output_state(False, pump)


    def read_sensor(self, pin):
        print("SPRAWDZANIE POZIOMU")
        print(self.config_gpio.get_input_state(pin))
        return self.config_gpio.get_input_state(pin)


    def main(self):
        while self.running:
            if self.check_scheduler():
                for tank, tank_details in self.config_manager.get_tank_gpio_pins_values().items():
                    print("ZBIORNIK:", tank)
                    if not self.running:
                        print("DOZOWANIE WYŁĄCZONE")
                        break
                    if not self.read_sensor(tank_details['sensor']):
                        print("POZIOM OK!")
                        self.fill_reservoir(tank_details['sensor'], tank_details['pump'])
                        self.valve_control()
                    print("PRZERWA!")
                    time.sleep(self.config_manager.get_settings_values()[2]) # Pause time
            time.sleep(self.loop_pause)


    def run_hardware(self):
        spawn(self.main)


