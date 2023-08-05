import os
import json

from openpyxl import load_workbook
from excel_to_json.sheet import Sheet
import excel_to_json.columntitle as columntitle
import excel_to_json.sheetname as sheetname
from excel_to_json.date_encoder import DateEncoder


class Book:
    def __init__(self):
        self.sheets = []

    def parse_file(self, file_path):
        wb = load_workbook(file_path)
        for ws in wb:
            sheet = Sheet(ws.title)
            sheet.parse(ws)
            self.sheets.append(sheet)
        # deal the joint
        for sheet in self.sheets:
            for target, join in sheet.joins.items():
                target_sheet_name = columntitle.join_target_sheet(target)
                target_column = columntitle.join_target_column(target)
                target_sheet = self.get_sheet(target_sheet_name)
                for join_identify, data in join.items():
                    target_sheet.get_anchor_setter(target_column, join_identify)(data)

    def out_file(self, path):
        # check predefined out file suffix, like .json or .yaml
        data = None
        for sheet in filter(lambda s: sheetname.is_outfile(s.title), self.sheets):
            try:
                data = self.get_data(sheet)
                f = open(os.path.join(path, sheetname.out_file_name(sheet.title)), 'w+', encoding='utf-8')
                f.write(data)
                f.close()
            except Exception as err:
                print(err)

    def out_console(self):
        # check predefined out file suffix, like .json or .yaml
        data = None
        for sheet in self.sheets:
            try:
                data = self.get_data(sheet)
                print(data)
            except Exception as err:
                print(err)

    def get_sheet(self, sheet_name):
        return next(filter(lambda s: sheetname.shortname(s.title) == sheet_name, self.sheets), None)

    @staticmethod
    def get_data(sheet):
        data = None
        if sheetname.is_json(sheet.title):
            data = Book.get_json_data(sheet)
        # can add yaml support
        return data

    @staticmethod
    def get_json_data(sheet):
        if not sheetname.is_array(sheet.title) and len(sheet.datas) == 1:
            data = json.dumps(sheet.datas[0], cls=DateEncoder, ensure_ascii=False)
        else:
            data = json.dumps(sheet.datas, cls=DateEncoder, ensure_ascii=False)
        return data

