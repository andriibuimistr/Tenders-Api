# -*- coding: utf-8 -*-


class RU(object):

    def __init__(self):
        pass

    # Main menu
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

    # Pages titles
    page_title_main_page = u'Главная страница'
    page_title_creation_of_tender = u'Создание закупки'
    page_title_bids_of_tender = u'Ставки закупки'
    page_title_creation_of_auction = u'Создание аукциона'
    page_title_bids_of_auctions = u'Ставки аукциона'
    page_title_platforms_management = u'Управление площадками'
    page_title_users_management = u'Управление пользователями'
    page_title_tenders_management = u'Управление закупками'
    page_title_user_preferences = u'Настройки пользователя'

    # Placeholders
    form_placeholder_number_of_lots = u'Кол-во лотов'
    form_placeholder_number_of_items = u'Кол-во предметов'
    form_placeholder_number_of_bids = u'Кол-во ставок'
    form_placeholder_accelerator = u'Ускорение'
    form_placeholder_company_id = u'ID компании'
    form_placeholder_paste_json = u'Место для вставки JSON'
    form_placeholder_platform_name = u'Имя площадки'
    form_placeholder_platform_url = u'Адрес площадки'
    form_placeholder_username = u'Имя пользователя'
    form_placeholder_password = u'Пароль'
    form_checkbox_features = u'Неценовые'
    form_checkbox_skip_auction = u'Без аукциона'
    form_checkbox_documents_for_tender = u'Документы к тендеру'
    form_checkbox_documents_for_bids = u'Документы к ставке'
    form_checkbox_rent = u'Аренда'
    form_checkbox_one_bid = u'Одна ставка'
    form_checkbox_insert_json = u'Вставить JSON'
    form_checkbox_get_json_from_cdb = u'JSON из ЦБД'

    # Buttons
    button_create_tender = u'Создать закупку'
    button_create_auction = u'Создать аукцион'
    button_delete_alerts = u'Удалить сообщения'
    button_show_bids = u'Показать ставки'
    button_add_to_company = u'Добавить'
    button_add = u'Добавить'
    button_save = u'Сохранить'
    button_format_json = u'Форматировать'
    button_get_json = u'Получить JSON'
    button_delete_tenders = u'Удалить закупки'

    # Sections names
    section_create_tender_response = u'Результаты запросов'
    section_list_of_bids = u'Ставки'
    section_input_json = u'Оригинальный JSON'
    section_output_json = u'Отформатированный JSON'
    section_list_of_platforms = u'Список площадок'
    section_list_of_users = u'Список пользователей'
    section_list_of_tenders = u'Список Закупок'
    section_popular_links = u'Популярные ссылки'

    # Labels
    label_company_identifier = u'Идентификатор комп-и'
    label_company_id = u'ID компании'
    label_platform = u'Площадка'
    label_id_in_cdb = u'ID в ЦБД'
    label_procurement_method_type = u'Тип процедуры'
    label_number_of_lots = u'Кол-во лотов'
    label_creator = u'Создатель'
    label_api_version = u'Версия API'
    label_status = u'Статус'
    label_added_to_site = u'На сайте'
    label_phone = u'Телефон'

    # Messages
    message_tender_has_no_bids = u'В базе данных нет ставок для данной закупки'
    message_auction_has_no_bids = u'В базе данных нет ставок для данной закупки'
    message_rendered_json_will_appear_here = u'Отформатированный JSON появится здесь'
    message_empty_list = u'Список пуст'
    message_all_rights_reserved = u'Все права защищены'

    # Hints
    hint_delete = u'Удалить'


