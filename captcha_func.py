import datetime

from captcha.image import ImageCaptcha
import random
import sqlite3
import xlsxwriter


number_list = ['0','1','2','3','4','5','6','7','8','9']
alphabet_lowercase = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
conn = sqlite3.Connection("shop_originals.db", check_same_thread=False)
cursor = conn.cursor()

def create_random_captcha_text(captcha_string_size=10):
    captcha_string_list = []
    base_char = alphabet_lowercase + number_list
    for i in range(captcha_string_size):
        # Select one character randomly.
        char = random.choice(base_char)
        # Append the character to the list.
        captcha_string_list.append(char)
    captcha_string = ''
    # Change the character list to string.
    for item in captcha_string_list:
        captcha_string += str(item)
    return captcha_string



def generate_image(text):
    image = ImageCaptcha(width = 280, height = 90)
    data = image.generate(text)
    image.write(text, '{}.png'.format(text))
    return text


def generate_excel():
    cursor.execute("SELECT * from user_data")
    res = cursor.fetchall()
    workbook = xlsxwriter.Workbook('datas.xlsx')
    worksheet = workbook.add_worksheet()
    dtime = str(datetime.datetime.today().date())

    header_data = [dtime,'user_id','telegram','twitter','tiktok','wallet', 'total ref', 'referal balance']
    for col_num, data in enumerate(header_data):
        worksheet.write(0, col_num, data,)
    for i,row in enumerate(res):
        for j,value in enumerate(row):
            worksheet.write(i+1, j, value)
    workbook.close()
    return 'datas.xlsx'


generate_excel()
