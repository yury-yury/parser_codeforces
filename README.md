## Условия проекта
### Описание

На сайте codeforces есть большая подборка задач (ссылка в формате отсортированности - это маленькая помощь в парсинге данных). На каждую тему есть десятки задач, но часто у одной задачи не одна, а сразу несколько тематик.
Задача

Написать парсер задач и их свойств

    Темы ("математика", "перебор", "графы" …)
    Количество решений задач
    Название + номер
    Сложность задачи (800 / 900 …. и тд)

Затем сохранить их в БД и дополнять, в случае если этой задачи нет - то добавлять.

Настроить парсинг страниц codeforces периодичностью 1 час.

Подключить Telegram-бота с возможностью выбрать сложность + тему (на нее отобразятся подборка задач) и поиском по задачам (выводится вся информация о конкретной задачке по запросу).
Теперь главный алгоритм

    Требуется для определенной сложности + тематики уметь получать подборку из 10 задач, которые преимущественно мы заранее распределим по контестам (набор задач)
    Цель – распределить задачи так, чтобы не было пересечений, то есть выбрали мы тему сортировки - на нее выдается нам 10 задач, при этом они принадлежат только этому контесту (никакому более)

Требуемый стэк

    python 3.10
    postgresql