from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, login_user, login_required, logout_user
from config_manager import ConfigManager
from config_gpio import ConfigGPIO
from user_manager import users
from hardware_control import HardwareControl
from gevent import monkey
monkey.patch_all()


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
config_manager = ConfigManager()

config_gpio = ConfigGPIO()
config_gpio.cleanup()
config_gpio.setmode()
config_gpio.setup_gpio(config_manager)

login_manager = LoginManager(app)
hardware_control = HardwareControl()

# Do usunięcia po zamontowaniu czujnika poziomu bufora
print("Opróżniam bufor przed uruchomieniem dozowania")
hardware_control.valve_control()



@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)

        if user and user.password == password:
            login_user(user)
            return redirect(url_for('main'))

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/")
@login_required
def main():
    return render_template('index.html', 
                           config_info=config_manager.get_settings_values(), 
                           sensor_values=config_gpio.get_inputs_states(config_manager), 
                           hardware_state=hardware_control.get_hardware_state()
                           )


@app.route("/edit_config", methods=['GET', 'POST'])
@login_required
def edit_config():
    if request.method == 'POST':
        config_values = {}
        work_time = request.form.get('WORK_TIME')
        valve_open_time = request.form.get('VALVE_OPEN_TIME')
        pause_time = request.form.get('PAUSE_TIME')
        start_time = request.form.get('START_TIME')
        stop_time = request.form.get('STOP_TIME')

        config_values['WORK_TIME'] = work_time
        config_values['VALVE_OPEN_TIME'] = valve_open_time
        config_values['PAUSE_TIME'] = pause_time
        config_values['START_TIME'] = start_time
        config_values['STOP_TIME'] = stop_time

        config_manager.set_settings_values_to_file(config_values)
        return redirect(url_for('main'))

    current_config = config_manager.get_settings_values()
    return render_template('edit_config.html', config_info=current_config)
    

@app.route('/start', methods=['POST'])
@login_required
def start_hardware():
    if not hardware_control.get_hardware_state():
        hardware_control.set_hardware_state(True)
        hardware_control.run_hardware()
        return redirect(url_for('main'))


@app.route('/stop', methods=['POST'])
@login_required
def stop_hardware():
    hardware_control.set_hardware_state(False)
    return redirect(url_for('main'))