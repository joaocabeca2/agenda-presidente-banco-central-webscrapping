from selenium import webdriver
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import csv

url_agenda_autoridades = 'https://www.bcb.gov.br/acessoinformacao/agendaautoridades'

# Configura o WebDriver do Edge
driver = webdriver.Edge(EdgeChromiumDriverManager().install())
wait = WebDriverWait(driver,10)

driver.get('https://www.bcb.gov.br/acessoinformacao/agendaautoridades')

#1 - Extrair dados da agenda do presidente do banco central, roberto campos neto, 
#desde 28 de fevereiro de 2023 até 28 de junho de 2024

select_day = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/app-root/app-root/div/div/main/dynamic-comp/'
                        'div/div/bcb-agenda-autoridades/div/div[1]/div[1]/bcb-seletor-datas/div/div/select[1]')))

select_month = driver.find_element(By.XPATH,'/html/body/app-root/app-root/div/div/main/dynamic-comp/div/div/'
                                   'bcb-agenda-autoridades/div/div[1]/div[1]/bcb-seletor-datas/div/div/select[2]')

select_year = driver.find_element(By.XPATH,'/html/body/app-root/app-root/div/div/main/dynamic-comp/div/'
                                  'div/bcb-agenda-autoridades/div/div[1]/div[1]/bcb-seletor-datas/div/div/select[3]')

year_to_be_selected= Select(select_year)
month_to_be_selected = Select(select_month)
day_to_be_selected = Select(select_day)

def pegar_dados_agenda(day,month,year):
    index_start_day = 27
    index_start_month = 1
    start_year = 2023
    index_end_day = 27
    index_end_month = 5
    end_year = 2024
    
    for y in range(start_year,end_year):
        year.select_by_value(str(y))
        for m in range(index_start_month,len(select_month.find_elements(By.TAG_NAME,'option'))):
            month.select_by_index(m)
            for d in range(index_start_day,len(select_day.find_elements(By.TAG_NAME,'option'))):
                day.select_by_index(d) 
                try:
                    nome = wait.until(EC.visibility_of_element_located((By.CLASS_NAME,'nome.mb-0'))).text
                except Exception as e:
                    pass
                else:
                    if nome.lower() == 'roberto campos neto':
                        print(f'Data: {d+1}_{m+1}_{y}')
                        cargo = driver.find_element(By.CLASS_NAME,'div.ExternalClass72AE2185EE52408AA8716DBA809F343C').text
                finally:
                    if y == end_year and m == index_end_month and d == index_end_day:
                        return 
            index_start_day = 0
        index_start_month = 0

pegar_dados_agenda(day_to_be_selected,month_to_be_selected,year_to_be_selected)

#2 - Apresentar as informações em uma tabela com as colunas: 
#assunto da reunião, local da reunião, cargo, orgão e entidade