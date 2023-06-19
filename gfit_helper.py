from __future__ import print_function

import datetime
import getopt
import json
import os.path
import sys
import time
from jproperties import Properties
import requests
import dateutil.relativedelta
from gsheets_helper import GSheetsHelper
from const import (
    SPREADSHEET_ID,
    HR_SHEET_ID,
    SLEEP_SHEET_ID,
    STRESS_SHEET_ID,
    HR_SHEET_RANGE,
    SLEEP_SHEET_RANGE,
    STRESS_SHEET_RANGE
)

os.environ['TZ'] = 'Asia/Kolkata'

gsheets_health = ""

current_date = datetime.date.today()

d_string = current_date.strftime('%Y-%m-%d')

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/fitness.activity.read',
          'https://www.googleapis.com/auth/fitness.activity.write',
          'https://www.googleapis.com/auth/fitness.blood_glucose.read',
          'https://www.googleapis.com/auth/fitness.blood_glucose.write',
          'https://www.googleapis.com/auth/fitness.blood_pressure.read',
          'https://www.googleapis.com/auth/fitness.blood_pressure.write',
          'https://www.googleapis.com/auth/fitness.body.read',
          'https://www.googleapis.com/auth/fitness.body.write',
          'https://www.googleapis.com/auth/fitness.body_temperature.read',
          'https://www.googleapis.com/auth/fitness.body_temperature.write',
          'https://www.googleapis.com/auth/fitness.heart_rate.read',
          'https://www.googleapis.com/auth/fitness.heart_rate.write',
          'https://www.googleapis.com/auth/fitness.location.read',
          'https://www.googleapis.com/auth/fitness.location.write',
          'https://www.googleapis.com/auth/fitness.nutrition.read',
          'https://www.googleapis.com/auth/fitness.nutrition.write',
          'https://www.googleapis.com/auth/fitness.oxygen_saturation.read',
          'https://www.googleapis.com/auth/fitness.oxygen_saturation.write',
          'https://www.googleapis.com/auth/fitness.reproductive_health.read',
          'https://www.googleapis.com/auth/fitness.reproductive_health.write',
          'https://www.googleapis.com/auth/fitness.sleep.read',
          'https://www.googleapis.com/auth/fitness.sleep.write'
          ]


