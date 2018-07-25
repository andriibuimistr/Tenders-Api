# -*- coding: utf-8 -*-


class RU(object):

    def __init__(self):
        pass

    main_page = u'Главная'
    menu_tenders = u'Тендеры'
    menu_auctions = u'Аукционы'
    menu_tools = u'Инструменты'
    menu_admin = u'Админка'
    menu_exit = u'Выйти'
    menu_create_tender = u'Создать тендер'
    menu_tender_bids = u'Ставки тендера'


class EN(object):
    def __init__(self):
        pass

    main_page = u'Main page'
    menu_tenders = u'Tenders'
    menu_auctions = u'Auctions'
    menu_tools = u'Tools'
    menu_admin = u'Admin'
    menu_exit = u'Sign out'
    menu_create_tender = u'Create tender'
    menu_tender_bids = u'Bids of tender'


class ES(object):
    def __init__(self):
        pass

    main_page = u'Inicio'
    menu_tenders = u'Licitaciones'
    menu_auctions = u'Subastas'
    menu_tools = u'Herramientas'
    menu_admin = u'Administrador'
    menu_exit = u'Salir'
    menu_create_tender = u'Crear licitación'
    menu_tender_bids = u'Apuestas de licitación'


class Translations(object):

    def __init__(self, language):
        self.lng = language
        self.default_lng = EN

    def class_selector(self):  # Select class for translations
        return {'ru': RU,
                'en': EN,
                'es': ES,
                }.get(self.lng, self.default_lng)

    # MAIN MENU TRANSLATIONS
    def main_page(self):
        return self.class_selector().main_page

    def menu_tenders(self):
        return self.class_selector().menu_tenders

    def menu_auctions(self):
        return self.class_selector().menu_auctions

    def menu_tools(self):
        return self.class_selector().menu_tools

    def menu_admin(self):
        return self.class_selector().menu_admin

    def menu_exit(self):
        return self.class_selector().menu_exit

    def menu_create_tender(self):
        return self.class_selector().menu_create_tender

    def menu_tender_bids(self):
        return self.class_selector().menu_tender_bids


print Translations('es').menu_tender_bids()
