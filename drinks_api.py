from flask import Flask, render_template, request, redirect, jsonify
import requests
from deep_translator import GoogleTranslator
import oracledb

connection = oracledb.connect(user="rm550489", password="140704", dsn="oracle.fiap.com.br/orcl")

app = Flask(__name__)
tasks = []

def translate_text(text):
    try:
        translated_text = GoogleTranslator(source='auto', target='pt').translate(text)
        return translated_text
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def pegar_info(bebida):
    url = f'https://www.thecocktaildb.com/api/json/v1/1/search.php?s={bebida}'
    response = requests.get(url)
    data = response.json()
    
    if 'drinks' in data:
        for drink in data['drinks']:
            drink['strInstructions'] = translate_text(drink['strInstructions'])
            drink['strCategory'] = translate_text(drink['strCategory'])
            drink['strGlass'] = translate_text(drink['strGlass'])
            tasks.append(drink)

    return redirect('/')

@app.route('/')
def index():
    return render_template('index.html', tasks=tasks)

@app.route('/pegar_bebida', methods=['POST'])
def pegar_bebida():
    nova_bebida = request.form.get('bebida')
    
    if nova_bebida:
        return pegar_info(nova_bebida)

    return redirect('/')

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
        INSERT INTO t_drinks(id_drink, nm_nome, ds_categoria, nm_copo)
        VALUES('{drink['idDrink']}', '{drink['strDrink']}', '{drink['strCategory']}', '{drink['strGlass']}')
    """

    cursor.execute(sql_insert)
    connection.commit()
    cursor.close()

    print(f'Bebida Curtida - ID: {idDrink}, Info: {info}')
    return jsonify({'message': 'Curtida com sucesso'})

if __name__ == '__main__':
    app.run(debug=True)
