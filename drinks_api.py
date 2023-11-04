from flask import Flask, render_template, request, url_for, redirect, jsonify
import requests
from googletrans import Translator
import oracledb
connection = oracledb.connect(user="xxxxxxx", password="xxxxxx", dsn="oracle.fiap.com.br/orcl")

app = Flask(__name__)
tras = Translator()
tasks = []

def pegar_info(bebida):
    url = f'https://www.thecocktaildb.com/api/json/v1/1/search.php?s={bebida}'
    response = requests.get(url)
    data = response.json()
    
    if 'drinks' in data:
        for drink in data['drinks']:
            drink['strInstructions'] = tras.translate(drink['strInstructions'], dest='pt').text
            drink['strCategory'] = tras.translate(drink['strCategory'], dest='pt').text
            drink['strGlass'] = tras.translate(drink['strGlass'], dest='pt').text
            tasks.append(drink)

    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('index.html', tasks=tasks)

@app.route('/pegar_bebida', methods=['POST'])
def pegar_bebida():
    nova_bebida = request.form.get('bebida')
    return pegar_info(nova_bebida)

@app.route('/curtir/<idDrink>', methods=['POST'])
def curtir(idDrink):
    
    data = request.get_json()
    info = data['info']
    cursor = connection.cursor()
    
    url = f'https://www.thecocktaildb.com/api/json/v1/1/lookup.php?i={idDrink}'
    response = requests.get(url)
    data = response.json()
    drink = data['drinks'][0]
    
    sql_insert = f"""
    INSERT INTO t_drinks(nm_nome, ds_categoria, nm_copo)
    VALUES('{drink['strDrink']}', '{drink['strCategory']}', '{drink['strGlass']}')
    """
    cursor.execute(sql_insert)
    connection.commit()
    cursor.close()

    print(f'Bebida Curtida - ID: {idDrink}, Info: {info}')
    return jsonify({'message': 'Curtida com sucesso'})

if __name__ == '__main__':
    app.run(debug=True)
