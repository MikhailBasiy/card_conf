import pandas as pd
import re
import logging

from collections import namedtuple

logging.basicConfig(level="INFO", filename="main.log", filemode="w")


def insert_nomenclature_set(
        result_tbl: list,
        cardproduct_name: str,
        common_wardrobe_data: tuple,
        case_properties: tuple,
        other_properties: tuple, 
        first_door: namedtuple,
        first_door_quantity: int,
        second_door: namedtuple = None,
        second_door_quantity: int = None) -> None:
    
    first_door_properties = (
        first_door.Номенклатура,
        first_door.Код_номенклатуры,
        first_door.Вариант_исполнения,
        first_door.Код_ВИ,
        first_door_quantity
    )
    result_tbl.append([cardproduct_name, *common_wardrobe_data, *case_properties, *other_properties])
    result_tbl.append([cardproduct_name, *common_wardrobe_data, *first_door_properties, *other_properties])

    if second_door:
        second_door_properties = (
            second_door.Номенклатура,
            second_door.Код_номенклатуры,
            second_door.Вариант_исполнения,
            second_door.Код_ВИ,
            second_door_quantity
        )
        result_tbl.append([cardproduct_name, *common_wardrobe_data, *second_door_properties, *other_properties])


def process_ekspress_site(file_cases, file_doors, wardrobe_series):
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
        wardrobe_case_color = wardrobe_case.Вариант_исполнения    
        
        wardrobe_case_profile_color = "Серебро профиль"
        wardrobe_case_quantity = 1
        # Корпус с шириной 1800 может быть как с 2, так и 3 дверями
        if wardrobe_case_width == 1800:
            doors_quantities = (2, 3)
        elif (wardrobe_case_width / 2) in (600, 700, 800, 900):
            doors_quantities = (2,)
        else:
            doors_quantities = (3,)
        
        for door_quantity in doors_quantities: 
            door_width = str(int(wardrobe_case_width / door_quantity))
            # Указание компоновки шкафа
            if wardrobe_case_depth == 440:
                wardrobe_case_equipment = f"Экспресс 45 {str(door_quantity)}х"
            else:
                wardrobe_case_equipment = f"Экспресс 60 {str(door_quantity)}х"

            wardrobe_type = f"{door_quantity}-х дверные"

            # Группировка характеристик для последующей записи
            common_wardrobe_data = (
                wardrobe_case_height,
                wardrobe_case_depth,
                wardrobe_case_width,
                wardrobe_case_equipment,
                wardrobe_case_color,
                wardrobe_case_profile_color
            )
            case_properties = (
                wardrobe_case.Номенклатура,
                wardrobe_case.Код_номенклатуры,
                wardrobe_case.Вариант_исполнения,
                wardrobe_case.Код_ВИ,
                wardrobe_case_quantity
            )
            other_properties = (
                "Бюджетная",
                "Нет",
                wardrobe_series,
                wardrobe_type,
            )

            # Поиск подходящих дверей по высоте и ширине, цвету корпуса
            # Также в выборку попадают двери не содержащие в названии цвет корпуса
            appropriate_doors = all_doors[
                all_doors["Номенклатура"].str.contains(f"{wardrobe_case_height}(?:Х|х|X|x){door_width}") &
                (all_doors["Вариант_исполнения"].str.contains(f"^{wardrobe_case_color}$", case=False) |
                ~all_doors["Вариант_исполнения"].str.contains("(?:снег|Бетон|диамант|Ясень|дуб|Венге|Сонома)", case=False))
            ]
            
            appropriate_doors_lst = list(appropriate_doors.itertuples())
            for idx, first_door in enumerate(appropriate_doors_lst):
                first_door_material = re.search("(ДСП|Зеркало)", first_door.Номенклатура).group(1)
                first_door_material = first_door_material.replace("ДСП", "ЛДСП")
                cardproduct_name = f"{wardrobe_series} {door_quantity}-х дверный ({first_door_material})"
                insert_nomenclature_set(
                    result_tbl,
                    cardproduct_name,
                    common_wardrobe_data,
                    case_properties,
                    other_properties, 
                    first_door,
                    door_quantity
                )
                for second_door in appropriate_doors_lst[(idx + 1):]:
                    second_door_quantity = 1
                    first_door_quantity = door_quantity - second_door_quantity
                    second_door_material = re.search("(ДСП|Зеркало)", second_door.Номенклатура).group(1)
                    second_door_material = second_door_material.replace("ДСП", "ЛДСП")
                    if first_door_quantity == 1 and first_door_material == "Зеркало":
                        first_door_material, second_door_material = second_door_material, first_door_material
                    cardproduct_name = f"{wardrobe_series} {door_quantity}-х дверный ({first_door_material}, {second_door_material})"
                    insert_nomenclature_set(
                        result_tbl,
                        cardproduct_name,
                        common_wardrobe_data,
                        case_properties,
                        other_properties, 
                        first_door,
                        first_door_quantity,    #
                        second_door,
                        second_door_quantity    #
                    )
                    if first_door_quantity > 1:
                        cardproduct_name = f"{wardrobe_series} {door_quantity}-х дверный ({second_door_material}, {first_door_material})"
                        insert_nomenclature_set(
                            result_tbl,
                            cardproduct_name,
                            common_wardrobe_data,
                            case_properties,
                            other_properties, 
                            first_door,
                            second_door_quantity,   #
                            second_door,
                            first_door_quantity     #
                        )

    result_df = pd.DataFrame(
        result_tbl, 
        columns=[
            "Наименование карточки",
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
            "Свойства. Класс",
            "Свойства. С фотопечатью",
            "Свойства. Серия",
            "Свойства. Тип шкафа"
        ]
    )
    return result_df