from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db_host = '82.163.176.242'
user = 'carrosde_python'
password = 'python'
d_base = 'carrosde_tenders'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://{}:{}@{}/{}'.format(user, password, db_host, d_base)
app.config['SQLALCHEMY_POOL_RECYCLE'] = 30
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 60
db = SQLAlchemy(app)


class Companies(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, primary_key=True)
    company_email = db.Column(db.String(255))
    company_id = db.Column(db.String(255))
    company_role_id = db.Column(db.String(255))
    platform_id = db.Column(db.String(255))
    company_identifier = db.Column(db.String(255))

    def __init__(self, id, company_email, company_id, company_role_id, platform_id, company_identifier):
        self.id = id
        self.company_email = company_email
        self.company_id = company_id
        self.company_role_id = company_role_id
        self.platform_id = platform_id
        self.company_identifier = company_identifier


class Tenders(db.Model):
    __tablename__ = 'tenders'
    id = db.Column(db.Integer, primary_key=True)
    tender_id_long = db.Column(db.String(255))
    tender_id_short = db.Column(db.String(255))
    tender_token = db.Column(db.String(255))
    procurementMethodType = db.Column(db.String(255))
    related_tender_id = db.Column(db.String(255))
    tender_status = db.Column(db.String(255))
    n_lots = db.Column(db.Integer)
    tender_platform_id = db.Column(db.Integer)
    company_uid = db.Column(db.Integer)
    added_to_site = db.Column(db.Integer)
    creator_id = db.Column(db.Integer)
    api_version = db.Column(db.String(255))

    def __init__(self, id, tender_id_long, tender_id_short, tender_token, procurementMethodType, related_tender_id,
                 tender_status, n_lots, tender_platform_id, company_uid, added_to_site, creator_id, api_version):
        self.id = id
        self.tender_id_long = tender_id_long
        self.tender_id_short = tender_id_short
        self.tender_token = tender_token
        self.procurementMethodType = procurementMethodType
        self.related_tender_id = related_tender_id
        self.tender_status = tender_status
        self.n_lots = n_lots
        self.tender_platform_id = tender_platform_id
        self.company_uid = company_uid
        self.added_to_site = added_to_site
        self.creator_id = creator_id
        self.api_version = api_version


class BidsTender(db.Model):
    __tablename__ = 'bids'
    id = db.Column(db.Integer, primary_key=True)
    bid_id = db.Column(db.String(255))
    bid_token = db.Column(db.String(255))
    tender_id = db.Column(db.String(255))
    bid_status = db.Column(db.String(255))
    bid_platform = db.Column(db.String(255))
    company_id = db.Column(db.Integer)
    added_to_site = db.Column(db.Integer)
    user_identifier = db.Column(db.String(255))

    def __init__(self, id, bid_id, bid_token, tender_id, bid_status, bid_platform,
                 company_id, added_to_site, user_identifier):
        self.id = id
        self.bid_id = bid_id
        self.bid_token = bid_token
        self.tender_id = tender_id
        self.bid_status = bid_status
        self.bid_platform_id = bid_platform
        self.company_uid = company_id
        self.added_to_site = added_to_site
        self.user_identifier = user_identifier


class Auctions(db.Model):
    __tablename__ = 'auctions'
    id = db.Column(db.Integer, primary_key=True)
    auction_id_long = db.Column(db.String(255))
    auction_id_short = db.Column(db.String(255))
    auction_token = db.Column(db.String(255))
    procurementMethodType = db.Column(db.String(255))
    related_auction_id = db.Column(db.String(255))
    auction_status = db.Column(db.String(255))
    n_lots = db.Column(db.Integer)
    auction_platform_id = db.Column(db.Integer)
    company_uid = db.Column(db.Integer)
    added_to_site = db.Column(db.Integer)
    creator_id = db.Column(db.Integer)
    cdb_version = db.Column(db.String(255))

    def __init__(self, id, auction_id_long, auction_id_short, auction_token, procurementMethodType, related_auction_id,
                 auction_status, n_lots, auction_platform_id, company_uid, added_to_site, creator_id, cdb_version):
        self.id = id
        self.auction_id_long = auction_id_long
        self.auction_id_short = auction_id_short
        self.auction_token = auction_token
        self.procurementMethodType = procurementMethodType
        self.related_auction_id = related_auction_id
        self.auction_status = auction_status
        self.n_lots = n_lots
        self.auction_platform_id = auction_platform_id
        self.company_uid = company_uid
        self.added_to_site = added_to_site
        self.creator_id = creator_id
        self.cdb_version = cdb_version


class BidsAuction(db.Model):
    __tablename__ = 'bids_auction'
    id = db.Column(db.Integer, primary_key=True)
    bid_id = db.Column(db.String(255))
    bid_token = db.Column(db.String(255))
    auction_id = db.Column(db.String(255))
    bid_status = db.Column(db.String(255))
    bid_platform = db.Column(db.String(255))
    company_id = db.Column(db.Integer)
    added_to_site = db.Column(db.Integer)
    user_identifier = db.Column(db.String(255))

    def __init__(self, id, bid_id, bid_token, auction_id, bid_status, bid_platform,
                 company_id, added_to_site, user_identifier):
        self.id = id
        self.bid_id = bid_id
        self.bid_token = bid_token
        self.auction_id = auction_id
        self.bid_status = bid_status
        self.bid_platform_id = bid_platform
        self.company_uid = company_id
        self.added_to_site = added_to_site
        self.user_identifier = user_identifier


class Platforms(db.Model):
    __tablename__ = 'platforms'
    id = db.Column(db.Integer, primary_key=True)
    platform_name = db.Column(db.String(255))
    platform_url = db.Column(db.String(255))
    platform_role = db.Column(db.Integer)

    def __init__(self, id, platform_name, platform_url, platform_role):
        self.id = id
        self.platform_name = platform_name
        self.platform_url = platform_url
        self.platform_role = platform_role


class PlatformRoles(db.Model):
    __tablename__ = 'platform_roles'
    id = db.Column(db.Integer, primary_key=True)
    platform_role_name = db.Column(db.String(255))

    def __init__(self, id, platform_role_name):
        self.id = id
        self.platform_role_name = platform_role_name


class Roles(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(255))

    def __init__(self, id, role_name):
        self.id = id
        self.role_name = role_name


class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    user_login = db.Column(db.String(255))
    user_password = db.Column(db.String(255))
    user_role_id = db.Column(db.Integer)
    active = db.Column(db.Integer)
    super_user = db.Column(db.Integer)
    user_lang_id = db.Column(db.Integer)

    def __init__(self, id, user_login, user_password, user_role_id, active, super_user, user_lang_id):
        self.id = id
        self.user_login = user_login
        self.user_password = user_password
        self.user_role_id = user_role_id
        self.active = active
        self.super_user = super_user
        self.user_lang_id = user_lang_id


class Languages(db.Model):
    __tablename__ = 'languages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    system_name = db.Column(db.String(255))
