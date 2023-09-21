from time import sleep
from typing import List, Optional, Dict, Any

import requests
from bs4 import BeautifulSoup as bs


def parser(page: int) -> Optional[List[Dict[str, Any]]]:
    """
    The parser function does not take parameters, when called, it makes a request to the URL specified
    in the URL_TEMPLATE variable, receives a response and parses the data with the formation
    of a list of dictionaries with the received data. Returns the generated list.
    """
    res: List[Optional[Dict[str, Any]]] = []
    base_url: str = "https://codeforces.com/problemset/"

    # response = requests.get(base_url)
    # print(response.status_code)
    #
    # if response.status_code == 200:
    #     print(response.text)
    #     soup = bs(response.text, "html.parser")
    #     all_page = soup.find('div', class_="pagination")
    #     find_num = int((all_page.contents[1].contents[-4].contents[1].contents[0].string).strip())
    #     print(find_num, type(find_num))

        # for i in range(1, find_num+1):
        # for i in range(1, 2):

    url: str = f"{base_url}page/{str(page)}?order=BY_SOLVED_DESC"
    # print(url)
    response = requests.get(url)
    # print(response.status_code)
    # print(response.text)
    if response.status_code == 200:
        soup = bs(response.text, "html.parser")
        all_task = soup.find_all('tr')

        for i in range(1, len(all_task)-1):
            dict_: dict = {}

            dict_['number'] = str(all_task[i].contents[1].contents[1].string).strip()
            dict_['name'] = str(all_task[i].contents[3].contents[1].contents[1].string).strip()
            try:
                dict_['category'] = [str(cat.string).strip()
                                 for cat in all_task[i].contents[3].contents[3].contents[1::2]]
            except:
                dict_['category'] = []
            try:
                dict_['difficulty'] = int(str(all_task[i].contents[7].contents[1].string).strip())
            except IndexError:
                dict_['difficulty'] = 0
            # print(all_task[i])
            try:
                dict_['solution'] = int(str(all_task[i].contents[9].contents[1].contents[1]).strip()[1:])
            except:
                dict_['solutnon'] = 0

            res.append(dict_)
            # pprint(dict_)

            # sleep(15)

    return res


def parser_num_page() -> Optional[int]:

    response = requests.get("https://codeforces.com/problemset/page/1?order=BY_SOLVED_DESC")

    if response.status_code == 200:
        soup = bs(response.text, "html.parser")
        all_page = soup.find('div', class_="pagination")
        find_num = int((all_page.contents[1].contents[-4].contents[1].contents[0].string).strip())
        # print(find_num, type(find_num))

        return find_num


if __name__ == '__main__':
    from pprint import pprint

    pprint(parser(90))
    # print(parser_num_page())
