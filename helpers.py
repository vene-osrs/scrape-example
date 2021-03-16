from re import compile
from datetime import datetime


def format_log(message):
    current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    print(f"[{current_time}] {message}")


def remove_html_tags(data):
    p = compile(r'<.*?>')
    return p.sub('', data)
