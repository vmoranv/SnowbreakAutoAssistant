import copy
import os
import re
import subprocess
import sys
from datetime import datetime
from functools import partial

import win32con
import win32gui
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt5.QtWidgets import QFrame, QWidget, QTreeWidgetItemIterator, QFileDialog
from qfluentwidgets import FluentIcon as FIF, InfoBar, InfoBarPosition, CheckBox, ComboBox, ToolButton, LineEdit, \
    BodyLabel, ProgressBar, FlyoutView, Flyout

from app.common.config import config
from app.common.logger import original_stdout, original_stderr, logger
from app.common.signal_bus import signalBus
from app.common.style_sheet import StyleSheet
from app.common.utils import get_all_children, get_date_from_api, get_gitee_text, get_start_arguments, \
    is_exist_snowbreak
from app.modules.base_task.base_task import BaseTask
from app.modules.chasm.chasm import ChasmModule
from app.modules.collect_supplies.collect_supplies import CollectSuppliesModule
from app.modules.enter_game.enter_game import EnterGameModule
from app.modules.get_reward.get_reward import GetRewardModule
from app.modules.ocr import ocr
from app.modules.person.person import PersonModule
from app.modules.shopping.shopping import ShoppingModule
from app.modules.use_power.use_power import UsePowerModule
from app.repackage.tree import TreeFrame_person, TreeFrame_weapon
from app.ui.home_interface import Ui_home
from app.view.base_interface import BaseInterface


class StartThread(QThread, BaseTask):
    is_running_signal = pyqtSignal(str)
    stop_signal = pyqtSignal()  # 添加停止信号

    def __init__(self, checkbox_dic):
        super().__init__()
        self.checkbox_dic = checkbox_dic
        self._is_running = True
        self.name_list_zh = ['自动登录', '领取物资', '商店购买', '刷体力', '人物碎片', '精神拟境', '领取奖励']

    def run(self):
        self.is_running_signal.emit('start')
        normal_stop_flag = True
        try:
            for key, value in self.checkbox_dic.items():
                if value:
                    index = int(re.search(r'\d+', key).group()) - 1
                    self.logger.info(f"当前任务：{self.name_list_zh[index]}")
                    if not self.init_auto('game'):
                        normal_stop_flag = False
                        break
                    self.auto.reset()
                    if index == 0:
                        module = EnterGameModule(self.auto, self.logger)
                        module.run()
                    elif index == 1:
                        module = CollectSuppliesModule(self.auto, self.logger)
                        module.run()
                    elif index == 2:
                        module = ShoppingModule(self.auto, self.logger)
                        module.run()
                    elif index == 3:
                        module = UsePowerModule(self.auto, self.logger)
                        module.run()
                    elif index == 4:
                        module = PersonModule(self.auto, self.logger)
                        module.run()
                    elif index == 5:
                        module = ChasmModule(self.auto, self.logger)
                        module.run()
                    elif index == 6:
                        module = GetRewardModule(self.auto, self.logger)
                        module.run()
                else:
                    # 如果value为false则进行下一个任务的判断
                    continue
        except Exception as e:
            ocr.stop_ocr()
            self.logger.warn(e)
            # traceback.print_exc()
        finally:
            # 运行完成
            if normal_stop_flag:
                self.is_running_signal.emit('end')
            else:
                # 未成功创建auto，没开游戏或屏幕比例不对
                self.is_running_signal.emit('no_auto')


def select_all(widget):
    # 遍历 widget 的所有子控件
    for checkbox in widget.findChildren(CheckBox):
        checkbox.setChecked(True)


def no_select(widget):
    # 遍历 widget 的所有子控件
    for checkbox in widget.findChildren(CheckBox):
        checkbox.setChecked(False)


