import sys
import random
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic, QtCore
import sqlite3
from PIL import Image, ImageDraw, ImageFont


class Hero:
    def __init__(self):
        self.stat = {'Сила': 1,
                     'Ловкость': 1,
                     'Телосложение': 1,
                     'Интеллект': 1,
                     'Мудрость': 1,
                     'Харизма': 1}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('static/ui/main.ui', self)
        self.setWindowTitle('Генератор DnD персонажей')
        # Открытия окна для определение пользователем характеристик
        self.stat.activated[str].connect(self.characteristics)
        # Создание персонажа
        self.generation.clicked.connect(self.generat)
        # Изменение уровня или опыта
        self.level.valueChanged.connect(self.update)
        self.expa.valueChanged.connect(self.update)
        self.expa_for_up = [0, 300, 900, 2700, 6500,
                            14000, 23000, 34000, 48000,
                            64000, 85000, 100000, 120000,
                            140000, 165000, 195000, 225000,
                            265000, 305000, 355000]
        self.player_name.setStyleSheet("QLineEdit {background-color: rgba(205, 133, 63, 0.75)}")
        self.character_name.setStyleSheet("QLineEdit {background-color: rgba(205, 133, 63, 0.75)}")
        self.cbstyle = """QComboBox QAbstractItemView {
                        border: 1px solid rgba(205, 133, 63, 0.75);
                        background: rgba(205, 133, 63, 0.75);
                        selection-background-color: black;
                        color: #500000;
                        }
                        QComboBox {
                        background: rgba(205, 133, 63, 0.75);
                        color: #500000;
                        }"""
        self.sbstyle = """QSpinBox QAbstractItemView {
                        border: 1px solid rgba(205, 133, 63, 0.75);
                        background: rgba(205, 133, 63, 0.75);
                        selection-background-color: black;
                        color: #500000;
                        }
                        QSpinBox {
                        background: rgba(205, 133, 63, 0.75);
                        color: #500000;
                        }"""
        self.race.setStyleSheet(self.cbstyle)
        self.clas.setStyleSheet(self.cbstyle)
        self.player_history.setStyleSheet(self.cbstyle)
        self.worldview.setStyleSheet(self.cbstyle)
        self.expa.setStyleSheet(self.sbstyle)
        self.level.setStyleSheet(self.sbstyle)
        self.stat.setStyleSheet(self.cbstyle)

    def update(self):
        # Функция связывающая уровень героя и его опыт
        if self.sender().objectName() == self.level.objectName():
            for i in range(20):
                if self.expa_for_up[i] > self.expa.value():
                    i -= 1
                    break
            if i + 1 != self.level.value():
                self.expa.setValue(self.expa_for_up[self.level.value() - 1])
        else:
            for i in range(20):
                if self.expa_for_up[i] > self.expa.value():
                    i -= 1
                    break
            self.level.setValue(i + 1)

    def generat(self):
        # Определение имени персонажа и пользователя
        hero.hero_name = self.character_name.text()
        if self.player_name.text() != '':
            hero.player_name = self.player_name.text()
        else:
            hero.player_name = 'SomeOne'
        # Получение значений введённых пользователем
        hero.hero_race = self.race.currentText()
        hero.hero_class = self.clas.currentText()
        hero.hero_history = self.player_history.currentText()
        hero.hero_world_view = self.worldview.currentText()
        hero.hero_level = self.level.value()
        hero.hero_expa = self.expa.value()
        con = sqlite3.connect('rules.db')
        cur = con.cursor()
        self.update_dices()
        # Выбор способа генерации
        if hero.hero_class != 'Не важно':
            # Генерация на основе класса
            self.generate_with_class(cur)
        elif self.stat.currentText() == 'Задать':
            # Генерация на основе характеристик
            self.generate_with_stat(cur)
        elif hero.hero_race != 'Не важно':
            # Генерация на основе расы
            self.generate_with_race(cur)
        elif hero.hero_history != 'Не важно':
            # Генерация на основе предыстории
            self.generate_with_history(cur)
        else:
            # Случайная генерация
            self.generate_without_parametrs(cur)
        # Заполнение листа персонажа
        self.delete_extra_dices()
        self.make_player_list(cur)
        con.close()

    def make_player_list(self, cur):
        im = Image.open('static/img/player_list.png')
        idraw = ImageDraw.Draw(im)
        text_type = 'arial.ttf'
        font = []
        for i in range(101):
            font.append(ImageFont.truetype(text_type, size=i))
        self.write_title(idraw, font)
        self.write_stats(idraw, font)
        self.write_spas_broski(idraw, font)
        self.write_skills(idraw, font, cur)
        self.write_passive_attention(idraw, font)
        self.write_other_parametrs(idraw, font)
        self.write_attacks(idraw, font)
        self.write_inventar(idraw, font, cur)
        self.write_vladenia(idraw, font)
        self.write_umenia(idraw, font)
        im.save('player_lists/' + hero.hero_name + '_' + hero.hero_class + '.png')
        im.show()

    def write_umenia(self, idraw, font):
        mxlen = 900 // max([len(i) for i in hero.hero_umenia]) + 3
        for i in range(len(hero.hero_umenia)):
            self.write_text(idraw, (1350, 1275 + i * mxlen), hero.hero_umenia[i], font[mxlen if mxlen < 45 else 44])

    def write_vladenia(self, idraw, font):
        mxlen = min([400 // len(hero.hero_vladenia), 700 // max([len(i) for i in hero.hero_vladenia])]) + 1
        for i in range(len(hero.hero_vladenia)):
            self.write_text(idraw, (150, 2050 + i * mxlen), hero.hero_vladenia[i], font[mxlen if mxlen < 45 else 44])

    def write_inventar(self, idraw, font, cur):
        mxlen = 700 // max([len(i) for i in hero.hero_inventar])
        hero.hero_inventar.sort()
        for i in range(len(hero.hero_inventar)):
            self.write_text(idraw, (882, 1950 + i * 68), hero.hero_inventar[i], font[mxlen if mxlen < 45 else 44])
        hero.hero_gold = cur.execute("""SELECT gold from history
        WHERE prehistory = ?""", (hero.hero_history, )).fetchall()[0][0]
        self.write_text(idraw, (786 if len(str(hero.hero_gold)) == 1 else 775, 2218), str(hero.hero_gold), font[39])

    def write_attacks(self, idraw, font):
        mxlen = 570 // max([len(i[0]) for i in hero.hero_weapon])
        for i in range(len(hero.hero_weapon)):
            self.write_text(idraw, (740, 1280 + i * 68), hero.hero_weapon[i][0], font[mxlen if mxlen < 45 else 44])
            self.write_text(idraw, (1080, 1282 + i * 68), hero.hero_weapon[i][1], font[mxlen if mxlen < 45 else 44])

    def write_other_parametrs(self, idraw, font):
        self.write_text(idraw, (768 if len(str(hero.hero_kd)) == 2 else 790, 470), str(hero.hero_kd), font[70])
        self.write_text(idraw, (1145, 470), str(hero.hero_speed), font[70])
        self.write_text(idraw, (955 if (hero.stat['Ловкость'] - 10) // 2 < 0 else 952, 470), '–' + str((hero.stat['Ловкость'] - 10) // 2)[1:] if (hero.stat['Ловкость'] - 10) // 2 < 0 else '+' + str((hero.stat['Ловкость'] - 10) // 2),
                        font[70])
        self.write_text(idraw, (975, 628), str(hero.hero_hp), font[50])
        self.write_text(idraw, (801 if len(str(hero.hero_hp_dice)) == 2 else 816, 1070), '1d' + str(hero.hero_hp_dice), font[50])

    def write_passive_attention(self, idraw, font):
        self.write_text(idraw, (117 if len(str(10 + hero.attention)) == 2 else 130, 1937), str(10 + hero.attention), font[40])

    def write_skills(self, idraw, font, cur):
        mxlen = []
        # Получение списка навыков и характеристик от которых они зависят
        skills = cur.execute("""SELECT skill, characteristic_id from skills""").fetchall()[:-1]
        for i in range(len(skills)):
            skills[i] = list(skills[i])
            skills[i][1] = cur.execute("""SELECT characteristic from characteristics
            WHERE (id = ?)""", (skills[i][1], )).fetchall()[0][0]
        # Нахождение максимальной длинны бонуса
        for i in range(len(skills)):
            if skills[i][0] in hero.hero_skills:
                mxlen.append(len('+' + str((hero.hero_level - 1) // 4 + 2 + (hero.stat[skills[i][1]] - 10) // 2) if str((hero.hero_level - 1) // 4 + 2 + (hero.stat[skills[i][1]] - 10) // 2)[0] != '-' else '–' + str((hero.hero_level - 1) // 4 + 2 + (hero.stat[skills[i][1]] - 10) // 2)[1:]))
        mxlen = max(mxlen)
        if mxlen == 2:
            # Если нет +10 и выше
            for i in range(len(skills)):
                if skills[i][0] in hero.hero_skills:
                    self.write_text(idraw, (370, 1040 + i * 44), '+' + str((hero.hero_level - 1) // 4 + 2 + (hero.stat[skills[i][1]] - 10) // 2) if len(str((hero.hero_level - 1) // 4 + 2 + (hero.stat[skills[i][1]] - 10) // 2)) == 1 else '–' + str((hero.hero_level - 1) // 4 + 2 + (hero.stat[skills[i][1]] - 10) // 2)[1:], font[40])
                    idraw.ellipse((330, 1058 + 44 * i, 350, 1078 + 44 * i), (0, 0, 0))
                    if skills[i][0] == 'Внимательность':
                        hero.attention = (hero.hero_level - 1) // 4 + 2 + (hero.stat[skills[i][1]] - 10) // 2
                else:
                    self.write_text(idraw, (370, 1040 + i * 44), '+' + str((hero.stat[skills[i][1]] - 10) // 2) if len(str((hero.stat[skills[i][1]] - 10) // 2)) == 1 else '–' + str((hero.stat[skills[i][1]] - 10) // 2)[1:], font[40])
                    if skills[i][0] == 'Внимательность':
                        hero.attention = (hero.stat[skills[i][1]] - 10) // 2
        else:
            # Если +10 и выше
            for i in range(len(skills)):
                if skills[i][0] in hero.hero_skills:
                    if len('+' + str((hero.hero_level - 1) // 4 + 2 + (hero.stat[skills[i][1]] - 10) // 2) if str((hero.hero_level - 1) // 4 + 2 + (hero.stat[skills[i][1]] - 10) // 2)[0] != '-' else '–' + str((hero.hero_level - 1) // 4 + 2 + (hero.stat[skills[i][1]] - 10) // 2)[1:]) == mxlen:
                        self.write_text(idraw, (370, 1050 + i * 44), '+' + str((hero.hero_level - 1) // 4 + 2 + (hero.stat[skills[i][1]] - 10) // 2) if str((hero.hero_level - 1) // 4 + 2 + (hero.stat[skills[i][1]] - 10) // 2)[0] != '-' else '–' + str((hero.hero_level - 1) // 4 + 2 + (hero.stat[skills[i][1]] - 10) // 2)[1:], font[25])
                    else:
                        self.write_text(idraw, (375, 1050 + i * 44), '+' + str((hero.hero_level - 1) // 4 + 2 + (hero.stat[skills[i][1]] - 10) // 2) if str((hero.hero_level - 1) // 4 + 2 + (hero.stat[skills[i][1]] - 10) // 2)[0] != '-' else '–' + str((hero.hero_level - 1) // 4 + 2 + (hero.stat[skills[i][1]] - 10) // 2)[1:], font[25])
                    idraw.ellipse((330, 1058 + 44 * i, 350, 1078 + 44 * i), (0, 0, 0))
                    if skills[i][0] == 'Внимательность':
                        hero.attention = (hero.hero_level - 1) // 4 + 2 + (hero.stat[skills[i][1]] - 10) // 2
                else:
                    self.write_text(idraw, (375, 1050 + i * 44), '+' + str((hero.stat[skills[i][1]] - 10) // 2) if str((hero.stat[skills[i][1]] - 10) // 2)[0] != '-' else '–' + str((hero.stat[skills[i][1]] - 10) // 2)[1:], font[25])
                    if skills[i][0] == 'Внимательность':
                        hero.attention = (hero.stat[skills[i][1]] - 10) // 2

    def write_spas_broski(self, idraw, font):
        # Нахождение максимальной длины юонуса спасброска характеристики
        mxlen = max([len(str((hero.hero_level - 1) // 4 + 2 + (hero.stat[h] - 10) // 2 if h in hero.hero_spas_bros else (hero.stat[h] - 10) // 2) if str((hero.hero_level - 1) // 4 + 2 + (hero.stat[h] - 10) // 2 if h in hero.hero_spas_bros else (hero.stat[h] - 10) // 2)[0] == '-' else '+' + str((hero.hero_level - 1) // 4 + 2 + (hero.stat[h] - 10) // 2 if h in hero.hero_spas_bros else (hero.stat[h] - 10) // 2)) for h in hero.stat.keys()])
        self.write_text(idraw, (325, 550), '+' + str((hero.hero_level - 1) // 4 + 2), font[50])
        char = list(hero.stat.keys())
        if mxlen == 2:
            # ЕСли бонус нет +10 и выше
            for i in range(len(char)):
                if char[i] in hero.hero_spas_bros:
                    self.write_text(idraw, (370, 660 + i * 45), '+' + str((hero.hero_level - 1) // 4 + 2 + (hero.stat[char[i]] - 10) // 2) if len(str((hero.hero_level - 1) // 4 + 2 + (hero.stat[char[i]] - 10) // 2)) == 1 else '–' + str((hero.hero_level - 1) // 4 + 2 + (hero.stat[char[i]] - 10) // 2)[1:], font[40])
                    idraw.ellipse((330, 678 + 45 * i, 350, 698 + 45 * i), (0, 0, 0))
                else:
                    self.write_text(idraw, (370, 660 + i * 45), '+' + str((hero.stat[char[i]] - 10) // 2) if len(str((hero.stat[char[i]] - 10) // 2)) == 1 else '–' + str((hero.stat[char[i]] - 10) // 2)[1:], font[40])
        else:
            # Если есть +10 и выше
            for i in range(len(char)):
                if char[i] in hero.hero_spas_bros:
                    if len('+' + str((hero.hero_level - 1) // 4 + 2 + (hero.stat[char[i]] - 10) // 2) if str((hero.hero_level - 1) // 4 + 2 + (hero.stat[char[i]] - 10) // 2)[0] != '-' else '–' + str((hero.hero_level - 1) // 4 + 2 + (hero.stat[char[i]] - 10) // 2)[1:]) == mxlen:
                        self.write_text(idraw, (370, 670 + i * 45), '+' + str((hero.hero_level - 1) // 4 + 2 + (hero.stat[char[i]] - 10) // 2) if str((hero.hero_level - 1) // 4 + 2 + (hero.stat[char[i]] - 10) // 2)[0] != '-' else '–' + str((hero.hero_level - 1) // 4 + 2 + (hero.stat[char[i]] - 10) // 2)[1:], font[25])
                    else:
                        self.write_text(idraw, (380, 670 + i * 45), '+' + str((hero.hero_level - 1) // 4 + 2 + (hero.stat[char[i]] - 10) // 2) if str((hero.hero_level - 1) // 4 + 2 + (hero.stat[char[i]] - 10) // 2)[0] != '-' else '–' + str((hero.hero_level - 1) // 4 + 2 + (hero.stat[char[i]] - 10) // 2)[1:], font[25])
                    idraw.ellipse((330, 678 + 45 * i, 350, 698 + 45 * i), (0, 0, 0))
                else:
                    self.write_text(idraw, (380, 670 + i * 45), '+' + str((hero.stat[char[i]] - 10) // 2) if len(str((hero.stat[char[i]] - 10) // 2)) == 1 else '–' + str((hero.stat[char[i]] - 10) // 2)[1:], font[25])

    def write_stats(self, idraw, font):
        self.write_text(idraw, (157 if len(str(hero.stat['Сила'])) > 1 else 175, 520), str(hero.stat['Сила']), font[50])
        self.write_text(idraw, (157, 603), '–' + str((hero.stat['Сила'] - 10) // 2)[1:] if (hero.stat['Сила'] - 10) // 2 < 0 else '+' + str((hero.stat['Сила'] - 10) // 2),
                        font[50])
        self.write_text(idraw, (157 if len(str(hero.stat['Ловкость'])) > 1 else 175, 755), str(hero.stat['Ловкость']), font[50])
        self.write_text(idraw, (157, 838), '–' + str((hero.stat['Ловкость'] - 10) // 2)[1:] if (hero.stat['Ловкость'] - 10) // 2 < 0 else '+' + str((hero.stat['Ловкость'] - 10) // 2),
                        font[50])
        self.write_text(idraw, (157 if len(str(hero.stat['Телосложение'])) > 1 else 175, 990), str(hero.stat['Телосложение']), font[50])
        self.write_text(idraw, (157, 1072), '–' + str((hero.stat['Телосложение'] - 10) // 2)[1:] if (hero.stat['Телосложение'] - 10) // 2 < 0 else '+' + str((hero.stat['Телосложение'] - 10) // 2),
                        font[50])
        self.write_text(idraw, (157 if len(str(hero.stat['Интеллект'])) > 1 else 175, 1225), str(hero.stat['Интеллект']), font[50])
        self.write_text(idraw, (157, 1306), '–' + str((hero.stat['Интеллект'] - 10) // 2)[1:] if (hero.stat['Интеллект'] - 10) // 2 < 0 else '+' + str((hero.stat['Интеллект'] - 10) // 2),
                        font[50])
        self.write_text(idraw, (157 if len(str(hero.stat['Мудрость'])) > 1 else 175, 1460), str(hero.stat['Мудрость']), font[50])
        self.write_text(idraw, (157, 1540), '–' + str((hero.stat['Мудрость'] - 10) // 2)[1:] if (hero.stat['Мудрость'] - 10) // 2 < 0 else '+' + str((hero.stat['Мудрость'] - 10) // 2),
                        font[50])
        self.write_text(idraw, (157 if len(str(hero.stat['Харизма'])) > 1 else 175, 1695), str(hero.stat['Харизма']), font[50])
        self.write_text(idraw, (157, 1774), '–' + str((hero.stat['Харизма'] - 10) // 2)[1:] if (hero.stat['Харизма'] - 10) // 2 < 0 else '+' + str((hero.stat['Харизма'] - 10) // 2),
                        font[50])

    def write_title(self, idraw, font):
        mxlen = 570 // max([len(hero.player_name), len(hero.hero_world_view), len(hero.hero_history), len(hero.hero_race)])
        self.write_text(idraw, (200, 205), hero.hero_name, font[900 // len(hero.hero_name) if 900 // len(hero.hero_name) < 40 else 39])
        self.write_text(idraw, (880, 160), hero.hero_class + ' ' + str(hero.hero_level) + 'ур.', font[mxlen if mxlen < 40 else 39])
        self.write_text(idraw, (1255, 160), hero.hero_history, font[mxlen if mxlen < 40 else 39])
        self.write_text(idraw, (1565, 160), hero.player_name, font[mxlen if mxlen < 40 else 39])
        self.write_text(idraw, (880, 250), hero.hero_race, font[mxlen if mxlen < 40 else 39])
        self.write_text(idraw, (1255, 250), hero.hero_world_view, font[mxlen if mxlen < 40 else 39])
        self.write_text(idraw, (1565, 250), str(hero.hero_expa), font[mxlen if mxlen < 40 else 39])

    def write_text(self, idraw, cord, txt, font):
        # Вывод текста на изображение
        idraw.text(cord, txt, font=font, fill=(0, 0, 0))

    def update_dices(self):
        con = sqlite3.connect('rules.db')
        cur = con.cursor()
        for i in range(20, 101, 80):
            cur.execute("""INSERT INTO dices(dice) VALUES(?)""", (i, ))
        con.commit()
        con.close()

    def delete_extra_dices(self):
        con = sqlite3.connect('rules.db')
        cur = con.cursor()
        for i in range(20, 101, 80):
            cur.execute("""DELETE from dices
            WHERE (dice = ?)""", (i, ))
        con.commit()
        con.close()

    def generate_without_parametrs(self, cur):
        self.generate_class_randomly(cur)
        self.generate_race(cur)
        self.generate_history(cur)
        self.generate_stats(cur)
        self.generate_not_important_parametrs(cur)

    def generate_with_history(self, cur):
        self.generate_class_with_history(cur)
        self.generate_stats(cur)
        self.generate_race(cur)
        self.generate_history(cur)
        self.generate_not_important_parametrs(cur)

    def generate_with_race(self, cur):
        self.generate_class_with_race(cur)
        self.generate_stats(cur)
        self.generate_history(cur)
        self.generate_not_important_parametrs(cur)

    def generate_with_stat(self, cur):
        self.generate_class_with_stat(cur)
        self.generate_race(cur)
        self.generate_history(cur)
        self.generate_not_important_parametrs(cur)

    def generate_with_class(self, cur):
        self.generate_race(cur)
        self.generate_history(cur)
        self.generate_stats(cur)
        self.generate_not_important_parametrs(cur)

    def generate_not_important_parametrs(self, cur):
        # Определение параметров, значение которых определяется уже выбранными
        self.generate_bonus_from_race(cur)
        self.generate_inventar(cur)
        self.generate_world_view()
        self.generate_armor(cur)
        self.generate_spas_broski(cur)
        self.generate_language(cur)
        self.generate_weapon(cur)
        self.generate_kd(cur)
        self.generate_initiative()
        self.generate_speed(cur)
        self.generate_hp_dice(cur)
        self.generate_hp()
        self.generate_skills(cur)
        self.generate_vladenia(cur)
        self.generate_umenia(cur)
        self.generate_name(cur)

    def generate_class_with_history(self, cur):
        # Определение класса, основываясь на предыстории
        clas = cur.execute("""SELECT class, history_id from main""").fetchall()
        history = cur.execute("""SELECT id from history
                    WHERE prehistory = ?""", (hero.hero_history,)).fetchall()[0][0]
        classes_for_select = []
        # Попытка найти класс с данной предысторией
        for i in clas:
            if history in i:
                classes_for_select.append(i[0])
        if len(classes_for_select) != 0:
            hero.hero_class = random.choice(classes_for_select)
        else:
            self.generate_class_randomly(cur)

    def generate_class_randomly(self, cur):
        # Случайный выбор класса
        clas = cur.execute("""SELECT class from main""").fetchall()
        hero.hero_class = random.choice(clas)[0]

    def generate_class_with_race(self, cur):
        # Определение класса, основываясь на расе
        clas = cur.execute("""SELECT class, race_1_id, race_2_id, race_3_id from main""").fetchall()
        race = cur.execute("""SELECT id from races
            WHERE race = ?""", (hero.hero_race, )).fetchall()[0][0]
        stop = False
        # Нахождение класса, для которого эта раса стоит на более приоритетном месте
        for i in range(3):
            for j in range(len(clas)):
                if clas[j][i + 1] == race:
                    hero.hero_class = clas[j][0]
                    stop = True
                    break
            if stop:
                break

    def generate_class_with_stat(self, cur):
        # Определение класса, основываясь на важных характеристиках
        clas = cur.execute("""SELECT class, imp_char_1, imp_char_2 from main""").fetchall()
        znach_stat = []
        for i in hero.stat.keys():
            znach_stat.append([hero.stat[i], i])
        znach_stat = sorted(znach_stat, reverse=True)
        for i in range(len(znach_stat)):
            znach_stat[i] = cur.execute("""SELECT id from characteristics
            WHERE characteristic = ?""", (znach_stat[i][1], )).fetchall()[0][0]
        imp_char = znach_stat[:2]
        znach_stat = znach_stat[2:]
        stop = False
        # Нахождение класса, для которого наивысшие характеристики являются важными
        while not stop:
            for i in range(len(imp_char)):
                for j in range(len(imp_char)):
                    if i != j:
                        for k in clas:
                            if imp_char[i] == k[1] and imp_char[j] == k[2]:
                                hero.hero_class = k[0]
                                stop = True
                                break
                    if stop:
                        break
                if stop:
                    break
            imp_char.append(znach_stat[0])
            del znach_stat[0]

    def generate_race(self, cur):
        if hero.hero_race == 'Не важно':
            hero.hero_race = cur.execute("""SELECT race from races
        WHERE (id = (SELECT race_1_id from main
        WHERE (class = ?)))""", (hero.hero_class, )).fetchall()[0][0]

    def generate_history(self, cur):
        if hero.hero_history == 'Не важно':
            hero.hero_history = cur.execute("""SELECT prehistory from history
        WHERE (id = (SELECT history_id from main
        WHERE (class = ?)))""", (hero.hero_class, )).fetchall()[0][0]

    def generate_inventar(self, cur):
        hero.hero_inventar = cur.execute("""SELECT equip from history
        WHERE prehistory = ?""", (hero.hero_history, )).fetchall()[0][0].split('; ')
        result = cur.execute("""SELECT equip from main
            WHERE (class = ?)""", (hero.hero_class,)).fetchall()[0][0].split('; ')
        for i in result:
            hero.hero_inventar.append(i)

    def generate_world_view(self):
        if hero.hero_world_view == 'Не важно':
            hero.hero_world_view = 'Нейтральное'

    def generate_stats(self, cur):
        self.stat_list = []
        if self.stat.currentText() == '4d6':
            self.distribute_4d6()
        elif self.stat.currentText() == 'Лесенка':
            self.distribute_ladder()
        # Если характеристики не были заданы пользователем
        if self.stat_list != []:
            self.stat_list.sort()
            result = cur.execute("""SELECT imp_char_1, imp_char_2 from main
                WHERE (class = ?)""", (hero.hero_class, )).fetchall()[0]
            char1 = cur.execute("""SELECT characteristic from characteristics
                WHERE (id = ?)""", (result[0], )).fetchall()[0][0]
            char2 = cur.execute("""SELECT characteristic from characteristics
                WHERE (id = ?)""", (result[1],)).fetchall()[0][0]
            char = list(hero.stat.keys())
            # Удаление важных характеристик из списка характеристик
            del char[char.index(char1)]
            del char[char.index(char2)]
            # Задание важным характеристикам наивысших значений
            hero.stat[char1] = self.stat_list.pop(len(self.stat_list) - 1)
            hero.stat[char2] = self.stat_list.pop(len(self.stat_list) - 1)
            # Определение остальных характеристик
            while char != []:
                i = random.randint(0, len(char) - 1)
                hero.stat[char[i]] = self.stat_list.pop(len(self.stat_list) - 1)
                del char[i]

    def generate_armor(self, cur):
        arm_id = cur.execute("""SELECT armor_id from main
                    WHERE (class = ?)""", (hero.hero_class,)).fetchall()[0][0]
        hero.hero_armor = cur.execute("""SELECT arm from armor
                    WHERE (id = ?)""", (arm_id,)).fetchall()[0][0]

    def generate_bonus_from_race(self, cur):
        # Добавление бонуса к характеристикам от выбранной расы
        hero.stat['Сила'] += cur.execute("""SELECT Сила from races
            WHERE (race = ?)""", (hero.hero_race, )).fetchall()[0][0]
        hero.stat['Ловкость'] += cur.execute("""SELECT Ловкость from races
                    WHERE (race = ?)""", (hero.hero_race,)).fetchall()[0][0]
        hero.stat['Телосложение'] += cur.execute("""SELECT Телосложение from races
                    WHERE (race = ?)""", (hero.hero_race,)).fetchall()[0][0]
        hero.stat['Интеллект'] += cur.execute("""SELECT Интеллект from races
                    WHERE (race = ?)""", (hero.hero_race,)).fetchall()[0][0]
        hero.stat['Мудрость'] += cur.execute("""SELECT Мудрость from races
                    WHERE (race = ?)""", (hero.hero_race,)).fetchall()[0][0]
        hero.stat['Харизма'] += cur.execute("""SELECT Харизма from races
                    WHERE (race = ?)""", (hero.hero_race,)).fetchall()[0][0]

    def generate_spas_broski(self, cur):
        sp_br = cur.execute("""SELECT spas_brosok_1, spas_brosok_2 from main
            WHERE (class = ?)""", (hero.hero_class, )).fetchall()[0]
        hero.hero_spas_bros = [i[0] for i in cur.execute("""SELECT characteristic from characteristics
            WHERE (id = ?) OR (id = ?)""", sp_br).fetchall()]

    def generate_language(self, cur):
        hero.hero_language = cur.execute("""SELECT langueges from races
            WHERE (race = ?)""", (hero.hero_race, )).fetchall()[0][0].split('; ')

    def generate_weapon(self, cur):
        wep1 = cur.execute("""SELECT weapon_1 from main
                                WHERE (class = ?)""", (hero.hero_class,)).fetchall()[0][0]
        wep2 = cur.execute("""SELECT weapon_2 from main
                                            WHERE (class = ?)""", (hero.hero_class,)).fetchall()[0][0]
        wep3 = cur.execute("""SELECT weapon_3 from main
                                            WHERE (class = ?)""", (hero.hero_class,)).fetchall()[0][0]
        wep1 = list(cur.execute("""SELECT weapon, damage, kol_damage_dice from weapons
                                            WHERE (id = ?)""", (wep1,)).fetchall()[0])
        wep2 = list(cur.execute("""SELECT weapon, damage, kol_damage_dice from weapons
                                                        WHERE (id = ?)""", (wep2,)).fetchall()[0])
        wep3 = list(cur.execute("""SELECT weapon, damage, kol_damage_dice from weapons
                                                        WHERE (id = ?)""", (wep3,)).fetchall()[0])
        hero.hero_weapon = [[wep1[0], '{}d{}'.format(wep1[2], cur.execute("""SELECT dice from dices
                                            WHERE (id = ?)""", (wep1[1],)).fetchall()[0][0])],
                            [wep2[0], '{}d{}'.format(wep2[2], cur.execute("""SELECT dice from dices
                                            WHERE (id = ?)""", (wep2[1],)).fetchall()[0][0])],
                            [wep3[0], '{}d{}'.format(wep3[2], cur.execute("""SELECT dice from dices
                                            WHERE (id = ?)""", (wep3[1],)).fetchall()[0][0])]]

    def generate_kd(self, cur):
        # Расчёт kd исходя из класса, характеристик и надетой экипировки
        if hero.hero_class == 'Варвар':
            hero.hero_kd = 10 + (hero.stat['Сила'] - 10) // 2 + (hero.stat['Телосложение'] - 10) // 2
        elif hero.hero_class == 'Монах':
            hero.hero_kd = 10 + ((hero.stat['Ловкость'] - 10) // 2) + (hero.stat['Мудрость'] - 10) // 2
        else:
            kd = cur.execute("""SELECT kd, bonus from armor
                    WHERE (arm = ?)""", (hero.hero_armor,)).fetchall()[0]
            if kd[1] == 0:
                hero.hero_kd = kd[0]
            elif kd[1] == 1:
                if (hero.stat['Ловкость'] - 10) // 2 >= 2:
                    hero.hero_kd = kd[0] + 2
                else:
                    hero.hero_kd = kd[0] + (hero.stat['Ловкость'] - 10) // 2
            else:
                hero.hero_kd = kd[0] + (hero.stat['Ловкость'] - 10) // 2

    def generate_initiative(self):
        hero.hero_initiative = (hero.stat['Ловкость'] - 10) // 2

    def generate_speed(self, cur):
        hero.hero_speed = cur.execute("""SELECT speed from races
                    WHERE (race = ?)""", (hero.hero_race,)).fetchall()[0][0]

    def generate_hp_dice(self, cur):
        hd = cur.execute("""SELECT health_dice_id from main
                                WHERE (class = ?)""", (hero.hero_class,)).fetchall()[0][0]
        hero.hero_hp_dice = cur.execute("""SELECT dice from dices
                                WHERE (id = ?)""", (hd,)).fetchall()[0][0]

    def generate_hp(self):
        hero.hero_hp = hero.hero_hp_dice + (hero.stat['Телосложение'] - 10) // 2
        for i in range(hero.hero_level - 1):
            hero.hero_hp += random.randint(1, hero.hero_hp_dice) + (hero.stat['Телосложение'] - 10) // 2
        if hero.hero_hp < 1:
            hero.hero_hp = 1

    def generate_skills(self, cur):
        # Получение навыков от класса и предыстории
        hero.hero_skills = cur.execute("""SELECT skill from skills
                    WHERE (id in (SELECT skill_1_id from main
                    WHERE class = ?)) OR (id in (SELECT skill_2_id from main
                    WHERE class = ?)) OR (id in (SELECT skill_3_id from main
                    WHERE class = ?))""", (hero.hero_class, hero.hero_class, hero.hero_class,)).fetchall()
        pre_skills = cur.execute("""SELECT skill_1, skill_2 from history
                    WHERE (id in (SELECT history_id from main
                    WHERE class = ?))""", (hero.hero_class,)).fetchall()[0]
        for i in pre_skills:
            hero.hero_skills.append(cur.execute("""SELECT skill from skills
                    WHERE (id = ?)""", (i,)).fetchall()[0])
        hero.hero_skills = [i[0] for i in hero.hero_skills]

    def function_for_sort(self, x, result1):
        if 'Щиты' in x:
            return 3
        if 'доспехи' in x:
            return 2
        if x in result1:
            return 1
        if x in hero.hero_language:
            return -1
        return 0

    def generate_umenia(self, cur):
        # Получения умений класса в зависимости от уровня персонажа
        hero.hero_umenia = []
        umenia_classa = cur.execute("""SELECT umenia from main
                WHERE class = ?""", (hero.hero_class,)).fetchall()[0][0].split('; ')
        for i in range(hero.hero_level):
            if i + 2 <= 20:
                res = umenia_classa[umenia_classa.index(str(i + 1)) + 1: umenia_classa.index(str(i + 2))]
            else:
                res = umenia_classa[umenia_classa.index(str(i + 1)) + 1:]
            for j in res:
                hero.hero_umenia.append(j)

    def generate_vladenia(self, cur):
        # Получение всех владений от рассы, класса и предыстории
        hero.hero_vladenia = []
        result1 = cur.execute("""SELECT instruments from history
                WHERE prehistory = ?""", (hero.hero_history,)).fetchall()[0][0].split('; ')
        result2 = cur.execute("""SELECT vladenie from main
                    WHERE (class = ?)""", (hero.hero_class,)).fetchall()[0][0].split('; ')
        result3 = cur.execute("""SELECT vladenie from races
                    WHERE (race = ?)""", (hero.hero_race,)).fetchall()[0][0].split('; ')
        for i in result2:
            hero.hero_vladenia.append(i)
        for i in hero.hero_language:
            hero.hero_vladenia.append(i)
        if ' ' not in result3:
            for i in result3:
                if 'доспехи' not in i:
                    class_wep = cur.execute("""SELECT class from weapon_classes 
                        WHERE id in (SELECT weapon_class from weapons
                        WHERE (weapon = ?))""", (i,)).fetchall()[0][0].split()[0] + ' оружие'
                    if class_wep not in hero.hero_vladenia:
                        hero.hero_vladenia.append(i)
                else:
                    if i not in hero.hero_vladenia:
                        hero.hero_vladenia.append(i)
        hero.hero_vladenia = list(set(hero.hero_vladenia))
        i = 0
        # Сортировка полученных владений
        while i < len(hero.hero_vladenia):
            if hero.hero_vladenia[i] == ' ':
                del hero.hero_vladenia[i]
            else:
                i += 1
        hero.hero_vladenia = sorted(hero.hero_vladenia, key=lambda x: self.function_for_sort(x, result1))

    def generate_name(self, cur):
        # Генерация имени персонажа, если оно не задано
        if hero.hero_name == '':
            hero.hero_name = cur.execute("""SELECT name from races
                                WHERE (race = ?)""", (hero.hero_race,)).fetchall()[0][0]

    def characteristics(self, text):
        if text == 'Задать':
            global st
            st.show()

    def distribute_4d6(self):
        # Задание характеристик методом 4d6
        for i in range(6):
            self.stat_list.append(sum(sorted([random.randint(1, 6), random.randint(1, 6),
                                              random.randint(1, 6), random.randint(1, 6)])[1:]))

    def distribute_ladder(self):
        # Задание характеристик лесенкой
        self.stat_list = [10, 10, 10, 13, 14, 15]


class Stats(QMainWindow):
    def __init__(stats_self):
        super().__init__()
        uic.loadUi('static/ui/chose_characteristics.ui', stats_self)
        stats_self.setWindowTitle('Характеристики')
        stats_self.mod = [stats_self.silamod, stats_self.lovkostmod,
                          stats_self.telomod, stats_self.intelmod,
                          stats_self.mudrostmod, stats_self.harizmamod]
        stats_self.save.clicked.connect(stats_self.sohr)
        stats_self.back.clicked.connect(stats_self.end)
        stats_self.sila.valueChanged.connect(stats_self.update)
        stats_self.lovkost.valueChanged.connect(stats_self.update)
        stats_self.telo.valueChanged.connect(stats_self.update)
        stats_self.intel.valueChanged.connect(stats_self.update)
        stats_self.mudrost.valueChanged.connect(stats_self.update)
        stats_self.harizma.valueChanged.connect(stats_self.update)
        sbstyle = """QSpinBox QAbstractItemView {
                        border: 1px solid rgba(205, 133, 63, 0.75);
                        background: rgba(205, 133, 63, 0.75);
                        selection-background-color: black;
                        color: #500000;
                        }
                        QSpinBox {
                        background: rgba(205, 133, 63, 0.75);
                        color: #500000;
                        }"""
        stats_self.sila.setStyleSheet(sbstyle)
        stats_self.lovkost.setStyleSheet(sbstyle)
        stats_self.telo.setStyleSheet(sbstyle)
        stats_self.intel.setStyleSheet(sbstyle)
        stats_self.mudrost.setStyleSheet(sbstyle)
        stats_self.harizma.setStyleSheet(sbstyle)

    def update(stats_self):
        # Нахождение объекта, который отвечает за отовражение модификатора изменённой характеристики
        for i in stats_self.mod:
            if stats_self.sender().objectName() + 'mod' == i.objectName():
                break
        # Изменение модификатора
        i.setText(str((stats_self.sender().value() - 10) // 2))
        i.setAlignment(QtCore.Qt.AlignCenter)

    def end(stats_self):
        stats_self.sila.setValue(hero.stat['Сила'])
        stats_self.lovkost.setValue(hero.stat['Ловкость'])
        stats_self.telo.setValue(hero.stat['Телосложение'])
        stats_self.intel.setValue(hero.stat['Интеллект'])
        stats_self.mudrost.setValue(hero.stat['Мудрость'])
        stats_self.harizma.setValue(hero.stat['Харизма'])
        st.close()

    def sohr(stats_self):
        hero.stat['Сила'] = stats_self.sila.value()
        hero.stat['Ловкость'] = stats_self.lovkost.value()
        hero.stat['Телосложение'] = stats_self.telo.value()
        hero.stat['Интеллект'] = stats_self.intel.value()
        hero.stat['Мудрость'] = stats_self.mudrost.value()
        hero.stat['Харизма'] = stats_self.harizma.value()
        st.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Windows')
    ex = MainWindow()
    st = Stats()
    hero = Hero()
    ex.show()
    sys.exit(app.exec_())