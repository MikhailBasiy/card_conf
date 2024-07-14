from copy import deepcopy

import pandas as pd
import re
from icecream import ic
import logging

logging.basicConfig(level="INFO", filename="main.log", filemode="w")


class Wardrobe:
    def __init__(self):
        self.card_name = ""
        self.article = ""
        self.coating_type = ""
        self.height = int
        self.depth = int
        self.width = int
        self.materials = ""
        self.case_materials = "лдсп"
        self.front_materials = ""
        self.size = ""
        self.case_color = ""
        self.manufacturer_case_color = ""
        self.manufacturer_front_materials = ""
        self.doors_type = "раздвижные"
        self.wardrobe_kind = ""
        self.for_storing = "одежды"
        self.fullsize_mirror = "Нет"
        self.model = "Экспресс"
        self.wardrobe_use = "в гардероб;в гостиную;в прихожую;в спальню"
        self.model_name = "Экспресс"
        self.series = "Экспресс"
        self.series_collection = ""
        self.installation_method = "стационарный"
        self.wardrobe_style = "современный"
        self.wardrobe_type = "шкаф-купе"
        self.wardrobe_form = "прямой"
        self.description = ""

        self.nomenclature_lst = []
    
    def add_nomenclature(self, nomenclature):
        self.nomenclature_lst.append(nomenclature)

    def append_to_tbl(self, result_tbl):
        for nomenclature in self.nomenclature_lst:
            result_tbl.append(
                [
                    self.card_name,
                    self.article,
                    self.coating_type,
                    self.height, 
                    self.depth, 
                    self.width,
                    self.materials,
                    self.case_materials,
                    self.front_materials,
                    self.size,
                    self.case_color,
                    self.manufacturer_case_color,
                    self.manufacturer_front_materials,
                    *nomenclature,
                    self.doors_type,
                    self.wardrobe_kind,
                    self.for_storing,
                    self.fullsize_mirror,
                    self.model,
                    self.wardrobe_use,
                    self.model_name,
                    self.series,
                    self.series_collection,
                    self.installation_method,
                    self.wardrobe_style,
                    self.wardrobe_type,
                    self.wardrobe_form,
                    self.description
                ]
        )


article_color = {
    "Белый снег": "B",
    "Бетон": "BT",
    "Венге": "V",
    "Крафт табачный": "KT",
    "Серый диамант": "DM",
    "Сонома": "S",
    "Ясень Анкор светлый": "SAS",
    "Ясень Шимо светлый": "SHS"
}
article_series_collection = {
    "Элемент": "E",
    "Медиум": "M",
    "Экспенс": "EK",
}


