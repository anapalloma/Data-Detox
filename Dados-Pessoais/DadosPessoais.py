#Python3
__author__ = 'Ana Palloma'

import pandas as pd 
from pathlib import Path
from fuzzywuzzy import fuzz, process

# Lê os dados
with pd.ExcelFile(file) as file:
    df = pd.read_excel(file)

class DadosPessoais:
    def __init__(self, df):
        self.df = df
        
    def converter_idade(self):
        #Calcula a idade em anos do usuário, na data da notificação.
        idades = []
        for idx, row in self.df.iterrows():
            dt_notificacao = row['DT_NOTIFIC']
            dt_nascimento = row['DT_NASC']
            if isinstance(dt_notificacao, str) or isinstance(dt_nascimento, str):
                idades.append(None)
            else:
                idade = pd.Timestamp(dt_notificacao).year - pd.Timestamp(dt_nascimento).year
                idades.append(idade)
        self.df['IDADE'] = idades
        
    def converter_sexo(self):
        self.df['CS_SEXO'].replace({'F': 'Feminino', 'M': 'Masculino', 'I': 'Ignorado'}, inplace=True)
        
    def converter_gestantes(self):
        self.df['CS_GESTANT'].replace({
            1: '1º Trimestre', 
            2: '2º Trimestre', 
            3: '3º Trimestre', 
            4: 'Idade gestacional ignorada', 
            5: 'Não', 
            6: 'Não se aplica', 
            9: 'Ignorado'
        }, inplace=True)
        
    def converter_raca(self):
        self.df['CS_RACA'].replace({
            1: 'Branca', 
            2: 'Preta', 
            3: 'Amarela', 
            4: 'Parda', 
            5: 'Indígena', 
            9: 'Ignorado'
        }, inplace=True)
        
    def converter_escolaridade(self):
        self.df['CS_ESCOL_N'] = self.df['CS_ESCOL_N'].fillna(9)
        self.df['CS_ESCOL_N'] = self.df['CS_ESCOL_N'].astype('int')

        self.df['CS_ESCOL_N'].replace({
            0: 'Analfabeto',
            1: '1ª a 4ª série incompleta do EF',
            2: '4ª série completa do EF',
            3: '5ª à 8ª série incompleta do EF',
            4: 'Ensino fundamental completo',
            5: 'Ensino médio incompleto',
            6: 'Ensino médio completo',
            7: 'Educação superior incompleta',
            8: 'Educação superior completa',
            9: 'Ignorado',
            10: 'Não se aplica'
        }, inplace=True)
    
    def converter_bairro(self):
        # Carrega a lista de bairros corretos de um arquivo separado
        bairros_path = Path('bairros_corretos.txt')
        with open(bairros_path) as f:
            bairros_corretos = f.read().splitlines()
        
        # Preenche valores ausentes
        self.df['NM_BAIRRO'] = self.df['NM_BAIRRO'].fillna('NAO INFORMADO')    

        # Corrige os nomes dos bairros usando fuzzy matching 
        def extrair_bairro(nome_bairro, bairros_corretos):
            opcao = process.extractOne(nome_bairro, bairros_corretos, score_cutoff=75)
            if opcao is None:
                return 'Nenhuma opção encontrada'
            return opcao[0]

        self.df['NM_BAIRRO_CORRIGIDO'], self.df['MENSAGEM'] = zip(*self.df['NM_BAIRRO'].apply(lambda nome_bairro: (
            extrair_bairro(nome_bairro, bairros_corretos),
            f"O nome '{nome_bairro}' foi corrigido para '{bairro_corrigido}'." if (bairro_corrigido := extrair_bairro(nome_bairro, bairros_corretos)) != nome_bairro else f"O bairro '{nome_bairro}' foi digitado corretamente."
        ))) 

    
    def converter_zona(self):
        self.df['CS_ZONA'].replace({1: 'Urbana', 2: 'Rural', 3: 'Periurbana', 9: 'Ignorado'}, inplace=True)

    def converter_ocupacao(self):
        # Cria um dicionário para armazenar as ocupações.
        ocupacoes = {}
        
        # Carrega a lista com o código e descrição das ocupações de um arquivo separado
        with open('ocupacoes.txt', 'r', encoding='ISO-8859-1') as f:
            for line in f:
                codigo, nome = line.strip().split(';')
                ocupacoes[int(codigo)] = nome
        self.df['ID_OCUPA_N'] = self.df['ID_OCUPA_N'].replace(ocupacoes)
    
    def converter_nulos(self):
        self.df = self.df.fillna('NAO INFORMADO')
        
    def salvar_como_excel(self, nome_arquivo):
        self.df.to_excel(nome_arquivo, index=False)

# Instancia a classe
dados_pessoais = DadosPessoais(df)

# Chama todos os métodos da classe DadosPessoais
dados_pessoais.converter_idade()
dados_pessoais.converter_sexo()
dados_pessoais.converter_raca()
dados_pessoais.converter_escolaridade()
dados_pessoais.converter_bairro()
dados_pessoais.converter_zona()
dados_pessoais.converter_gestantes()
dados_pessoais.converter_ocupacao()
dados_pessoais.converter_nulos()

dados_pessoais.salvar_como_excel(file)
    
    