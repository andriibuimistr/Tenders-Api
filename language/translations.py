# -*- coding: utf-8 -*-
from flask import render_template


class RU(object):

    def __init__(self):
        pass

    # Main menu
    @staticmethod
    def menus(key):
        return {'menu_main_page': u'Главная',
                'menu_tenders': u'Тендеры',
                'menu_auctions': u'Аукционы',
                'menu_tools': u'Инструменты',
                'menu_admin': u'Админка',
                'menu_exit': u'Выйти',
                'menu_item_create_tender': u'Создать тендер',
                'menu_item_create_monitoring': u'Создать мониторинг',
                'menu_item_tender_bids': u'Ставки тендера',
                'menu_item_create_auction': u'Создать аукцион',
                'menu_item_create_privatization': u'Создать аукцион МП',
                'menu_item_auction_bids': u'Ставки аукциона',
                'menu_item_platforms': u'Площадки',
                'menu_item_users': u'Пользователи',
                'menu_item_list_of_tenders': u'Список закупок',
                'menu_item_list_of_auctions': u'Список аукционов',
                'menu_item_list_of_reports': u'Список отчетов',
                'menu_item_preferences': u'Настройки'}.get(key, key)

    # Pages titles
    @staticmethod
    def page_titles(key):
        return {'page_title_main_page': u'Главная страница',
                'page_title_creation_of_tender': u'Создание закупки',
                'page_title_bids_of_tender': u'Ставки закупки',
                'page_title_creation_of_monitoring': u'Создание мониторинга',
                'page_title_creation_of_auction': u'Создание аукциона',
                'page_title_creation_of_privatization': u'Создание аукциона МП',
                'page_title_bids_of_auctions': u'Ставки аукциона',
                'page_title_platforms_management': u'Управление площадками',
                'page_title_users_management': u'Управление пользователями',
                'page_title_tenders_management': u'Управление закупками',
                'page_title_auctions_management': u'Управление аукционами',
                'page_title_reports_management': u'Управление отчетами',
                'page_title_user_preferences': u'Настройки пользователя',
                'page_title_report_info': u'Управление отчетом'}.get(key, key)

    # Placeholders
    @staticmethod
    def forms(key):
        return {'form_placeholder_number_of_lots': u'Кол-во лотов',
                'form_placeholder_number_of_items': u'Кол-во предметов',
                'form_placeholder_number_of_bids': u'Кол-во ставок',
                'form_placeholder_accelerator': u'Ускорение',
                'form_placeholder_accelerator_asset': u'Ускорение актива',
                'form_placeholder_accelerator_lot': u'Ускорение лота',
                'form_placeholder_company_id': u'ID компании',
                'form_placeholder_paste_json': u'Место для вставки JSON',
                'form_placeholder_platform_name': u'Имя площадки',
                'form_placeholder_platform_url': u'Адрес площадки',
                'form_placeholder_username': u'Имя пользователя',
                'form_placeholder_password': u'Пароль',
                'form_placeholder_tender_id_long': u'ID закупки',
                'form_checkbox_features': u'Неценовые',
                'form_checkbox_skip_auction': u'Без аукциона',
                'form_checkbox_documents_for_tender': u'Документы к тендеру',
                'form_checkbox_documents_for_monitoring': u'Документы к мониторингу',
                'form_checkbox_documents_for_bids': u'Документы к ставке',
                'form_checkbox_rent': u'Аренда',
                'form_checkbox_one_bid': u'Одна ставка',
                'form_checkbox_insert_json': u'Вставить JSON',
                'form_checkbox_get_json_from_cdb': u'JSON из ЦБД',
                'form_checkbox_enable_tender_id_input': u'Новая закупка'}.get(key, key)

    # Buttons
    @staticmethod
    def buttons(key):
        return {'button_create_tender': u'Создать закупку',
                'button_create_monitoring': u'Создать мониторинг',
                'button_create_auction': u'Создать аукцион',
                'button_delete_alerts': u'Удалить сообщения',
                'button_show_bids': u'Показать ставки',
                'button_add_to_company': u'Добавить',
                'button_add': u'Добавить',
                'button_save': u'Сохранить',
                'button_format_json': u'Форматировать',
                'button_get_json': u'Получить JSON',
                'button_delete_tenders': u'Удалить закупки',
                'button_delete_auctions': u'Удалить аукционы',
                'button_send': u'Отправить',
                'button_edit': u'Редактировать',
                'button_add_file_input': u'+ файл'}.get(key, key)

    # Sections names
    @staticmethod
    def sections(key):
        return {'section_create_tender_response': u'Результаты запросов',
                'section_create_monitoring_response': u'Результаты запросов',
                'section_list_of_bids': u'Ставки',
                'section_input_json': u'Оригинальный JSON',
                'section_output_json': u'Отформатированный JSON',
                'section_list_of_platforms': u'Список площадок',
                'section_list_of_users': u'Список пользователей',
                'section_list_of_tenders': u'Список закупок',
                'section_list_of_auctions': u'Список аукционов',
                'section_popular_links': u'Популярные ссылки',
                'section_add_bug_report': u'Добавить отчет',
                'section_edit_bug_report': u'Редактирование отчета',
                'section_list_of_reports': u'Список отчетов'}.get(key, key)

    # Labels
    @staticmethod
    def labels(key):
        return {'label_company_identifier': u'Идентификатор комп-и',
                'label_company_id': u'ID компании',
                'label_platform': u'Площадка',
                'label_id_in_cdb': u'ID в ЦБД',
                'label_procurement_method_type': u'Тип процедуры',
                'label_number_of_lots': u'Кол-во лотов',
                'label_creator': u'Создатель',
                'label_api_version': u'Версия API',
                'label_status': u'Статус',
                'label_added_to_site': u'На сайте',
                'label_phone': u'Телефон',
                'label_report_title': u'Тема',
                'label_report_type': u'Тип отчета',
                'label_report_content': u'Описание',
                'label_report_priority': u'Приоритет',
                'label_report_file': u'Вложения',
                'label_report_status': u'Статус',
                'label_report_id': u'ID',
                'label_user_interface_language': u'Язык'}.get(key, key)

    # Messages
    @staticmethod
    def messages(key):
        return {'message_tender_has_no_bids': u'В базе данных нет ставок для данной закупки',
                'message_auction_has_no_bids': u'В базе данных нет ставок для данной закупки',
                'message_rendered_json_will_appear_here': u'Отформатированный JSON появится здесь',
                'message_empty_list': u'Список пуст',
                'message_all_rights_reserved': u'Все права защищены'}.get(key, key)

    # Hints
    @staticmethod
    def hints(key):
        return {'hint_delete': u'Удалить',
                'hint_add_report': u'Добавить отчет',
                'hint_project_on_github': u'Проект на GitHub'}.get(key, key)  # + hint_button_up

    # Texts
    @staticmethod
    def texts(key):
        return {'text_add_bug_report_success': u'Отчет был успешно отправлен!',
                'text_edit_bug_report_success': u'Изменения были успешно сохранены!'}.get(key, key)

    # Report statuses
    @staticmethod
    def report_statuses(key):
        return {'report_status_new': u'Новый',
                'report_status_inprogress': u'В работе',
                'report_status_reopened': u'Переоткрыт',
                'report_status_done': u'Готово'}.get(key, key)

    # Report types
    @staticmethod
    def report_types(key):
        return {'report_type_bug': u'Ошибка',
                'report_type_improvement': u'Улучшение',
                'report_type_task': u'Задача'}.get(key, key)

    # Report priorities
    @staticmethod
    def report_priorities(key):
        return {'report_priority_highest': u'Оч. высокий',
                'report_priority_high': u'Высокий',
                'report_priority_medium': u'Средний',
                'report_priority_low': u'Низкий',
                'report_priority_lowest': u'Оч. низкий'}.get(key, key)

    # Alerts
    @staticmethod
    def alerts(key):
        return {'alert_error_404_no_auction_id': u'Аукцион с данным ID отсутствует в локальной базе данных',
                'alert_error_404_no_tender_id': u'Закупка с данным ID отсутствует в локальной базе данных',
                'alert_error_403_general': u'У вас недостаточно прав на выполнение данной операции'}.get(key, key)


