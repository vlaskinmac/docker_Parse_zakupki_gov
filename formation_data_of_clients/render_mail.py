import datetime
import re

from jinja2 import Environment, FileSystemLoader, select_autoescape


def get_text_for_body(email_address):
    gmail_adress = re.search(r"@gmail", str(email_address))
    if gmail_adress:
        filename = 'gmail_documents_list.txt'
    else:
        filename = 'documents_list.txt'
    with open(filename) as file:
        documents = file.read()
    return documents


def rebuild(result_collect_parametres):

    banks_price = None
    current_date = datetime.datetime.now()

    for value in result_collect_parametres.values():
        term_bg = value[0]['term_contract']
        summ_bg = value[0]['summ_bg']
        tender_number = value[0]['tender_number']
        winner_inn = value[0]['winner_inn']
        full_name = value[0]['full_name']

        datetime_obj = datetime.datetime.strptime(term_bg, "%d.%m.%Y")
        term_days_obj = datetime_obj - current_date
        for prices in value:
            banks_price = prices['banks_prices']

        env = Environment(
            loader=FileSystemLoader('.'),
            autoescape=select_autoescape(['html'])
        )
        best_price = banks_price[0]['price_bg']
        bank_name = banks_price[0]['name']


        template = env.get_template('e_mail.html')

        # os.makedirs('pages', exist_ok=True)
        # for page in pages:

        rendered_page = template.render(
            banks=banks_price[1:],
            best_price=best_price,
            term_bg=term_bg,
            summ_bg=summ_bg,
            bank=bank_name,
            tender_number=tender_number,
            term_days=term_days_obj.days,
            winner_inn=winner_inn,
            full_name=full_name,
            document=get_text_for_body(value[0]["email_address"]))


        # print(rendered_page)
        with open(f'index.html', 'w', encoding="utf8") as file:
            file.write(rendered_page)
        return rendered_page, bank_name, best_price

# rebuild()






# def rebuild(result_collect_parametres):
#     banks_price = None
#     current_date = datetime.datetime.now()
#     with open('documents_list.txt') as file:
#         documents = file.read()
#
#     for value in result_collect_parametres.values():
#         term_bg = value[0]['term_contract']
#         summ_bg = value[0]['summ_bg']
#         tender_number = value[0]['tender_number']
#
#         datetime_obj = datetime.datetime.strptime(term_bg, "%d.%m.%Y")
#         term_days_obj = datetime_obj - current_date
#
#         for prices in value:
#             banks_price = prices['banks_prices']
#
#         env = Environment(
#             loader=FileSystemLoader('.'),
#             autoescape=select_autoescape(['html'])
#         )
#         best_price = banks_price[0]['price_bg']
#         bank_name = banks_price[0]['name']
#
#         template = env.get_template('e_mail.html')
#
#         # os.makedirs('pages', exist_ok=True)
#         # for page in pages:
#
#         rendered_page = template.render(
#             banks=banks_price[1:],
#             best_price=best_price,
#             term_bg=term_bg,
#             summ_bg=summ_bg,
#             bank=bank_name,
#             tender_number=tender_number,
#             term_days=term_days_obj.days,
#             document=documents,
#         )
#         # print(rendered_page)
#
#         with open(f'index.html', 'w', encoding="utf8") as file:
#             file.write(rendered_page)
#
#         return rendered_page

# rebuild()
