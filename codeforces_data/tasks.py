from time import sleep
from typing import List, Dict, Any

from celery import shared_task

from codeforces_data.fill_db import fill_db
from codeforces_data.parsers import parser, parser_num_page


@shared_task
def periodic_task() -> None:
    num_page: int = parser_num_page()
    for page in range(1, num_page+1):
        data: List[Dict[str, Any]] = parser(page)
        fill_db(data=data)
        sleep(30)
