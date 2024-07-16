from airflow import DAG
from airflow.operators.python import PythonOperator
import requests
from sqlalchemy import create_engine, text 
import json
from datetime import timedelta
import smtplib
import pandas as pd 
from datetime import datetime 

def formatDate(date):
    formated_date = pd.to_datetime(date).dt.tz_localize(None)
    formated_date = formated_date.astype(str).replace('NaT','') 
    return formated_date

def execQry(engine, qry):
    try:
        with engine.begin() as conn:
            conn.execute(text(qry))
        conn.close()
    except KeyError as err:
        raise err
def get_last_id():
    db_pg = create_engine("postgresql+psycopg2://{usuario}:{senha}@{servidor}:5432/{bd}"
                        .format(usuario='root', senha='root',
                                servidor='postgres_api', bd='teste'))

    qry = 'select max(api_code) last_id from api_content '
    df_last_id = pd.read_sql(con=db_pg.raw_connection(), sql=qry)
    last_id = int(1811657 if df_last_id['last_id'][0] == None else df_last_id['last_id'][0])

    return last_id 

def fetch_data():
    token = "G5n2w1lm*eJF$UukF5c^bN5Re#"
    last_id = get_last_id()
    try:
        response = requests.post(
            'https://app.alunos.me/api/ahoy_viewer_ti',
            headers={'Content-Type': 'application/json'},
            data=json.dumps({"token": token, "idahoy": last_id})
        )
        status = response.raise_for_status()
        print(status)
        data = response.json()
        return data
    except Exception as err:
        if "Unauthorized" in str(err):
            data = {}
            return data
        else:
            response = requests.post(
                'https://app.alunos.me/api/ahoy_viewer_ti',
                headers={'Content-Type': 'application/json'},
                data=json.dumps({"token": token, "idahoy": 1972657})
            )


def process_data(ti):
    data = ti.xcom_pull(task_ids='fetch_data')
    if len(data) > 0:
        df = pd.DataFrame(data)
        
        df['opened_at'] = formatDate(df['opened_at'])
        df['clicked_at'] = formatDate(df['clicked_at'])
        df['sent_at'] = formatDate(df['sent_at'])


        return df
    else:
        print('SEM DADOS PARA COLETAR')
        return pd.DataFrame()

def store_data(ti):
    data = ti.xcom_pull(task_ids='process_data')
    if len(data) > 0:
        db_pg = create_engine("postgresql+psycopg2://{usuario}:{senha}@{servidor}:5432/{bd}"
                            .format(usuario='root', senha='root',
                                    servidor='postgres_api', bd='teste'))

        companies = data['company'].unique()
        campaigns = data.groupby(['campaign', 'id_campaign']).size().reset_index().iloc[:, :2]

        for company in companies:
            qry = f'''
            INSERT INTO api_company (company_name,inserted) VALUES ('{company}', NOW())
            ON CONFLICT (company_name) DO NOTHING;
            '''
            try:
                execQry(db_pg,qry)
            except ValueError as err:
                print(f'ERRO > {err}\nQuery > {qry}')
            
        for i in range(len(campaigns)):
            qry = f'''
            INSERT INTO api_campaign (campaign_name,campaign_code,inserted) VALUES ('{campaigns['campaign'][i]}', '{campaigns['id_campaign'][i]}',NOW())
            ON CONFLICT (campaign_name) DO NOTHING;
            '''
            try:
                execQry(db_pg,qry)
            except ValueError as err:
                print(f'ERRO > {err}\nQuery > {qry}')
        
        qry_search_cpny = f'''SELECT distinct id as company_fk, company_name as company from api_company '''
        qry_search_cmpgn = f'''SELECT distinct id as campaign_fk, campaign_code as id_campaign from api_campaign'''

        df_campaigns = pd.read_sql(con=db_pg.raw_connection(), sql=qry_search_cmpgn)
        df_companies = pd.read_sql(con=db_pg.raw_connection(), sql=qry_search_cpny)

        data = pd.merge(data, df_campaigns[['id_campaign', 'campaign_fk']], on='id_campaign', how='left')
        data = pd.merge(data, df_companies[['company', 'company_fk']], on='company', how='left')

        for i in range(len(data)):
            qry = f'''
            INSERT INTO api_content (api_code,id_campaign,id_company,user_type,"to",mailer,subject,sent_at,"token",opened_at,clicked_at,inserted) 
            VALUES ({data['id'][i]},'{data['campaign_fk'][i]}','{data['company_fk'][i]}','{data['user_type'][i]}','{data['to'][i]}','{data['mailer'][i]}','{data['subject'][i]}','{data['sent_at'][i]}','{data['token'][i]}','{data['opened_at'][i]}','{data['clicked_at'][i]}',NOW())
            '''.replace("''",'NULL')
            try:
                execQry(db_pg, qry)
            except ValueError as err:
                print(f'ERRO > {err}\nQuery > {qry}')
    else:
        print('SEM DADOS PARA INSERIR')





def send_email(context):
    msg = f"Task failed: {context['task_instance_key_str']}\n\nError: {context['exception']}"
    server = smtplib.SMTP('smtp.mailersend.net', 587)
    server.starttls()
    server.login("MS_sIX2Rm@somosyoung.com.br", "ty8IvsmHa3Sdbk01")
    server.sendmail("MS_sIX2Rm@somosyoung.com.br", "contatorodrigomatos1@gmail.com", msg)
    server.quit()

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 7, 15),
    'email_on_failure': True,
    'email_on_retry': False,
    'on_failure_callback': send_email,
    'retries': 10,
    'retry_delay': timedelta(minutes=1),
    'provide_context': True
}


dag = DAG(
    'teste_young',
    default_args=default_args,
    description='Coleta, tratamento e inserção',
    schedule_interval='10 * * * *',
    max_active_runs=1,
)



fetch_data = PythonOperator(
    task_id='fetch_data',
    python_callable=fetch_data,
    provide_context=True,
    dag=dag,
)

process_data = PythonOperator(
    task_id='process_data',
    python_callable=process_data,
    provide_context=True,
    dag=dag,
)

store_data = PythonOperator(
    task_id='store_data',
    python_callable=store_data,
    provide_context=True,
    dag=dag,
)

fetch_data >> process_data >> store_data