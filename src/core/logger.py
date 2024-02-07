LOG_HANDLER = ['console',]
LOG_FORMAT_VERBOSE = (
    '%(asctime)s - %(name)s - %(levelname)s: '
    '%(funcName)s - %(lineno)d - %(message)s'
)

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': LOG_FORMAT_VERBOSE,
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'filehandler': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'filename': 'logs/storage_log.log',
            'mode': 'a',
            'backupCount': 3,
            'maxBytes': 10000,
            'encoding': 'utf-8',
        },
    },
    'root': {
        'level': 'DEBUG',
        'formatter': LOG_FORMAT_VERBOSE,
        'handlers': LOG_HANDLER,
    },
}
