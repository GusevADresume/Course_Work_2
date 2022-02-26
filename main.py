import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from app_user import User
from search import Finder
from db import Мemorizer


class Talker():
    def __init__(self, bot_token):
        self.bot_token = bot_token
        self.user_token = ''
        self.user_id = ''
        self.user = ''
        self.photo_list = []
        self.vk = vk_api.VkApi(
            token=self.bot_token)
        self.longpoll = VkLongPoll(self.vk)
        self.item = {}
        self.candidate_list = []
        self.memorizer = ''
        self.like_flag = False
        self.user_token_flag = True

    def write_msg(self, message, att='') -> None:
        self.vk.method('messages.send',
                       {'user_id': self.user_id, 'message': message, "attachment": att, 'random_id': 0})

    def listener(self) -> object:
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    return event

    def complete_list(self) -> None:
        if self.candidate_list == []:
            self.user = User(self.user_id, self.user_token)
            self.candidate_list = Finder(self.user,self.user_token).sorter()
        else:
            print('')

    def answer_to_user(self):
        self.complete_list()
        self.memorizer = Мemorizer()
        for self.item in self.candidate_list:
            if self.memorizer.find_previos_value(self.item) == []:
                candidate = User(self.item['id'], self.user_token)
                self.photo_list = candidate.get_best_photos()
                self.memorizer.add_to_common_list(self.item)
                self.send_photo()
                yield f"{candidate.attribute_list['first_name']} {candidate.attribute_list['last_name']}\nhttps://vk.com/id{candidate.attribute_list['id']}"

    def send_photo(self) -> None:
        for i in self.photo_list:
            self.write_msg('', f"photo{i['owner_id']}_{i['id']}")

    def like(self) -> None:
        if len(self.photo_list) != 0:
            nums = []
            for num in range(len(self.photo_list)):
                nums.append(num)
            self.write_msg(f"Выберите номер фото из списка {nums} ")
            self.like_flag = True
        else:
            return self.write_msg('Пользователь не выкладывал фото')

    def send_like(self, num) -> None:
        self.user.likes(self.photo_list[int(num)]['id'])
        self.write_msg('Лайк поставлен')
        self.like_flag = False

    def remeber_user_token(self, value) -> None:
        if len(value)<80:
            self.write_msg('Введите токен пользователя со всеми правами')
        if len(value) > 80:
            self.write_msg('Пожалуйста, введите команду поиск')
            self.user_token = value
            self.user_token_flag = False

    def handler(self) -> None:
        while True:
            event = self.listener()
            self.user_id = event.user_id
            if self.user_token_flag:
                self.remeber_user_token(event.text.lower())
            elif event.text.lower() == 'поиск':
                self.write_msg('Поиск может занять несколько минут, подождите...')
                search_res = self.answer_to_user()
                self.write_msg(next(search_res))
                self.write_msg(
                    'Введите "лайк" если хотите поставить лайк.\n Введите "w" что бы добавить пользователя в избранное.\n Введите "b" что бы добавить пользователя в черный список. \n Введите "дальше" что бы пролистнуть')
            elif event.text.lower() == 'дальше':
                self.write_msg(next(search_res))
                self.write_msg(
                    'Введите "лайк" если хотите поставить лайк.\n Введите "w" что бы добавить пользователя в избранное.\n Введите "b" что бы добавить пользователя в черный список. \n Введите "дальше" что бы пролистнуть')
            elif event.text.lower() == 'лайк':
                self.like()
            elif event.text.lower() == 'w':
                self.memorizer.add_to_whitelist(self.item)
                self.write_msg(next(search_res))
            elif event.text.lower() == 'b':
                self.memorizer.add_to_blacklist(self.item)
                self.write_msg(next(search_res))
            elif self.like_flag:
                self.send_like(event.text)
                self.write_msg('Следуйте предыдущим инструкциям')
            else:
                self.write_msg('Пожалуйста, введите команду поиск')

if __name__ == '__main__':
    bot_token = input('Введите токен группы')
    tk = Talker(bot_token)
    tk.handler()
