import tkinter as tk
from tkinter.filedialog import askopenfilename
import pandas as pd
import re

import icecream

from processor_ekspress_site import process_ekspress_site
from processor_ekspress_MP import process_ekspress_MP
from processor_optima_series import process_optima
from processor_prime_site import process_prime_site

from test_result import test_result

import logging

logging.basicConfig(level="DEBUG", filename="main.log", filemode="w")


def open_file(reply_var: tk.StringVar, 
              btn: tk.Button, 
              filename: str) -> pd.DataFrame:
    filepath = askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
    if filepath:
        try:
            globals()[f"{filename}"] = pd.read_excel(filepath)
            logging.info(f"Файл успешно загружен: {filepath}")
            reply_var.set(f"Успешно загружен файл: {filepath}")
            btn.configure(text="Выбрать другой файл")
            return
        except Exception as error:
            logging.error(f"ОШибка при попытке открыть файл: {filepath}")
            reply_var.set("Возникла ошибка во время загрузки файла!\n\n" \
                          "Повторите действие или выберите другой файл")
            logging.error(f"Ошибка при открытии файла и присвоении данных " \
                          f"глобальной переменной\nОшибка: {error}")
            return
    reply_var.set("Неверно указан путь к файлу")
    logging.error(f"Возникла ошибка при указании пути к файлу!\n" \
                  f"Указан путь: {filepath}") 
    return


def get_series(file: pd.DataFrame) -> str:
    # Поиск подстроки между кавычками («», "" или '')
    series = re.search(
        "(Локер|Оптим|Широкий Прайм|Прайм|Экспресс|Эста)", 
        file.iloc[0]["Номенклатура"]
    ).group(1)
    if series and file["Номенклатура"].str.contains(f"{series}").all():
        return series
    else:
        return None
    

def process_data(file_cases: pd.DataFrame, 
                 file_doors: pd.DataFrame, 
                 cases_series: str) -> pd.DataFrame:
    if cases_series == "Экспресс":
        if for_MP_enabled.get():
            return process_ekspress_MP(file_cases, file_doors, cases_series)    # TODO: remove seires
        else:
            return process_ekspress_site(file_cases, file_doors, cases_series)  # TODO: remove seires
    elif cases_series == "Оптим":
        return process_optima(file_cases, file_doors, cases_series)             # TODO: remove seires
    elif cases_series == "Прайм":
        return process_prime_site(file_cases, file_doors)
    else:
        logging.error(f"Ошибка запуска обработки для серии: {cases_series}")
        return pd.DataFrame()
    

def write_file(result_df: pd.DataFrame, 
               reply_var: tk.StringVar, 
               filename: str) -> None:
    logging.info(f"Запись полученных данных.")
    reply_var.set("Осуществляется запись полученных данных...")
    try:
        result_df.to_excel(filename, index=False, engine="xlsxwriter")
    except Exception as error:
        logging.error(f"Ошибка при попытке записи файла!\nОшибка: {error}")
        reply_var.set("Возникла ошибка при попытке записи файла!\n\n" \
                      "Обратитесь к разработчику.")
        return
    finally:
        reply_var.set(f"Данные успешно сформированы и сохранены в файле {filename}")
        return


def launch_process(reply_var: tk.StringVar, 
                   file_cases: pd.DataFrame | None, 
                   file_doors: pd.DataFrame | None) -> None:
    if (file_cases is None) or (file_doors is None):
        logging.info(f"Попытка создания таблиц без файлов с номенклатурой")
        reply_var.set("Вы не выбрали файлы с номенклатурой!\n\n" \
                      "Программа не может быть запущена без этих файлов")
        return
    cases_series = get_series(file_cases)
    doors_series = get_series(file_doors)
    if cases_series != doors_series or cases_series is None:
        logging.info(f"Ошибка при проверке серии корпусов")
        reply_var.set("Ошибка при проверке серии корпусов!\n\n" \
                      "Пожалуйста, проверьте соответствуют ли загруженные " \
                      "данные одной серии.")
        return
    try:
        logging.info(f"Запуск процедуры создания таблиц для серии {cases_series}")
        result_df = process_data(file_cases, file_doors, cases_series)
    except Exception as error:
        logging.error(f"Ошибка при запуске процедуры создания таблиц\nОшибка: {error}")
        reply_var.set("Ошибка на этапе формирования таблиц.\n\n" \
                      "Обратитесь к разработчику.")
        return
    if result_df.empty:
        logging.error(f"Получен пустой датафрейм")
        reply_var.set("Получена пустая таблица.\n\n" \
                      "Пожалуйста, проверьте данные на соответствие одной серии," \
                      "и запустите процедуру повторно.\n"
                      "В случае повторения ошибки обратитесь к разработчику.")
        return
    else:
        write_file(result_df, reply_var, filename="result.xlsx")

    if test_enabled.get():
        try:
            logging.info(f"Запуск проверки сформированных данных")
            reply_var.set("Процедура проверки таблицы успешно запущена.")
            tested_result = test_result(result_df, file_cases, file_doors)
        except Exception as error:
            logging.error(f"Ошибка при выполнении проверки таблицы\nОшибка: {error}")
            reply_var.set("Ошибка при выполнении проверки таблицы.\n\n" \
                          "Обратитесь к разработчику.")
            return
        write_file(tested_result, reply_var, filename="test_result.xlsx")    
    return


