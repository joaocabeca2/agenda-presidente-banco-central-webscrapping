from selenium import webdriver
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import google.generativeai as genai
import re
import json
import csv
from time import sleep


url_agenda_autoridades = 'https://www.bcb.gov.br/acessoinformacao/agendaautoridades'
api_key = 'AIzaSyCl17ZZs8Q1Iznjb3ufUyyGCVPcnd9yEsA'
genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_name="gemini-1.0-pro")

prompt = """
Você é uma assistente que trabalha para o presidente do banco do brasil e precisa
Apresentar as informações de um texto em um json, seguindo o seguinte formato: 
{horario_inicio: '',horario_termino: '', assunto_reuniao: '', local_reuniao: '',orgao: '',entidade: ''}
Observação: retorne apenas o json.

texto:
"""


# Configura o WebDriver do Edge
driver = webdriver.Edge(EdgeChromiumDriverManager().install())
wait = WebDriverWait(driver,5)

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

def is_reuniao(texto,palavra):
    return re.search(r'\b'+re.escape(palavra)+r'\b',texto)

def escrever_csv(dados):
    with open('dados_agenda_reunioes.csv','a',newline='',encoding='utf8') as csvfile:
        escritor_csv = csv.writer(csvfile)
        escritor_csv.writerow(dados)

def limpar_json_response(json_response):
    return json_response.replace('```','').replace('json','').replace('```','')
def pegar_dados_agenda(day,month,year):
    index_start_day = 27
    index_start_month = 1
    start_year = 2023
    index_end_day = 27
    index_end_month = 5
    end_year = 2024
    
    with open('dados_agenda_reunioes.csv','w',newline='',encoding='utf8') as csvfile:
        escritor_csv = csv.writer(csvfile)
        escritor_csv.writerow(['horario_inicio','horario_termino','data','cargo','assunto','local','orgao','entidade'])

    for y in range(start_year,end_year):
        year.select_by_value(str(y))
        for m in range(index_start_month,len(select_month.find_elements(By.TAG_NAME,'option'))):
            month.select_by_index(m)
            for d in range(index_start_day,len(select_day.find_elements(By.TAG_NAME,'option'))):
                day.select_by_index(d) 
                try:
                    nome = wait.until(EC.presence_of_element_located((By.CLASS_NAME,'nome.mb-0'))).text
                except Exception as e:
                    pass
                else:
                        try:
                            if nome.lower() == 'roberto campos neto':
                                data = str(d+1)+'_'+str(m+1)+'_'+str(y)
                                cargo = driver.execute_script("""return document.querySelector('div.cargo').textContent""")
                                presid = driver.find_element(By.CLASS_NAME,'col-md-8')
                                elementos = driver.execute_script("""var presid = arguments[0];
                                                          return presid.querySelectorAll('div.col-md-8 div div div')""",presid)
                            for elemento in elementos:
                                texto = elemento.text.lower()
                                if is_reuniao(texto,'reunião'):
                                    response = model.generate_content(prompt+texto)
                                    resposta_limpa = limpar_json_response(response.text)
                                    dados_reuniao = json.loads(resposta_limpa)
                                    print(resposta_limpa)
                                    sleep(2)
                                    dados = [dados_reuniao['horario_inicio'],
                                            dados_reuniao['horario_termino'],
                                            data,cargo,dados_reuniao['assunto_reuniao'],
                                            dados_reuniao['local_reuniao'],
                                            dados_reuniao['orgao'],
                                            dados_reuniao['entidade']]
                                    escrever_csv(dados)
                        except Exception:
                            pass
                finally:
                    if y == end_year and m == index_end_month and d == index_end_day:
                        return 
            index_start_day = 0
        index_start_month = 0

pegar_dados_agenda(day_to_be_selected,month_to_be_selected,year_to_be_selected)

#2 - Apresentar as informações em uma tabela com as colunas: 
#assunto da reunião, local da reunião, cargo, orgão e entidade