class EN(object):
    def __init__(self):
        pass

    # Main menu
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

    # Pages titles
    page_title_main_page = u'Main page'
    page_title_creation_of_tender = u'Creation of tender'
    page_title_bids_of_tender = u'Bids of tender'
    page_title_creation_of_auction = u'Creation of auction'
    page_title_bids_of_auctions = u'Bids of auction'
    page_title_platforms_management = u'Platforms management'
    page_title_users_management = u'Users management'
    page_title_tenders_management = u'Tenders management'
    page_title_user_preferences = u'User Settings'

    # Placeholders
    form_placeholder_number_of_lots = u'Number of lots'
    form_placeholder_number_of_items = u'Number of items'
    form_placeholder_number_of_bids = u'Number of bids'
    form_placeholder_accelerator = u'Accelerator'
    form_placeholder_company_id = u'Company ID'
    form_placeholder_paste_json = u'Paste your JSON here'
    form_placeholder_platform_name = u'Platform name'
    form_placeholder_platform_url = u'Platform url'
    form_placeholder_username = u'Username'
    form_placeholder_password = u'Password'
    form_checkbox_features = u'Features'
    form_checkbox_skip_auction = u'Skip auction'
    form_checkbox_documents_for_tender = u'Documents for tender'
    form_checkbox_documents_for_bids = u'Documents for bids'
    form_checkbox_rent = u'Rent'
    form_checkbox_one_bid = u'One bid'
    form_checkbox_insert_json = u'Insert JSON'
    form_checkbox_get_json_from_cdb = u'Get JSON from CDB'

    # Buttons
    button_create_tender = u'Create tender'
    button_create_auction = u'Create auction'
    button_delete_alerts = u'Delete messages'
    button_show_bids = u'Show bids'
    button_add_to_company = u'Add'
    button_add = u'Add'
    button_save = u'Save'
    button_format_json = u'Format'
    button_get_json = u'Get JSON'
    button_delete_tenders = u'Delete tenders'

    # Sections names
    section_create_tender_response = u'Requests results'
    section_list_of_bids = u'Bids'
    section_input_json = u'Original JSON'
    section_output_json = u'Output JSON'
    section_list_of_platforms = u'List of platforms'
    section_list_of_users = u'List of users'
    section_list_of_tenders = u'List of tenders'
    section_popular_links = u'Popular links'

    # Labels
    label_company_identifier = u'Company identifier'
    label_company_id = u'Company ID'
    label_platform = u'Platform'
    label_id_in_cdb = u'ID in CDB'
    label_procurement_method_type = u'Type of procurement'
    label_number_of_lots = u'Number of lots'
    label_creator = u'Creator'
    label_api_version = u'API version'
    label_status = u'Status'
    label_added_to_site = u'Added to site'
    label_phone = u'Phone number'

    # Messages
    message_tender_has_no_bids = u'There are no bids for this tender in the database'
    message_auction_has_no_bids = u'There are no bids for this auction in the database'
    message_rendered_json_will_appear_here = u'Formatted JSON will appear here'
    message_empty_list = u'List is empty'
    message_all_rights_reserved = u'All rights reserved'

    # Hints
    hint_delete = u'Delete'


