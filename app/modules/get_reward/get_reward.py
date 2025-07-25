import time

from app.common.config import config
from app.modules.automation.timer import Timer


class GetRewardModule:
    def __init__(self, auto, logger):
        self.auto = auto
        self.logger = logger
        self.is_log = False

    def run(self):
        self.is_log = config.isLog.value
        self.auto.back_to_home()
        self.receive_work()
        self.receive_credential()

    def receive_work(self):
        timeout = Timer(30).start()
        first_finish_flag = False
        execution_flag = False
        while True:
            self.auto.take_screenshot()

            if self.auto.find_element(['定', '期', '周', '常'], 'text', crop=(
                    988 / 1920, 238 / 1080, 1083 / 1920, 288 / 1080),
                                      is_log=self.is_log) and not self.auto.click_element('键领取', 'text', crop=(
                    24 / 1920, 959 / 1080, 231 / 1920, 1032 / 1080), is_log=self.is_log):
                break
            if self.auto.click_element('获得道具', 'text', crop=(824 / 1920, 0, 1089 / 1920, 129 / 1080),
                                       is_log=self.is_log):
                first_finish_flag = True
                continue
            if self.auto.find_element('目标达成', 'text', crop=(1248 / 2560, 602 / 1440, 1595 / 2560, 724 / 1440),
                                      is_log=self.is_log):
                first_finish_flag = True
            if self.auto.click_element('键领取', 'text', crop=(24 / 1920, 959 / 1080, 231 / 1920, 1032 / 1080),
                                       is_log=self.is_log):
                continue
            if self.auto.click_element('查看详情', 'text', crop=(839 / 1920, 222 / 1080, 1049 / 1920, 290 / 1080),
                                       is_log=self.is_log):
                execution_flag = True
                self.auto.press_key('esc')
                time.sleep(0.2)
                continue
            if first_finish_flag:
                self.auto.click_element('定期', 'text', crop=(0, 225 / 1080, 128 / 1920, 282 / 1080),
                                        is_log=self.is_log)
                time.sleep(0.5)
                continue
            if self.auto.click_element('任务', 'text', crop=(1445 / 1920, 321 / 1080, 1552 / 1920, 398 / 1080),
                                       is_log=self.is_log):
                time.sleep(0.3)
                continue
            else:
                if not execution_flag:
                    self.auto.click_element('app/resource/images/reward/execution.png', 'image',
                                            crop=(812 / 1920, 891 / 1080, 908 / 1920, 985 / 1080), is_log=self.is_log)
                    first_finish_flag = True
            if self.auto.click_element('等级提升', 'text', crop=(824 / 1920, 0, 1089 / 1920, 129 / 1080)):
                self.auto.press_key('esc')
                continue

            if timeout.reached():
                self.logger.error("领取任务奖励超时")
                break
        self.auto.back_to_home()

    def receive_credential(self):
        timeout = Timer(30).start()
        first_finish_flag = False
        enter_flag = False
        while True:
            self.auto.take_screenshot()

            if first_finish_flag and self.auto.find_element(['凭证', '时装'], 'text',
                                                            crop=(2045 / 2560, 1050 / 1440, 2191 / 2560, 1109 / 1440),
                                                            is_log=self.is_log) and not self.auto.click_element(
                    '键领取', 'text', crop=(0, 950 / 1080, 295 / 1920, 1), is_log=self.is_log):
                break
            if not enter_flag:

                self.auto.click_element('凭证', 'text', crop=(280 / 1920, 541 / 1080, 389 / 1920, 607 / 1080),
                                        is_log=self.is_log)
                time.sleep(0.5)
                if not self.auto.find_element('凭证', 'text', crop=(280 / 1920, 541 / 1080, 389 / 1920, 607 / 1080),
                                              is_log=self.is_log, take_screenshot=True):
                    enter_flag = True
            else:
                if self.auto.click_element('键领取', 'text', crop=(0, 950 / 1080, 295 / 1920, 1),
                                           is_log=self.is_log):
                    continue
                if self.auto.click_element('获得道具', 'text', crop=(824 / 1920, 0, 1089 / 1920, 129 / 1080),
                                           is_log=self.is_log):
                    first_finish_flag = True
                    continue
                if not first_finish_flag:
                    if self.auto.find_element(['凭证', '时装'], 'text',
                                              crop=(2045 / 2560, 1050 / 1440, 2191 / 2560, 1109 / 1440),
                                              is_log=self.is_log):
                        self.auto.click_element_with_pos((int(1286 / self.auto.scale_x), int(1005 / self.auto.scale_y)))
                        time.sleep(0.3)
                        continue
                    if not self.auto.click_element('键领取', 'text', crop=(0, 950 / 1080, 295 / 1920, 1),
                                                   take_screenshot=True, is_log=self.is_log):
                        first_finish_flag = True
                else:
                    if self.auto.click_element(['奖', '励'], 'text', crop=(912 / 1920, 994 / 1080, 1067 / 1920, 1),
                                               is_log=self.is_log):
                        continue

            if timeout.reached():
                self.logger.error("领取凭证奖励超时")
                break
        self.auto.back_to_home()
