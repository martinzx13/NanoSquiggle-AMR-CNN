import pandas as pd
import os

# Define o caminho absoluto para evitar o erro FileNotFoundError
# Substitui 'fc66170' pelo teu utilizador se for diferente
base_path = "/home/fc66170/Klebsiella_POD5/pod5_data/KP1779/"
input_file = os.path.join(base_path, "KP1779_resultado_final.csv")
output_file = os.path.join(base_path, "KP1779_resultado_RELEVANTE.csv")

try:
    # 1. Carregar o ficheiro usando o caminho completo
    print(f"📖 A ler: {input_file}")
    df = pd.read_csv(input_file)

    # 2. Aplicar o filtro de rigor (95% identidade e 500bp de comprimento)
    df_filtered = df[(df['pident'] >= 95) & (df['length'] >= 500)]

    # 3. Guardar com as legendas (index=False mantém as colunas mas remove a numeração das linhas)
    df_filtered.to_csv(output_file, index=False)

    print(f"✅ Sucesso! Gerado: {output_file}")
    print(f"📊 Matches de alta confiança: {len(df_filtered)}")

except FileNotFoundError:
    print(f"❌ ERRO: O ficheiro não foi encontrado em: {input_file}")
    print("Verifica se o script 03 correu bem e gerou o ficheiro nesse local.")
