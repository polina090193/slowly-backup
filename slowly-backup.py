import os
from datetime import datetime
import requests

slowly_base_api_url = 'https://api.getslowly.com/'
all_friends_path = 'users/me/friends/v2'
attachments_path = 'attachments/'

file = open("token.txt", "r")
token = file.read()

def build_slowly_api_url_with_token(relative_path):
    return f"{slowly_base_api_url}{relative_path}?token={token}"

def build_all_letters_of_a_friend_path(friend_id):
    return f"friend/{friend_id}/all"

current_date = datetime.now().strftime('%d-%m-%Y')

friends = requests.get(
    build_slowly_api_url_with_token(all_friends_path))

if friends.status_code == 200:

  friends_list = friends.json()['friends']

  for friend in friends_list:
      print(f"Saving {friend['name']}'s letters...\n")
      friend_id = friend['id']
      friend_name = friend['name']

      all_letters = requests.get(
        build_slowly_api_url_with_token(build_all_letters_of_a_friend_path(friend_id)))
      
      if all_letters.status_code == 200:

        all_letters_list = all_letters.json()['comments']['data']

        for index, letter in enumerate(all_letters_list):
          letter_date = datetime.strptime(letter['deliver_at'], '%Y-%m-%d %H:%M:%S')
          letter_date_str = letter_date.strftime('%d-%m-%Y')

          print(f"Saving {letter_date_str} of {friend['name']}...")

          letter_dir_name = f"slowly-backups/{current_date}/{friend_name}/{index + 1} {letter_date_str}"

          os.makedirs(letter_dir_name, exist_ok=True)

          # Saving text
          text_file_name = f"{letter_dir_name}/{current_date}_{friend_name}_text.txt"

          with open(text_file_name, 'w', encoding='utf-8') as file:
            file.write(letter['body'])

          # Saving attachments
          if (letter['attachments'] is not None):
            attachments_names_list = letter['attachments'].split(",")
            print(f"{len(attachments_names_list)} attachments found. Saving...")

            for attachment_name in attachments_names_list:
              if (attachment_name is not None) and (len(attachment_name) > 0):
                attachment = requests.get(build_slowly_api_url_with_token(attachments_path + attachment_name))
              
                attachment_file_name = f"{letter_dir_name}/{attachment_name}"

                if attachment.status_code == 200:
                  with open(attachment_file_name, 'wb') as file:
                      file.write(attachment.content)
                  print(f"{attachment_name} saved!")
                else:
                    print(f"Failed to download the attachment: {attachment_name}")

          print(f"{letter_date_str} done!\n")

        print(f"{friend['name']}'s letters backup done!\n\n")
      
      else:
        print("Failed to download the letters.")
    
else:
  print("Failed to download the friends list.")