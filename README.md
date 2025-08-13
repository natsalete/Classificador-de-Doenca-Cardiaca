# 🫀 Classificador de Doença Cardíaca
 
Este projeto consiste em uma **análise de dados** e **classificação de risco de doenças cardíacas** utilizando a plataforma **KNIME** e posteriormente um **sistema em Python** para prever a probabilidade de um paciente apresentar problemas cardíacos.

<p align="center">
  <img src="https://github.com/user-attachments/assets/df9c7016-90d9-45d6-887a-adacfae9a8da" 
       alt="Fluxo de trabalho no KNIME" 
       width="80%" 
       style="border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);" />
</p>


## 📊 Base de Dados
A base utilizada foi o dataset ["Heart Disease Dataset"](https://www.kaggle.com/datasets/johnsmith88/heart-disease-dataset) disponível no Kaggle.  
O conjunto de dados contém informações clínicas e exames laboratoriais de pacientes, como idade, pressão arterial, colesterol, frequência cardíaca máxima, entre outros.

## ⚙️ Fluxo no KNIME
No KNIME, o fluxo de trabalho envolveu:
- **Pré-processamento dos dados**: limpeza, normalização e filtragem de colunas.
- **Correlação Linear** para análise inicial das variáveis.
- **Treinamento e teste** de múltiplos algoritmos de machine learning:
  - `RProp MLP Learner`
  - `PNN Learner (DDA)`
  - `Decision Tree Learner`
  - `k-Nearest Neighbor`
  - `Random Forest Learner`
  - `SVM Learner`
- **Avaliação de desempenho** dos modelos com métricas e visualizações (PCA, Scatter Plot).
- Escolha do **melhor modelo** com base na performance: **Decision Tree Learner**.

## 🏆 Modelo Final
O modelo de **Árvore de Decisão** apresentou o melhor desempenho e foi exportado no formato **PMML**.

## 💻 Sistema em Python
Foi desenvolvido um sistema em Python que utiliza o modelo PMML treinado para prever se um paciente tem risco de desenvolver problemas cardíacos.

🔗 **Acesse o sistema online:** [Classificador de Doença Cardíaca](https://classificador-de-doenca-cardiaca.onrender.com/)

### Tecnologias utilizadas:
- **KNIME Analytics Platform** (para análise e modelagem)
- **Python** (para integração e sistema web)
- **Flask** (backend web)
- **sklearn2pmml / JPMML** (para exportação e uso do modelo)
- **HTML + CSS** (interface web)


## 🚀 Como executar localmente
1. Clone este repositório:
```bash
   git clone https://github.com/natsalete/Classificador-de-Doenca-Cardiaca.git
```
2. Acesse a pasta do projeto:
```bash
   cd Classificador-de-Doenca-Cardiaca
```
3. Instale as dependências:
```bash
   pip install -r requirements.txt
```
4. Execute o sistema:
```bash
   python app.py
```
5. Acesse no navegador:
```bash
   http://127.0.0.1:5000
```
---

## 📝 Licença
Este projeto está licenciado sob a **MIT License** – veja o arquivo [LICENSE](LICENSE) para mais detalhes.