root = tk.Tk()
root.geometry("570x320")
root.title("Создание таблиц для обработчика карточек УМФ")
root.iconphoto(False, tk.PhotoImage(file="e1.png"))
### Фрейм загрузки файла с корпусами шкафов (cases)
frm_cases = tk.Frame(root)
lbl_cases = tk.Label(frm_cases, text="Выберите Excel файл с номенклатурой корпусов: ")
btn_cases = tk.Button(
    frm_cases, 
    text="Выбрать файл",
    fg="gray30",
    command=lambda: open_file(reply_var_cases, btn_cases, "file_cases")
)
reply_var_cases = tk.StringVar(value="")
lbl_reply_cases = tk.Label(frm_cases, textvariable=reply_var_cases)
frm_cases.pack(fill="x")
lbl_cases.grid(row=1, column=1)
btn_cases.grid(row=1, column=2)
lbl_reply_cases.grid(row=2, column=1, columnspan=99, sticky="w")
lbl_reply_cases = tk.Label(frm_cases, textvariable=reply_var_cases)
### Фрейм загрузки файла с дверями шкафов (doors)
frm_doors = tk.Frame(root)
reply_var_doors = tk.StringVar(value="")
lbl_doors = tk.Label(frm_doors, text="Выберите Excel файл с номенклатурой дверей: ")
btn_doors = tk.Button(
    frm_doors, 
    text="Выбрать файл",
    fg="gray30",
    command=lambda: open_file(reply_var_doors, btn_doors, "file_doors")
)
lbl_reply_doors = tk.Label(frm_doors, textvariable=reply_var_doors)
frm_doors.pack(fill="x")
lbl_doors.grid(row=1, column=1)
btn_doors.grid(row=1, column=2)
lbl_reply_doors.grid(row=2, column=1, columnspan=99, sticky="w")
### Checkbutton карточки для маркетплейсов
frm_chkbtn_for_MP = tk.Frame(root)
for_MP_enabled = tk.IntVar()
chkbtn_for_MP = tk.Checkbutton(
    frm_chkbtn_for_MP, 
    text="Подготовка данных для маркетплейсов",
    variable=for_MP_enabled
)
frm_chkbtn_for_MP.pack(fill="x")
chkbtn_for_MP.pack(side="left", pady=5)
### Checkbutton проверки результатов
frm_chkbtn_test = tk.Frame(root)
test_enabled = tk.IntVar()
chkbtn_test = tk.Checkbutton(
    frm_chkbtn_test, 
    text="Выполнить проверку полученных результатов",
    variable=test_enabled
)
frm_chkbtn_test.pack(fill="x")
chkbtn_test.pack(side="left", pady=5)
### Кнопка запуска создания таблицы
file_cases = None
file_doors = None
frm_btn = tk.Frame(root)
btn_launch = tk.Button(
    frm_btn, 
    text="Запуск", 
    command=lambda: launch_process(service_message_var, file_cases, file_doors))
frm_btn.pack(fill="x")
btn_launch.pack(side="right", padx=15, ipadx=25, ipady=10)
### Фрейм для служебных сообщений
frm_service_messages = tk.LabelFrame(root, text="Служебные сообщения", fg="grey")
service_message_var = tk.StringVar(value="Чтобы создать таблицы для обработчика карточек УМФ, \n" \
                                         "выберите файлы с подходящей номенклатурой корпусов и дверей. \n" \
                                         "Серии корпусов и дверей должны совпадать.")
lbl_service_messages = tk.Label(
    frm_service_messages, 
    textvariable=service_message_var, 
    height=100, 
    justify="left")
frm_service_messages.pack(fill="x")
lbl_service_messages.pack(side="left")


if __name__ == "__main__":
    root.mainloop()