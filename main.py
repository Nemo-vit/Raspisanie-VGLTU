from datetime import datetime, timedelta
from datetime import date

from babel import dates
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

import sys
from PyQt5.QtGui import QRegion, QFont, QColor, QIcon, QPainter, QPen
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import Qt
from PyQt5 import QtCore

group_code = ""

# --------------------------------- ТЕКУЩЕЕ РАСПИСАНИЕ ------------------------------------
def get_current_table():
    # Получение текущей даты
    current_datetime = datetime.now()
    current_day = current_datetime.day
    current_month = current_datetime.month
    current_year = current_datetime.year
    formatted_date = dates.format_date(
        date(current_year, current_month, current_day),
        format='long',
        locale='ru_RU'
    )
    current_date = formatted_date[:formatted_date.find(" ",formatted_date.find(" ")+1)]

    # Получение кода страницы
    # Драйвер + открытие страницы
    chrome_options = Options()
    chrome_options.add_argument("--headless") # Включает режим без открытия страницы
    service = ChromeService(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    url = "https://vgltu.ru/obuchayushchimsya/raspisanie-zanyatij/"
    driver.get(url)
    # Выполнение действия
    input_field = driver.find_element(By.ID, "searchGroup")
    global group_code
    input_field.send_keys(group_code)
    # Ждём прогрузки страницы
    time.sleep(2)
    # Выполнение действия
    input_field = driver.find_element(By.ID, "raspButtonGroup")
    input_field.click()
    # Ждём прогрузки страницы
    time.sleep(2)
    # Получение HTML кода
    html_code = driver.page_source
    # Вывод кода в файл
    with open("page.txt", 'w', encoding='utf-8') as file:
        file.write(html_code)
    file.close()
    # Закрытие браузера
    driver.quit()

    # Получение моих строк
    # Поиск стартовой строки
    fin = open("page.txt",encoding='utf-8')
    i = 0
    for line in fin:
        if current_date in line:
            i+=1
            break
        else:
            i+=1
    fin.close()
    start_string = i - 3
    # Поиск конечной строки
    # Вычисляем следующую дату (завтра)
    today = datetime.today()
    tomorrow = today + timedelta(days=1)
    next_month = tomorrow.month
    next_day = tomorrow.day
    next_year = tomorrow.year
    formatted_date = dates.format_date(
        date(next_year, next_month, next_day),
        format='long',
        locale='ru_RU'
    )
    next_date = formatted_date[:formatted_date.find(" ",formatted_date.find(" ")+1)]
    # Получаем номер последней строки
    fin = open("page.txt",encoding='utf-8')
    j = 0
    for line in fin:
        if next_date in line:
            j+=1
            break
        else:
            j+=1
    fin.close()
    end_string = j - 4
    # Выписывание моих строк
    fin = open("page.txt",encoding='utf-8')
    c = 0
    fout = open("current_table.txt", 'w', encoding='utf-8')
    for line in fin:
        if start_string<=c<=end_string:
            c+=1
            fout.write(line)
        elif c<i:
            c+=1
        elif c>j:
            break
    fout.close()
    fin.close()

    # Красивый вывод в консоль
    fin = open("current_table.txt", "r", encoding='utf-8')
    fout = open("raspisanie.txt", "w", encoding='utf-8')
    line_count = 1
    go_cycle = 0
    good_sign = 0
    second_predm = 0
    lection = 0
    lec_line_counting = 0
    lec_line = 0
    fout.write(current_date+ "\n")
    for line in fin:
        # день
        if line_count == 6:
            fout.write(line.replace(" ", ""))
        # подгруппа и предмет
        if ("1 п.г." in line or "2 п.г." in line) and line_count == (good_sign + 2) and go_cycle == 1 and not("лек." in  line or "Лек." in  line or "Физ" in  line):
            fout.write("\n" + line[line.find("<") + 4:line.find("<") + 10] + "\n" + line[32:line.find("<")])
        elif line_count == (good_sign + 11) and "2 п.г." in line and not("лек." in  line or "Лек." in  line or "Физ" in  line):
            fout.write(line[line.find("<") + 4:line.find("<") + 10] + "\n" + line[32:line.find("<")])
            second_predm = 1
            go_cycle = 0
        elif ("лек." in  line or "Лек." in  line or "Физ" in  line or "Пр." in  line or "пр." in  line) and not("1 п.г." in line) and not("2 п.г." in line):
            lec_line = line_count
            lec_line_counting = 1
            fout.write("\n" + line[32:line.find("<")])
            go_cycle = 0
            lection = 1
        if "<br>" in line and lection == 1 and lec_line_counting == 1:
            lec_line += 1
        if (".<br>" in line or "Вак" in line) and lection == 1 and lec_line_counting == 1:
            lec_line_counting = 0
        # фио препода
        if line_count == (good_sign + 6) and go_cycle == 1:
            fout.write("\n" + line[32:line.find("<")] + "\n")
            go_cycle = 0
        elif line_count == (good_sign + 15) and second_predm == 1:
            second_predm = 0
            fout.write("\n" + line[32:line.find("<")] + "\n")
        elif lec_line_counting == 0 and lection == 1:
            lection = 0
            fout.write("\n" + line[32:line.find("<")] + "\n")
        # время
        if "<td style=\"width:75px\" rowspan=" in line:
            fout.write("\n" + line[71:82])
            good_sign = line_count
            go_cycle = 1
        line_count += 1
# -----------------------------------------------------------------------------------------

# ------------------------------------ РАБОТА С ОКНАМИ ------------------------------------
class MyThread(QtCore.QThread):
    my_signal = QtCore.pyqtSignal(int)
    def  __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
    def run(self):
        while True:
            get_current_table()
            fin = open("raspisanie.txt", "r", encoding='utf-8')
            line_number = 1
            er = 0
            for line in fin:
                if (line_number == er+3) and ("2 п.г." in line):
                    break
                elif line_number == er+3:
                    er = 0
                if "1 п.г." in line:
                    er = line_number
                if (("лек." in line) or ("Лек." in line) or ("Физ" in  line) or ("Пр." in  line) or ("пр." in  line)) and not(er+1==line_number):
                    break
                else:
                    line_number +=1
            fin.close()
            #print(line_number)
            fin = open("raspisanie.txt", "r", encoding='utf-8')
            needed_line_number = 1
            start_time = ""
            for line in fin:
                if (needed_line_number == line_number-4 and ":" in line) or (needed_line_number == line_number-1 and ":" in line) or (needed_line_number == line_number-2 and ":" in line):
                    start_time = line[:5]
                    break
                else:
                    needed_line_number += 1
            fin.close()
            #print(needed_line_number)
            #print(start_time)
            for i in range(0,59):
                current_time = datetime.now()
                current_min = current_time.minute
                current_hour = current_time.hour
                if int(start_time[0]) == 0:
                    minutes_left = (int(start_time[1]) * 60 + int(start_time[3:5])) - (current_hour * 60 + current_min)
                else:
                    minutes_left = (int(start_time[:2])*60 + int(start_time[3:5])) - (current_hour*60 + current_min)
                if 0 < minutes_left < 60:
                    self.my_signal.emit(minutes_left)
                    break
                else:
                    time.sleep(60)

class GetGroupCode(QWidget):
    def __init__(self):
        super().__init__()
        # параметры окна
        self.setWindowTitle("Ввод группы")
        icon = QIcon('logo.png')
        self.setWindowIcon(icon)
        self.setGeometry(850, 430, 300, 200)
        self.setFixedSize(300, 200)
        self.setStyleSheet("background-color: rgb(255, 255, 255);")
        # Вывод текста в окно
        font = QFont("Arial", 14)
        self.lab = QLabel("Введите код группы:", parent=self)
        self.lab.setFont(font)
        self.lab.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lab.setGeometry(0, 20, 300, 20)
        # Поле для ввода группы
        self.lineEdit = QLineEdit(parent=self)
        self.lineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lineEdit.setGeometry(100, 80, 100, 20)
        self.lineEdit.setText("ИС4-242-ОМ")
        self.lineEdit.setObjectName("lineEdit")
        # Кнопка
        self.btn1 = QPushButton("Выполнить", self)
        self.btn1.move(114, 130)
        self.btn1.clicked.connect(self.button_clicked)

    def button_clicked(self):
        global group_code
        group_code = self.lineEdit.text()
        self.round_window = RoundWidget()
        self.round_window.show()
        self.close()

class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        # параметры окна
        global group_code
        window_name = "Расписание группы " + group_code
        self.setWindowTitle(window_name)
        icon = QIcon('logo.png')
        self.setWindowIcon(icon)
        self.setGeometry(630, 340, 1000, 400)
        self.setFixedSize(1000, 400)
        self.setStyleSheet("background-color: rgb(255, 255, 255);")
        # Получение переменных с данными расписания и их вывод в окно
        font = QFont("Arial", 14)
        self.l_1pg = QLabel("1 п.г.", parent=self)
        self.l_1pg.setFont(font)
        self.l_1pg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.l_1pg.setGeometry(0, 40, 499, 20)
        self.l_2pg = QLabel("2 п.г.", parent=self)
        self.l_2pg.setFont(font)
        self.l_2pg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.l_2pg.setGeometry(501, 40, 499, 20)
        fin = open("raspisanie.txt", "r", encoding='utf-8')
        line_count = 1
        go_cycle = 0
        good_sign = 0
        second_predm = 0
        lection = 0
        predm = 0
        just_second_predm = 0
        current_place = 0
        for line in fin:
            if line_count == good_sign+1 and "2 п.г." in line:
                just_second_predm = 1
            # Дата
            if line_count == 1:
                self.l_date = QLabel(line, parent=self)
                self.l_date.setFont(font)
                self.l_date.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.l_date.setGeometry(0, 0, 1000, 20)
            # день
            if line_count == 2:
                self.l_day_w = QLabel(line, parent=self)
                self.l_day_w.setFont(font)
                self.l_day_w.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.l_day_w.setGeometry(0, 20, 1000, 20)
            # подгруппа и предмет
            if line_count == (good_sign + 2) and go_cycle == 1 and not ("лек." in line or "Лек." in line or "Физ" in  line) and just_second_predm == 0:
                self.l_predm = QLabel(line, parent=self)
                self.l_predm.setFont(font)
                self.l_predm.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.l_predm.setGeometry(0, current_place_predm, 499, 20)
            elif line_count == (good_sign + 2) and go_cycle == 1 and not ("лек." in line or "Лек." in line or "Физ" in  line) and just_second_predm == 1:
                self.l_predm = QLabel(line, parent=self)
                self.l_predm.setFont(font)
                self.l_predm.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.l_predm.setGeometry(501, current_place_predm, 499, 20)
                second_predm = 1
                go_cycle = 0
            elif line_count == (good_sign + 5) and ("лаб" in line or "пр" in line or "Пр" in line) and not ("лек." in line or "Лек." in line or "Физ" in  line):
                self.l_predm = QLabel(line, parent=self)
                self.l_predm.setFont(font)
                self.l_predm.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.l_predm.setGeometry(501, current_place_predm, 499, 20)
                second_predm = 1
                go_cycle = 0
            elif "лек." in line or "Лек." in line or "Физ" in  line or "Пр." in  line or "пр." in  line:
                self.l_predm = QLabel(line, parent=self)
                self.l_predm.setFont(font)
                self.l_predm.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.l_predm.setGeometry(0, current_place_predm, 1000, 20)
                go_cycle = 0
                lection = 1
            # фио препода
            if line_count == (good_sign + 3) and go_cycle == 1 and second_predm == 0 and just_second_predm == 0:
                self.l_prepod = QLabel(line, parent=self)
                self.l_prepod.setFont(font)
                self.l_prepod.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.l_prepod.setGeometry(0, current_place_prepod, 499, 20)
                go_cycle = 0
            elif line_count == (good_sign + 3) and second_predm == 1 and just_second_predm == 1:
                just_second_predm == 0
                second_predm = 0
                self.l_prepod = QLabel(line, parent=self)
                self.l_prepod.setFont(font)
                self.l_prepod.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.l_prepod.setGeometry(501, current_place_prepod, 499, 20)
            elif line_count == (good_sign + 6):
                second_predm = 0
                self.l_prepod = QLabel(line, parent=self)
                self.l_prepod.setFont(font)
                self.l_prepod.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.l_prepod.setGeometry(501, current_place_prepod, 499, 20)
            elif line_count == (good_sign + 2) and lection == 1:
                self.l_prepod = QLabel(line, parent=self)
                self.l_prepod.setFont(font)
                self.l_prepod.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.l_prepod.setGeometry(0, current_place_prepod, 1000, 20)
                lection = 0
            # время
            if ":" in line:
                current_place += 60
                self.l_time = QLabel(line, parent=self)
                self.l_time.setFont(font)
                self.l_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.l_time.setGeometry(0, current_place, 1000, 20)
                predm += 1
                current_place_predm = current_place + 20
                current_place_prepod = current_place_predm + 20
                good_sign = line_count
                go_cycle = 1
            line_count += 1

    def paintEvent(self, e):
        # Вертикальная линия по центру
        painter = QPainter(self)
        # цвет и толщина линии
        pen = QPen(Qt.black, 1)
        painter.setPen(pen)
        # Рисование вертикальной линии
        painter.drawLine(500, 0, 500, 400)

class RoundWidget(QWidget):
    def __init__(self):
        super().__init__()
        # параметры окна
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setGeometry(1855, 983, 60, 60)
        self.set_round_window()
        self.setWindowOpacity(0.5)
        self.setStyleSheet("background-color: rgb(135, 206, 250);")
        # Буква
        self.label = QLabel('R', parent=self)
        # Шрифт и размер
        font = QFont("Arial", 35)
        self.label.setFont(font)
        # Цвет текста
        blue_R = self.label.palette()
        blue_R.setColor(blue_R.WindowText, QColor(0, 0, 255))
        self.label.setPalette(blue_R)
        # Положение буквы
        self.label.move(14, 5)
        self.mythread = MyThread()
        self.mythread.my_signal.connect(self.get_signal)
        self.mythread.start()

    def set_round_window(self):
        # Создаем круговую маску
        path = QRegion(self.rect(), QRegion.Ellipse)
        self.setMask(path)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = event.pos()

    def mouseMoveEvent(self, event):
        if self.oldPos is not None:
            delta = event.pos() - self.oldPos
            self.move(self.pos() + delta)

    def mouseReleaseEvent(self, event):
        self.oldPos = None

    def mouseDoubleClickEvent(self, event):
        self.main_window = MainWidget()
        self.main_window.show()
        self.setStyleSheet("background-color: rgb(135, 206, 250);")

    def get_signal(self, minutes_left):
        if 0 < minutes_left < 60:
            self.setStyleSheet("background-color: rgb(255, 0, 0);")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Создание окна
    widget = GetGroupCode()
    # Показать окно
    widget.show()

    sys.exit(app.exec_())
# -----------------------------------------------------------------------------------------
