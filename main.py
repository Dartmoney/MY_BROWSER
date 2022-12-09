from __future__ import unicode_literals
import sys


import pytube
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sqlite3


def get_result(name):
    con = sqlite3.connect(name)
    p, k = input().split()
    # Создание курсора
    cur = con.cursor()
    # Выполнение запроса и получение всех результатов
    result = cur.execute(f"""SELECT Team.name as Tname,
    Team.weapon as Tw,
    time_on_duty as time 
    FROM Schedule
    LEFT JOIN Team ON Team.id = Schedule.team_id
    LEFT JOIN Places_to_protect ON Places_to_protect.ID = Schedule.place_id
    WHERE (Places_to_protect.title = '{p}') AND loophole_number = '{k}'
    ORDER BY time
    """).fetchall()

    con.commit()

    con.close()


class Download(QObject):
    reportProgress = pyqtSignal(int, list)
    calculationFinished = pyqtSignal()

    def __init__(self, url, kachestvo):
        super().__init__()
        self.url = url.split("&")[0]
        self.kach = kachestvo

    def run(self):
        yt = pytube.YouTube(self.url)
        yt = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()
        if len(yt) > 2 and self.kach == "Среднее":
            yt = yt[1]
            yt.download()
        elif self.kach == "Высокое":
            yt = yt[0]
            yt.download()
        else:
            yt = yt[-1]
            yt.download()


