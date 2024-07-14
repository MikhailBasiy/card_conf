from copy import deepcopy

import pandas as pd
import re
import logging

from icecream import ic

logging.basicConfig(level="INFO", filename="main.log", filemode="w")


class Wardrobe:
    def __init__(self):
        self.card_name = ""
        self.basic_conf = ""
        self.height = 2300
        self.depth = 570
        self.width = int
        self.equipment = ""
        self.case_color = ""
        self.profile_color = "Серебро профиль"
        self.front_material_1 = ""
        self.front_material_2 = ""
        self.front_material_3 = ""
        self.front_material_4 = ""
        self.front_material_5 = ""
        self.video_youtube = '<iframe width="560" height="315" src="https://www.youtube.com/embed/I8arklqFEvU?si=7qsKUNfhkEZwg0G8" ' \
                             'title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; ' \
                             'gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>'
        self.klass = "Бюджетная"
        self.with_photoprint = "Нет"
        self.series = "Прайм"
        self.kind = ""
        self.description = ""
        self.front_name = ""

        self.nomenclature_lst = []
    
    def add_nomenclature(self, nomenclature):
        self.nomenclature_lst.append(nomenclature)

    def append_to_tbl(self, result_tbl):
        for nomenclature in self.nomenclature_lst:
            result_tbl.append(
                [
                    self.card_name,
                    self.basic_conf,
                    self.height,
                    self.depth,
                    self.width,
                    self.equipment,
                    self.case_color,
                    self.profile_color,
                    self.front_material_1,
                    self.front_material_2,
                    self.front_material_3,
                    self.front_material_4,
                    self.front_material_5,
                    *nomenclature,
                    self.video_youtube,
                    self.klass,
                    self.with_photoprint,
                    self.series,
                    self.kind,
                    self.description,
                    self.front_name
                ]
        )


