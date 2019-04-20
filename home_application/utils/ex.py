# -*- coding: utf-8 -*-

import xlrd
from datetime import date, datetime

import json


def parse_excel(path):
    # 文件位置

    ex_file = xlrd.open_workbook(path)

    # 获取目标EXCEL文件sheet名

    # print ex_file.sheet_names()

    # ------------------------------------

    # 若有多个sheet，则需要指定读取目标sheet例如读取sheet2

    # sheet2_name=ex_file.sheet_names()[0]

    # ------------------------------------
    sheet = ex_file.sheet_by_index(0)

    # 打印sheet的名称，行数，列数

    print sheet.name
    print sheet.nrows
    print sheet.ncols

    # 获取整行或者整列的值
    task_map = {}
    tasks = sheet.col_values(1)[1:]
    remarks = sheet.col_values(2)[1:]
    operators = sheet.col_values(3)[1:]

    for i in range(len(tasks)):
        task_map[str(i)] = {
            'task': tasks[i],
            'remark': remarks[i],
            'operators': operators[i],
            'done': 0,
        }

    return json.dumps(task_map)

    # 获取单元格内容
    #
    # print sheet.cell(1,0).value.encode('utf-8')
    #
    # print sheet.cell_value(1,0).encode('utf-8')
    #
    # print sheet.row(1)[0].value.encode('utf-8')

    # 打印单元格内容格式


if __name__ == '__main__':
    print parse_excel(r'/Users/enzo/Downloads/help/checklist.xls')
