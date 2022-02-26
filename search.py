import requests
from dateutil import parser
from datetime import datetime as DT
import binascii
from db import Мemorizer
from app_user import User
import time


class Finder():
    def __init__(self, user, token):
        self.token = token
        self.user = user
        self.attribute_list = user.attribute_list
        self.param_dict = self.request_param()
        self.match_index = 0

    def request_param(self) -> dict:
        param_dict = {}
        param_dict['age_from'] = (self.age_calc(self.attribute_list['bdate'])) - 5
        param_dict['age_to'] = (self.age_calc(self.attribute_list['bdate'])) + 5
        param_dict['sex'] = 1 if self.attribute_list['sex'] == 2 else 2
        param_dict['city'] = self.attribute_list['city']['id']
        return param_dict

    def age_calc(self, date) -> int:
        result = (DT.date(DT.now()) - (DT.date(parser.parse(date)))).days // 365
        return result

    def request(self, status) -> list:
        age_request = 9
        respons_list = []
        for i in range(age_request):
            time.sleep(1)
            url = 'https://api.vk.com/method/users.search/'
            params = {'access_token': self.token, 'sort': 1, 'offset': 0, 'count': 1000,
                      'common_count': 0, 'sex': self.param_dict['sex'], 'status': status,
                      'age_from': self.param_dict['age_from'] + i, 'age_to': self.param_dict['age_to'],
                      'city': self.param_dict['city'],
                      'fields': 'interests, about, books, music, connections, people_main, life_main, personal, political',
                      'v': '5.131'}
            respons = requests.get(url, params=params)
            respons_list = respons_list + respons.json()['response']['items']
        return respons_list

    def matcher(self, user_profile, candidate_profile) -> bool:
        try:
            self.match_index += self._direct_matching(user_profile['personal']['religion_id'],
                                                      candidate_profile['personal']['religion_id'])
        except:
            self.match_index += 2
        try:
            self.match_index += self._direct_matching(user_profile['personal']['political'],
                                                      candidate_profile['personal']['political'])
        except:
            self.match_index += 2
        try:
            self.match_index += self._direct_matching(user_profile['personal']['life_main'],
                                                      candidate_profile['personal']['life_main'])
        except:
            self.match_index += 2
        try:
            self.match_index += self._not_direct_match(user_profile['personal']['smoking'],
                                                       candidate_profile['personal']['smoking'], 'habits')
        except:
            self.match_index += 2
        try:
            self.match_index += self._not_direct_match(user_profile['personal']['life_main'],
                                                       candidate_profile['personal']['life_main'])
        except:
            self.match_index += 2
        try:
            self.match_index += self.compaire(user_profile['personal']['inspired_by'],
                                              candidate_profile['personal']['inspired_by'])
        except:
            self.match_index += 2
        try:
            self.match_index += self.lang_macth(user_profile['personal']['langs'],
                                                candidate_profile['personal']['langs'])
        except:
            self.match_index += 2
        try:
            self.match_index += self.compaire(user_profile['about'], candidate_profile['about'])
        except:
            self.match_index += 2
        try:
            self.match_index += self.compaire(user_profile['interests'], candidate_profile['interests'])
        except:
            self.match_index += 2
        try:
            self.match_index += self.compaire(user_profile['books'], candidate_profile['books'])
        except:
            self.match_index += 2

        if self.match_index >= 190:
            return True
        else:
            return False

    def lang_macth(self, value1, value2) -> int:
        result = 0
        for i in value1:
            if i in value2:
                result += 3
        return result

    def canonize_text(self, value) -> list:
        symbols = '.,!?:;-\n\r()'
        words = (u'это', u'как', u'так',
                 u'и', u'в', u'над',
                 u'к', u'до', u'не',
                 u'на', u'но', u'за',
                 u'то', u'с', u'ли',
                 u'а', u'во', u'от',
                 u'со', u'для', u'о',
                 u'же', u'ну', u'вы',
                 u'бы', u'что', u'кто',
                 u'он', u'она')
        return ([x for x in [y.strip(symbols) for y in value.lower().split()] if x and (x not in words)])

    def shingle(self, value) -> list:
        shingleLen = 3
        out = []
        for i in range(len(value) - (shingleLen - 1)):
            out.append(binascii.crc32(' '.join([x for x in value[i:i + shingleLen]]).encode('utf-8')))

        return out

    def compaire(self, value1, value2) -> int:
        same = 0
        for i in range(len(value1)):
            if value1[i] in value2:
                same += 1

        result = int(same * 2 / float(len(value1) + len(value2)) * 10)
        if result >= 9:
            return 9
        elif result >= 7:
            return 5
        elif result > 5:
            return 3
        else:
            return 0

    def _direct_matching(self, value1, value2) -> int:
        if value1 == value2:
            return 9
        else:
            return 0

    def _not_direct_match(self, value1, value2, flag='') -> int:
        m_list = ['56', '65', '82', '28']
        if flag == 'habits':
            if abs(value1 - value2) <= 1:
                return 9
            if abs(value1 - value2) <= 3:
                return 5
            else:
                return 0
        else:
            if value1 == value2:
                return 9
            elif str(value1) + str(value2) in m_list:
                return 5
            else:
                return 0

    def check_common_subscriptions(self, item) -> None:
        try:
            candidate = User(item['id'])
            for group in candidate.group_list():
                if group in self.user.group_list():
                    self.match_index += 2
            for friend in candidate.friends_list:
                if friend in self.user.friends_list:
                    self.match_index += 9
        except:
            self.match_index += 0

    def sorter(self) -> dict:
        search_list = []
        memorizer = Мemorizer()
        req_list = self.request(6) + self.request(1) + self.request(5)
        for item in req_list:
            if self.matcher(self.attribute_list, item):
                self.check_common_subscriptions(item)
                if self.match_index >= 210:
                    if memorizer.find_previos_value(item) == []:
                        search_list.append(item)
                        self.match_index = 0
            else:
                continue
        return search_list



