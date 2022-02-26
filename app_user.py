import requests
import time


class User():

    def __init__(self, id, token):
        self.id = id
        self.app_token = token
        self.attribute_list = self.about_info()
        self.g_list = self.group_list()
        self.friends_list = self.friend_list()

    def about_info(self) -> list:
        url = 'https://api.vk.com/method/users.get/'
        params = {'user_id': self.id, 'access_token': self.app_token, 'v': '5.131',
                  'fields': 'bdate, about, sex, city,  books, music, interests, connections,life_main, relation, people_main, life_main, personal, political'}
        respons = requests.get(url, params=params)
        return respons.json()['response'][0]


    def group_list(self) -> list:
        url = 'https://api.vk.com/method/groups.get/'
        params = {'user_id': self.id, 'access_token': self.app_token, 'v': '5.131'}
        respons = requests.get(url, params=params)
        return respons.json()

    def friend_list(self) -> list:
        url = 'https://api.vk.com/method/friends.get/'
        param = {'user_id': self.id, 'access_token': self.app_token, 'v': '5.131'}
        try:
            response = requests.get(url, params=param)
            return response.json()['response']['items']
        except:
            return []

    def get_best_photos(self) -> list:
        user_photos = []
        try:
            photo_dict = {'id': '', 'popularity_index': '', 'owner_id': ''}
            url = f'https://api.vk.com/method/photos.get/'
            params = {'user_id': self.id, 'access_token': self.app_token, 'v': '5.131', 'album_id': 'profile',
                      'extended': '1'}
            respons = requests.get(url, params=params)
            time.sleep(1)
            for item in respons.json()['response']['items']:
                photo_dict['id'] = item['id']
                photo_dict['popularity_index'] = int(item['likes']['count']) + int(item['comments']['count'])
                photo_dict['owner_id'] = item['owner_id']
                user_photos.append(photo_dict)
                photo_dict = {'id': '', 'popularity_index': '', 'owner_id': ''}
                user_photos = sorted(user_photos, key=lambda d: d['popularity_index'])[-3:]
        except:
            user_photos = []

        user_photos = user_photos + self.tagged_photos()
        return user_photos

    def tagged_photos(self) -> list:
        user_photos = []
        try:
            photo_dict = {'id': '', 'popularity_index': '', 'owner_id': ''}
            url = f'https://api.vk.com/method/photos.getUserPhotos/'
            params = {'user_id': self.id, 'access_token': self.app_token, 'v': '5.131', 'extended': '1'}
            respons = requests.get(url, params=params)
            for item in respons.json()['response']['items']:
                photo_dict['id'] = item['id']
                print('try2', type(user_photos))
                photo_dict['popularity_index'] = int(item['likes']['count']) + int(item['comments']['count'])
                photo_dict['owner_id'] = item['owner_id']
                user_photos.append(photo_dict)
                photo_dict = {'id': '', 'popularity_index': '', 'owner_id': ''}
        except:
            user_photos = []
        return user_photos

    def likes(self, photo_id):
        url = f'https://api.vk.com/method/likes.add/'
        params = {'user_id': self.id, 'access_token': self.app_token, 'type': 'photo', 'v': '5.131',
                  'item_id': photo_id}
        respons = requests.get(url, params=params)
        return respons.json()