def process_prime_site(file_cases, file_doors):
    all_cases = file_cases.rename(columns={
        file_cases.columns[1]: "Код_номенклатуры", 
        file_cases.columns[2]: "Вариант_исполнения", 
        file_cases.columns[3]: "Код_ВИ"}
    )
    all_doors = file_doors.rename(columns={
        file_doors.columns[1]: "Код_номенклатуры", 
        file_doors.columns[2]: "Вариант_исполнения", 
        file_doors.columns[3]: "Код_ВИ"}
    )
    result_tbl = []
    for case in all_cases.itertuples():
        wardrobe = Wardrobe()
        doors_quantity, wardrobe.width = map(
            int, re.search("(\d)-(\d{3,})", case.Номенклатура).groups()
        )
        if doors_quantity == 2:
            wardrobe.kind = "2-х дверные"
            wardrobe.equipment = "Прайм 2х"
        elif doors_quantity == 3:
            wardrobe.kind = "3-х дверные"
            wardrobe.equipment = "Прайм 3х"
        door_width = str(int((wardrobe.width / doors_quantity) * 10))
        wardrobe.case_color = case.Вариант_исполнения.replace("Светлый", "светлый")
        # Поиск подходящих дверей по высоте и ширине, цвету корпуса, а также
        # содержащие в названии соответствующий корпусу цвет или вовсе не 
        # содержащие в названии цвет корпуса (для зеркал, фотопечати и пр.)
        appropriate_doors = all_doors[
            all_doors["Номенклатура"].str.contains(f" {door_width} ") &
            (all_doors["Вариант_исполнения"].str.contains(f"^{wardrobe.case_color}$", case=False) |
            ~all_doors["Вариант_исполнения"].str.contains("(?:снег|бетон|венге|дуб|ясень|сонома|диамант)", case=False))
        ]
        if not appropriate_doors.empty:  
            case_properties = (
                case.Номенклатура,
                case.Код_номенклатуры,
                case.Вариант_исполнения,
                case.Код_ВИ,
                case_quantity := 1
            )
            appropriate_doors = list(appropriate_doors.itertuples())
            for idx, single_door in enumerate(appropriate_doors):
                same_doors_wardrobe = deepcopy(wardrobe)
                single_door_material = re.search("(ДСП|Зеркало)", 
                                                 single_door.Номенклатура).group(1)
                single_door_material = single_door_material.replace('ДСП', 'ЛДСП')
                same_doors_wardrobe.card_name = f"{wardrobe.series} {doors_quantity}-дверный " \
                                                f"({single_door_material})"
                door_properties = (
                    single_door.Номенклатура,
                    single_door.Код_номенклатуры,
                    single_door.Вариант_исполнения,
                    single_door.Код_ВИ,
                    doors_quantity
                )
                same_doors_wardrobe.add_nomenclature(case_properties)
                same_doors_wardrobe.add_nomenclature(door_properties)
                same_doors_wardrobe.append_to_tbl(result_tbl)

                for second_door in appropriate_doors[(idx + 1):]:
                    different_doors_wardrobe_1 = deepcopy(wardrobe)
                    first_door_material = single_door_material
                    second_door_material = re.search("(ДСП|Зеркало)", second_door.Номенклатура).group(1)
                    second_door_quantity = 1
                    first_door_quantity = doors_quantity - second_door_quantity
                    # "Зеркало" в наименовании стоит на первом месте только если таких дверей больше 1
                    if first_door_quantity == 1 and first_door_material == "Зеркало":
                        first_door_material, second_door_material = second_door_material, first_door_material
                    # Наименование карточки
                    different_doors_wardrobe_1.card_name = f"{wardrobe.series} {doors_quantity}-дверный " \
                                                           f"({first_door_material}, {second_door_material})"
                    first_door_properties = (
                        single_door.Номенклатура,
                        single_door.Код_номенклатуры,
                        single_door.Вариант_исполнения,
                        single_door.Код_ВИ,
                        first_door_quantity
                    )
                    second_door_properties = (
                        second_door.Номенклатура,
                        second_door.Код_номенклатуры,
                        second_door.Вариант_исполнения,
                        second_door.Код_ВИ,
                        second_door_quantity
                    )
                    different_doors_wardrobe_1.add_nomenclature(case_properties)
                    different_doors_wardrobe_1.add_nomenclature(first_door_properties)
                    different_doors_wardrobe_1.add_nomenclature(second_door_properties)
                    different_doors_wardrobe_1.append_to_tbl(result_tbl)

                    if first_door_quantity > 1:
                        different_doors_wardrobe_2 = deepcopy(wardrobe)
                        # Наименование карточки
                        different_doors_wardrobe_2.card_name = f"{wardrobe.series} {doors_quantity}-дверный " \
                                                               f"({second_door_material}, {first_door_material})"
                        first_door_properties = (
                            single_door.Номенклатура,
                            single_door.Код_номенклатуры,
                            single_door.Вариант_исполнения,
                            single_door.Код_ВИ,
                            second_door_quantity
                        )
                        second_door_properties = (
                            second_door.Номенклатура,
                            second_door.Код_номенклатуры,
                            second_door.Вариант_исполнения,
                            second_door.Код_ВИ,
                            first_door_quantity
                        )
                        different_doors_wardrobe_2.add_nomenclature(case_properties)
                        different_doors_wardrobe_2.add_nomenclature(second_door_properties)
                        different_doors_wardrobe_2.add_nomenclature(first_door_properties)
                        different_doors_wardrobe_2.append_to_tbl(result_tbl)

    result_df = pd.DataFrame(
        result_tbl, 
        columns=[
            "Наименование карточки",
            "Характеристика.Базовая конфигурация",
            "Характеристика.Высота, мм",
            "Характеристика.Глубина, мм",
            "Характеристика.Ширина, мм",
            "Характеристика.Компоновка корпуса",
            "Характеристика.Цвет Корпуса",
            "Характеристика.Цвет Профиля",
            "Характеристика. Материал фасада 1",
            "Характеристика. Материал фасада 2",
            "Характеристика. Материал фасада 3",
            "Характеристика. Материал фасада 4",
            "Характеристика. Материал фасада 5",
            "Номенклатура",
            "Номенклатура. Код",
            "Вариант исполнения",
            "Вариант исполнения. Код",
            "Количество",
            "Свойства.Видео (YouTube)",
            "Свойства. Класс",
            "Свойства. С фотопечатью",
            "Свойства. Серия",
            "Свойства. Тип шкафа",
            "Описание",
            "Наименование фасада"
        ]
    )
    return result_df