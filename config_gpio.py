import RPi.GPIO as GPIO

class ConfigGPIO:
    def __init__(self):
        pass


    def setmode(self):
        GPIO.setmode(GPIO.BCM)


    def cleanup(self):
        GPIO.cleanup()


    def setup_gpio(self, config_details):
        valves_pins = config_details.get_valves_gpio_pins_values()
        pumps_pins = config_details.get_pumps_gpio_pins_values()
        sensors_pins = config_details.get_sensors_gpio_pins_values()

        for _, pin in valves_pins.items():
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH)

        for _, pin in pumps_pins.items():
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH)

        for _, pin in sensors_pins.items():
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    

    def get_inputs_states(self, config):
        input_states = {}
        for sensor, state in config.get_sensors_gpio_pins_values().items():
            input_states[sensor] = GPIO.input(state)
        return input_states
    

    def get_input_state(self, pin):
        return GPIO.input(pin)


    def set_output_state(self, state, pin):
        if state:
            GPIO.output(pin, GPIO.LOW)
        else:
            GPIO.output(pin, GPIO.HIGH)
        


