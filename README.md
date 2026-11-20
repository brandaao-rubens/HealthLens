# HealthLens

Sistema web em Python que estima o risco de quatro condições de saúde a partir de dados de exames: **doença cardiovascular, diabetes, doença renal crônica e doença hepática**. O usuário envia um exame em PDF ou preenche os valores, recebe o risco calculado por modelos de machine learning com recomendações, e pode conversar com um assistente de IA (Gemini) que explica os resultados e o histórico.

> Projeto de estudo. Não substitui avaliação médica.

## Funcionalidades

- **Central de diagnóstico:** upload de exame (PDF), extração dos valores e cálculo de risco para as quatro condições.
- **Páginas por condição:** formulário, nível de risco e recomendações para cada uma.
- **Assistente IA:** agente com Gemini que explica exames e riscos em linguagem simples, sem dar diagnóstico.
- **Histórico:** login de usuário e registro das avaliações em SQLite.
- **Explicabilidade:** valores SHAP para entender o que pesou em cada previsão.

## Tecnologias

Python · Streamlit · scikit-learn · XGBoost · Optuna · SHAP · pandas · Plotly · SQLite · Google Gemini API

## Estrutura

```
src/
├── preprocessing/        # limpeza dos dados brutos de cada doença
├── feature_engineering/  # criação das variáveis usadas nos modelos
├── model_training/       # treino, calibração e escolha do melhor modelo
├── explainability.py     # gráficos SHAP
└── app/
    ├── dashboard.py      # ponto de entrada do Streamlit
    ├── pages/            # telas (upload, condições, agente, histórico, login)
    ├── modules/          # motores de risco, recomendações, leitura de PDF, banco
    └── ui/               # estilos e componentes visuais
```

## Como rodar

```bash
git clone https://github.com/brandaao-rubens/HealthLens.git
cd HealthLens
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # coloque sua GOOGLE_API_KEY
```

### 1. Dados

Os datasets são públicos e não ficam no repositório. Baixe-os e salve em `data/raw/` com estes nomes:

| Arquivo | Dataset |
| --- | --- |
| `cardiovascular_raw.csv` | Cardiovascular Disease Dataset (Kaggle) |
| `diabetes_prediction_dataset.csv` | Diabetes Prediction Dataset (Kaggle) |
| `kidney_disease.csv` | Chronic Kidney Disease (UCI) |
| `indian_liver_patient.csv` | Indian Liver Patient Dataset (UCI) |

### 2. Treinar os modelos

Rode a partir da raiz do projeto, para cada doença (`cardio`, `diabetes`, `kidney`, `liver`):

```bash
python src/preprocessing/preprocessing_cardio.py
python src/feature_engineering/feature_engineering_cardio.py
python src/model_training/model_training_cardio.py
```

Os modelos são salvos em `models/classifiers/`.

### 3. Abrir o app

```bash
streamlit run src/app/dashboard.py
```

## Autor

Rubens Rocha Brandão · Engenharia da Computação, UFG