class EN(object):
    def __init__(self):
        pass

    # Main menu
    @staticmethod
    def menus(key):
        return {'menu_main_page': u'Main page',
                'menu_tenders': u'Tenders',
                'menu_auctions': u'Auctions',
                'menu_tools': u'Tools',
                'menu_admin': u'Admin',
                'menu_exit': u'Sign out',
                'menu_item_create_tender': u'Create tender',
                'menu_item_create_monitoring': u'Create monitoring',
                'menu_item_tender_bids': u'Bids of tender',
                'menu_item_create_auction': u'Create auction',
                'menu_item_create_privatization': u'Create auction SP',
                'menu_item_auction_bids': u'Bids of auction',
                'menu_item_platforms': u'Platforms',
                'menu_item_users': u'Users',
                'menu_item_list_of_tenders': u'List of tenders',
                'menu_item_list_of_auctions': u'List of auctions',
                'menu_item_list_of_reports': u'List of reports',
                'menu_item_preferences': u'Preferences'}.get(key, key)

    # Pages titles
    @staticmethod
    def page_titles(key):
        return {'page_title_main_page': u'Main page',
                'page_title_creation_of_tender': u'Creation of tender',
                'page_title_bids_of_tender': u'Bids of tender',
                'page_title_creation_of_monitoring': u'Creation of monitoring',
                'page_title_creation_of_auction': u'Creation of auction',
                'page_title_bids_of_auctions': u'Bids of auction',
                'page_title_creation_of_privatization': u'Creation of auction SP',
                'page_title_platforms_management': u'Platforms management',
                'page_title_users_management': u'Users management',
                'page_title_tenders_management': u'Tenders management',
                'page_title_auctions_management': u'Auctions management',
                'page_title_reports_management': u'Reports management',
                'page_title_user_preferences': u'User Settings',
                'page_title_report_info': u'Report management'}.get(key, key)

    # Placeholders
    @staticmethod
    def forms(key):
        return {'form_placeholder_number_of_lots': u'Number of lots',
                'form_placeholder_number_of_items': u'Number of items',
                'form_placeholder_number_of_bids': u'Number of bids',
                'form_placeholder_accelerator': u'Accelerator',
                'form_placeholder_accelerator_asset': u'Asset accelerator',
                'form_placeholder_accelerator_lot': u'Lot accelerator',
                'form_placeholder_company_id': u'Company ID',
                'form_placeholder_paste_json': u'Paste your JSON here',
                'form_placeholder_platform_name': u'Platform name',
                'form_placeholder_platform_url': u'Platform url',
                'form_placeholder_username': u'Username',
                'form_placeholder_password': u'Password',
                'form_placeholder_tender_id_long': u'Tender ID',
                'form_checkbox_features': u'Features',
                'form_checkbox_skip_auction': u'Skip auction',
                'form_checkbox_documents_for_tender': u'Documents for tender',
                'form_checkbox_documents_for_monitoring': u'Documents for monitoring',
                'form_checkbox_documents_for_bids': u'Documents for bids',
                'form_checkbox_rent': u'Rent',
                'form_checkbox_one_bid': u'One bid',
                'form_checkbox_insert_json': u'Insert JSON',
                'form_checkbox_get_json_from_cdb': u'Get JSON from CDB',
                'form_checkbox_enable_tender_id_input': u'New tender'}.get(key, key)

    # Buttons
    @staticmethod
    def buttons(key):
        return {'button_create_tender': u'Create tender',
                'button_create_monitoring': u'Create monitoring',
                'button_create_auction': u'Create auction',
                'button_delete_alerts': u'Delete messages',
                'button_show_bids': u'Show bids',
                'button_add_to_company': u'Add',
                'button_add': u'Add',
                'button_save': u'Save',
                'button_format_json': u'Format',
                'button_get_json': u'Get JSON',
                'button_delete_tenders': u'Delete tenders',
                'button_delete_auctions': u'Delete auctions',
                'button_send': u'Send',
                'button_edit': u'Edit',
                'button_add_file_input': u'+ file'}.get(key, key)

    # Sections names
    @staticmethod
    def sections(key):
        return {'section_create_tender_response': u'Requests results',
                'section_create_monitoring_response': u'Requests results',
                'section_list_of_bids': u'Bids',
                'section_input_json': u'Original JSON',
                'section_output_json': u'Output JSON',
                'section_list_of_platforms': u'List of platforms',
                'section_list_of_users': u'List of users',
                'section_list_of_tenders': u'List of tenders',
                'section_list_of_auctions': u'List of auctions',
                'section_popular_links': u'Popular links',
                'section_add_bug_report': u'Add report',
                'section_edit_bug_report': u'Edit report',
                'section_list_of_reports': u'List of reports'}.get(key, key)

    # Labels
    @staticmethod
    def labels(key):
        return {'label_company_identifier': u'Company identifier',
                'label_company_id': u'Company ID',
                'label_platform': u'Platform',
                'label_id_in_cdb': u'ID in CDB',
                'label_procurement_method_type': u'Type of procurement',
                'label_number_of_lots': u'Number of lots',
                'label_creator': u'Creator',
                'label_api_version': u'API version',
                'label_status': u'Status',
                'label_added_to_site': u'Added to site',
                'label_phone': u'Phone number',
                'label_report_title': u'Subject',
                'label_report_type': u'Report type',
                'label_report_content': u'Description',
                'label_report_priority': u'Priority',
                'label_report_file': u'Attachments',
                'label_report_status': u'Status',
                'label_report_id': u'ID',
                'label_user_interface_language': u'Language'}.get(key, key)

    # Messages
    @staticmethod
    def messages(key):
        return {'message_tender_has_no_bids': u'There are no bids for this tender in the database',
                'message_auction_has_no_bids': u'There are no bids for this auction in the database',
                'message_rendered_json_will_appear_here': u'Formatted JSON will appear here',
                'message_empty_list': u'List is empty',
                'message_all_rights_reserved': u'All rights reserved'}.get(key, key)

    # Hints
    @staticmethod
    def hints(key):
        return {'hint_delete': u'Delete',
                'hint_add_report': u'Add report',
                'hint_project_on_github': u'Project on GitHub'}.get(key, key)

    # Texts
    @staticmethod
    def texts(key):
        return {'text_add_bug_report_success': u'Report was submitted successfully!',
                'text_edit_bug_report_success': u'The changes have been successfully saved!'}.get(key, key)

    # Report statuses
    @staticmethod
    def report_statuses(key):
        return {'report_status_new': u'New',
                'report_status_inprogress': u'In progress',
                'report_status_reopened': u'Re-opened',
                'report_status_done': u'Done'}.get(key, key)

    # Report types
    @staticmethod
    def report_types(key):
        return {'report_type_bug': u'Bug',
                'report_type_improvement': u'Improvement',
                'report_type_task': u'Task'}.get(key, key)

    # Report priorities
    @staticmethod
    def report_priorities(key):
        return {'report_priority_highest': u'Highest',
                'report_priority_high': u'High',
                'report_priority_medium': u'Medium',
                'report_priority_low': u'Low',
                'report_priority_lowest': u'Lowest'}.get(key, key)

    # Alerts
    @staticmethod
    def alerts(key):
        return {'alert_error_404_no_auction_id': u'Auction with this ID doesn\'t exist in the local database',
                'alert_error_404_no_tender_id': u'Tender with this ID doesn\'t exist in the local database',
                'alert_error_403_general': u'You are not allowed to perform this action'}.get(key, key)


