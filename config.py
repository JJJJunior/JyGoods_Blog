#*-*coding: utf-8 *-*

import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = 'hard to guess xj_csu@qq.com'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    JYGOODS_ADMIN = 'xj_csu@qq.com'
    JYGOODS_MAIL_SUBJECT_PREFIX = '[JyGoods]'
    JYGOODS_MAIL_SENDER = 'JyGoods <xj_csu@qq.com>'
    JYGOODS_POSTS_PER_PAGE = 20
    JYGOODS_FOLLOWERS_PER_PAGE = 10
    JYGOODS_COMMENTS_PER_PAGE = 10
    UPLOAD_FOLDER = os.path.join(basedir + 'upload/')


    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'xj_csu'
    MAIL_PASSWORD = 'SD!((1308'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + \
                              os.path.join(basedir, 'data-dev.sqlite')




class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + \
                              os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + \
                              os.path.join(basedir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
