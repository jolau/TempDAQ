from threading import Thread
from w1thermsensor import W1ThermSensor
import csv
import sys
from datetime import datetime
from pathlib import Path
import yaml
from apscheduler.schedulers.blocking import BlockingScheduler
from gpiozero import LED


def main(config_file_path):
    with open(config_file_path, 'r') as config_file:
        config_yaml = yaml.full_load(config_file)

        target_directory_path = Path(config_yaml["storage_directory"])
        interval = config_yaml["interval"]
        if config_yaml["status_led"]:
            status_led = LED(config_yaml["status_led_pin"])
            status_led.on()
        else:
            status_led = None

        sensor_names = {sensor["id"]: sensor["name"] for sensor in config_yaml["sensors"]}

    temp_csv_path = get_temp_csv_path(target_directory_path)

    with open(temp_csv_path, 'w+', buffering=1) as temp_csv_file:
        temp_sensors = W1ThermSensor.get_available_sensors()

        temp_csv_fieldnames = get_temp_dict(temp_sensors, sensor_names).keys()
        temp_csv_writer = csv.DictWriter(temp_csv_file, temp_csv_fieldnames)
        temp_csv_writer.writeheader()

        scheduler = BlockingScheduler()
        scheduler.add_job(log_temperature, 'interval', (sensor_names, temp_csv_writer, temp_sensors, status_led),
                          seconds=interval, next_run_time=datetime.now())

        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            pass


def get_temp_csv_path(target_directory_path):
    target_directory_path.mkdir(exist_ok=True)
    current_timestamp = datetime.utcnow().strftime("%FT%H_%M_%S")
    return target_directory_path.joinpath("temp_data_" + current_timestamp + ".csv")


def log_temperature(sensor_mapping, temp_csv_writer, temp_sensors, status_led=None):
    if status_led is not None:
        status_led.blink(on_time=0.1, off_time=0.1)

    data_dict = get_temp_dict(temp_sensors, sensor_mapping)
    print(data_dict)
    temp_csv_writer.writerow(data_dict)

    if status_led is not None:
        status_led.blink(on_time=1, off_time=1)


def get_temp_dict(temp_sensors, sensor_mapping):
    data_dict = {'timestamp': datetime.utcnow().isoformat()}

    temps = get_temps(temp_sensors)

    for (sensor_id, temp) in temps.items():
        # add sensor name : temperature map, take sensor.id as name if no name pair exists
        data_dict.update({sensor_mapping.get(sensor_id, sensor_id) + " [°C]": temp})

    return data_dict


def get_temps(temp_sensors):
    temps = {}

    threads = []
    for sensor in temp_sensors:
        process = Thread(target=get_temp, args=[sensor, temps])
        process.start()
        threads.append(process)
    for process in threads:
        process.join()

    return temps


def get_temp(sensor, temps):
    temps.update({sensor.id: sensor.get_temperature()})


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        sys.exit("No config file path as command line argument was given.")

    configFilePath = Path(sys.argv[1])

    main(configFilePath)
