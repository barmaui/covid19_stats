import requests
import pprint
from bs4 import BeautifulSoup
from datetime import datetime
import ast

def extract_val_list(json_data):
    """ """
    start_val = json_data.find('[', json_data.find('data')) + 1
    end_val= json_data.find(']', json_data.find('data'))
    val_list = json_data[start_val:end_val].split(',')
    val_list = [int(cases) if cases != 'null' else 0 for cases in val_list]
    return val_list


def retrieve_old_data(url, country):
    URL = f'https://www.worldometers.info/coronavirus/{url}'
    page = requests.get(URL)
    record = []
    soup = BeautifulSoup(page.content, 'html.parser')
    print(country)
    # New cases
    graph_cases = soup.find(id='graph-cases-daily').next_element.next_element
    json_data_cases = graph_cases.text.strip()
    start_date = json_data_cases.find('[')
    end_date = json_data_cases.find(']') + 1
    date_list = ast.literal_eval(json_data_cases[start_date:end_date])
    date_list = [datetime.strptime(f'{date} 20', '%b %d %y').strftime('%Y-%m-%d') for date in date_list]
    val_list = extract_val_list(json_data_cases)
    # Total cases
    graph_tot_cases = soup.find(id='coronavirus-cases-log').next_element.next_element.next_element.next_element.next_element.next_element
    tot_cases_val_list = extract_val_list(graph_tot_cases.text.strip())
    # Active cases
    graph_tot_act_cases = soup.find(id='graph-active-cases-total').next_element.next_element
    act_cases_val_list = extract_val_list(graph_tot_act_cases.text.strip())
    # New Deaths
    if soup.find(id='graph-deaths-daily'):
        graph_deaths = soup.find(id='graph-deaths-daily').next_element.next_element
        death_val_list = extract_val_list(graph_deaths.text.strip())
        # Total Deaths
        graph_tot_deaths = soup.find(id='coronavirus-deaths-log').next_element.next_element.next_element.next_element.next_element.next_element
        tot_death_val_list = extract_val_list(graph_tot_deaths.text.strip())
        for i, date in enumerate(date_list):
            record.append(f'{country},{date},{tot_cases_val_list[i]},{val_list[i]},{tot_death_val_list[i]},{death_val_list[i]},{act_cases_val_list[i]}\n')
    else:
        for i, date in enumerate(date_list):
            record.append(f'{country},{date},{tot_cases_val_list[i]},{val_list[i]},0,0,{act_cases_val_list[i]}\n')

    return record


def retrieve_data(output):
    """
    Web scrap the chemical book website
    :param casno: paramater of the search
    :return:
    """
    URL = f'https://www.worldometers.info/coronavirus/#countries'
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    table = soup.find('tbody')
    if table is None:
        return 'Not Found\n'
    new_cases_dic = {}
    for row in table.find_all('tr'):
        cells = row.find_all('td')
        country = cells[0].text.strip()
        if cells[0].find('a'):
            record = retrieve_old_data(cells[0].find('a')['href'], country)
        else:
            continue
        for row in record:
            output.write(row)

if __name__ == '__main__':
    output = open('test.csv', 'w')
    output.write('country,date,total_cases,new_cases,total_deaths,new_deaths,active_cases\n')
    retrieve_data(output)
    output.close()