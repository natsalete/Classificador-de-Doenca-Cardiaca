from flask import Flask, request, jsonify, render_template
import xml.etree.ElementTree as ET
import os

app = Flask(__name__)

class PMMLTreeClassifier:
    def __init__(self, pmml_file):
        self.tree = ET.parse(pmml_file)
        self.root = self.tree.getroot()
        self.namespace = {'pmml': 'http://www.dmg.org/PMML-4_2'}
        
        # Extrair informações do modelo
        self.data_fields = self._extract_data_fields()
        self.tree_model = self._extract_tree_model()
        
    def _extract_data_fields(self):
        """Extrai informações dos campos de dados do PMML"""
        data_fields = {}
        data_dict = self.root.find('.//pmml:DataDictionary', self.namespace)
        
        for field in data_dict.findall('.//pmml:DataField', self.namespace):
            field_name = field.get('name')
            data_type = field.get('dataType')
            op_type = field.get('optype')
            
            # Extrair intervalos para normalização
            interval = field.find('.//pmml:Interval', self.namespace)
            if interval is not None:
                left_margin = float(interval.get('leftMargin'))
                right_margin = float(interval.get('rightMargin'))
                data_fields[field_name] = {
                    'type': data_type,
                    'optype': op_type,
                    'min': left_margin,
                    'max': right_margin
                }
            else:
                data_fields[field_name] = {
                    'type': data_type,
                    'optype': op_type
                }
                
        return data_fields
    
    def _extract_tree_model(self):
        """Extrai o modelo de árvore do PMML"""
        tree_model = self.root.find('.//pmml:TreeModel', self.namespace)
        return tree_model
    
    def normalize_data(self, data):
        """Normaliza os dados de entrada baseado nos ranges originais"""
        # Ranges originais estimados baseados em dados típicos de doenças cardíacas
        ranges = {
            'age': {'min': 29, 'max': 77},
            'sex': {'min': 0, 'max': 1},
            'cp': {'min': 0, 'max': 3},
            'trestbps': {'min': 94, 'max': 200},
            'thalach': {'min': 71, 'max': 202},
            'exang': {'min': 0, 'max': 1}
        }
        
        normalized_data = {}
        for field, value in data.items():
            if field in ranges:
                min_val = ranges[field]['min']
                max_val = ranges[field]['max']
                # Normalização min-max para [0,1]
                normalized_data[field] = (value - min_val) / (max_val - min_val)
            else:
                normalized_data[field] = value
                
        return normalized_data
    
    def traverse_tree(self, node, data):
        """Percorre a árvore de decisão para fazer a predição"""
        # Verificar se é um nó folha
        score = node.get('score')
        
        # Encontrar predicados
        predicates = node.findall('.//pmml:SimplePredicate', self.namespace)
        
        if not predicates:
            # Nó folha - retornar apenas o score
            return score
        
        # Avaliar predicados
        for child in node.findall('.//pmml:Node', self.namespace):
            predicate = child.find('.//pmml:SimplePredicate', self.namespace)
            if predicate is not None:
                field = predicate.get('field')
                operator = predicate.get('operator')
                value = float(predicate.get('value'))
                
                if field in data:
                    data_value = data[field]
                    
                    if operator == 'lessOrEqual' and data_value <= value:
                        return self.traverse_tree(child, data)
                    elif operator == 'greaterThan' and data_value > value:
                        return self.traverse_tree(child, data)
        
        # Se nenhum predicado foi satisfeito, retornar score atual
        return score
    
    def predict(self, data):
        """Faz a predição usando o modelo PMML"""
        # Normalizar dados
        normalized_data = self.normalize_data(data)
        
        # Encontrar o nó raiz da árvore
        root_node = self.tree_model.find('.//pmml:Node', self.namespace)
        
        # Percorrer a árvore
        prediction = self.traverse_tree(root_node, normalized_data)
        
        return {
            'prediction': prediction
        }

# Carregar o modelo PMML
model = PMMLTreeClassifier('paste.txt')  # Assumindo que o arquivo PMML está salvo como paste.txt

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Receber dados do formulário
        data = request.json
        
        # Fazer a predição
        result = model.predict(data)
        
        # Interpretar resultado
        prediction = result['prediction']
        
        # Gerar resposta personalizada sem probabilidades
        if prediction == 'No':
            html_response = f"""
            <div class="result success">
                <h3>✅ Resultado: Baixo risco de doença cardíaca</h3>
                <p><strong>Classificação:</strong> Sem indicação de doença cardíaca</p>
                <p><em>Resultado positivo! Continue mantendo hábitos saudáveis.</em></p>
            </div>
            """
        else:
            html_response = f"""
            <div class="result warning">
                <h3>🚨 Resultado: Risco de doença cardíaca</h3>
                <p><strong>Classificação:</strong> Indicação de possível doença cardíaca</p>
                <p><strong>⚠️ Recomendação:</strong> Procure um cardiologista para avaliação detalhada e exames complementares.</p>
                <p><em>Este resultado é apenas uma indicação baseada em dados estatísticos e não substitui a avaliação médica profissional.</em></p>
            </div>
            """
        
        return jsonify({
            'prediction': prediction,
            'html': html_response
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'html': f'<div class="result error">Erro ao processar dados: {str(e)}</div>'
        }), 500

import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # usa a porta definida pela Render ou 5000
    app.run(host='0.0.0.0', port=port, debug=True)
