# -*- coding: utf-8 -*-


class RU(object):

    def __init__(self):
        pass

    menu_main_page = u'Главная'
    menu_tenders = u'Тендеры'
    menu_auctions = u'Аукционы'
    menu_tools = u'Инструменты'
    menu_admin = u'Админка'
    menu_exit = u'Выйти'
    menu_item_create_tender = u'Создать тендер'
    menu_item_tender_bids = u'Ставки тендера'
    menu_item_create_auction = u'Создать аукцион'
    menu_item_auction_bids = u'Ставки аукциона'
    menu_item_platforms = u'Площадки'
    menu_item_users = u'Пользователи'
    menu_item_list_of_tenders = u'Список закупок'
    menu_item_preferences = u'Настройки'

    page_title_main_page = u'Главная страница'
    page_title_creation_of_tender = u'Создание закупки'
    page_title_bids_of_tender = u'Ставки закупки'
    page_title_creation_of_auction = u'Создание аукциона'
    page_title_bids_of_auctions = u'Ставки аукциона'
    page_title_platforms_management = u'Управление площадками'
    page_title_users_management = u'Управление пользователями'
    page_title_tenders_management = u'Управление закупками'
    page_title_user_preferences = u'Настройки пользователя'


class EN(object):
    def __init__(self):
        pass

    menu_main_page = u'Main page'
    menu_tenders = u'Tenders'
    menu_auctions = u'Auctions'
    menu_tools = u'Tools'
    menu_admin = u'Admin'
    menu_exit = u'Sign out'
    menu_item_create_tender = u'Create tender'
    menu_item_tender_bids = u'Bids of tender'
    menu_item_create_auction = u'Create auction'
    menu_item_auction_bids = u'Bids of auction'
    menu_item_platforms = u'Platforms'
    menu_item_users = u'Users'
    menu_item_list_of_tenders = u'List of tenders'
    menu_item_preferences = u'Preferences'

    page_title_main_page = u'Main page'
    page_title_creation_of_tender = u'Creation of tender'
    page_title_bids_of_tender = u'Bids of tender'
    page_title_creation_of_auction = u'Creation of auction'
    page_title_bids_of_auctions = u'Bids of auction'
    page_title_platforms_management = u'Platforms management'
    page_title_users_management = u'Users management'
    page_title_tenders_management = u'Tenders management'
    page_title_user_preferences = u'User Settings'


class ES(object):
    def __init__(self):
        pass

    menu_main_page = u'Inicio'
    menu_tenders = u'Licitaciones'
    menu_auctions = u'Subastas'
    menu_tools = u'Herramientas'
    menu_admin = u'Administrador'
    menu_exit = u'Salir'
    menu_item_create_tender = u'Crear licitación'
    menu_item_tender_bids = u'Apuestas de licitación'
    menu_item_create_auction = u'Crear subasta'
    menu_item_auction_bids = u'Apuestas de subasta'
    menu_item_platforms = u'Plataformas'
    menu_item_users = u'Usuarios'
    menu_item_list_of_tenders = u'Lista de licitaciones'
    menu_item_preferences = u'Preferencias'

    page_title_main_page = u'Página de inicio'
    page_title_creation_of_tender = u'Creación de licitación'
    page_title_bids_of_tender = u'Apuestas de licitación'
    page_title_creation_of_auction = u'Creación de subasta'
    page_title_bids_of_auctions = u'Apuestas de subasta'
    page_title_platforms_management = u'Gestión de plataformas'
    page_title_users_management = u'Gestión de usuarios'
    page_title_tenders_management = u'Gestión de licitaciones'
    page_title_user_preferences = u'Configuración del usuario'


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
    def menu_main_page(self):
        return self.class_selector().menu_main_page

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

    def menu_item_create_tender(self):
        return self.class_selector().menu_item_create_tender

    def menu_item_tender_bids(self):
        return self.class_selector().menu_item_tender_bids

    def menu_item_create_auction(self):
        return self.class_selector().menu_item_create_auction

    def menu_item_auction_bids(self):
        return self.class_selector().menu_item_auction_bids

    def menu_item_platforms(self):
        return self.class_selector().menu_item_platforms

    def menu_item_users(self):
        return self.class_selector().menu_item_users

    def menu_item_list_of_tenders(self):
        return self.class_selector().menu_item_list_of_tenders

    def menu_item_preferences(self):
        return self.class_selector().menu_item_preferences

    # PAGES TITLES
    def page_title_main_page(self):
        return self.class_selector().page_title_main_page

    def page_title_creation_of_tender(self):
        return self.class_selector().page_title_creation_of_tender

    def page_title_bids_of_tender(self):
        return self.class_selector().page_title_bids_of_tender

    def page_title_creation_of_auction(self):
        return self.class_selector().page_title_creation_of_auction

    def page_title_bids_of_auctions(self):
        return self.class_selector().page_title_bids_of_auctions

    def page_title_platforms_management(self):
        return self.class_selector().page_title_platforms_management

    def page_title_users_management(self):
        return self.class_selector().page_title_users_management

    def page_title_tenders_management(self):
        return self.class_selector().page_title_tenders_management

    def page_title_user_preferences(self):
        return self.class_selector().page_title_user_preferences
