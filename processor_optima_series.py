import pandas as pd
import re
import logging

logging.basicConfig(level="INFO", filename="main.log", filemode="w")
  

def process_optima(file_cases, file_doors):
    result_tbl = []
    all_wardrobe_cases = file_cases
    all_wardrobe_cases = all_wardrobe_cases.rename(columns={
        "Код номенклатуры": "Код_номенклатуры", 
        "Вариант исполнения": "Вариант_исполнения", 
        "Код ВИ": "Код_ВИ"}
    )
    all_doors = file_doors
    all_doors = all_doors.rename(columns={
        "Код номенклатуры": "Код_номенклатуры", 
        "Вариант исполнения": "Вариант_исполнения", 
        "Код ВИ": "Код_ВИ"}
    )

    for wardrobe_case in all_wardrobe_cases.itertuples():
        # Парсинг характеристик корпуса шкафа (wardrobe_case)
        wardrobe_case_width, wardrobe_case_height, wardrobe_case_depth = map(int, re.findall("\d{3,4}", wardrobe_case.Номенклатура))
        wardrobe_case_equipment = re.search("К-(\d,\d)", wardrobe_case.Номенклатура)[1]
        wardrobe_case_color, profile_color_pattern = re.findall("([^/]+)/([^/]+)", wardrobe_case.Вариант_исполнения)[0]           
        # Шаблон цвета профиля для сравнения (одним словом - "Белый", "Бронза" и пр.) и замена Ё на Е
        profile_color_pattern = re.search("^(\w+)", profile_color_pattern).group()
        profile_color_pattern = profile_color_pattern.replace("ё", "е")
        wardrobe_case_profile_color = profile_color_pattern + f" профиль"
        # Вычисление прочих характеристик
        wardrobe_case_quantity = 1
        doors_quantity = int(re.search("(\d)-х дверный", wardrobe_case.Номенклатура).group(1))
        wardrobe_type = f"{doors_quantity}-х дверные"
        door_width = str(int(wardrobe_case_width / doors_quantity))
        # Группировка характеристик для последующей записи
        common_wardrobe_data = (
            wardrobe_case_height,
            wardrobe_case_depth,
            wardrobe_case_width,
            wardrobe_case_equipment,
            wardrobe_case_color,
            wardrobe_case_profile_color
        )
        wardrobe_nomenclature = (
            wardrobe_case.Номенклатура,
            wardrobe_case.Код_номенклатуры,
            wardrobe_case.Вариант_исполнения,
            wardrobe_case.Код_ВИ,
            wardrobe_case_quantity
        )
        other_data = (
            wardrobe_type,
        )     
        
        # Поиск подходящих дверей по высоте и ширине, цвету профиля, цвету корпуса
        # Также в выборку попадают двери не содержащие в названии цвет корпуса
        appropriate_doors = all_doors[
            all_doors["Номенклатура"].str.contains(f"{wardrobe_case_height}(?:Х|х|X|x){door_width}") &                            
            all_doors["Вариант исполнения"].str.contains(f"/{profile_color_pattern}[^/]*$", case=False) &
            (all_doors["Вариант исполнения"].str.contains(f"{wardrobe_case_color}/[^/]*$", case=False) |
            ~all_doors["Вариант исполнения"].str.contains("(?:снег|Бетон|диамант|Ясень|дуб|Венге)", case=False))
        ]
        for appropriate_door in appropriate_doors.itertuples():
            door_nomenclature = (
                appropriate_door.Номенклатура,
                appropriate_door.Код_номенклатуры,
                appropriate_door.Вариант_исполнения,
                appropriate_door.Код_ВИ,
                doors_quantity
                )
            result_tbl.append([*common_wardrobe_data, *wardrobe_nomenclature, *other_data])
            result_tbl.append([*common_wardrobe_data, *door_nomenclature, *other_data])

    result_df = pd.DataFrame(
        result_tbl, 
        columns=[
            "Характеристика.Высота, мм",
            "Характеристика.Глубина, мм",
            "Характеристика.Ширина, мм",
            "Характеристика.Компоновка корпуса",
            "Характеристика.Цвет Корпуса",
            "Характеристика.Цвет Профиля",
            "Номенклатура",
            "Номенклатура. Код",
            "Вариант исполнения",
            "Вариант исполнения. Код",
            "Количество",
            "Свойства. Тип шкафа"
        ]
    )
    return result_df



