from flask import Flask, render_template, request, url_for, redirect
import requests
from googletrans import Translator
app = Flask(__name__)
tras= Translator()
tasks = []

def pegar_info(bebida):
    url = f'https://www.thecocktaildb.com/api/json/v1/1/search.php?s={bebida}'
    response = requests.get(url)
    data = response.json()
    
    # Verifique se a chave 'drinks' existe nos dados da API
    if 'drinks' in data:
        # Adicione todas as bebidas à lista 'tasks'
        for drink in data['drinks']:
            drink['strInstructions'] = tras.translate(drink['strInstructions'], dest='pt').text
            drink['strCategory'] = tras.translate(drink['strCategory'], dest='pt').text
            drink['strGlass'] = tras.translate(drink['strGlass'], dest='pt').text
            tasks.append(drink)

    
    return redirect(url_for('index'))


@app.route('/')
def index():
    return render_template('index.html', tasks = tasks)

@app.route('/pegar_bebida', methods=['POST'])
def pegar_bebida():
    nova_bebida = request.form.get('bebida')
    return pegar_info(nova_bebida)
    

if __name__ == '__main__':
    app.run(debug=True)