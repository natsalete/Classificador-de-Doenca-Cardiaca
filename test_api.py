import requests
import json

# URL da API local
API_URL = "http://localhost:5000/predict"

def test_prediction(data, description):
    """Testa uma predição com os dados fornecidos"""
    print(f"\n🔍 Testando: {description}")
    print(f"Dados: {data}")
    
    try:
        response = requests.post(
            API_URL,
            headers={'Content-Type': 'application/json'},
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Predição: {result['prediction']}")
            print(f"📊 Probabilidades: {result['probabilities']}")
            print("=" * 50)
        else:
            print(f"❌ Erro: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao servidor. Certifique-se de que o Flask está rodando.")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    print("🫀 Testando Sistema de Classificação de Doença Cardíaca")
    print("=" * 60)
    
    # Teste 1: Paciente com baixo risco
    test_prediction({
        'age': 35,
        'sex': 0,     # feminino
        'cp': 3,      # assintomático
        'trestbps': 110,
        'thalach': 180,
        'exang': 0    # sem angina por exercício
    }, "Paciente jovem, feminino, assintomático")
    
    # Teste 2: Paciente com risco moderado
    test_prediction({
        'age': 55,
        'sex': 1,     # masculino
        'cp': 1,      # angina atípica
        'trestbps': 140,
        'thalach': 130,
        'exang': 0
    }, "Paciente de meia-idade, masculino, com angina atípica")
    
    # Teste 3: Paciente com alto risco
    test_prediction({
        'age': 65,
        'sex': 1,     # masculino
        'cp': 0,      # angina típica
        'trestbps': 160,
        'thalach': 100,
        'exang': 1    # com angina por exercício
    }, "Paciente idoso, masculino, com angina típica e exercício")
    
    # Teste 4: Paciente feminino mais velha
    test_prediction({
        'age': 60,
        'sex': 0,     # feminino
        'cp': 2,      # dor não-anginosa
        'trestbps': 150,
        'thalach': 120,
        'exang': 1
    }, "Paciente feminino, 60 anos, com dor não-anginosa")
    
    # Teste 5: Paciente jovem masculino
    test_prediction({
        'age': 40,
        'sex': 1,     # masculino
        'cp': 3,      # assintomático
        'trestbps': 120,
        'thalach': 170,
        'exang': 0
    }, "Paciente jovem masculino, assintomático")

    print("\n📋 Para testar interativamente, acesse: http://localhost:5000")
    print("💡 Dica: Execute 'python app.py' em outro terminal para iniciar o servidor")