def process_ekspress_MP(file_cases, file_doors):
    all_cases = file_cases
    all_cases = all_cases.rename(columns={
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
    result_tbl = []
    for case in all_cases.itertuples():
        wardrobe = Wardrobe()
        # Определение свойств корпуса как криетриев подбора
        wardrobe.manufacturer_case_color = case.Вариант_исполнения.replace("Светлый", "светлый")
        wardrobe_case_width, wardrobe_case_height, wardrobe_case_depth = map(
            int, re.findall("\d{3,4}", case.Номенклатура)
        )
        # Корпус с шириной 1800 может быть как с 2, так и 3 дверями
        if wardrobe_case_width == 1800:                                 # TODO: вынести создание карточек для широкого экспресса в отдельный файл???
            doors_quantities = (2, 3)
        elif (wardrobe_case_width / 2) in (600, 700, 800, 900):
            doors_quantities = (2,)
        else:
            doors_quantities = (3,)
        
        for door_quantity in doors_quantities: 
            door_width = str(int(wardrobe_case_width / door_quantity))
            # Поиск подходящих дверей по высоте и ширине, цвету корпуса
            # Также в выборку попадают двери , содержащие в названии соответствующий корпусу цвет
            # или вовсе не содержащие в названии цвет корпуса (для зеркал, фотопечати и пр.)
            appropriate_doors = all_doors[
                all_doors["Номенклатура"].str.contains(f"{wardrobe_case_height}(?:Х|х|X|x){door_width}") &
                (all_doors["Вариант_исполнения"].str.contains(f"^{wardrobe.manufacturer_case_color}$", case=False) |
                ~all_doors["Вариант_исполнения"].str.contains("(?:снег|Бетон|диамант|Ясень|дуб|Венге|Сонома)", case=False))
            ]

            if not appropriate_doors.empty:
                wardrobe.manufacturer_case_color = wardrobe.manufacturer_case_color.replace("Дуб табачный", "Крафт табачный")
                wardrobe.height = int(wardrobe_case_height / 10)
                wardrobe.depth = int(wardrobe_case_depth / 10)
                wardrobe.width = int(wardrobe_case_width / 10)
                if wardrobe.depth == 44:
                    wardrobe.depth = 45
                wardrobe.size = "х".join(
                    map(
                        str,
                        (wardrobe.width,
                        wardrobe.depth,
                        wardrobe.height
                        )
                    )
                )
                if wardrobe.manufacturer_case_color in ("Белый снег"):
                    wardrobe.case_color = "белый"
                elif wardrobe.manufacturer_case_color in ("Бетон", "Серый диамант", "Ясень Анкор светлый"):
                    wardrobe.case_color = "серый"
                elif wardrobe.manufacturer_case_color in ("Венге", "Крафт табачный"):
                    wardrobe.case_color = "коричневый"
                elif wardrobe.manufacturer_case_color in ("Сонома", "Ясень Шимо светлый"):
                    wardrobe.case_color = "бежевый"

                if door_quantity == 2:
                    wardrobe.wardrobe_kind = "двухдверный"
                elif door_quantity == 3:
                    wardrobe.wardrobe_kind = "трехдверный"

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
                    single_door_material = re.search("(ДСП|Зеркало)", single_door.Номенклатура).group(1)
                    # Наименование карточки
                    same_doors_wardrobe.card_name = f"Шкаф-купе {wardrobe.series}, {door_quantity}дв. " \
                                                           f"{single_door_material.replace('Зеркало', 'Зеркала')}, " \
                                                           f"{same_doors_wardrobe.size}"
                    # Материалы фасада
                    same_doors_wardrobe.front_materials = single_door_material.replace("ДСП", "ЛДСП").lower()
                    same_doors_wardrobe.manufacturer_front_materials = same_doors_wardrobe.front_materials.replace(
                        "лдсп", 
                        wardrobe.manufacturer_case_color
                    ).replace("зеркало","Зеркало")
                    # Вид покрытия
                    same_doors_wardrobe.coating_type =  same_doors_wardrobe.front_materials.replace(
                        "лдсп", 
                        "матовое"
                    ).replace(
                        "зеркало", 
                        "зеркальное"
                    )
                    # Все материалы
                    same_doors_wardrobe.materials = ";".join(
                        (same_doors_wardrobe.case_materials, 
                        same_doors_wardrobe.front_materials)
                    ).replace("лдсп;лдсп", "лдсп")
                    # Зеркало в полный рост
                    if "зеркало" in same_doors_wardrobe.front_materials:
                        same_doors_wardrobe.fullsize_mirror = "Да"
                    # Серия (Коллекция)
                    if same_doors_wardrobe.front_materials == "лдсп":
                        same_doors_wardrobe.series_collection = "Элемент"
                    elif same_doors_wardrobe.front_materials == "зеркало":
                        same_doors_wardrobe.series_collection = "Экспенс"
                    else: 
                        same_doors_wardrobe.series_collection = "Медиум"
                    # Артикул
                    same_doors_wardrobe.article = f"{same_doors_wardrobe.depth if same_doors_wardrobe.depth == 45 else 1}" \
                              f"E{article_series_collection[same_doors_wardrobe.series_collection]}" \
                              f"{'D' if door_quantity == 2 else 'T'}" \
                              f"_{same_doors_wardrobe.width}" \
                              f"{same_doors_wardrobe.height if same_doors_wardrobe.height == 240 else ''}" \
                              f"_{article_color.get(same_doors_wardrobe.manufacturer_case_color, '')}"
                    
                    door_properties = (
                        single_door.Номенклатура,
                        single_door.Код_номенклатуры,
                        single_door.Вариант_исполнения,
                        single_door.Код_ВИ,
                        door_quantity
                    )

                    same_doors_wardrobe.add_nomenclature(case_properties)
                    same_doors_wardrobe.add_nomenclature(door_properties)
                    same_doors_wardrobe.append_to_tbl(result_tbl)

                    for second_door in appropriate_doors[(idx + 1):]:
                        different_doors_wardrobe_1 = deepcopy(wardrobe)
                        first_door_material = single_door_material
                        second_door_material = re.search("(ДСП|Зеркало)", second_door.Номенклатура).group(1)
                        second_door_quantity = 1
                        first_door_quantity = door_quantity - second_door_quantity
                        # "Зеркало" в наименовании стоит на первом месте только если таких дверей больше 1
                        if first_door_quantity == 1 and first_door_material == "Зеркало":
                            first_door_material, second_door_material = second_door_material, first_door_material
                        # Наименование карточки
                        different_doors_wardrobe_1.card_name = f"Шкаф-купе {wardrobe.series}, {door_quantity}дв. " \
                                                                      f"{first_door_material}/{second_door_material}, " \
                                                                      f"{different_doors_wardrobe_1.size}"
                        # Материалы фасада
                        different_doors_wardrobe_1.front_materials = ";".join((first_door_material, second_door_material)).replace("ДСП", "ЛДСП").lower()
                        different_doors_wardrobe_1.manufacturer_front_materials = different_doors_wardrobe_1.front_materials.replace(
                            "лдсп", 
                            wardrobe.manufacturer_case_color
                        ).replace("зеркало","Зеркало")
                        # Вид покрытия
                        different_doors_wardrobe_1.coating_type =  different_doors_wardrobe_1.front_materials.replace(
                            "лдсп", 
                            "матовое"
                        ).replace(
                            "зеркало", 
                            "зеркальное"
                        )
                        # Все материалы
                        different_doors_wardrobe_1.materials = ";".join(
                            (different_doors_wardrobe_1.case_materials, 
                             different_doors_wardrobe_1.front_materials)
                        ).replace("лдсп;лдсп", "лдсп")
                        # Зеркало в полный рост
                        if "зеркало" in different_doors_wardrobe_1.front_materials:
                            different_doors_wardrobe_1.fullsize_mirror = "Да"
                        # Серия (Коллекция)
                        if different_doors_wardrobe_1.front_materials == "лдсп":
                            different_doors_wardrobe_1.series_collection = "Элемент"
                        elif different_doors_wardrobe_1.front_materials == "зеркало":
                            different_doors_wardrobe_1.series_collection = "Экспенс"
                        else: 
                            different_doors_wardrobe_1.series_collection = "Медиум"
                        
                        # Артикул
                        different_doors_wardrobe_1.article = f"{different_doors_wardrobe_1.depth if different_doors_wardrobe_1.depth == 45 else 1}" \
                              f"E{article_series_collection[different_doors_wardrobe_1.series_collection]}" \
                              f"{'D' if door_quantity == 2 else 'T'}" \
                              f"_{different_doors_wardrobe_1.width}" \
                              f"{different_doors_wardrobe_1.height if different_doors_wardrobe_1.height == 240 else ''}" \
                              f"_{article_color.get(different_doors_wardrobe_1.manufacturer_case_color, '')}"
                        
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
                            different_doors_wardrobe_2.card_name = f"Шкаф-купе {wardrobe.series}, {door_quantity}дв. " \
                                                                          f"{second_door_material}/{first_door_material}, " \
                                                                          f"{different_doors_wardrobe_2.size}"
                            # Материалы фасада
                            different_doors_wardrobe_2.front_materials = different_doors_wardrobe_1.front_materials
                            different_doors_wardrobe_2.manufacturer_front_materials = different_doors_wardrobe_2.front_materials.replace(
                                "лдсп", 
                                wardrobe.manufacturer_case_color
                            ).replace("зеркало","Зеркало")
                            # Вид покрытия
                            different_doors_wardrobe_2.coating_type =  different_doors_wardrobe_2.front_materials.replace(
                                "лдсп", 
                                "матовое"
                            ).replace(
                                "зеркало", 
                                "зеркальное"
                            )
                            # Все материалы
                            different_doors_wardrobe_2.materials = ";".join(
                                (different_doors_wardrobe_2.case_materials, 
                                different_doors_wardrobe_2.front_materials)).replace("лдсп;лдсп", "лдсп")
                            # Зеркало в полный рост
                            if "зеркало" in different_doors_wardrobe_2.front_materials:
                                different_doors_wardrobe_2.fullsize_mirror = "Да"
                            # Серия (Коллекция)
                            if different_doors_wardrobe_2.front_materials == "лдсп":
                                different_doors_wardrobe_2.series_collection = "Элемент"
                            elif different_doors_wardrobe_2.front_materials == "зеркало":
                                different_doors_wardrobe_2.series_collection = "Экспенс"
                            else: 
                                different_doors_wardrobe_2.series_collection = "Медиум"

                            # Артикул
                            different_doors_wardrobe_2.article = f"{different_doors_wardrobe_2.depth if different_doors_wardrobe_2.depth == 45 else 1}" \
                                f"E{article_series_collection[different_doors_wardrobe_2.series_collection]}" \
                                f"{'D' if door_quantity == 2 else 'T'}" \
                                f"_{different_doors_wardrobe_2.width}" \
                                f"{different_doors_wardrobe_2.height if different_doors_wardrobe_2.height == 240 else ''}" \
                                f"_{article_color.get(different_doors_wardrobe_2.manufacturer_case_color, '')}"

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
            "Характеристика. Артикул",
            "Характеристика.Вид покрытия",
            "Характеристика. Высота в сантиметрах",
            "Характеристика. Глубина в сантиметрах",
            "Характеристика. Ширина в сантиметрах",
            "Характеристика.Материал",
            "Характеристика.Материал корпуса",
            "Характеристика.Материал фасада",
            "Характеристика. Размеры (ШxГxВ), в сантиметрах",
            "Характеристика. Цвет каркаса",
            "Характеристика. Цвет каркаса от производителя",
            "Характеристика. Цвет фасада от производителя",
            "Номенклатура",
            "Номенклатура. Код",
            "Вариант исполнения",
            "Вариант исполнения. Код",
            "Количество",
            "Свойство. Вид дверей",
            "Свойство. Вид шкафа",
            "Свойство. Для хранения",
            "Свойство. Зеркало в полный рост",
            "Свойство. Модель",
            "Свойство. Назначение",
            "Свойство. Наименование модели (Модель)",
            "Свойство. Серия",
            "Свойство. Серия (Коллекция)",
            "Свойство. Способ установки",
            "Свойство. Стиль",
            "Свойство. Тип",
            "Свойство.Форма шкафа",
            "Описание"
        ]
    )
    return result_df
