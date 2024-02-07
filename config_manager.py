import configparser
from ast import literal_eval
from datetime import datetime


class InvalidConfigurationError(Exception):
    pass


class ConfigManager:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.valve_pins = ['valve1']
        self.pumps_pins = ['pump1', 'pump2', 'pump3', 'pump4']
        self.sensors_pins = ['sensor1', 'sensor2', 'sensor3', 'sensor4']
        

    def _read_file(self):
        try:
            self.config.read('config.txt')
            if 'settings' not in self.config or not self.config.has_section('settings'):
                raise configparser.Error("Brak sekcji 'settings' w pliku konfiguracyjnym.")
        except configparser.Error as e:
            print(f"Błąd odczytu pliku konfiguracyjnego: {e}")
            self.config = configparser.ConfigParser()


    def _verify_settings_values(self):
        self._read_file()
        try:
            try:
                work_time = int(literal_eval(self.config.get('settings', 'WORK_TIME')))
                if work_time <= 0:
                    raise InvalidConfigurationError("WORK_TIME musi być liczbą dodatnią.")
            except ValueError:
                raise InvalidConfigurationError("WORK_TIME musi być liczbą.")

            try:
                valve_open_time = int(literal_eval(self.config.get('settings', 'VALVE_OPEN_TIME')))
                if valve_open_time <= 0:
                    raise InvalidConfigurationError("VALVE_OPEN_TIME musi być liczbą dodatnią.")
            except ValueError:
                raise InvalidConfigurationError("VALVE_OPEN_TIME musi być liczbą.")

            try:
                pause_time = int(literal_eval(self.config.get('settings', 'PAUSE_TIME')))
                if pause_time <= 0:
                    raise InvalidConfigurationError("PAUSE_TIME musi być liczbą dodatnią.")
            except ValueError:
                raise InvalidConfigurationError("PAUSE_TIME musi być liczbą.")

            try:
                start_time_str = self.config.get('settings', 'START_TIME')
                if not (start_time_str.isdigit() and len(start_time_str) == 4):
                    raise InvalidConfigurationError("Nieprawidłowy format dla START_TIME. Oczekiwano liczby 4-cyfrowej.")

                start_time = datetime.strptime(start_time_str, '%H%M').time()
                if not (0 <= start_time.hour < 24 and 0 <= start_time.minute < 60):
                    raise InvalidConfigurationError("Nieprawidłowy format czasu dla START_TIME. Oczekiwano HHMM.")
            except ValueError:
                raise InvalidConfigurationError("Problem z START_TIME.")

            try:
                stop_time_str = self.config.get('settings', 'STOP_TIME')
                if not (stop_time_str.isdigit() and len(stop_time_str) == 4):
                    raise InvalidConfigurationError("Nieprawidłowy format dla STOP_TIME. Oczekiwano liczby 4-cyfrowej.")

                stop_time = datetime.strptime(stop_time_str, '%H%M').time()
                if not (0 <= stop_time.hour < 24 and 0 <= stop_time.minute < 60):
                    raise InvalidConfigurationError("Nieprawidłowy format czasu dla STOP_TIME. Oczekiwano HHMM.")
            except ValueError:
                raise InvalidConfigurationError("Problem z STOP_TIME.")

            if stop_time <= start_time:
                raise InvalidConfigurationError("STOP_TIME nie może być wcześniejsze lub równe START_TIME.")

            return work_time, valve_open_time, pause_time, start_time_str, stop_time_str
        
        except (InvalidConfigurationError, ValueError) as e:
            print(f"Błąd weryfikacji konfiguracji: {e}")
            return None


    def _check_values(self, pin_names):
        results = {}

        self._read_file()

        try:
            for pin_name in pin_names:
                try:
                    pin_value = int(literal_eval(self.config.get('gpio_pins', pin_name)))
                    if pin_value <= 0:
                        raise InvalidConfigurationError(f"{pin_name} musi być liczbą dodatnią.")
                    results[pin_name] = pin_value
                except ValueError:
                     raise InvalidConfigurationError(f"{pin_name} musi być liczbą.")

            return results
        
        except (InvalidConfigurationError, ValueError) as e:
            print(f"Błąd weryfikacji konfiguracji: {e}")
            return None        


    def _verify_values(self, pins):
        return self._check_values(pins)


    def get_settings_values(self):
        values = self._verify_settings_values()
        return values if values is not None else False
    

    def get_sensors_gpio_pins_values(self):
        values = self._verify_values(self.sensors_pins)
        return values if values is not None else False


    def get_pumps_gpio_pins_values(self):
        values = self._verify_values(self.pumps_pins)
        return values if values is not None else False
    

    def get_valves_gpio_pins_values(self):
        values = self._verify_values(self.valve_pins)
        return values if values is not None else False
    

    def get_tank_gpio_pins_values(self):
        tanks = {}
        sensors = self._verify_values(self.sensors_pins)
        pumps = self._verify_values(self.pumps_pins)
        tank1 = {'pump': pumps['pump1'], 'sensor': sensors['sensor1']}
        tank2 = {'pump': pumps['pump2'], 'sensor': sensors['sensor2']}
        tank3 = {'pump': pumps['pump3'], 'sensor': sensors['sensor3']}
        tank4 = {'pump': pumps['pump4'], 'sensor': sensors['sensor4']}
        tanks['tank1'] = tank1
        tanks['tank2'] = tank2
        tanks['tank3'] = tank3
        tanks['tank4'] = tank4
        return tanks


    def set_settings_values_to_file(self, values):
        try:
            with open('config.txt', 'w') as file:
                for key, value in values.items():
                    self.config.set('settings', key, str(value))
                self.config.write(file)
        except IOError as e:
            print(f"Błąd zapisu do pliku konfiguracyjnego: {e}")



