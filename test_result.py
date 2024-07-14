import pandas as pd

def test_result(result_df, file_cases, file_doors):
    '''
    Функция сопоставляет столбец сформированной программой таблицы,
    содержащую каркасы (cases) и двери (doors) шкафов, с соответствующими 
    столбцами исходных таблиц и возвращает перечень неиспользованной номенклатуры
    '''
    unused_cases = file_cases.merge(result_df, how="left", on=["Номенклатура", "Вариант исполнения"], indicator=True)
    unused_cases = unused_cases.query("_merge == 'left_only'")[["Номенклатура", "Код номенклатуры", "Вариант исполнения", "Код ВИ"]]

    unused_doors = file_doors.merge(result_df, how="left", on=["Номенклатура", "Вариант исполнения"], indicator=True)
    unused_doors = unused_doors.query("_merge == 'left_only'")[["Номенклатура", "Код номенклатуры", "Вариант исполнения", "Код ВИ"]]

    unused_items = pd.concat([unused_cases, unused_doors])
    unused_items.to_excel("Неиспользованная номенклатура.xlsx", engine="xlsxwriter")

    result_data = result_df.groupby(["Номенклатура", "Вариант исполнения"], as_index=False)[["Номенклатура", "Вариант исполнения"]].size()

    result_data.to_excel("Количество номенклатуры.xlsx")
    return result_data


if __name__ == "__main__":
    result_df = pd.read_excel("result.xlsx")
    file_cases = pd.read_excel("Корпуса.xlsx")
    file_doors = pd.read_excel("Двери.xlsx")
    test_result(result_df, file_cases, file_doors)