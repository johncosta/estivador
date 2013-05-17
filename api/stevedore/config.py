DEFAULT = {
    'host': '127.0.0.1',
    'port': 6379,
    'db': 0
}


DEFAULT_DATABASE = 'sqlite:///stevedore.db'
DEFAULT_DATABASE_OPTIONS = {
    'echo': False,
    'pool_recycle': 3600,
    'echo_pool': True
}

TEST_DATABASE = 'sqlite:///stevedore_test.db'
TEST_DATABASE_OPTIONS = {
    'echo': False,
    'pool_recycle': 3600,
    'echo_pool': True
}