class Example(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(Example, self).__init__(*args, **kwargs)
        # создание таблицы
        self.tabs = QTabWidget()

        # включение режима документа в true
        self.tabs.setDocumentMode(True)

        # добавление действия при двойном щелчке
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)

        # добавление действия при изменении вкладки
        self.tabs.currentChanged.connect(self.current_tab_changed)

        # обеспечение возможности закрытия вкладок
        self.tabs.setTabsClosable(True)

        # добавление действия при запросе закрытия вкладки
        self.tabs.tabCloseRequested.connect(self.close_current_tab)

        # создание вкладок в качестве центрального виджета
        self.setCentralWidget(self.tabs)

        # создание статус бара
        self.status = QStatusBar()

        # добавление статус бара в главное окно
        self.setStatusBar(self.status)

        # создание навигации
        navtb = QToolBar("Navigation")

        # добавление навигации в главное окно
        self.addToolBar(navtb)

        # создание кнопки-действия для возвращения на предыдущую страничку
        back_btn = QAction("<-", self)

        # подсказка о том что делает кнопка (для дальнейших апдейтов)
        back_btn.setStatusTip("Back to previous page")
        # добавление действия к кнопке домой
        # возвращение браузера на предыдущую страничку
        back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())

        # добавление этого действия в навигацию
        # кнопка домой
        navtb.addAction(back_btn)
        home_btn = QAction(self)
        home_btn.setIcon(QIcon("home.png"))
        home_btn.setStatusTip("Go home")
        home_btn.triggered.connect(self.navigate_home)
        navtb.addAction(home_btn)

        # создание кнопки вперед
        next_btn = QAction("->", self)
        next_btn.setStatusTip("Forward to next page")

        # добавление действия этой кнопке
        # пересылка на следующую страничку
        next_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())
        navtb.addAction(next_btn)

        # создание кнопки перезагрузки
        reload_btn = QAction("🔃", self)
        reload_btn.setStatusTip("Reload page")

        # добавление этой кнопке действия
        # перезагрузка странички браузера
        reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
        navtb.addAction(reload_btn)

        # создание QLineEdit для урл открытых страничек
        self.urlbar = QLineEdit()

        # добавление действия при нажатии возврата
        self.urlbar.returnPressed.connect(self.navigate_to_url)

        # добавление в навигацию
        navtb.addWidget(self.urlbar)

        # добавление кнопки стоп
        stop_btn = QAction("❌", self)
        stop_btn.setStatusTip("Stop loading current page")

        # добавление этой кнопке действия
        # останавливает загрузку странички
        stop_btn.triggered.connect(lambda: self.tabs.currentWidget().stop())
        navtb.addAction(stop_btn)
        # добавление кнопки для скачивания ролика с ютуба
        download_bt = QAction(self)
        # добавление иконки для этой кнопки
        download_bt.setIcon(QIcon("download.png"))
        # добавление описания
        download_bt.setStatusTip("Download, open video")
        # действие при нажатии
        download_bt.triggered.connect(self.downloading)
        # добавление в браузер
        navtb.addAction(download_bt)
        # создание кнопки для добавления в избранное
        fav_but = QAction(self)
        # добавление ей иконки
        fav_but.setIcon(QIcon("folower.png"))
        # описание
        fav_but.setStatusTip("do in favourites page")
        # действие при нажатии кнопки
        fav_but.triggered.connect(self.fav_in)
        # добавление в браузер
        navtb.addAction(fav_but)
        # добавление кнопки для просмотра избранного
        favorits_but = QAction(self)
        # добавление ей иконки
        favorits_but.setIcon(QIcon("Folowers.jpg"))
        # описание
        favorits_but.setStatusTip("favorites page")
        # добавление действия
        favorits_but.triggered.connect(self.fav_out)
        # добавление в браузер
        navtb.addAction(favorits_but)
        # отображение всего
        self.add_new_tab(QUrl('http://www.google.com'), 'Homepage')
        self.show()

    def fav_out(self):
        con = sqlite3.connect("folowers_page.db")
        # Создание курсора
        cur = con.cursor()
        # Выполнение запроса и получение всех результатов
        result = cur.execute(f"""SELECT Genre From genres
                """).fetchall()
        # создаем список групп
        p = []
        # проходимся по результату запроса и записываем все в список групп
        for i in result:
            p.append(i[0])
        # диалоговое окно с выбором группы
        gruppa, ok_pressed = QInputDialog.getItem(
            self, "Выберите группу", "группы",
            p, 1, False)
        if ok_pressed:
            # проходимся в базе данных по всем страничкам которые находятся в данной группе
            result = cur.execute(f"""SELECT PageN FROM webs
            WHERE GenreID = '{gruppa}'""")
            # создаем список для того что бы загрузить в него все странички
            p = []
            # создаем переменную для проверки на то есть в базе данных хоть какая-то страничка или нет
            k = False
            # цикл для забрасывания всех данных в список и проверки есть ли данные вообще
            for i in result:
                p.append(i[0])
                if i[0]:
                    k = True

            if k:
                # диалоговое окно с выбором странички на кооторую хоти перейти
                page, ok_pressed = QInputDialog.getItem(
                    self, "Выберите ссылку", "ссылки",
                    p, 1, False)
                if ok_pressed:
                    # создаем экземпляр qurl и открываем выбранную ссылку в новом окне
                    url = QUrl(page)
                    self.add_new_tab(url)
            else:
                # сообщение о ошибке
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Ошибка")
                msg.setText("в этой группе нет сохраненых страничек")
                msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                retval = msg.exec_()

        con.commit()
        con.close()

    def fav_in(self):
        con = sqlite3.connect("folowers_page.db")
        # Создание курсора
        cur = con.cursor()
        # Выполнение запроса и получение всех результатов
        result = cur.execute(f"""SELECT Genre From genres
        """).fetchall()
        # список для закидывания сюда  всех существующих групп для диалогового окна
        p = []
        for i in result:
            p.append(i[0])
        # строчка для возможности выбрать создания новой группы в диалоговом окне
        p.append("Создать новую группу")
        # диалог
        gruppa, ok_pressed = QInputDialog.getItem(
            self, "Выберите группу", "группы",
            p, 1, False)
        if ok_pressed:
            # ссылка на открытую в данный момент страничку
            url = self.urlbar.text()
            url = url.split()[0]

            if gruppa == "Создать новую группу":
                # диалог для ввода названия группы
                name, ok_pressed = QInputDialog.getText(self, "Введите название",
                                                        "Название группы")
                if ok_pressed:
                    # запрос для ввода новой группы в базу данных
                    cur.execute(f"""INSERT INTO genres (Genre) VALUES ('{name}')""")
                    # запрос для ввода новой странички в базу данных
                    cur.execute(f"""INSERT INTO webs (PageN,GenreID) VALUES ('{url}','{name}')""")
            else:
                # запрос для ввода новой странички в существующую группу в базе данных
                cur.execute(f"""INSERT INTO webs (PageN,GenreID) VALUES ('{url}','{gruppa}')""")

        con.commit()

        con.close()

    # метод для названия моего браузера
    def update_title(self, browser):
        if browser != self.tabs.currentWidget():
            return
        title = self.tabs.currentWidget().page().title()
        self.setWindowTitle("% s - Браузер Ислама" % title)

    # метод для возвращения на домашнюю страничку
    def navigate_home(self, browser):
        # открытие домашней странички
        self.tabs.currentWidget().setUrl(QUrl("http://www.google.com"))

    def tab_open_doubleclick(self, i):

        # изменение индекса
        # если нет вкладки под щелчком мыши
        if i == -1:
            # создание новой таблицы
            self.add_new_tab()

        # когда таблица изменяется

    def current_tab_changed(self, i):

        # получить урл
        qurl = self.tabs.currentWidget().url()

        # обновление урла
        self.update_urlbar(qurl, self.tabs.currentWidget())

        # обнволение названия
        self.update_title(self.tabs.currentWidget())

        # когда таблица закрыта

    def close_current_tab(self, i):

        # если есть только одна вкладка
        if self.tabs.count() < 2:
            return

        # удалить вкладку
        self.tabs.removeTab(i)

    # метод, вызываемый строкой edit при нажатии клавиши return
    def navigate_to_url(self):
        # возвращение урла
        q = QUrl(self.urlbar.text())

        # если урл пуст
        if q.scheme() == "":
            # установка в html
            q.setScheme("http")

        # открытие станички в браузере
        self.tabs.currentWidget().setUrl(q)

    # метод для скачивания роликов с ютуба
    def downloading(self):

        url = self.urlbar.text()
        url = url.split()[0]
        if "https://www.youtube.com/watch?v=" not in url:
            # создание окна сообщения для предупреждения пользователя о том что он не открыл видео
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Ошибка")
            msg.setText("вы не открыли видео на ютубе")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            retval = msg.exec_()
        else:
            # диалоговое окно с вопросом о качестве скачивания
            kachestvo, ok_pressed = QInputDialog.getItem(
                self, "Выберите качество", "Качество",
                ("Высокое", "Среднее", "Низкое"), 1, False)
            if ok_pressed:
                # создаем новый поток
                self.thread = QThread()
                # создаем новый обьект класса довнлоад
                self.download = Download(url, kachestvo)
                # переносим обьект на новый поток
                self.download.moveToThread(self.thread)
                # запускаем в новом потоке функцию run класса download
                self.thread.started.connect(self.download.run)
                # запускаем поток
                self.thread.start()
                # останавливаем поток
                self.thread.exit()

    # добавление новой таблицы
    def add_new_tab(self, qurl=None, label="Blank"):

        # если урл пустой
        if qurl is None:
            qurl = QUrl('http://www.google.com')

        # создание места для браузера
        browser = QWebEngineView()

        # настройка урла для веб энджайна
        browser.setUrl(qurl)

        # индекс для веб энджайна в таблице
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)

        # обновление урла
        browser.urlChanged.connect(lambda qurl, browser=browser:
                                   self.update_urlbar(qurl, browser))

        # добавление действия в браузер по завершении загрузки
        # заголовок таблицы
        browser.loadFinished.connect(lambda _, i=i, browser=browser:
                                     self.tabs.setTabText(i, browser.page().title()))

    # метод для обновления урл адреса
    # этот метод вызывает QWebEngineView object
    def update_urlbar(self, q, browser=None):
        if browser != self.tabs.currentWidget():
            return
        # установка текста в строку для урл
        self.urlbar.setText(q.toString())

        # настройка позиции курсора в строке для урл
        self.urlbar.setCursorPosition(0)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("Браузер Ислама")
    ex = Example()
    ex.show()
    sys.exit(app.exec())
