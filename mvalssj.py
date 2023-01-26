import mysql.connector
import datetime
import requests
import time
import json
import os

class TelegramBot:
    def __init__(self):
        token = '5875849109:AAFcq83RBJvMRg_taPpPsrqpUbRZGigr6zc'
        self.url_base = f'https://api.telegram.org/bot{token}/'

    def Iniciar(self):
        update_id = None
        print ("Bot acordado!\n")
        while True:
          try:
            atualizacao = self.obter_novas_mensagens(update_id)
            dados = atualizacao["result"]
            if dados:
                for dado in dados:
                    update_id = dado['update_id']
                    mensagem = str(dado["message"]["text"])
                    chat_id = dado["message"]["from"]["id"]
                    eh_primeira_mensagem = int(
                        dado["message"]["message_id"]) == 1
                    resposta = self.criar_resposta(
                        mensagem, eh_primeira_mensagem)
                    self.responder(resposta, chat_id)
                    print("Usuário: ", dado["message"]["text"])
                    print ("Bot: ",resposta,"\n")

                    mydb = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    passwd="",
                    database="mvalssjbot"
                    )

                    # Criando a tabela de pedidos
                    mycursor = mydb.cursor()
                    # mycursor.execute("CREATE TABLE pedidos (opcao VARCHAR(255), data_hora DATETIME)")

                    # Inserindo um pedido na tabela
                    sql = "INSERT INTO pedidos (opcao, data_hora) VALUES (%s, %s)"
                    val = (mensagem, datetime.datetime.now())
                    mycursor.execute(sql, val)

                    mydb.commit()

          except:
             print ("erro")


    # Obter mensagens
    def obter_novas_mensagens(self, update_id):
        link_requisicao = f'{self.url_base}getUpdates?timeout=100'
        if update_id:
            link_requisicao = f'{link_requisicao}&offset={update_id + 1}'
        resultado = requests.get(link_requisicao)
        return json.loads(resultado.content)

    # Criar uma resposta
    def criar_resposta(self, mensagem, eh_primeira_mensagem):
        # Connect to the database
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="",
            database="mvalssjbot"
        )

        # Create a cursor to execute the query
        mycursor = mydb.cursor()

        # Select the CTE from the table
        query = "SELECT id, cte FROM pedidos WHERE cte = %s"
        mycursor.execute(query, (mensagem,))

        # Fetch the result
        result = mycursor.fetchone()

        if eh_primeira_mensagem == True or result != None:                       
            return f'''Olá bem vindo ao seu CTE Digite o número do status da sua atividade:{os.linesep}1 - Cheguei no cliente{os.linesep}2 - Carga entregue{os.linesep}3 - Retornando para o armazem{os.linesep}4 - Trajeto finalizado'''
        elif result != None:
            # Exibir linha da tabela para o usuário validar se é a correta
            id, cte = result
            return f'''Linha encontrada: ID: {id}, CTE: {cte}. Confirmar status?(s/n)'''        
        elif mensagem == '1':
            return f'''Cheguei no cliente{os.linesep}Confirmar status?(s/n)
            '''
        elif mensagem == '2':
            return f'''Carga entregue{os.linesep}Confirmar status?(s/n)
            '''
        elif mensagem == '3':
            return f'''Retornando para o armazem{os.linesep}Confirmar status?(s/n)'''

        elif mensagem == '4':
            return f'''Trajeto finalizado{os.linesep}Confirmar status?(s/n)'''

        elif mensagem.lower() in ('s', 'sim'):

            # Atualizar status no banco de dados
            query = "UPDATE pedidos SET status = 1 WHERE id = 1"
            mycursor.execute(query)
            mydb.commit()
            return f'''Status atualizado com sucesso!'''

        elif mensagem.lower() in ('n', 'não'):
            return ''' Status não Confirmado! '''
        else:
            return 'Insira o numero do CTE com 5 digitos:'

    # Responder
    def responder(self, resposta, chat_id):
        link_requisicao = f'{self.url_base}sendMessage?chat_id={chat_id}&text={resposta}'
        
        requests.get(link_requisicao)


bot = TelegramBot()
bot.Iniciar()