from flask import Flask, request, jsonify, render_template_string
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

# Template HTML
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Classificador de Doença Cardíaca</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 600px; margin: 0 auto; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, select { width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; }
        button { background-color: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background-color: #0056b3; }
        .result { margin-top: 20px; padding: 15px; border-radius: 4px; }
        .success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .warning { background-color: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }
        .error { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🫀 Classificador de Doença Cardíaca</h1>
        <p>Preencha os dados abaixo para avaliar o risco de doença cardíaca:</p>
        
        <form id="heartForm">
            <div class="form-group">
                <label for="age">Idade (29-77 anos):</label>
                <input type="number" id="age" name="age" min="29" max="77" required>
            </div>
            
            <div class="form-group">
                <label for="sex">Sexo:</label>
                <select id="sex" name="sex" required>
                    <option value="">Selecione...</option>
                    <option value="0">Feminino</option>
                    <option value="1">Masculino</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="cp">Tipo de dor no peito:</label>
                <select id="cp" name="cp" required>
                    <option value="">Selecione...</option>
                    <option value="0">Angina típica</option>
                    <option value="1">Angina atípica</option>
                    <option value="2">Dor não-anginosa</option>
                    <option value="3">Assintomático</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="trestbps">Pressão arterial em repouso (94-200 mmHg):</label>
                <input type="number" id="trestbps" name="trestbps" min="94" max="200" required>
            </div>
            
            <div class="form-group">
                <label for="thalach">Frequência cardíaca máxima (71-202 bpm):</label>
                <input type="number" id="thalach" name="thalach" min="71" max="202" required>
            </div>
            
            <div class="form-group">
                <label for="exang">Angina induzida por exercício:</label>
                <select id="exang" name="exang" required>
                    <option value="">Selecione...</option>
                    <option value="0">Não</option>
                    <option value="1">Sim</option>
                </select>
            </div>
            
            <button type="submit">Classificar</button>
        </form>
        
        <div id="result"></div>
    </div>
    
    <script>
        document.getElementById('heartForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const data = Object.fromEntries(formData);
            
            // Converter para números
            for (let key in data) {
                if (key !== 'target') {
                    data[key] = parseFloat(data[key]);
                }
            }
            
            fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('result').innerHTML = data.html;
            })
            .catch(error => {
                document.getElementById('result').innerHTML = 
                    '<div class="result error">Erro ao processar a solicitação: ' + error + '</div>';
            });
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

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

if __name__ == '__main__':
    app.run(debug=True)