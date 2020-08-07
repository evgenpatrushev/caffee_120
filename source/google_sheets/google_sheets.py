import os
import json
import string
import httplib2
import pandas as pd
from googleapiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))


class GoogleSheets:
    # Имя файла с закрытым ключом, вы должны подставить свое
    CREDENTIALS_FILE = os.getenv("CREDENTIALS_FILE",
                                 os.path.join(THIS_FOLDER, 'config/pythonsheetscoffee-285613-c935d679e55c.json'))

    # Читаем ключи из файла
    if os.getenv('HEROKU'):
        CREDENTIALS_FILE = json.loads(CREDENTIALS_FILE)
        credentials = \
            ServiceAccountCredentials._from_parsed_json_keyfile(CREDENTIALS_FILE,
                                                                ['https://www.googleapis.com/auth/spreadsheets',
                                                                 'https://www.googleapis.com/auth/drive'])
    else:
        credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                                       ['https://www.googleapis.com/auth/spreadsheets',
                                                                        'https://www.googleapis.com/auth/drive'])

    httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
    service = discovery.build('sheets', 'v4', credentials=credentials)
    spreadsheetId = os.getenv("SPREADSHEET_ID")

    def __init__(self, title='Coffee 120 clients', sheet_title='sheet1'):
        self.title_spreadsheet = title
        self.title_sheet = sheet_title

        # if no SPREADSHEET_ID at os environment variables get id from csv config (local)
        if not self.spreadsheetId:
            self.change_spreadsheet_id()

        # get range of columns - letters and number of columns
        ranges = [f'{sheet_title}']

        value_render_option = 'UNFORMATTED_VALUE'

        request = self.service.spreadsheets().values().batchGet(spreadsheetId=self.spreadsheetId, ranges=ranges,
                                                                valueRenderOption=value_render_option,
                                                                # dateTimeRenderOption=date_time_render_option
                                                                )
        # get response like 'sheet_title!A1:G3000'
        response = request.execute()['valueRanges'][0]['range']
        response_sheet_title, range_ = response.split('!')

        if response_sheet_title != sheet_title:
            raise Exception('!sheet_title! different from !spreadsheetId! sheet title')

        start, end = range_.split(':')
        self.start_letter = start[0]
        self.end_letter = end[0]

        alphabet = list(string.ascii_uppercase)

        self.columns = alphabet.index(self.end_letter) + 1
        self.range = f"{self.title_sheet}!{self.start_letter}1:{self.end_letter}1"

        # self.add_row([["start server"]])

    def change_spreadsheet_id(self, index_in_csv=-1):
        df = pd.read_csv(os.path.join(THIS_FOLDER, 'config/spreadsheet.csv'))
        self.spreadsheetId = str(df.iloc[index_in_csv].values[0])

    def create_spreadsheet(self, title=None, sheet_title=None, row_count=3000, column_count=7):
        # NOT SERVER FUNCTION

        self.columns = column_count

        if title is not None:
            self.title_spreadsheet = title

        if sheet_title is not None:
            self.title_sheet = sheet_title

        df = pd.read_csv(os.path.join(THIS_FOLDER, 'config/spreadsheet.csv'))
        spreadsheet = self.service.spreadsheets().create(body={
            'properties': {'title': f'{self.title_spreadsheet}', 'locale': 'ru_RU'},
            'sheets': [{'properties': {'sheetType': 'GRID',
                                       'sheetId': 0,
                                       'title': self.title_sheet,
                                       'gridProperties': {'rowCount': row_count, 'columnCount': column_count}}}]
        }).execute()

        self.spreadsheetId = spreadsheet['spreadsheetId']  # сохраняем идентификатор файла
        df = df.append({'sheetid': self.spreadsheetId}, ignore_index=True)
        df.to_csv(os.path.join(THIS_FOLDER, 'config/spreadsheet.csv'), index=False)
        print('https://docs.google.com/spreadsheets/d/' + self.spreadsheetId)

    def open_properties(self, address, permission_type='writer'):
        # NOT SERVER FUNCTION

        # Выбираем работу с Google Drive и 3 версию API
        driveService = discovery.build('drive', 'v3', http=self.httpAuth)
        if permission_type == 'owner':
            transferOwnership = True
        else:
            transferOwnership = False

        access = driveService.permissions().create(
            transferOwnership=transferOwnership,
            fileId=self.spreadsheetId,
            body={'type': 'user', 'role': permission_type, 'emailAddress': f'{address}@gmail.com'}).execute()
        # apply permission
        driveService.files().update(
            fileId=self.spreadsheetId,
            body={'permissionIds': [access['id']]}).execute()

    def delete_sheet(self, sheet_id):
        # UNUSED FUNCTION

        requests = [{
            "deleteSheet": {
                "sheetId": 0
            }
        }]
        body = {'requests': requests}
        request = self.service.spreadsheets().batchUpdate(spreadsheetId=sheet_id, body=body)
        response = request.execute()

    def add_row(self, information):

        # information like :
        # [
        #     ["Door", "$15", "2", "3/15/2016"],
        #     ["Engine", "$100", "1", "3/20/2016"],
        # ]

        value_range_body = {
            "range": self.range,
            "majorDimension": "ROWS",
            "values": information,
        }
        value_input_option = 'RAW'
        insert_data_option = 'INSERT_ROWS'

        request = self.service.spreadsheets().values().append(spreadsheetId=self.spreadsheetId,
                                                              range=self.range,
                                                              valueInputOption=value_input_option,
                                                              # insertDataOption=insert_data_option,
                                                              body=value_range_body)
        response = request.execute()

    def __del__(self):
        self.add_row([["End server"]])

# if __name__ == '__main__':
#     cls = GoogleSheets()
#     cls.add_row([["start server"]])
#
# cls.create_spreadsheet()
# cls.open_properties('patrushev9911', permission_type='writer')
# cls.open_properties('patrushev9911', permission_type='owner')
# cls.open_properties('coffeeshop120', permission_type='owner')