class GFitExport:

    def __init__(self, configuration_path):
        global gsheets_health
        self.configuration_path = configuration_path
        self.credentials_path = self.configuration_path + "/credentials/credentials.json"
        # self.gsheet_properties_path = self.configuration_path + "/gsheet.properties"
        # self.gsheet_properties_map = self.load_gsheet_properties_map(
        #     self.gsheet_properties_path)
        self.SPREADSHEET_ID = SPREADSHEET_ID
        self.HR_SHEET_ID = HR_SHEET_ID
        self.SLEEP_SHEET_ID = SLEEP_SHEET_ID
        gsheets_health = GSheetsHelper(SCOPES, self.credentials_path)

    # def load_gsheet_properties_map(self, gsheet_properties_path):
    #     configs = Properties()
    #     with open(gsheet_properties_path, 'rb') as config_file:
    #         configs.load(config_file)
    #     gsheet_prop_dict = {}

    #     for config_item in configs.items():
    #         gsheet_prop_dict[config_item[0]] = config_item[1].data

    #     return gsheet_prop_dict

    def send_heart_bpm_to_gsheet(self, d_string):
        print('Below epoch times will be used for google fit apis: \nstartTimeMillis {0}\nendTimeMillis {1}'.format(
            self.get_start_time_millis(d_string), self.get_end_time_millis(d_string)))
        self.delete_any_prev_existing_data(gsheets_health, self.SPREADSHEET_ID, HR_SHEET_ID, HR_SHEET_RANGE,
                                           columns=["Date", "T1200_0100", "T0100_0200", "T0200_0300", "T0300_0400",
                                                    "T0400_0500",
                                                    "T0500_0600", "T0600_0700", "T0700_0800", "T0800_0900",
                                                    "T0900_1000", "T1000_1100", "T1100_1200", "T1200_1300",
                                                    "T1300_1400",
                                                    "T1400_1500", "T1500_1600", "T1600_1700",
                                                    "T1700_1800", "T1800_1900", "T1900_2000", "T2000_2100",
                                                    "T2100_2200",
                                                    "T2200_2300", "T2300_2359"])
        hr_data_map = self.get_heart_bpm(self.get_start_time_millis(
            d_string), self.get_end_time_millis(d_string))
        values = [
            [
                d_string, hr_data_map["00:00:00"], hr_data_map["01:00:00"], hr_data_map["02:00:00"],
                hr_data_map["03:00:00"], hr_data_map["04:00:00"], hr_data_map["05:00:00"],
                hr_data_map["06:00:00"], hr_data_map["07:00:00"], hr_data_map["08:00:00"], hr_data_map["09:00:00"],
                hr_data_map["10:00:00"], hr_data_map["11:00:00"],
                hr_data_map["12:00:00"], hr_data_map["13:00:00"], hr_data_map["14:00:00"], hr_data_map["15:00:00"],
                hr_data_map["16:00:00"], hr_data_map["17:00:00"],
                hr_data_map["18:00:00"], hr_data_map["19:00:00"], hr_data_map["20:00:00"], hr_data_map["21:00:00"],
                hr_data_map["22:00:00"], hr_data_map["23:00:00"]
            ]

        ]
        body = {
            'values': values
        }
        gsheets_health.append_row_to_sheet(
            self.SPREADSHEET_ID, HR_SHEET_RANGE, body)

    def send_sleep_to_gsheet(self, d_string):
        'Sleep!A2:G'
        self.delete_any_prev_existing_data(gsheets_health, self.SPREADSHEET_ID, SLEEP_SHEET_ID, SLEEP_SHEET_RANGE,
                                           columns=["Date", "SleepStartTime", "SleepEndTime", "Awake", "Light", "Deep",
                                                    "REM"])
        sleep_map = self.get_sleep_data(self.get_start_time_millis(
            d_string), self.get_end_time_millis(d_string))
        values = [
            [
                d_string, sleep_map[7], sleep_map[8], sleep_map[1], sleep_map[4], sleep_map[5], sleep_map[6]
            ]

        ]
        body = {
            'values': values
        }
        gsheets_health.append_row_to_sheet(
            self.SPREADSHEET_ID, SLEEP_SHEET_RANGE, body)

    def delete_any_prev_existing_data(self, gsheets_health, spreadsheet_id, sheet_id, range_name, columns):
        matching_rows = gsheets_health.get_matching_rows(
            spreadsheet_id, range_name, "Date", d_string, columns)

        for i in range(0, matching_rows.size):
            gsheets_health.delete_row_matching_row(
                spreadsheet_id, sheet_id, int(matching_rows[0]) + 1)

    def get_start_time_millis(self, d_string):
        epoch = int(time.mktime(time.strptime(
            str(d_string) + " 00:00:00", '%Y-%m-%d %H:%M:%S')))
        return epoch * 1000

    def get_end_time_millis(self, d_string):
        epoch = int(time.mktime(time.strptime(
            str(d_string) + " 23:59:59", '%Y-%m-%d %H:%M:%S')))
        return epoch * 1000

    def get_current_date(self):
        current_date = datetime.date.today()

        print("CURRENT DAY : ", current_date)
        return current_date

    def get_offset_date(self, how_many_days_behind):
        old_date = datetime.date.today() - datetime.timedelta(how_many_days_behind)

        print("OLD DATE : ", old_date)
        return old_date

    def get_heart_bpm(self, startTimeMillis, endTimeMillis):
        hr_data_map = {
            "00:00:00": 0,
            "01:00:00": 0,
            "02:00:00": 0,
            "03:00:00": 0,
            "04:00:00": 0,
            "05:00:00": 0,
            "06:00:00": 0,
            "07:00:00": 0,
            "08:00:00": 0,
            "09:00:00": 0,
            "10:00:00": 0,
            "11:00:00": 0,
            "12:00:00": 0,
            "13:00:00": 0,
            "14:00:00": 0,
            "15:00:00": 0,
            "16:00:00": 0,
            "17:00:00": 0,
            "18:00:00": 0,
            "19:00:00": 0,
            "20:00:00": 0,
            "21:00:00": 0,
            "22:00:00": 0,
            "23:00:00": 0,
        }
        response = requests.post(
            "https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate",
            headers={
                "Authorization": "Bearer " + gsheets_health.get_auth_token(),
                "content-type": "application/json",
            },

            data=json.dumps({
                "aggregateBy": [{
                    "dataTypeName": "com.google.heart_rate.bpm"
                }],
                "bucketByTime": {"durationMillis": 3600000},

                "startTimeMillis": startTimeMillis,
                "endTimeMillis": endTimeMillis
            })
        )

        json_data = (response.json()['bucket'])
        for item in json_data:
            start_date_time = datetime.datetime.fromtimestamp(
                int(item['startTimeMillis']) / 1000)
            starttime_string = start_date_time.strftime('%H:%M:%S')
            end_date_time = datetime.datetime.fromtimestamp(
                int(item['endTimeMillis']) / 1000)
            endtime_string = end_date_time.strftime('%H:%M:%S')
            for data_item in item['dataset']:
                if len(data_item['point']) > 0:
                    hrVal = int(data_item['point'][0]['value'][0]['fpVal'])
                    hr_data_map[starttime_string] = hrVal
        return hr_data_map

    def get_sleep_data(self, start_time_millis, end_time_millis):
        # just for reference
        sleep_def_map = {
            1: "Awake",
            2: "Sleep",
            3: "OutOfBed",
            4: "Light",
            5: "Deep",
            6: "REM"
        }

        # initial values are all initialized to 0
        sleep_data_map = {
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            6: 0,
            7: "",
            8: ""
        }

        response = requests.post(
            "https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate",
            headers={
                "Authorization": "Bearer " + gsheets_health.get_auth_token(),
                "content-type": "application/json",
            },
            data=json.dumps({
                "aggregateBy": [{
                    "dataTypeName": "com.google.sleep.segment"
                }],
                "startTimeMillis": start_time_millis,
                "endTimeMillis": end_time_millis
            })
        )
        json_data = (response.json()['bucket'])
        for item in json_data:
            for data_item in item['dataset']:
                i = 0
                if len(data_item['point']) > 0:

                    for eachPoint in data_item['point']:

                        dt1 = datetime.datetime.fromtimestamp(
                            int(int(eachPoint['startTimeNanos']) / 1000000000))
                        if (i == 0):
                            i = i + 1
                            sleep_start_time_epoch = dt1

                        dt2 = datetime.datetime.fromtimestamp(
                            int(int(eachPoint['endTimeNanos']) / 1000000000))  # 1977-06-07 23:44:50
                        sleep_end_time_epoch = dt2
                        rd = dateutil.relativedelta.relativedelta(dt2, dt1)

                        sleep_data_map[eachPoint['value'][0]['intVal']] = sleep_data_map[
                            eachPoint['value'][0][
                                'intVal']] + rd.minutes

                    sleep_data_map[7] = sleep_start_time_epoch.strftime(
                        '%H:%M:%S')
                    sleep_data_map[8] = sleep_end_time_epoch.strftime(
                        '%H:%M:%S')
        return sleep_data_map


def main():
    """Basic usage of the application.
    gfit_helper.py -d <date in yyyy-mm-dd format>
    """
    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv, "d:",
                                   ["date ="])
    except getopt.GetoptError:
        print('gfit_helper.py -d <date in yyyy-mm-dd format>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('gfit_helper.py -d <date in yyyy-mm-dd format>')
            sys.exit()
        elif opt in ("-d", "--date"):
            global d_string
            d_string = arg

    print('This date will be used to fetch data from google fit apis:', d_string)
    gfit_export = GFitExport("configuration/sunny")
    gfit_export.send_heart_bpm_to_gsheet(d_string)
    gfit_export.send_sleep_to_gsheet(d_string)


if __name__ == "__main__":
    main()
