import autogen

config_list = [
    {
        'model': '',
        'api_type': 'open_ai',
        'base_url': 'http://localhost:1234/v1',
        'api_key': 'NULL'
    }
]

llm_config = {
    'timeout': 600,
    'seed': 42,
    'config_list': config_list,
    'temperature': 0
}