class Home(QFrame, Ui_home, BaseInterface):
    def __init__(self, text: str, parent=None):
        super().__init__()
        self.setting_name_list = ['登录', '物资', '商店', '体力', '碎片']
        self.person_dic = {
            "人物碎片": "item_person_0",
            "肴": "item_person_1",
            "安卡希雅": "item_person_2",
            "里芙": "item_person_3",
            "辰星": "item_person_4",
            "茉莉安": "item_person_5",
            "芬妮": "item_person_6",
            "芙提雅": "item_person_7",
            "瑟瑞斯": "item_person_8",
            "琴诺": "item_person_9",
            "猫汐尔": "item_person_10",
            "晴": "item_person_11",
            "恩雅": "item_person_12",
            "妮塔": "item_person_13",
        }
        self.weapon_dic = {
            "武器": "item_weapon_0",
            "彩虹打火机": "item_weapon_1",
            "草莓蛋糕": "item_weapon_2",
            "深海呼唤": "item_weapon_3",
        }

        self.setupUi(self)
        self.setObjectName(text.replace(' ', '-'))
        self.parent = parent

        self.is_running = False
        self.select_person = TreeFrame_person(parent=self.ScrollArea, enableCheck=True)
        self.select_weapon = TreeFrame_weapon(parent=self.ScrollArea, enableCheck=True)

        self.game_hwnd = None

        self._initWidget()
        self._connect_to_slot()
        self.redirectOutput(self.textBrowser_log)

        self.check_game_window_timer = QTimer()
        self.check_game_window_timer.timeout.connect(self.check_game_open)
        self.checkbox_dic = None

        # self.get_tips()
        if config.checkUpdateAtStartUp.value:
            self.update_online()

    def _initWidget(self):
        for tool_button in self.SimpleCardWidget_option.findChildren(ToolButton):
            tool_button.setIcon(FIF.SETTING)

        # 设置combobox选项
        after_use_items = ['无动作', '退出游戏和代理', '退出代理', '退出游戏']
        power_day_items = ['1', '2', '3', '4', '5', '6']
        power_usage_items = ['活动材料本', '其他待开发']
        self.ComboBox_after_use.addItems(after_use_items)
        self.ComboBox_power_day.addItems(power_day_items)
        self.ComboBox_power_usage.addItems(power_usage_items)
        self.LineEdit_c1.setPlaceholderText("未输入")
        self.LineEdit_c2.setPlaceholderText("未输入")
        self.LineEdit_c3.setPlaceholderText("未输入")
        self.LineEdit_c4.setPlaceholderText("未输入")

        self.BodyLabel_enter_tip.setText(
            "### 提示\n* 去设置里选择你的区服\n* 建议勾选“自动打开游戏”，勾选后根据上方教程选择好对应的路径\n* 点击“开始”按钮会自动打开游戏")
        self.BodyLabel_person_tip.setText(
            "### 提示\n* 输入代号而非全名，比如想要刷“凯茜娅-朝翼”，就输入“朝翼”")
        self.PopUpAniStackedWidget.setCurrentIndex(0)
        self.TitleLabel_setting.setText("设置-" + self.setting_name_list[self.PopUpAniStackedWidget.currentIndex()])
        self.PushButton_start.setShortcut("F1")
        self.PushButton_start.setToolTip("快捷键：F1")

        self.gridLayout.addWidget(self.select_person, 1, 0)
        self.gridLayout.addWidget(self.select_weapon, 2, 0)

        self._load_config()
        # 和其他控件有相关状态判断的，要放在load_config后
        self.ComboBox_power_day.setEnabled(self.CheckBox_is_use_power.isChecked())
        self.PushButton_select_directory.setEnabled(self.CheckBox_open_game_directly.isChecked())

        StyleSheet.HOME_INTERFACE.apply(self)
        # 使背景透明，适应主题
        self.ScrollArea.enableTransparentBackground()
        self.ScrollArea_tips.enableTransparentBackground()

    def _connect_to_slot(self):
        self.PushButton_start.clicked.connect(self.on_start_button_click)
        self.PrimaryPushButton_path_tutorial.clicked.connect(self.on_path_tutorial_click)
        self.PushButton_select_all.clicked.connect(lambda: select_all(self.SimpleCardWidget_option))
        self.PushButton_no_select.clicked.connect(lambda: no_select(self.SimpleCardWidget_option))
        self.PushButton_select_directory.clicked.connect(self.on_select_directory_click)

        self.ToolButton_entry.clicked.connect(lambda: self.set_current_index(0))
        self.ToolButton_collect.clicked.connect(lambda: self.set_current_index(1))
        self.ToolButton_shop.clicked.connect(lambda: self.set_current_index(2))
        self.ToolButton_use_power.clicked.connect(lambda: self.set_current_index(3))
        self.ToolButton_person.clicked.connect(lambda: self.set_current_index(4))

        self.CheckBox_open_game_directly.stateChanged.connect(self.change_auto_open)

        signalBus.sendHwnd.connect(self.set_hwnd)

        self._connect_to_save_changed()

    def _load_config(self):
        for widget in self.findChildren(QWidget):
            # 动态获取 config 对象中与 widget.objectName() 对应的属性值
            config_item = getattr(config, widget.objectName(), None)
            if config_item:
                if isinstance(widget, CheckBox):
                    widget.setChecked(config_item.value)  # 使用配置项的值设置 CheckBox 的状态
                elif isinstance(widget, ComboBox):
                    # widget.setPlaceholderText("未选择")
                    widget.setCurrentIndex(config_item.value)
                elif isinstance(widget, LineEdit):
                    widget.setText(str(config_item.value))
        self._load_item_config()

    def _load_item_config(self):
        item = QTreeWidgetItemIterator(self.select_person.tree)
        while item.value():
            config_item = getattr(config, self.person_dic[item.value().text(0)], None)
            item.value().setCheckState(0, Qt.Checked if config_item.value else Qt.Unchecked)
            item += 1

        item2 = QTreeWidgetItemIterator(self.select_weapon.tree)
        while item2.value():
            config_item2 = getattr(config, self.weapon_dic[item2.value().text(0)], None)
            item2.value().setCheckState(0, Qt.Checked if config_item2.value else Qt.Unchecked)
            item2 += 1

    def _connect_to_save_changed(self):
        # 人物和武器的单独保存
        self.select_person.itemStateChanged.connect(self.save_item_changed)
        self.select_weapon.itemStateChanged.connect(self.save_item2_changed)

        children_list = get_all_children(self)
        for children in children_list:
            # 此时不能用lambda，会使传参出错
            if isinstance(children, CheckBox):
                # children.stateChanged.connect(lambda: save_changed(children))
                children.stateChanged.connect(partial(self.save_changed, children))
            elif isinstance(children, ComboBox):
                children.currentIndexChanged.connect(partial(self.save_changed, children))
            elif isinstance(children, LineEdit):
                children.editingFinished.connect(partial(self.save_changed, children))

    def set_hwnd(self, hwnd):
        self.game_hwnd = hwnd

    def on_path_tutorial_click(self):
        """查找启动器路径教程，记得添加进build路径"""
        view = FlyoutView(
            title="如何查找对应游戏路径",
            content='不管你是哪个渠道服的玩家，第一步都应该先去设置里选服\n国际服选完服之后选择类似"E:\SteamLibrary\steamapps\common\SNOWBREAK"的路径\n官服和b服的玩家打开尘白启动器，新版或者旧版启动器都找到启动器里对应的设置\n在下面的路径选择中找到并选择刚才你看到的路径',
            image="asset/path_tutorial.png",
            isClosable=True,
        )
        # 调整布局
        view.widgetLayout.insertSpacing(1, 5)
        view.widgetLayout.addSpacing(5)

        w = Flyout.make(view, self.PrimaryPushButton_path_tutorial, self)
        view.closed.connect(w.close)

    def update_online(self):
        """通过gitee在线更新"""
        text = get_gitee_text("update_data.txt")
        # 返回字典说明必定出现报错了
        if isinstance(text, dict):
            logger.error(text["error"])
            return
        # 只有在获得新内容的时候才做更新动作,text[0]为第一行：坐标等数据
        if text[0] != config.update_data.value or not config.date_tip.value:
            if config.isLog.value:
                logger.info(f'获取到更新信息：{text[0]}')
            # 更新配置
            config.set(config.update_data, text[0])

            data = text[0].split("_")
            # 设置任务名
            config.set(config.task_name, data[9])
            # 更新链活动提醒
            url = f"https://www.cbjq.com/api.php?op=search_api&action=get_article_detail&catid={data[10]}&id={data[11]}"
            self.get_tips(url=url)
            # 更新材料和深渊位置在use_power.py
        else:
            #
            self.get_tips()

    def on_select_directory_click(self):
        """ 选择启动器路径 """
        # file_path, _ = QFileDialog.getOpenFileName(self, "选择启动器", config.LineEdit_game_directory.value,
        #                                            "Executable Files (*.exe);;All Files (*)")
        folder = QFileDialog.getExistingDirectory(self, '选择游戏文件夹', "./")
        if not folder or config.LineEdit_game_directory.value == folder:
            return
        self.LineEdit_game_directory.setText(folder)
        self.LineEdit_game_directory.editingFinished.emit()

    def change_auto_open(self, state):
        if state == 2:
            InfoBar.success(
                title='已开启',
                content=f"点击“开始”按钮时将自动启动游戏",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=2000,
                parent=self
            )
        else:
            InfoBar.success(
                title='已关闭',
                content=f"点击“开始”按钮时不会自动启动游戏",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=2000,
                parent=self
            )

    def open_game_directly(self):
        """直接启动游戏"""
        # 用户提供的能在启动器找到的路径
        start_path = config.LineEdit_game_directory.value
        start_path = start_path.replace("/", "\\")
        game_channel = config.server_interface.value
        exe_path = os.path.join(start_path, r'game\Game\Binaries\Win64\Game.exe')
        try:
            # 检查游戏主程序是否存在
            if not os.path.exists(exe_path):
                logger.error(f'游戏主程序不存在: {exe_path}')
                return
            launch_args = get_start_arguments(start_path, game_channel)
            if not launch_args:
                logger.error(f"游戏启动失败未找到对应参数，start_path：{start_path}，game_channel:{game_channel}")
                return
            else:
                if not is_exist_snowbreak():
                    # 尝试以管理员权限运行
                    subprocess.Popen([exe_path] + launch_args)
                    logger.debug(f'正在启动 {exe_path} {launch_args}')
                else:
                    logger.info(f"游戏窗口已存在")
                self.check_game_window_timer.start(500)
        except FileNotFoundError:
            logger.error(f'没有找到对应文件: {exe_path}')
        except Exception as e:
            logger.error(f'出现报错: {e}')

    def check_game_open(self):
        hwnd = is_exist_snowbreak()
        if hwnd:
            self.check_game_window_timer.stop()
            logger.info(f'已检测到游戏窗口：{hwnd}')
            self.after_start_button_click(self.checkbox_dic)

    def on_start_button_click(self):
        """点击开始按钮后的逻辑"""
        checkbox_dic = {}
        for checkbox in self.SimpleCardWidget_option.findChildren(CheckBox):
            if checkbox.isChecked():
                checkbox_dic[checkbox.objectName()] = True
            else:
                checkbox_dic[checkbox.objectName()] = False

        # 开启游戏:勾选且游戏窗口未打开时启用
        if config.CheckBox_open_game_directly.value and not is_exist_snowbreak():
            self.checkbox_dic = checkbox_dic
            self.open_game_directly()
        else:
            self.after_start_button_click(checkbox_dic)

    def after_start_button_click(self, checkbox_dic):
        if any(checkbox_dic.values()):
            if not self.is_running:
                # 对字典进行排序
                sorted_dict = dict(
                    sorted(checkbox_dic.items(), key=lambda item: int(re.search(r'\d+', item[0]).group())))
                # logger.debug(sorted_dict)
                self.redirectOutput(self.textBrowser_log)
                self.start_thread = StartThread(sorted_dict)
                self.start_thread.start()
                self.start_thread.is_running_signal.connect(self.handle_start)
            else:
                self.start_thread.stop()
        else:
            logger.error("需要至少勾选一项任务才能开始")
            # InfoBar.error(
            #     title='未勾选工作',
            #     content="需要至少勾选一项工作才能开始",
            #     orient=Qt.Horizontal,
            #     isClosable=False,  # disable close button
            #     position=InfoBarPosition.TOP_RIGHT,
            #     duration=2000,
            #     parent=self
            # )

    def handle_start(self, str_flag):
        """设置按钮"""
        if str_flag == 'start':
            self.is_running = True
            self.set_checkbox_enable(False)
            self.PushButton_start.setText("停止")
        elif str_flag == 'end':
            self.is_running = False
            self.set_checkbox_enable(True)
            self.PushButton_start.setText("开始")
            # 后处理
            self.after_finish()
            self.resize_window()  # 把窗口还原成原本位置
        elif str_flag == 'no_auto':
            self.is_running = False
            self.set_checkbox_enable(True)
            self.PushButton_start.setText("开始")
            text = "助手会自动缩放窗口至1920*1080" if config.autoScaling.value else "然后手动缩放窗口到16:9并贴在屏幕左上角"
            InfoBar.error(
                title='未成功初始化auto',
                content=f"打开游戏（不是启动器），{text}，然后再点击开始",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=2000,
                parent=self
            )

    def resize_window(self):
        # 恢复窗口
        if config.is_resize.value is not None:
            state = config.is_resize.value
            config.set(config.is_resize, None)
            win32gui.SetWindowPos(
                self.game_hwnd,
                win32con.HWND_TOP,
                state[0],  # 原始左边界
                state[1],  # 原始上边界
                state[2] - state[0],  # 宽度
                state[3] - state[1],  # 高度
                win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE
            )

    def after_finish(self):
        # 任务结束后的后处理
        if self.ComboBox_after_use.currentIndex() == 0:
            return
        elif self.ComboBox_after_use.currentIndex() == 1:
            if self.game_hwnd:
                win32gui.SendMessage(self.game_hwnd, win32con.WM_CLOSE, 0, 0)
            else:
                self.logger.warn('home未获取窗口句柄，无法关闭游戏')
            self.parent.close()
        elif self.ComboBox_after_use.currentIndex() == 2:
            self.parent.close()
        elif self.ComboBox_after_use.currentIndex() == 3:
            if self.game_hwnd:
                win32gui.SendMessage(self.game_hwnd, win32con.WM_CLOSE, 0, 0)
            else:
                self.logger.warn('home未获取窗口句柄，无法关闭游戏')

    def set_checkbox_enable(self, enable: bool):
        for checkbox in self.findChildren(CheckBox):
            checkbox.setEnabled(enable)

    def set_current_index(self, index):
        try:
            self.TitleLabel_setting.setText("设置-" + self.setting_name_list[index])
            self.PopUpAniStackedWidget.setCurrentIndex(index)
        except Exception as e:
            self.logger.error(e)

    def save_changed(self, widget):
        # logger.debug(f"触发save_changed:{widget.objectName()}")
        # 当与配置相关的控件状态改变时调用此函数保存配置
        if isinstance(widget, CheckBox):
            config.set(getattr(config, widget.objectName(), None), widget.isChecked())
            if widget.objectName() == 'CheckBox_is_use_power':
                self.ComboBox_power_day.setEnabled(widget.isChecked())
            elif widget.objectName() == 'CheckBox_open_game_directly':
                self.PushButton_select_directory.setEnabled(widget.isChecked())
        elif isinstance(widget, ComboBox):
            config.set(getattr(config, widget.objectName(), None), widget.currentIndex())
        elif isinstance(widget, LineEdit):
            # 对坐标进行数据转换处理
            if 'x1' in widget.objectName() or 'x2' in widget.objectName() or 'y1' in widget.objectName() or 'y2' in widget.objectName():
                config.set(getattr(config, widget.objectName(), None), int(widget.text()))
            else:
                config.set(getattr(config, widget.objectName(), None), widget.text())

    def save_item_changed(self, index, check_state):
        # print(index, check_state)
        config.set(getattr(config, f"item_person_{index}", None), False if check_state == 0 else True)

    def save_item2_changed(self, index, check_state):
        # print(index, check_state)
        config.set(getattr(config, f"item_weapon_{index}", None), False if check_state == 0 else True)

    def get_time_difference(self, date_due: str):
        """
        通过给入终止时间获取剩余时间差和时间百分比
        :param date_due: 持续时间，格式'03.06-04.17'
        :return:如果活动过期，则返回None,否则返回时间差，剩余百分比
        """
        current_year = datetime.now().year
        start_time = datetime.strptime(f"{current_year}.{date_due.split('-')[0]}", "%Y.%m.%d")
        end_time = datetime.strptime(f"{current_year}.{date_due.split('-')[1]}", "%Y.%m.%d")
        if end_time.month < start_time.month:
            end_time = datetime.strptime(f"{current_year + 1}.{date_due.split('-')[1]}", "%Y.%m.%d")
        # 获取当前日期和时间
        now = datetime.now()

        total_difference = end_time - start_time
        total_day = total_difference.days + 1
        if now < start_time:
            # 将当前日期替换成开始日期
            now = start_time
        time_difference = end_time - now
        days_remaining = time_difference.days + 1
        if days_remaining < 0:
            return 0, 0

        return days_remaining, (days_remaining / total_day) * 100, days_remaining == total_day

    def get_tips(self, url=None):
        if url:
            tips_dic = get_date_from_api(url)
            if "error" in tips_dic.keys():
                logger.error(tips_dic["error"])
                return
            config.set(config.date_tip, tips_dic)
        else:
            if not config.date_tip.value:
                InfoBar.error(
                    title='活动日程更新失败',
                    content=f"本地没有存储信息且未获取到url",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP_RIGHT,
                    duration=2000,
                    parent=self
                )
                return
            tips_dic = copy.deepcopy(config.date_tip.value)
        for key, value in tips_dic.items():
            tips_dic[key] = self.get_time_difference(value)

        index = 0
        items_list = []
        try:
            for key, value in tips_dic.items():
                if self.SimpleCardWidget_tips.findChild(BodyLabel, name=f"BodyLabel_tip_{index + 1}"):
                    BodyLabel_tip = self.SimpleCardWidget_tips.findChild(BodyLabel, name=f"BodyLabel_tip_{index + 1}")
                else:
                    # 创建label
                    BodyLabel_tip = BodyLabel(self.scrollAreaWidgetContents_tips)
                    BodyLabel_tip.setObjectName(f"BodyLabel_tip_{index + 1}")
                if self.SimpleCardWidget_tips.findChild(ProgressBar, name=f"ProgressBar_tip{index + 1}"):
                    ProgressBar_tip = self.SimpleCardWidget_tips.findChild(ProgressBar,
                                                                           name=f"ProgressBar_tip{index + 1}")
                else:
                    # 创建进度条
                    ProgressBar_tip = ProgressBar(self.scrollAreaWidgetContents_tips)
                    ProgressBar_tip.setObjectName(f"ProgressBar_tip{index + 1}")
                if value[0] == 0:
                    BodyLabel_tip.setText(f"{key}已结束")
                else:
                    if value[2]:
                        BodyLabel_tip.setText(f"{key}未开始")
                    else:
                        BodyLabel_tip.setText(f"{key}剩余：{value[0]}天")
                ProgressBar_tip.setValue(int(value[1]))
                items_list.append([BodyLabel_tip, ProgressBar_tip, value[1]])

                index += 1
            items_list.sort(key=lambda x: x[2])
            for i in range(len(items_list)):
                self.gridLayout_tips.addWidget(items_list[i][0], i + 1, 0, 1, 1)
                self.gridLayout_tips.addWidget(items_list[i][1], i + 1, 1, 1, 1)
            # 传入url时说明是新数据，此时才需要提醒
            if url:
                InfoBar.success(
                    title='活动日程更新成功',
                    content=f"获取到新的活动信息，已更新至“提醒”",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP_RIGHT,
                    duration=2000,
                    parent=self
                )

        except Exception as e:
            logger.error(f"更新控件出错：{e}")

    def closeEvent(self, event):
        # 恢复原始标准输出
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        super().closeEvent(event)
