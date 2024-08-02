import os
import pandas as pd

EXCEL_PATH = r"C:\Users\luzo.neto\OneDrive - Sicoob\Meus Arquivos\historico_perguntas_respostas.xlsx"

def save_to_excel(question, answer):
    if os.path.exists(EXCEL_PATH):
        df = pd.read_excel(EXCEL_PATH)
    else:
        df = pd.DataFrame(columns=["Pergunta", "Resposta"])

    new_entry = pd.DataFrame({"Pergunta": [question], "Resposta": [answer]})
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_excel(EXCEL_PATH, index=False)