class ES(object):
    def __init__(self):
        self.lang = 'ES'

    # Main menu
    @staticmethod
    def menus(key):
        return {'menu_main_page': u'Inicio',
                'menu_tenders': u'Licitaciones',
                'menu_auctions': u'Subastas',
                'menu_tools': u'Herramientas',
                'menu_admin': u'Administrador',
                'menu_exit': u'Salir',
                'menu_item_create_tender': u'Crear licitación',
                'menu_item_create_monitoring': u'Crear supervisión',
                'menu_item_tender_bids': u'Apuestas de licitación',
                'menu_item_create_auction': u'Crear subasta',
                'menu_item_create_privatization': u'Crear subasta PP',
                'menu_item_auction_bids': u'Apuestas de subasta',
                'menu_item_platforms': u'Plataformas',
                'menu_item_users': u'Usuarios',
                'menu_item_list_of_tenders': u'Lista de licitaciones',
                'menu_item_list_of_auctions': u'Lista de subastas',
                'menu_item_list_of_reports': u'Lista de informes',
                'menu_item_preferences': u'Preferencias'}.get(key, key)

    # Pages titles
    @staticmethod
    def page_titles(key):
        return {'page_title_main_page': u'Página de inicio',
                'page_title_creation_of_tender': u'Creación de licitación',
                'page_title_bids_of_tender': u'Apuestas de licitación',
                'page_title_creation_of_monitoring': u'Creación de supervisión',
                'page_title_creation_of_auction': u'Creación de subasta',
                'page_title_bids_of_auctions': u'Apuestas de subasta',
                'page_title_creation_of_privatization': u'Creación de subasta PP',
                'page_title_platforms_management': u'Gestión de plataformas',
                'page_title_users_management': u'Gestión de usuarios',
                'page_title_tenders_management': u'Gestión de licitaciones',
                'page_title_auctions_management': u'Gestión de subastas',
                'page_title_reports_management': u'Gestión de informes',
                'page_title_user_preferences': u'Configuración del usuario',
                'page_title_report_info': u'Gestión de informe'}.get(key, key)

    # Placeholders
    @staticmethod
    def forms(key):
        return {'form_placeholder_number_of_lots': u'Núm. de lotes',
                'form_placeholder_number_of_items': u'Núm. de artículos',
                'form_placeholder_number_of_bids': u'Núm. de apuestas',
                'form_placeholder_accelerator': u'Acelerador',
                'form_placeholder_accelerator_asset': u'Acelerador del activo',
                'form_placeholder_accelerator_lot': u'Acelerador del lote',
                'form_placeholder_company_id': u'ID de compañía',
                'form_placeholder_paste_json': u'Lugar para insertar JSON',
                'form_placeholder_platform_name': u'Nombre de plataforma',
                'form_placeholder_platform_url': u'URL de plataforma',
                'form_placeholder_username': u'Nombre de usuario',
                'form_placeholder_password': u'Contraseña',
                'form_placeholder_tender_id_long': u'ID de licitación',
                'form_checkbox_features': u'Características',
                'form_checkbox_skip_auction': u'Saltar subasta',
                'form_checkbox_documents_for_tender': u'Documentos de licitación',
                'form_checkbox_documents_for_monitoring': u'Documentos de supervisión',
                'form_checkbox_documents_for_bids': u'Documentos de apuestas',
                'form_checkbox_rent': u'Alquiler',
                'form_checkbox_one_bid': u'Una apuesta',
                'form_checkbox_insert_json': u'Insertar JSON',
                'form_checkbox_get_json_from_cdb': u'Obtener JSON de BCD',
                'form_checkbox_enable_tender_id_input': u'Nueva licitación'}.get(key, key)

    # Buttons
    @staticmethod
    def buttons(key):
        return {'button_create_tender': u'Crear licitación',
                'button_create_monitoring': u'Crear supervisión',
                'button_create_auction': u'Crear subasta',
                'button_delete_alerts': u'Eliminar mensajes',
                'button_show_bids': u'Mostrar apuestas',
                'button_add_to_company': u'Añadir',
                'button_add': u'Añadir',
                'button_save': u'Guardar',
                'button_format_json': u'Formatear',
                'button_get_json': u'Obtener JSON',
                'button_delete_tenders': u'Eliminar licitaciones',
                'button_delete_auctions': u'Eliminar subastas',
                'button_send': u'Enviar',
                'button_edit': u'Editar',
                'button_add_file_input': u'+ archivo'}.get(key, key)

    # Sections names
    @staticmethod
    def sections(key):
        return {'section_create_tender_response': u'Resultados de las solicitudes',
                'section_create_monitoring_response': u'Resultados de las solicitudes',
                'section_list_of_bids': u'Apuestas',
                'section_input_json': u'JSON original',
                'section_output_json': u'JSON formateado',
                'section_list_of_platforms': u'Lista de plataformas',
                'section_list_of_users': u'Lista de usuarios',
                'section_list_of_tenders': u'Lista de licitaciones',
                'section_list_of_auctions': u'Lista de subastas',
                'section_popular_links': u'Enlaces populares',
                'section_add_bug_report': u'Añadir informe',
                'section_edit_bug_report': u'Editar informe',
                'section_list_of_reports': u'Lista de informes'}.get(key, key)

    # Labels
    @staticmethod
    def labels(key):
        return {'label_company_identifier': u'Identificador de compañía',
                'label_company_id': u'ID de compañía',
                'label_platform': u'Plataforma',
                'label_id_in_cdb': u'ID en BCD',
                'label_procurement_method_type': u'Tipo de licitación',
                'label_number_of_lots': u'Núm. de lotes',
                'label_creator': u'Creador',
                'label_api_version': u'Versión de API',
                'label_status': u'Estado',
                'label_added_to_site': u'En plataforma',
                'label_phone': u'Teléfono',
                'label_report_title': u'Tema',
                'label_report_type': u'Tipo de informe',
                'label_report_content': u'Descripción',
                'label_report_priority': u'Prioridad',
                'label_report_file': u'Archivos adjuntos',
                'label_report_status': u'Estado',
                'label_report_id': u'ID',
                'label_user_interface_language': u'Idioma'}.get(key, key)

    # Messages
    @staticmethod
    def messages(key):
        return {'message_tender_has_no_bids': u'No hay apuestas para esta licitación en la base de datos',
                'message_auction_has_no_bids': u'No hay apuestas para esta subasta en la base de datos',
                'message_rendered_json_will_appear_here': u'JSON formateado aparecerá aquí',
                'message_empty_list': u'La lista no contiene elementos',
                'message_all_rights_reserved': u'Necesita permiso para realizar esta acción'}.get(key, key)

    # Hints
    @staticmethod
    def hints(key):
        return {'hint_delete': u'Borrar',
                'hint_add_report': u'Añadir informe',
                'hint_project_on_github': u'Proyecto en GitHub'}.get(key, key)

    # Texts
    @staticmethod
    def texts(key):
        return {'text_add_bug_report_success': u'El informe fue enviado con éxito!',
                'text_edit_bug_report_success': u'Los cambios se han guardado con éxito!'}.get(key, key)

    # Report statuses
    @staticmethod
    def report_statuses(key):
        return {'report_status_new': u'Nuevo',
                'report_status_inprogress': u'En curso',
                'report_status_reopened': u'Reabierto',
                'report_status_done': u'Listo'}.get(key, key)

    # Report types
    @staticmethod
    def report_types(key):
        return {'report_type_bug': u'Error',
                'report_type_improvement': u'Mejora',
                'report_type_task': u'Tarea'}.get(key, key)

    # Report priorities
    @staticmethod
    def report_priorities(key):
        return {'report_priority_highest': u'Muy alta',
                'report_priority_high': u'Alta',
                'report_priority_medium': u'Media',
                'report_priority_low': u'Baja',
                'report_priority_lowest': u'Muy baja'}.get(key, key)

    # Alerts
    @staticmethod
    def alerts(key):
        return {'alert_error_404_no_auction_id': u'Subasta con este ID no existe en la base de datos local',
                'alert_error_404_no_tender_id': u'Licitación con este ID no existe en la base de datos local',
                'alert_error_403_general': u'You are not allowed to perform this action'}.get(key, key)


