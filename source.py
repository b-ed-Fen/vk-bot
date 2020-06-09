import os
import requests
import time
import vk_api
from datetime import datetime, date, timedelta
from time import strftime

from pycbrf.toolbox import ExchangeRates
from vk_api.longpoll import VkLongPoll

token = os.environ.get("KEY")
second_group = os.environ.get("second group")
vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)
count = 0
lost = 0

photo_id = ["photo-191088353_457239574", "photo-191088353_457239575", "photo-191088353_457239576",
            "photo-191088353_457239577", "photo-191088353_457239578", "photo-191088353_457239579",
            "photo-191088353_457239580", "photo-191088353_457239581", "photo-191088353_457239582",
            "photo-191088353_457239583", "photo-191088353_457239584", "photo-191088353_457239585",
            "photo-191088353_457239586", "photo-191088353_457239587", "photo-191088353_457239573"]


def invoice_week(dt):
    w = datetime(dt.year, dt.month, dt.day)
    w = w.strftime("%d %b %Y")
    d = time.strptime(w, "%d %b %Y")

    if int(dt.isoweekday()) == 7:
        return int(strftime("%U", d))
    else:
        return int(strftime("%U", d)) + 1


def parity():
    if (invoice_week(date.today()) % 2) == 0:  # зеркальна настоящей
        return "Нечетная"
    else:
        return "Четная"


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message})


def photo(user_id, num, random_value):
    vk.method("messages.send",
              {"peer_id": user_id, "message": "Неделя: " + str(parity()), "attachment": photo_id[num-1],
               "random_id": random_value})


print("-invoice week: " + str(invoice_week(date.today())))  # проверка значения на сервере
print("-GMT3: " + str(datetime.now() + timedelta(minutes=180)))  # GMT +3 время


def notrandom():
    millis = int(round(time.time() * 1000))
    answer = (str(millis)[(len(str(millis)) - 7):len(str(millis))])
    return int(answer)


def course():
    today = datetime.today()
    rates = ExchangeRates(today.strftime("%Y-%m-%d"))
    value = {'USD': rates['USD'].value, 'EUR': rates['EUR'].value, 'UAH': rates['UAH'].value}
    return value


def group_check(id):
    temp = ''
    for i in second_group:
        if i != ',':
            temp += i
        else:
            if int(temp) == id:
                return True
            temp = ''
    return False


# Основной цикл
while True:
    try:
        start_time = time.time()
        messages = vk.method("messages.getConversations", {"offset": 0, "count": 20, "filter": "unanswered"})

        if messages["count"] > 0:
            id = messages["items"][0]["last_message"]["from_id"]
            body = messages["items"][0]["last_message"]["text"]
            command = body[1:].lower()
            d = 0
            if group_check(id):
                d += 7

            if body[0] == "/":
                count += 1
                if (command == "пн") or (command == "понедельник"):
                    d += 1

                elif (command == "вт") or (command == "вторник"):
                    d += 2

                elif (command == "ср") or (command == "среда"):
                    d += 3

                elif (command == "чт") or (command == "четверг"):
                    d += 4

                elif (command == "пт") or (command == "пятница"):
                    d += 5

                elif (command == "сб") or (command == "суббота"):
                    d += 6

                elif (command == "вс") or (command == "воскресенье "):
                    d += 7

                elif (command == "с") or (command == "c") or (command == "сегодня"):
                    d = (datetime.now() + timedelta(minutes=180)).isoweekday()
                    if group_check(id):
                        d += 7

                elif (command == "з") or (command == "завтра"):
                    d = (datetime.now() + timedelta(minutes=180)).isoweekday() + 1
                    if d > 7:
                        d = 1
                    if group_check(id):
                        d += 7

                elif command == "сейчас":
                    answer = str(date.today()) + "\n" + "Номер дня недели: " + str(
                        (datetime.now() + timedelta(minutes=180)).isoweekday()) + "\n" + "Неделя: " + str(parity())
                    vk.method("messages.send", {"peer_id": id, "message": answer, "random_id": notrandom()})

                elif command == "команды":
                    answer = {
                        "Вот команды, которые на которые у меня есть ответ:"
                        + "\n/сейчас – вызвать: полную дату, номер дня недели, четность и нечетность недели. "
                        + "\n/день_недели – например «/понедельник» или «/пн»."
                        + "\n/с или /сегодня – расписание на сегодня. "
                        + "\n/з или /завтра – расписание на завтра."
                        + "\n/курс - курс доллара к рублю по цб."
                        + "\n/команды – вызвать этот текс снова."
                    }
                    vk.method("messages.send", {"peer_id": id, "message": answer, "random_id": notrandom()})

                elif command == "хтоя":
                    count -= 1
                    answer = {
                        "Твой id: " + str(id)
                        + "\nМой id: " + str(notrandom()) + " (временно)"
                        + "\nНомер недели: " + str(invoice_week(datetime.now() + timedelta(minutes=180)))
                        + "\nКол. успешных запросов:   " + str(count)
                        + "\nКол. запросов без ответа: " + str(lost)
                        + "\nСерверное время: " + str(datetime.now())
                        + "\nВычисленное время: " + str(datetime.now() + timedelta(minutes=180))
                        + "\nВремя выполнения этой комманды: " + str(time.time() - start_time)}

                    vk.method("messages.send", {"peer_id": id, "message": answer, "random_id": notrandom()})

                elif command == "курс":
                    value = course()
                    answer = "1 $ = " + str(value['USD']) + " ₽\n"
                    answer += "1 $ = " + str(value['EUR']) + " €\n"
                    answer += "1 $ = " + str(value['UAH']) + " ₴\n"
                    vk.method("messages.send", {"peer_id": id, "message": answer, "random_id": notrandom()})

                else:
                    count -= 1
                    lost += 1
                    vk.method("messages.send", {"peer_id": id,
                                                "message": "Мне не известна эта команда...\nДля просмотра команд "
                                                           "напишите /команды",
                                                "random_id": notrandom()})

            if body.lower() == "f":
                photo(id, 15, notrandom())

            if d > 0:
                photo(id, d, notrandom())
                d = 0
                
    except Exception as e:
        time.sleep(150)
        print(str(e))
