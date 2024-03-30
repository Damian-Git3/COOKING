class CommonConfig:
    SECRET_KEY = "MySecretKey"

class DevelopmentConfig(CommonConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:root@localhost/don_galleto_bd'
    
config = {
    'development': DevelopmentConfig
}