class Translations(object):

    def __init__(self, language):
        self.lng = language
        self.default_lng = EN

    def language_selector(self):  # Select class for translations
        return {'ru': RU,
                'en': EN,
                'es': ES,
                }.get(self.lng, self.default_lng)

    # MAIN MENU TRANSLATIONS
    def menu(self, key):
        return self.language_selector().menus(key)

    # PAGES TITLES
    def page_title(self, key):
        return self.language_selector().page_titles(key)

    # FORMS ELEMENTS
    def form(self, key):
        return self.language_selector().forms(key)

    # BUTTONS
    def button(self, key):
        return self.language_selector().buttons(key)

    # SECTIONS
    def section(self, key):
        return self.language_selector().sections(key)

    # LABELS
    def label(self, key):
        return self.language_selector().labels(key)

    # MESSAGES
    def message(self, key):
        return self.language_selector().messages(key)

    # HINTS
    def hint(self, key):
        return self.language_selector().hints(key)

    # TEXTS
    def text(self, key):
        return self.language_selector().texts(key)

    # REPORT STATUS
    def report_status(self, key):
        return self.language_selector().report_statuses(key)

    # REPORT TYPE
    def report_type(self, key):
        return self.language_selector().report_types(key)

    # REPORT PRIORITY
    def report_priority(self, key):
        return self.language_selector().report_priorities(key)

    # ALERTS
    def alert(self, key):
        return self.language_selector().alerts(key)


class Alerts(object):

    def __init__(self):
        pass

    @staticmethod
    def error_404_not_found(message_key):
        return render_template('alerts/error/error_404_not_found.html', alert_text=message_key)

    @staticmethod
    def error_403_forbidden(message_key):
        return render_template('alerts/error/error_403_forbidden.html', alert_text=message_key)


alert = Alerts()
