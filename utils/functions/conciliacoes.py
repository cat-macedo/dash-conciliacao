# Função auxiliar para somar valores agrupados por data
def somar_por_data(df, col_data, col_valor, datas):
  s = df.groupby(col_data)[col_valor].sum()
  # s.index = pd.to_datetime(s.index).date  # garante que o índice é só data
  return s.reindex(datas, fill_value=0).reset_index(drop=True).astype(float)


# Função auxiliar para calcular diferenças de contas a pagar e receber
def calcula_diferencas(df, coluna_principal, colunas_valores):
  soma = 0
  diferenca = 0
  soma = sum(df[col] for col in colunas_valores)
  diferenca = df[coluna_principal] - soma
  return diferenca
