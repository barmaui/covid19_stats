""""""

def retrieve_daily_data(request):
    """
    Web scrap the chemical book website
    :param casno: paramater of the search
    :return:
    """
    import requests
    from bs4 import BeautifulSoup
    from datetime import datetime, timedelta
    from google.cloud import storage

    yesterday = datetime.today() - timedelta(days=1)
    date_y = yesterday.strftime('%Y-%m-%d')
    client = storage.Client()
    bucket = client.get_bucket('covid19stats')
    blob = bucket.blob(f'daily_stats.csv')
    URL = f'https://www.worldometers.info/coronavirus/#countries'
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    table = soup.find_all('tbody')
    table = table[3]
    items = table.find_all('tr', {'style': ""})
    temp = ''
    if table is None:
        return 'Not Found\n'
    for row in items[1:]:
        cells = row.find_all('td')
        country = cells[0].text.strip()
        total_cases = int(cells[1].text.strip().replace(',', ''))
        if cells[2].text.strip():
            new_cases = int(cells[2].text.strip()[1:].replace(',', ''))
        else:
            new_cases = 0
        if cells[3].text.strip():
            total_deaths = int(cells[3].text.strip().replace(',', ''))
        else:
            total_deaths = 0
        if cells[4].text.strip():
            new_deaths = int(cells[4].text.strip()[1:].replace(',', ''))
        else:
            new_deaths = 0
        if cells[6].text.strip():
            act_cases = int(cells[6].text.strip().replace(',', ''))
        else:
            act_cases = 0
        temp += f'{country},{date_y},{total_cases},{new_cases},{total_deaths},{new_deaths},{act_cases}\n'
    blob.upload_from_string(temp)

    return 'Data published'
