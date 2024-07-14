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
        self.doors_type = ""
        self.wardrobe_kind = "двухдверный"
        self.for_storing = "одежды"
        self.fullsize_mirror = "Нет"
        self.model = "Локер"
        self.wardrobe_use = "в гардероб;в гостиную;в прихожую;в спальню"
        self.model_name = "Локер"
        self.series = "Локер"
        self.series_collection = "???"
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


def process_locker_MP(file_cases, file_doors):
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
        wardrobe.height, wardrobe.width, wardrobe.depth = re.search("\d{4}х\d{3,4}х\d{3}").groups()
        ic(wardrobe.height, wardrobe.width, wardrobe.depth)
        # Поиск подходящих дверей по высоте и ширине, цвету корпуса
        # Также в выборку попадают двери , содержащие в названии соответствующий корпусу цвет
        # или вовсе не содержащие в названии цвет корпуса (для зеркал, фотопечати и пр.)
        appropriate_doors = all_doors[
            all_doors["Номенклатура"].str.contains(f"{wardrobe.width}") &
            all_doors["Вариант_исполнения"].str.contains(f"^{wardrobe.manufacturer_case_color}$", case=False)
        ]
        if not appropriate_doors.empty:
            wardrobe.manufacturer_case_color = wardrobe.manufacturer_case_color.replace("Дуб табачный", "Крафт табачный")
            wardrobe.size = "х".join(
                map(str, (wardrobe.width, wardrobe.depth, wardrobe.height))
            )
            wardrobe.height = int(wardrobe.height / 10)
            wardrobe.depth = int(wardrobe.depth / 10)
            wardrobe.width = int(wardrobe.width / 10)

            if wardrobe.manufacturer_case_color in ("Белый снег"):
                wardrobe.case_color = "белый"
            elif wardrobe.manufacturer_case_color in ("Бетон", "Серый диамант", "Ясень Анкор светлый"):
                wardrobe.case_color = "серый"
            elif wardrobe.manufacturer_case_color in ("Венге", "Крафт табачный"):
                wardrobe.case_color = "коричневый"
            elif wardrobe.manufacturer_case_color in ("Сонома", "Ясень Шимо светлый"):
                wardrobe.case_color = "бежевый"

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
                same_doors_wardrobe.card_name = f"Шкаф {wardrobe.series} 2-х дверный " \
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
                    "лдсп", "матовое").replace("зеркало", "зеркальное")
                # Все материалы
                same_doors_wardrobe.materials = ";".join(
                    (same_doors_wardrobe.case_materials, 
                    same_doors_wardrobe.front_materials)
                ).replace("лдсп;лдсп", "лдсп")
                # Артикул
                same_doors_wardrobe.article = f"{same_doors_wardrobe.depth if same_doors_wardrobe.depth == 45 else 1}" \
                            f"E{article_series_collection[same_doors_wardrobe.series_collection]}" \
                            f"_{same_doors_wardrobe.width}" \
                            f"{same_doors_wardrobe.height if same_doors_wardrobe.height == 240 else ''}" \
                            f"_{article_color.get(same_doors_wardrobe.manufacturer_case_color, '')}"
                
                door_properties = (
                    single_door.Номенклатура,
                    single_door.Код_номенклатуры,
                    single_door.Вариант_исполнения,
                    single_door.Код_ВИ,
                    doors_quantity := 1
                )

                same_doors_wardrobe.add_nomenclature(case_properties)
                same_doors_wardrobe.add_nomenclature(door_properties)
                same_doors_wardrobe.append_to_tbl(result_tbl)

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