from jinja2 import Environment, FileSystemLoader, select_autoescape


def rebuild(result_collect_parametres):
    banks_price = None
    for value in result_collect_parametres.values():
        term_bg = value[0]['term_contract']
        summ_bg = value[0]['summ_bg']
        tender_number = value[0]['tender_number']

        for prices in value:
            banks_price = prices['banks_prices']

        env = Environment(
            loader=FileSystemLoader('.'),
            autoescape=select_autoescape(['html'])
        )
        best_price = banks_price[0]['price_bg']
        bank_name = banks_price[0]['name']

        template = env.get_template('e_mail.html')
        # with open('filejson.json') as json_file:
        #     book_collection = json.load(json_file)
        # os.makedirs('pages', exist_ok=True)
        # for page in pages:

        rendered_page = template.render(
            banks=banks_price[1:],
            best_price=best_price,
            term_bg=term_bg,
            summ_bg=summ_bg,
            bank=bank_name,
            tender_number=tender_number)
        # print(rendered_page)

        with open(f'index.html', 'w', encoding="utf8") as file:
            file.write(rendered_page)

        return rendered_page

# rebuild()
