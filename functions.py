import ast
import pandas as pd
import psycopg2
from pandas.conftest import index
import hypothesis
import pytest
from sqlalchemy import create_engine
from kaggle.api.kaggle_api_extended import KaggleApi
import kaggle

def download_and_save_csv(dataset_name, download_path='./'):

    kaggle.api.dataset_download_files(dataset_name, path=download_path, unzip=True)
    #download_and_save_csv("edoardoscarpaci/italian-food-recipes", "./")

# Funzione per inserire gli ingredienti nella tabella 'ingredients'
def insert_ingredients(connection, cursor):
    list01 = take_recipe_ingredients(connection, cursor)
    ingredients = list01  # Ad esempio [['Biscotti Digestive', '240g'], ...]
    print(ingredients)
    # Ciclo per ogni ingrediente
    for ingredient in ingredients:
        if not ingredient:
            break

        ingredient_name = ingredient[0]  # Estrae il nome dell'ingrediente

        # Verifica se l'ingrediente esiste già nella tabella
        cursor.execute(f"SELECT ing_id_ingredient FROM ingredients WHERE ing_name ILIKE %s", (ingredient_name,))
        existing_ingredient = cursor.fetchall()

        if not existing_ingredient:  # Se non esiste, lo inseriamo
            cursor.execute(f"INSERT INTO ingredients (ing_name) VALUES (%s)", (ingredient_name,))
            cursor.connection.commit()
            print(f"Ingrediente {ingredient_name} inserito")
        else:
            print(f"L'ingrediente {ingredient_name} esiste già.")

    print("inserimento ingredienti finito")


# Funzione per ottenere gli ingredienti da una ricetta e inserirli nella tabella
def take_recipe_ingredients(connection, cursor):
    # Ottieni la lista degli ingredienti per la ricetta con id `recipe_id`
    cursor.execute("SELECT rec_ingredients FROM recipe")
    result = cursor.fetchall()
    result_clean = [ingredient for sublist in result for ingredient in ast.literal_eval(sublist[0])]
    return result_clean


def search_recipe(list, cursor):
    cursor.execute(f"""
        create temporary table tmp1(
            ing varchar(50)
        );""")
    cursor.connection.commit()

    for item in list:
        cursor.execute("INSERT INTO tmp1 (ing) VALUES (%s)", (item,))
    cursor.connection.commit()
    cursor.execute(F"""   
        create temporary table tmp2(
            nome varchar(50)
        );
        
        insert into tmp2(nome)
        select ing_name
                from ingredients,tmp1
                where ing_name ilike ing;
        
        insert into search_log (ing_log)
        select * from tmp2;
        
        
        create temporary table tmp3(
            id3 integer,
            name3 varchar(225),
            ing3 text
        );
        --tutte le ricette che hanno gli ingredienti
        insert into tmp3
        select rec_id, rec_name,rec_ingredients 
        when from recipe,tmp2
        where rec_ingredients ilike '%'||nome||'\\''%'  ;
        
        --contiene il numero di ingredienti inseriti dall'utente
        create temporary table tmp4(
            conteggio integer
        );
        
        insert into tmp4
        select count(*) from tmp2;
        
        --inserisco l'id della reicetta e le volte che compare nella ricerca precedente, quella in cui cerco le ricette che hanno gli ingredienti
        create temporary table tmp5(
            id5 integer,
            cont5 integer
        );
        
        
        insert into tmp5(id5,cont5)
        select id3,count(*) 
        from tmp3
        group by 1;
        
        create temporary table tmp6(
            id6 integer
        );
        --seleziono solamente quelle che hanno lo stesso numero di ingredienti alle volte che compaiono nelle selezione delle ricette per ingredienti
        insert into tmp6 (id6)
        select id5 from 
        tmp5,tmp4 where conteggio = cont5;
        
        select rec_id,rec_name,rec_category,rec_link,rec_number,rec_ingredients,rec_steps from recipe
        join tmp6 on rec_id = id6""")
    data = cursor.fetchall()

    pd_find_prod = pd.DataFrame(data,columns=('rec_id','rec_name','rec_category','rec_link','rec_number','rec_ingredients','rec_steps'))

    cursor.execute("""              
                drop table tmp1;
                drop table tmp2;
                drop table tmp3;
                drop table tmp4;
                drop table tmp5;
                drop table tmp6""")
    cursor.connection.commit()
    return pd_find_prod



def open_connection_DB():
    connection = psycopg2.connect(host="database-2.cze6c0csmaso.us-east-2.rds.amazonaws.com",
                                    port="5432",
                                    database="DB_1",
                                    user="alberto",
                                    password="Review2108?"
                                    )

    cursor = connection.cursor()
    return connection,cursor

def close_connection_DB(connection,cursor):

    if cursor:
        cursor.close()
        connection.close()



def load_gz_recipe_to_table(connection,cursor):

    engine = create_engine('postgresql+psycopg2://alberto:Review2108?@database-2.cze6c0csmaso.us-east-2.rds.amazonaws.com:5432/DB_1')
    df = pd.read_csv("gz_recipe.csv", sep=",",low_memory=False)
    df = df.drop(df.columns[0], axis=1)
    df.rename(columns={
        'Nome': 'rec_name',  # Adatta questi nomi a quelli del tuo database
        'Categoria': 'rec_category',
        'Link': 'rec_link',
        'Persone/Pezzi': 'rec_number',
        'Ingredienti': 'rec_ingredients',
        'Steps': 'rec_steps'

        }, inplace=True)
    chunk_size = 500
    for start in range(0, len(df), chunk_size):
        chunk = df.iloc[start:start + chunk_size]
        chunk.to_sql('recipe', engine,if_exists='append', index=False)
