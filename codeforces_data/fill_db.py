from typing import List, Dict, Any

from codeforces_data.models import Category, Task


def fill_db(data: List[Dict[str, Any]]) -> None:

    for _dict in data:
        categories: list = _dict.pop('category')
        categories_item = []
        for cat in categories:
            try:
                cat_item = Category.objects.get(name=cat)
            except Category.DoesNotExist:
                cat_item = Category(name=cat)
                cat_item.save()

            categories_item.append(cat_item)

        try:
            task = Task.objects.get(number=_dict['number'])
        except Task.DoesNotExist:
            task = Task(**_dict)
            task.save()
            for category in categories_item:
                task.categories.add(category)

        else:
            task.name = _dict['name']
            task.difficutly = _dict['difficulty']
            task.solution = _dict['solution']
            task.categories.clear()
            for category in categories_item:
                task.categories.add(category)

        finally:
            task.save()
