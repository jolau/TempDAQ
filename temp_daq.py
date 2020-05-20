import time
from w1thermsensor import W1ThermSensor
import csv
import sys
from datetime import datetime
from pathlib import Path


def main(target_directory_path):
    target_directory_path.mkdir(exist_ok=True)
    current_timestamp = datetime.utcnow().strftime("%FT%H_%M_%S")

    temp_csv_filename = target_directory_path.joinpath("temp_data_" + current_timestamp + ".csv")

    with open(temp_csv_filename, 'w+', buffering=1) as temp_csv_file:
        temp_sensors = W1ThermSensor.get_available_sensors()
        temp_csv_fieldnames = ['timestamp'] + [sensor.id for sensor in temp_sensors]

        temp_csv_writer = csv.DictWriter(temp_csv_file, temp_csv_fieldnames)
        temp_csv_writer.writeheader()

        while True:
            data_dict = {'timestamp': datetime.utcnow().isoformat()}
            data_dict.update({sensor.id: sensor.get_temperature() for sensor in temp_sensors})

            print(data_dict)
            temp_csv_writer.writerow(data_dict)

            time.sleep(5)


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        sys.exit("No target directory as command line argument was given.")

    dirPath = Path(sys.argv[1])

    main(dirPath)
