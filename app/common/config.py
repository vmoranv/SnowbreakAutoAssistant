# coding:utf-8
import sys
from enum import Enum

from PyQt5.QtCore import QLocale
from qfluentwidgets import (qconfig, QConfig, ConfigItem, OptionsConfigItem, BoolValidator,
                            OptionsValidator, Theme, ConfigSerializer)

from .setting import CONFIG_FILE


class Language(Enum):
    """ Language enumeration """

    CHINESE_SIMPLIFIED = QLocale(QLocale.Chinese, QLocale.China)
    CHINESE_TRADITIONAL = QLocale(QLocale.Chinese, QLocale.HongKong)
    ENGLISH = QLocale(QLocale.English)
    AUTO = QLocale()


class LanguageSerializer(ConfigSerializer):
    """ Language serializer """

    def serialize(self, language):
        return language.value.name() if language != Language.AUTO else "Auto"

    def deserialize(self, value: str):
        return Language(QLocale(value)) if value != "Auto" else Language.AUTO


def isWin11():
    return sys.platform == 'win32' and sys.getwindowsversion().build >= 22000


class Config(QConfig):
    """ Config of application """

    # 主页面
    date_tip = ConfigItem("home_interface_enter", "date_tip", [
        ["活动", "2025-1-23", "2025-3-6"],
        ["辰星卡池", "2025-1-23", "2025-3-6"],
        ["肴卡池", "2025-2-6", "2025-3-6"],
        ["异星守护", "2025-2-13", "2025-3-5"],
        ["悖论迷宫", "2025-2-6", "2025-2-27"],
        ["钓鱼大赛", "2025-1-23", "2025-3-6"],
        ["噬神斗场", "2025-1-23", "2025-2-20"],
        ["古宅异变", "2025-2-10", "2025-2-24"],
        ["绝地防线", "2025-2-17", "2025-3-3"],
        ["勇者游戏", "2025-1-25", "2025-2-8"],
    ])
    LineEdit_starter_directory = ConfigItem("home_interface_enter", "LineEdit_starter_directory", "./")
    LineEdit_link = ConfigItem("home_interface_enter", "LineEdit_link",
                               "https://www.cbjq.com/api.php?op=search_api&action=get_article_detail&catid=7131&id=270")
    CheckBox_auto_open_starter = ConfigItem("home_interface_enter", "CheckBox_auto_open_starter", False,
                                            BoolValidator())

    CheckBox_entry_1 = ConfigItem("home_interface_option", "CheckBox_entry", False, BoolValidator())
    CheckBox_stamina_2 = ConfigItem("home_interface_option", "CheckBox_stamina", False, BoolValidator())
    CheckBox_shop_3 = ConfigItem("home_interface_option", "CheckBox_shop", False, BoolValidator())
    CheckBox_use_power_4 = ConfigItem("home_interface_option", "CheckBox_use_power", False, BoolValidator())
    CheckBox_person_5 = ConfigItem("home_interface_option", "CheckBox_person", False, BoolValidator())
    CheckBox_chasm_6 = ConfigItem("home_interface_option", "CheckBox_chasm", False, BoolValidator())
    CheckBox_reward_7 = ConfigItem("home_interface_option", "CheckBox_reward", False, BoolValidator())

    CheckBox_buy_3 = ConfigItem("home_interface_shopping", "CheckBox_buy_3", False, BoolValidator())
    CheckBox_buy_4 = ConfigItem("home_interface_shopping", "CheckBox_buy_4", False, BoolValidator())
    CheckBox_buy_5 = ConfigItem("home_interface_shopping", "CheckBox_buy_5", False, BoolValidator())
    CheckBox_buy_6 = ConfigItem("home_interface_shopping", "CheckBox_buy_6", False, BoolValidator())
    CheckBox_buy_7 = ConfigItem("home_interface_shopping", "CheckBox_buy_7", False, BoolValidator())
    CheckBox_buy_8 = ConfigItem("home_interface_shopping", "CheckBox_buy_8", False, BoolValidator())
    CheckBox_buy_9 = ConfigItem("home_interface_shopping", "CheckBox_buy_9", False, BoolValidator())
    CheckBox_buy_10 = ConfigItem("home_interface_shopping", "CheckBox_buy_10", False, BoolValidator())
    CheckBox_buy_11 = ConfigItem("home_interface_shopping", "CheckBox_buy_11", False, BoolValidator())
    CheckBox_buy_12 = ConfigItem("home_interface_shopping", "CheckBox_buy_12", False, BoolValidator())
    CheckBox_buy_13 = ConfigItem("home_interface_shopping", "CheckBox_buy_13", False, BoolValidator())
    CheckBox_buy_14 = ConfigItem("home_interface_shopping", "CheckBox_buy_14", False, BoolValidator())
    CheckBox_buy_15 = ConfigItem("home_interface_shopping", "CheckBox_buy_15", False, BoolValidator())

    item_person_0 = ConfigItem("home_interface_shopping_person", "item_person_0", False, BoolValidator())
    item_person_1 = ConfigItem("home_interface_shopping_person", "item_person_1", False, BoolValidator())
    item_person_2 = ConfigItem("home_interface_shopping_person", "item_person_2", False, BoolValidator())
    item_person_3 = ConfigItem("home_interface_shopping_person", "item_person_3", False, BoolValidator())
    item_person_4 = ConfigItem("home_interface_shopping_person", "item_person_4", False, BoolValidator())
    item_person_5 = ConfigItem("home_interface_shopping_person", "item_person_5", False, BoolValidator())
    item_person_6 = ConfigItem("home_interface_shopping_person", "item_person_6", False, BoolValidator())
    item_person_7 = ConfigItem("home_interface_shopping_person", "item_person_7", False, BoolValidator())
    item_person_8 = ConfigItem("home_interface_shopping_person", "item_person_8", False, BoolValidator())
    item_person_9 = ConfigItem("home_interface_shopping_person", "item_person_9", False, BoolValidator())
    item_person_10 = ConfigItem("home_interface_shopping_person", "item_person_10", False, BoolValidator())
    item_person_11 = ConfigItem("home_interface_shopping_person", "item_person_11", False, BoolValidator())
    item_person_12 = ConfigItem("home_interface_shopping_person", "item_person_12", False, BoolValidator())
    item_person_13 = ConfigItem("home_interface_shopping_person", "item_person_13", False, BoolValidator())

    item_weapon_0 = ConfigItem("home_interface_shopping_weapon", "item_weapon_0", False, BoolValidator())
    item_weapon_1 = ConfigItem("home_interface_shopping_weapon", "item_weapon_1", False, BoolValidator())
    item_weapon_2 = ConfigItem("home_interface_shopping_weapon", "item_weapon_2", False, BoolValidator())
    item_weapon_3 = ConfigItem("home_interface_shopping_weapon", "item_weapon_3", False, BoolValidator())

    ComboBox_after_use = OptionsConfigItem("home_interface_after_use", "ComboBox_after_use", 0,
                                           OptionsValidator([-1, 0, 1, 2, 3]))
    ComboBox_power_day = OptionsConfigItem("home_interface_power", "ComboBox_power_day", -1,
                                           OptionsValidator([-1, 0, 1, 2, 3, 4, 5]))
    ComboBox_power_usage = OptionsConfigItem("home_interface_power", "ComboBox_power_usage", -1,
                                             OptionsValidator([-1, 0, 1, 2, 3, 4, 5]))
    CheckBox_is_use_power = ConfigItem("home_interface_power", "CheckBox_is_use_power", False, BoolValidator())
    LineEdit_task_name = ConfigItem("home_interface_power", "LineEdit_task_name", "")
    LineEdit_stuff_x1 = ConfigItem("home_interface_power", "LineEdit_stuff_x1", 156)
    LineEdit_stuff_y1 = ConfigItem("home_interface_power", "LineEdit_stuff_y1", 744)
    LineEdit_stuff_x2 = ConfigItem("home_interface_power", "LineEdit_stuff_x2", 223)
    LineEdit_stuff_y2 = ConfigItem("home_interface_power", "LineEdit_stuff_y2", 787)
    LineEdit_chasm_x1 = ConfigItem("home_interface_power", "LineEdit_chasm_x1", 1940)
    LineEdit_chasm_y1 = ConfigItem("home_interface_power", "LineEdit_chasm_y1", 540)
    LineEdit_chasm_x2 = ConfigItem("home_interface_power", "LineEdit_chasm_x2", 2053)
    LineEdit_chasm_y2 = ConfigItem("home_interface_power", "LineEdit_chasm_y2", 595)
    chasm_pos = ConfigItem("home_interface_power", "chasm_pos", (
        0.53203125,
        0.3819444444444444,
        0.5625,
        0.41388888888888886
    ))
    stuff_pos = ConfigItem("home_interface_power", "stuff_pos",
                           (
                               0.0265625,
                               0.36666666666666664,
                               0.052734375,
                               0.3854166666666667
                           ))
    # gitee上获取到的更新数据的分辨率尺度
    resolution_scale = ConfigItem("home_interface_power", "resolution_scale", 2560)

    LineEdit_c1 = ConfigItem("home_interface_person", "LineEdit_c1", "")
    LineEdit_c2 = ConfigItem("home_interface_person", "LineEdit_c2", "")
    LineEdit_c3 = ConfigItem("home_interface_person", "LineEdit_c3", "")
    LineEdit_c4 = ConfigItem("home_interface_person", "LineEdit_c4", "")
    # 角色总数，用于翻页
    all_characters = ConfigItem("home_interface_person", "all_characters", 37)
    CheckBox_is_use_chip = ConfigItem("home_interface_person", "CheckBox_is_use_chip", False, BoolValidator())

    CheckBox_mail = ConfigItem("home_interface_reward", "CheckBox_mail", False, BoolValidator())
    CheckBox_fish_bait = ConfigItem("home_interface_reward", "CheckBox_fish_bait", False, BoolValidator())
    CheckBox_dormitory = ConfigItem("home_interface_reward", "CheckBox_dormitory", False, BoolValidator())

    # main window
    micaEnabled = ConfigItem("MainWindow", "MicaEnabled", isWin11(), BoolValidator())
    language = OptionsConfigItem(
        "MainWindow", "Language", Language.AUTO, OptionsValidator(Language), LanguageSerializer(), restart=True)
    is_ocr = ConfigItem("MainWindow", "is_ocr", False, BoolValidator())
    dpiScale = OptionsConfigItem(
        "MainWindow", "DpiScale", "Auto", OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]), restart=True)
    position = ConfigItem("MainWindow", "position", None)

    # 设置相关
    enter_interface = OptionsConfigItem("setting_personal", "enter_interface", 0, OptionsValidator([0, 1, 2]))
    server_interface = OptionsConfigItem("setting_personal", "server_interface", 0, OptionsValidator([0, 1, 2, 3]))
    checkUpdateAtStartUp = ConfigItem("Update", "CheckUpdateAtStartUp", True, BoolValidator())
    isLog = ConfigItem("setting_personal", "isLog", False, BoolValidator())
    showScreenshot = ConfigItem("setting_personal", "showScreenshot", False, BoolValidator())
    saveScaleCache = ConfigItem("setting_personal", "saveScaleCache", False, BoolValidator(), restart=True)
    autoScaling = ConfigItem("setting_personal", "autoScaling", True, BoolValidator())
    update_proxies = ConfigItem("Update", "update_proxies", '')
    cpu_support_avx2 = ConfigItem("about", "cpu_support_avx2", None)
    ocr_use_gpu = ConfigItem("setting_personal", "ocr_use_gpu", True)
    is_resize = ConfigItem("setting_personal", "is_resize", None)

    # 自动化相关
    game_title_name = ConfigItem("automation", "game_title_name", "尘白禁区")
    # 钓鱼相关
    CheckBox_is_save_fish = ConfigItem("add_fish", "CheckBox_is_save_fish", False, BoolValidator())
    CheckBox_is_limit_time = ConfigItem("add_fish", "CheckBox_is_limit_time", False, BoolValidator())
    SpinBox_fish_times = ConfigItem("add_fish", "SpinBox_fish_times", 1)
    LineEdit_fish_base = ConfigItem("add_fish", "LineEdit_fish_base", "22,255,255")
    LineEdit_fish_lower = ConfigItem("add_fish", "LineEdit_fish_lower", "20,220,245")
    LineEdit_fish_upper = ConfigItem("add_fish", "LineEdit_fish_upper", "25,255,255")
    ComboBox_fishing_mode = OptionsConfigItem("add_fish", "ComboBox_fishing_mode", 0, OptionsValidator(
        [0, 1]))
    LineEdit_fish_key = ConfigItem("add_fish", "LineEdit_fish_key", "space")
    fish_key_list = ConfigItem("add_fish", "fish_key_list", ['shift', 'space', 'ctrl'])
    ComboBox_lure_type = OptionsConfigItem("add_fish", "ComboBox_lure_type", 0,
                                           OptionsValidator([0, 1, 2, 3, 4, 5, 6, 7]))
    # 常规行动相关
    SpinBox_action_times = ConfigItem("add_action", "SpinBox_action_times", 20)
    ComboBox_run = OptionsConfigItem("add_action", "ComboBox_run", 0, OptionsValidator([0, 1]))
    # 信源解析相关
    SpinBox_max_solutions = ConfigItem("jigsaw", "SpinBox_max_solutions", 10)
    LineEdit_jigsaw_piece_1 = ConfigItem("pieces_num", "LineEdit_jigsaw_piece_1", "0")
    LineEdit_jigsaw_piece_2 = ConfigItem("pieces_num", "LineEdit_jigsaw_piece_2", "0")
    LineEdit_jigsaw_piece_3 = ConfigItem("pieces_num", "LineEdit_jigsaw_piece_3", "0")
    LineEdit_jigsaw_piece_4 = ConfigItem("pieces_num", "LineEdit_jigsaw_piece_4", "0")
    LineEdit_jigsaw_piece_5 = ConfigItem("pieces_num", "LineEdit_jigsaw_piece_5", "0")
    LineEdit_jigsaw_piece_6 = ConfigItem("pieces_num", "LineEdit_jigsaw_piece_6", "0")
    LineEdit_jigsaw_piece_7 = ConfigItem("pieces_num", "LineEdit_jigsaw_piece_7", "0")
    LineEdit_jigsaw_piece_8 = ConfigItem("pieces_num", "LineEdit_jigsaw_piece_8", "0")
    LineEdit_jigsaw_piece_9 = ConfigItem("pieces_num", "LineEdit_jigsaw_piece_9", "0")
    LineEdit_jigsaw_piece_10 = ConfigItem("pieces_num", "LineEdit_jigsaw_piece_10", "0")
    LineEdit_jigsaw_piece_11 = ConfigItem("pieces_num", "LineEdit_jigsaw_piece_11", "0")
    # 心动水弹相关
    SpinBox_water_win_times = ConfigItem("add_water", "SpinBox_water_win_times", 5)
    Slider_count_threshold = ConfigItem("add_water", "Slider_count_threshold", 60)
    Slider_template_threshold = ConfigItem("add_water", "Slider_template_threshold", 60)
    # 异星守护相关
    ComboBox_mode = OptionsConfigItem("add_alien", "ComboBox_mode", 0, OptionsValidator([0, 1]))
    # 迷宫相关
    ComboBox_mode_maze = OptionsConfigItem("add_maze", "ComboBox_mode_maze", 0, OptionsValidator([0, 1]))
    # 按摩相关
    ComboBox_wife = OptionsConfigItem("add_massaging", "ComboBox_wife", 0, OptionsValidator([0, 1, 2, 3, 4]))
    # 酒馆相关
    ComboBox_card_mode = OptionsConfigItem("add_drink", "ComboBox_card_mode", 0, OptionsValidator([0, 1]))
    SpinBox_drink_times = ConfigItem("add_drink", "SpinBox_drink_times", -1)
    CheckBox_is_speed_up = ConfigItem("add_drink", "CheckBox_is_speed_up", False, BoolValidator())


config = Config()
config.themeMode.value = Theme.AUTO
qconfig.load(str(CONFIG_FILE.absolute()), config)
