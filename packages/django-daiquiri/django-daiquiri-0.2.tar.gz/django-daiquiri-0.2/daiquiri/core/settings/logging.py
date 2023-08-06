import os

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        }
    },
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s: %(message)s'
        },
        'name': {
            'format': '[%(asctime)s] %(levelname)s %(name)s %(funcName)s: %(message)s'
        },
        'console': {
            'format': '[%(asctime)s] %(message)s'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'error_log': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': 'error.log',
            'formatter': 'default'
        },
        'daiquiri_log': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'daiquiri.log',
            'formatter': 'name'
        },
        'sql_log': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.FileHandler',
            'filename': 'sql.log',
            'formatter': 'default'
        },
        'rules_log': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.FileHandler',
            'filename': 'rules.log',
            'formatter': 'default'
        },
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'console'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False
        },
        'django.request': {
            'handlers': ['mail_admins', 'error_log'],
            'level': 'ERROR',
            'propagate': True
        },
        'django.db.backends': {
            'handlers': ['sql_log'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False
        },
        'daiquiri': {
            'handlers': ['daiquiri_log'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False
        },
        'rules': {
            'handlers': ['rules_log'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False
        }
    }
}
