import requests
import pprint
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import ast


def retrieve_old_data(url, country):
    URL = f'https://www.worldometers.info/coronavirus/{url}'
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, 'html.parser')
    graph = soup.find(id='graph-cases-daily').next_element.next_element
    jsonData = graph.text.strip()
    start_date = jsonData.find('[')
    end_date = jsonData.find(']') + 1
    date_list = ast.literal_eval(jsonData[start_date:end_date])
    date_list = [datetime.strptime(f'{date} 20', '%b %d %y').strftime('%d-%m-%Y') for date in date_list]
    start_val = jsonData.find('[', jsonData.find('data')) + 1
    end_val = jsonData.find(']', jsonData.find('data'))
    val_list = jsonData[start_val:end_val].split(',')
    val_list = [int(cases) if cases != 'null' else 0 for cases in val_list]
    record = []
    for i, date in enumerate(date_list):
        record.append({'country': country, 'date': date, 'new_cases': val_list[i]})

    return record

def retrieve_daily_data(output):
    """
    Web scrap the chemical book website
    :param casno: paramater of the search
    :return:
    """
    yesterday = datetime.today() - timedelta(days=1)
    date_y = yesterday.strftime('%Y-%m-%d')
    URL = f'https://www.worldometers.info/coronavirus/#countries'
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    table = soup.find_all('tbody')
    table = table[3]
    items = table.find_all('tr', {'style': ""})
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
        output.write(f'{country},{date_y},{total_cases},{new_cases},{total_deaths},{new_deaths},{act_cases}\n')

if __name__ == '__main__':
    output = open('test.csv', 'w')
    output.write('country,date,total_cases,new_cases,total_deaths,new_deaths,active_cases\n')
    retrieve_daily_data(output)