class ES(object):
    def __init__(self):
        pass

    # Main menu
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

    # Pages titles
    page_title_main_page = u'Página de inicio'
    page_title_creation_of_tender = u'Creación de licitación'
    page_title_bids_of_tender = u'Apuestas de licitación'
    page_title_creation_of_auction = u'Creación de subasta'
    page_title_bids_of_auctions = u'Apuestas de subasta'
    page_title_platforms_management = u'Gestión de plataformas'
    page_title_users_management = u'Gestión de usuarios'
    page_title_tenders_management = u'Gestión de licitaciones'
    page_title_user_preferences = u'Configuración del usuario'

    # Placeholders
    form_placeholder_number_of_lots = u'Núm. de lotes'
    form_placeholder_number_of_items = u'Núm. de artículos'
    form_placeholder_number_of_bids = u'Núm. de apuestas'
    form_placeholder_accelerator = u'Acelerador'
    form_placeholder_company_id = u'ID de compañía'
    form_placeholder_paste_json = u'Lugar para insertar JSON'
    form_placeholder_platform_name = u'Nombre de plataforma'
    form_placeholder_platform_url = u'URL de plataforma'
    form_placeholder_username = u'Nombre de usuario'
    form_placeholder_password = u'Contraseña'
    form_checkbox_features = u'Características'
    form_checkbox_skip_auction = u'Saltar subasta'
    form_checkbox_documents_for_tender = u'Documentos de licitación'
    form_checkbox_documents_for_bids = u'Documentos de apuestas'
    form_checkbox_rent = u'Alquiler'
    form_checkbox_one_bid = u'Una apuesta'
    form_checkbox_insert_json = u'Insertar JSON'
    form_checkbox_get_json_from_cdb = u'Obtener JSON de BCD'

    # Buttons
    button_create_tender = u'Crear licitación'
    button_create_auction = u'Crear subasta'
    button_delete_alerts = u'Eliminar mensajes'
    button_show_bids = u'Mostrar apuestas'
    button_add_to_company = u'Añadir'
    button_add = u'Añadir'
    button_save = u'Guardar'
    button_format_json = u'Formatear'
    button_get_json = u'Obtener JSON'
    button_delete_tenders = u'Eliminar licitaciones'

    # Sections names
    section_create_tender_response = u'Resultados de las solicitudes'
    section_list_of_bids = u'Apuestas'
    section_input_json = u'JSON original'
    section_output_json = u'JSON formateado'
    section_list_of_platforms = u'Lista de plataformas'
    section_list_of_users = u'Lista de usuarios'
    section_list_of_tenders = u'Lista de licitaciones'
    section_popular_links = u'Enlaces populares'

    # Labels
    label_company_identifier = u'Identificador de compañía'
    label_company_id = u'ID de compañía'
    label_platform = u'Plataforma'
    label_id_in_cdb = u'ID en BCD'
    label_procurement_method_type = u'Tipo de licitación'
    label_number_of_lots = u'Núm. de lotes'
    label_creator = u'Creador'
    label_api_version = u'Versión de API'
    label_status = u'Estado'
    label_added_to_site = u'En plataforma'
    label_phone = u'Teléfono'

    # Messages
    message_tender_has_no_bids = u'No hay apuestas para esta licitación en la base de datos'
    message_auction_has_no_bids = u'No hay apuestas para esta subasta en la base de datos'
    message_rendered_json_will_appear_here = u'JSON formateado aparecerá aquí'
    message_empty_list = u'La lista no contiene elementos'
    message_all_rights_reserved = u'Todos los derechos reservados'

    # Hints
    hint_delete = u'Borrar'


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

    # FORMS ELEMENTS
    def form_placeholder_number_of_lots(self):
        return self.class_selector().form_placeholder_number_of_lots

    def form_placeholder_number_of_items(self):
        return self.class_selector().form_placeholder_number_of_items

    def form_placeholder_number_of_bids(self):
        return self.class_selector().form_placeholder_number_of_bids

    def form_placeholder_accelerator(self):
        return self.class_selector().form_placeholder_accelerator

    def form_placeholder_company_id(self):
        return self.class_selector().form_placeholder_company_id

    def form_placeholder_paste_json(self):
        return self.class_selector().form_placeholder_paste_json

    def form_placeholder_platform_name(self):
        return self.class_selector().form_placeholder_platform_name

    def form_placeholder_platform_url(self):
        return self.class_selector().form_placeholder_platform_url

    def form_placeholder_username(self):
        return self.class_selector().form_placeholder_username

    def form_placeholder_password(self):
        return self.class_selector().form_placeholder_password

    def form_checkbox_features(self):
        return self.class_selector().form_checkbox_features

    def form_checkbox_skip_auction(self):
        return self.class_selector().form_checkbox_skip_auction

    def form_checkbox_documents_for_tender(self):
        return self.class_selector().form_checkbox_documents_for_tender

    def form_checkbox_documents_for_bids(self):
        return self.class_selector().form_checkbox_documents_for_bids

    def form_checkbox_rent(self):
        return self.class_selector().form_checkbox_rent

    def form_checkbox_one_bid(self):
        return self.class_selector().form_checkbox_one_bid

    def form_checkbox_insert_json(self):
        return self.class_selector().form_checkbox_insert_json

    def form_checkbox_get_json_from_cdb(self):
        return self.class_selector().form_checkbox_get_json_from_cdb

    # BUTTONS
    def button_create_tender(self):
        return self.class_selector().button_create_tender

    def button_create_auction(self):
        return self.class_selector().button_create_auction

    def button_delete_alerts(self):
        return self.class_selector().button_delete_alerts

    def button_show_bids(self):
        return self.class_selector().button_show_bids

    def button_add_to_company(self):
        return self.class_selector().button_add_to_company

    def button_add(self):
        return self.class_selector().button_add

    def button_save(self):
        return self.class_selector().button_save

    def button_format_json(self):
        return self.class_selector().button_format_json

    def button_get_json(self):
        return self.class_selector().button_get_json

    def button_delete_tenders(self):
        return self.class_selector().button_delete_tenders

    # SECTIONS
    def section_create_tender_response(self):
        return self.class_selector().section_create_tender_response

    def section_list_of_bids(self):
        return self.class_selector().section_list_of_bids

    def section_input_json(self):
        return self.class_selector().section_input_json

    def section_output_json(self):
        return self.class_selector().section_output_json

    def section_list_of_platforms(self):
        return self.class_selector().section_list_of_platforms

    def section_list_of_users(self):
        return self.class_selector().section_list_of_users

    def section_list_of_tenders(self):
        return self.class_selector().section_list_of_tenders

    def section_popular_links(self):
        return self.class_selector().section_popular_links

    # LABELS
    def label_company_identifier(self):
        return self.class_selector().label_company_identifier

    def label_company_id(self):
        return self.class_selector().label_company_id

    def label_platform(self):
        return self.class_selector().label_platform

    def label_id_in_cdb(self):
        return self.class_selector().label_id_in_cdb

    def label_procurement_method_type(self):
        return self.class_selector().label_procurement_method_type

    def label_number_of_lots(self):
        return self.class_selector().label_number_of_lots

    def label_creator(self):
        return self.class_selector().label_creator

    def label_api_version(self):
        return self.class_selector().label_api_version

    def label_status(self):
        return self.class_selector().label_status

    def label_added_to_site(self):
        return self.class_selector().label_added_to_site

    def label_phone(self):
        return self.class_selector().label_phone

    # MESSAGES
    def message_tender_has_no_bids(self):
        return self.class_selector().message_tender_has_no_bids

    def message_auction_has_no_bids(self):
        return self.class_selector().message_auction_has_no_bids

    def message_rendered_json_will_appear_here(self):
        return self.class_selector().message_rendered_json_will_appear_here

    def message_empty_list(self):
        return self.class_selector().message_empty_list

    def message_all_rights_reserved(self):
        return self.class_selector().message_all_rights_reserved

    # HINTS
    def hint_delete(self):
        return self.class_selector().hint_delete
