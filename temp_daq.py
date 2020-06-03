from w1thermsensor import W1ThermSensor
import csv
import sys
from datetime import datetime
from pathlib import Path
import yaml
from apscheduler.schedulers.blocking import BlockingScheduler


def main(config_file_path):
    with open(config_file_path, 'r') as config_file:
        config_yaml = yaml.full_load(config_file)

        target_directory_path = Path(config_yaml["storage_directory"])
        sensor_mapping = {sensor["id"]: sensor["name"] for sensor in config_yaml["sensors"]}

    target_directory_path.mkdir(exist_ok=True)
    current_timestamp = datetime.utcnow().strftime("%FT%H_%M_%S")
    temp_csv_filename = target_directory_path.joinpath("temp_data_" + current_timestamp + ".csv")

    with open(temp_csv_filename, 'w+', buffering=1) as temp_csv_file:
        temp_sensors = W1ThermSensor.get_available_sensors()
        temp_csv_fieldnames = get_temp_dict(temp_sensors, sensor_mapping).keys()

        temp_csv_writer = csv.DictWriter(temp_csv_file, temp_csv_fieldnames)
        temp_csv_writer.writeheader()

        scheduler = BlockingScheduler()
        scheduler.add_job(log_temperature, 'interval', (sensor_mapping, temp_csv_writer, temp_sensors), seconds=5)
        scheduler.start()


def log_temperature(sensor_mapping, temp_csv_writer, temp_sensors):
    data_dict = get_temp_dict(temp_sensors, sensor_mapping)
    print(data_dict)
    temp_csv_writer.writerow(data_dict)


def get_temp_dict(temp_sensors, sensor_mapping):
    data_dict = {'timestamp': datetime.utcnow().isoformat()}
    # add sensor name : temperature map, take sensor.id as name if no name pair exists
    data_dict.update({sensor_mapping.get(sensor.id, sensor.id): sensor.get_temperature() for sensor in temp_sensors})
    return data_dict


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        sys.exit("No config file path as command line argument was given.")

    configFilePath = Path(sys.argv[1])

    main(configFilePath)
