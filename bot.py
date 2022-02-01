import random
import json
import requests
from configparser import ConfigParser
from random_username.generate import generate_username
from faker import Faker
import pprint


class Bot():
    def __init__(self,
                 config_file_path='config.ini',
                 base_url='http://127.0.0.1:8000/api/v1'
                 ):
        config = ConfigParser()
        config.read(config_file_path)
        self.base_url = base_url
        self.number_of_users = int(config['preferences']['number_of_users'])
        self.max_posts_per_user = int(
            config['preferences']['max_posts_per_user'])
        self.max_likes_per_user = int(
            config['preferences']['max_likes_per_user'])
        self.session = requests.Session()

    def generate_fake_user(self):
        username = generate_username(1)[0]
        email = username + "@mail.com"
        password = "password123"
        return {
            'username': username,
            "email": email,
            'password': password
        }

    def generate_fake_post(self):
        fake = Faker()
        title = fake.paragraph(nb_sentences=1)
        content = fake.paragraph(nb_sentences=random.randint(1, 5))
        return {
            'title': title,
            'content': content
        }

    def save_json(self, data, filename):
        json_obj = json.dumps(data, indent=4)
        with open(filename, 'w') as f:
            f.write(json_obj)
        print('JSON Written')

    def create_posts(self, token):
        url = f"{self.base_url}/posts/"
        headers = {
            'Authorization': f"Token {token}",
        }
        ammount = random.randint(0, self.max_posts_per_user)
        for i in range(ammount):
            data = self.generate_fake_post()
            response = requests.post(url,
                                     data=data,
                                     headers=headers
                                     )
            print('Creating Post', response.status_code)

    def list_posts_excluding_author(self, user_id):
        url = f"{self.base_url}/posts/"
        response = requests.get(url).json()

        new_response = []
        for post in response:
            if post['author'] != user_id:
                new_response.append(post)

        return new_response

    def like_posts(self, token, user_id):

        posts = self.list_posts_excluding_author(user_id)
        posts_ids = []
        for post in posts:
            posts_ids.append(post['id'])

        ammount = random.randint(0, self.max_likes_per_user)
        for i in range(ammount):
            post_to_like = random.choice(posts_ids)
            url = f"{self.base_url}/posts/like-dislike/{post_to_like}/"
            headers = {
                'Authorization': f"Token {token}",
            }
            response = self.session.get(url,
                                        headers=headers
                                        )
            print('Liking Post', response.status_code)

    def register_users(self):
        register_url = f"{self.base_url}/accounts/register/"

        users = []
        for i in range(self.number_of_users):
            payload = self.generate_fake_user()
            response = self.session.post(register_url, data=payload)
            print('Creating User', response.status_code)
            user_id = response.json()['user']['id']
            token = response.json()['token']
            self.create_posts(token)  # Creates random posts with this user
            self.like_posts(token, user_id)  # Likes random posts
            payload['token'] = token
            payload['id'] = user_id
            users.append(payload)

        self.save_json(users, 'users.json')


bot = Bot()
bot.register_users()
