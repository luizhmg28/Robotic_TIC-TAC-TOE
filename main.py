# --Bibliotecas para identificação-- #
import cv2
import numpy as np 
from keras.models import load_model
import time
import paho.mqtt.client as mqtt
import math

# --Bibliotecas para comandar o robô-- #
from commands import robot
import os
from dotenv import load_dotenv
load_dotenv()


# --Conexão com o LED via mqtt-- #
def handler(client, userdata, flgs, rc:int ):
    if rc == 0:
        print("Conexão estabelecida com sucesso")
    else:
        print("Conexão malsucedida")
cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id = CLIENT_MQTT)
cliente.on_connect = handler
cliente.username_pw_set(USERNAME_BROKER, PASSWORD_BROKER) 
cliente.connect(IP_BROKER, PORT_BROKER)

# --Criação das funções de acender LED verde ou vermelho-- #
def permitir_jogada():
    cliente.publish(TOPIC_BROKER, "led_verde")
def proibir_jogada():
    cliente.publish(TOPIC_BROKER, "led_vermelho")
proibir_jogada()

#--------------------------------Mapa de posições-----------------------------------#

# --Posição inicial para visualização da malha--  #
p1 = "248.00, -13.75, 622.20, 180.00, 0.00, -178.50" 

#------------------------------------Linha 1----------------------------------------#
p2_aereo = "130.00, -120.00, 440.00, -180.00, 0.00, -180.00" 
p2       = "130.00, -120.00, 431.00, -180.00, 0.00, -180.00" 
p3 =       "305.00, -122.00, 429.00, -180.00, 0.00, -180.00" 
p3_aereo = "305.00, -122.00, 440.00, -180.00, 0.00, -180.00" 

#------------------------------------Linha 2----------------------------------------#
p4_aereo = "130.00, -50.00, 440.00, -180.00, 0.00, -180.00"
p4 =       "130.00, -50.00, 431.00, -180.00, 0.00, -180.00"
p5 =       "305.00, -52.00, 431.00, -180.00, 0.00, -180.00"
p5_aereo = "305.00, -52.00, 440.00, -180.00, 0.00, -180.00"

#------------------------------------Linha 3----------------------------------------#
p6_aereo = "180.00, -180.00, 440.00, -180.00, 0.00, -180.00"
p6 =       "180.00, -180.00, 431.00, -180.00, 0.00, -180.00"
p7 =       "183.30,    0.00, 431.00, -180.00, 0.00, -180.00"
p7_aereo = "183.30,    0.00, 440.00, -180.00, 0.00, -180.00"

#------------------------------------Linha 4----------------------------------------#
p8_aereo = "249.00, -180.00, 440.00, -180.00, 0.00, -180.00"
p8 =       "249.00, -180.00, 431.00, -180.00, 0.00, -180.00"
p9 =       "252.30,    0.00, 428.75, -180.00, 0.00, -180.00"
p9_aereo = "252.30,    0.00, 440.00, -180.00, 0.00, -180.00"

#-----------------------Posições centrais dos quadrantes-----------------------------#
a1 = "155.30,-146.50, 431.00,-180.00, 0.00, -180.00"
a2 = "155.30,-85.00, 431.00,-180.00, 0.00, -180.00"
a3 = "155.30,-22.00, 431.00,-180.00, 0.00, -180.00"
a4 = "217.30,-146.50, 431.00,-180.00, 0.00, -180.00"
a5 = "217.30,-85.00, 431.00,-180.00, 0.00, -180.00"
a6 = "217.30,-22.00, 431.00,-180.00, 0.00, -180.00"
a7 = "280.30,-146.50 ,431.00,-180.00, 0.00, -180.00"
a8 = "280.30,-85.00, 431.00,-180.00, 0.00, -180.00"
a9 = "280.30,-20.00, 431.00,-180.00, 0.00, -180.00"
 
#--------------------------------Parametrização-------------------------------------#
host = os.getenv("IP")
port = os.getenv("PORT")
robo = robot()
robo.connect_to_robot(host, int(port))
robo.start_control() #Inicia o controle
robo.servo_on() #Liga o servo
robo.set_speed(200)
time.sleep(3)

#-------------------------------Movimento do robô-----------------------------------#
#                     A PARTIR DAQUI O ROBO ENTRARÁ EM MOVIMENTO                    #
# Robô vai à posição inicial 
robo.initial_position(p1)
# Desenho da malha
robo.draw_mesh(p5_aereo, p5, p4, p4_aereo, p2_aereo, p2, 
               p3, p3_aereo, p9_aereo, p9, p8, p8_aereo, p7_aereo, p7, p6, p6_aereo)
robo.initial_position(p1) #Retorna o robo à posição de inicio


# --Inicializa a captura de vídeo da câmera-- #
camera = cv2.VideoCapture(0 , cv2.CAP_DSHOW)
if not camera.isOpened():
    print("Erro ao abrir a câmera.")

# Carrega o modelo pré-definido de rede neural treinado no site Teachable machine
model = load_model("keras_model.h5", compile = False)
data = np.ndarray(shape= (1, 224, 224, 3), dtype= np.float32)

# Classes de possíveis classificação de objetos
classes = ["X", "O", "Vazio"]

# VERIFICA é a variável boleana que diz se foi possível capturar a imagem
VERIFICA, imagem = camera.read()
if not VERIFICA:
    print("Erro ao capturar imagem inicialmente.")

#-----------------Função de detecção de elementos-------------------#
def Detectar_X_ou_O(imagem):
    imagem_X_ou_O = cv2.resize(imagem,(224, 224))#Formata a imagem para 224x224 pixels, pois é como a rede neural da TeachableMachine processa melhor
    imagem_X_ou_O = np.asarray(imagem_X_ou_O)# Converte a imagem para matriz
    imagem_X_ou_O_Normal = (imagem_X_ou_O.astype(np.float32)/127.0 ) - 1 #Parte dos cálculos presentes no teachable machine
    data[0] = imagem_X_ou_O_Normal# Primeiro elemento da matriz
    predicao = model.predict(data)
    index = np.argmax(predicao)
    confiabilidade = predicao[0][index]
    classe = classes[index]
    return classe, confiabilidade

# --Definição das coordenadas dos quadrantes que o programa verificará-- #
coordenadas_quadrantes = [
        [(380,  30), (490, 150)],  # Quadrante 1 (topo esquerdo) 
        [(380, 180), (490, 293)],  # Quadrante 2 (topo centro)
        [(380, 320), (490, 420)],  # Quadrante 3 (topo direito)

        [(220,  30), (345, 150)],  # Quadrante 4 (centro esquerdo)
        [(220, 180), (345, 293)],  # Quadrante 5 (centro)
        [(220, 320), (345, 420)],  # Quadrante 6 (centro direito)

        [(90,  30), ( 185, 150)],  # Quadrante 7 (baixo esquerdo)
        [(90, 180), ( 185, 293)],  # Quadrante 8 (baixo centro)
        [(90, 320), ( 185, 420)],  # Quadrante 9 (baixo direito)
    ]

# --Loop para ajustar a câmera de acordo com os quadrantes-- #
camera_pronta = False
while camera_pronta == False:

    VERIFICA, imagem = camera.read()
    if not VERIFICA:
        print("Erro ao capturar imagem no loop.")

    imagem = cv2.resize(imagem, (640, 480))    
    
    #--------Cria os retângulos que servem de gabarito--------#
    cv2.rectangle(imagem, (380, 30), (490, 150), (0, 0, 255), 2)
    cv2.rectangle(imagem, (380, 180), (490, 293), (0, 0, 255), 2)
    cv2.rectangle(imagem, (380, 320), (490, 420), (0, 0, 255), 2)
    cv2.rectangle(imagem, (220, 30), (345, 150), (0, 0, 255), 2)
    cv2.rectangle(imagem, (220, 180), (345, 293), (0, 0, 255), 2)
    cv2.rectangle(imagem, (220, 320), (345, 420), (0, 0, 255), 2)
    cv2.rectangle(imagem, (90, 30), (185, 150), (0, 0, 255), 2)
    cv2.rectangle(imagem, (90, 180), (185, 293), (0, 0, 255), 2)
    cv2.rectangle(imagem, (90, 320), (185, 420), (0, 0, 255), 2)

    #-------Rotaciona a imagem pois a câmera está de lado-------#
    imagem = cv2.rotate(imagem, cv2.ROTATE_90_COUNTERCLOCKWISE) 

    #------------------Escreve a frase de cima------------------#
    cv2.rectangle(imagem, (30, 60), (450, 120), (255, 255, 255), -1)
    cv2.putText(imagem, 'Verifique os quadrantes', (30, 100), cv2.FONT_HERSHEY_COMPLEX, 1,(0, 0, 0), 2)  

    #--------------Mostra a imagem com quadrantes--------------#
    cv2.imshow("Gabarito", imagem)

    #---------Espera que a tecla espaço seja apertada---------#
    if cv2.waitKey(5) == ord(' '):
        cv2.destroyAllWindows()
        camera_pronta = True

# --- Detecta X ou O em todos os quadrantes --- #
def visualizar_valores(imagem_a_visualizar):
    valores_vistos = []
    for coord in coordenadas_quadrantes:
        x1, y1 = coord[0]
        x2, y2 = coord[1]
        quadrante = imagem_a_visualizar[y1:y2, x1:x2]
        classe, confiaaa = Detectar_X_ou_O(quadrante)  
        if classe == "Vazio":
            classe = " "

        valores_vistos.append(classe)
    return valores_vistos

#--Função para analisar se há alguma posição vencedora no tabuleiro--#
def analisar_vitoria(board):
    # -----------------Analisa as linhas horizontais---------------- #
    if (board[0] == board[1] == board[2]) and (board[0] != " "):
        return board[0]
    elif (board[3] == board[4] == board[5]) and (board[3] != " "):
        return board[3]
    elif (board[6] == board[7] == board[8]) and (board[6] != " "):
        return board[6]

    # -----------------Analisa as linhas verticais---------------- #
    elif (board[0] == board[3] == board[6]) and (board[0] != " "):
        return board[0]
    elif (board[1] == board[4] == board[7]) and (board[1] != " "):
        return board[1]
    elif (board[2] == board[5] == board[8]) and (board[2] != " "):
        return board[2]
    
    # -----------------Analisa as linhas diagonais---------------- #
    elif (board[0] == board[4] == board[8]) and (board[0] != " "):
        return board[0]

    elif (board[2] == board[4] == board[6]) and (board[2] != " "):
        return board[2]
    
    # --Retorna o vencedor, caso não exista retorna um valor vazio-- #
    else:
        return None

# --Retorna verdadeiro ou falso para velha se o tabuleiro não tiver nenhum espaço vazio-- #
def velha(board):
    velha = None
    if not " " in board:
        velha = True
    return velha

'''
Para decisão das jogadas do jogo da velha está sendo usado o método minimax que funciona simulando 
as jogadas como se estivesse enfrentando o melhor jogador possíevl, dessa forma ele escolhe sempre
alguma ramificação que ganhe ou empate com o jogador, visto que ele visualizou todas as jogadas pos-
síveis a partir daquela situação.
'''

# --Heurística para lógica do jogo da velha-- #
def heuristica(board, Jogador):
    h = 0
    if Jogador == "X":
        Oponente = "O"

    elif Jogador == "O":
        Oponente = "X"

    '''
    A heurística é utilizada para poupar processamento e não ser necessário verificar todas as ramificações.

    Nessa primeira parte da heurística é verificado se não há jogadas do oponente nas linhas, caso não haja 
    ele adiciona o "valor" daquela jogada elevado ao quadrado somada com o próprio valor, que se inicia em 0.
    '''

    # --Verifica cada linha horizontal-- #
    if (board[0] != Oponente) and (board[1] != Oponente) and (board[2] != Oponente):
        h += pow(((board[0] == Jogador) + (board[1] == Jogador) + (board[2] == Jogador)) , 2)
    if (board[3] != Oponente) and (board[4] != Oponente) and (board[5] != Oponente):
        h += pow(((board[3] == Jogador) + (board[4] == Jogador) + (board[5] == Jogador)) , 2)
    if (board[6] != Oponente) and (board[7] != Oponente) and (board[8] != Oponente):
        h += pow(((board[6] == Jogador) + (board[7] == Jogador) + (board[8] == Jogador)) , 2)

    # --Verifica cada linha vertical-- #
    if (board[0] != Oponente) and (board[3] != Oponente) and (board[6] != Oponente):
        h += pow(((board[0] == Jogador) + (board[3] == Jogador) + (board[6] == Jogador)) , 2)
    if (board[1] != Oponente) and (board[4] != Oponente) and (board[7] != Oponente):
        h += pow(((board[1] == Jogador) + (board[4] == Jogador) + (board[7] == Jogador)) , 2)
    if (board[2] != Oponente) and (board[5] != Oponente) and (board[8] != Oponente):
        h += pow(((board[2] == Jogador) + (board[5] == Jogador) + (board[8] == Jogador)) , 2)

    # --Verifica cada linha diagonal-- #
    if (board[0] != Oponente) and (board[4] != Oponente) and (board[8] != Oponente):
        h += pow(((board[0] == Jogador) + (board[4] == Jogador) + (board[8] == Jogador)) , 2)
    if (board[2] != Oponente) and (board[4] != Oponente) and (board[6] != Oponente):
        h += pow(((board[2] == Jogador) + (board[4] == Jogador) + (board[6] == Jogador)) , 2)

    '''
    Faz o mesmo que na primeira parte, porém agora retira as posições próprias para dessa forma
    considerar apenas as jogadas possíveis, ou seja lugares vazios.
    '''

    # --Verifica cada linha horizontal-- #
    if (board[0] != Jogador) and (board[1] != Jogador) and (board[2] != Jogador):
        h -= pow(((board[0] == Oponente) + (board[1] == Oponente) + (board[2] == Oponente)) , 2)
    if (board[3] != Jogador) and (board[4] != Jogador) and (board[5] != Jogador):
        h -= pow(((board[3] == Oponente) + (board[4] == Oponente) + (board[5] == Oponente)) , 2)
    if (board[6] != Jogador) and (board[7] != Jogador) and (board[8] != Jogador):
        h -= pow(((board[6] == Oponente) + (board[7] == Oponente) + (board[8] == Oponente)) , 2)

    # --Verifica cada linha vertical-- #
    if (board[0] != Jogador) and (board[1] != Jogador) and (board[2] != Jogador):
        h -= pow(((board[0] == Oponente) + (board[3] == Oponente) + (board[6] == Oponente)) , 2)
    if (board[1] != Jogador) and (board[4] != Jogador) and (board[7] != Jogador):
        h -= pow(((board[1] == Oponente) + (board[4] == Oponente) + (board[7] == Oponente)) , 2)
    if (board[2] != Jogador) and (board[5] != Jogador) and (board[8] != Jogador):
        h -= pow(((board[2] == Oponente) + (board[5] == Oponente) + (board[8] == Oponente)) , 2)

    # --Verifica cada linha diagonal-- #
    if (board[0] != Jogador) and (board[4] != Jogador) and (board[8] != Jogador):
        h -= pow(((board[0] == Oponente) + (board[4] == Oponente) + (board[8] == Oponente)) , 2)
    if (board[2] != Jogador) and (board[4] != Jogador) and (board[6] != Jogador):
        h -= pow(((board[2] == Oponente) + (board[4] == Oponente) + (board[6] == Oponente)) , 2)

    return h

# --Função para retornar o tabuleiro novo após a simulação da jogada-- #
def jogada(board, pos, Jogador):
    novo_tabuleiro = board.copy()
    novo_tabuleiro[pos] = Jogador
    return novo_tabuleiro

# --Função para indicar quais as jogadas que podem ser executadas ainda-- #
def listar_jogadas_possiveis(board):
    jogadas_possiveis = []
    for indice in range(9):
        if board[indice] == " ":
            jogadas_possiveis.append(indice)
    return jogadas_possiveis

# --Função responsável pela recursão-- #

def minimax(board, Jogador, Eu, maxdepth = 9):
    vencedor = analisar_vitoria(board)

    # --Atribui um grande valor para as vitórias-- #
    if vencedor == Eu:
        return 300

    # --Atribui um péssimo valor para as derrotas-- #
    if (vencedor) and (vencedor != Eu):
        return -300
    
    # --Atribui valor 0 para empates-- #
    if (not vencedor) and (velha(board)):
        return 0

    # --Caso o número de ramificações analisadas passe do maxdepth ele segue a heurística,
    # dessa forma poupa processamento pois não precisa analisar o restante possível-- #
    if maxdepth == 0:
        return heuristica(board, Jogador)

    jogadas_possiveis = listar_jogadas_possiveis(board)

    # --Inicia a recursão atribuindo valores as possíveis jogadas de acordo com os processos anteriores-- #
    if Jogador == Eu:         #MAX
        best = -math.inf
        for cada in jogadas_possiveis:
            resultado = jogada(board, cada, Jogador)
            valor = minimax(resultado, "O" if Jogador == "X" else "X", Eu, maxdepth = maxdepth - 1)
            if valor > best:
                best = valor
        return best

    else:                     #MIN
        best = math.inf
        for cada in jogadas_possiveis:
            resultado = jogada(board, cada, Jogador)
            valor = minimax(resultado, "O" if Jogador == "X" else "X", Eu, maxdepth = maxdepth - 1)
            if valor < best:
                best = valor
        return best

# --Escolhe a melhor jogada a se fazer de acordo com os valores a elas atribuídos-- #
def bestaction(board, Eu):
    jogadas_possiveis = listar_jogadas_possiveis(board)
    best = -math.inf
    best_action = None
    for cada in jogadas_possiveis:
        resultado = jogada(board, cada, Eu)
        valor = minimax(resultado, "O" if Eu == "X" else "X", Eu, 9)
        if valor > best:
            best = valor
            best_action = cada
    return best_action

# --Função de finalização do loop-- #
def tchau(Ganhador):
    vezes = 0
    if Ganhador:
        print(f"O jogador {Ganhador} venceu")
        while vezes < 10:
            permitir_jogada()
            time.sleep(0.3)
            proibir_jogada()
            time.sleep(0.3)
            vezes = vezes + 1
    else:
        print("Empate")
        while vezes < 30:
            permitir_jogada()
            time.sleep(0.1)
            proibir_jogada()
            time.sleep(0.1)
            vezes = vezes + 1

    camera.release()
    cv2.destroyAllWindows()
    loop = False
    
# --Função para captura da imagem da câmera por determinadas vezes-- #
def delay(tempo):
    contagem = 0
    while contagem < tempo:
        VERIFICA, imagem = camera.read()
        if not VERIFICA:
            print("Erro ao capturar a imagem no loop.")
        if cv2.waitKey(5) == 27:
            camera.release()
            cv2.destroyAllWindows()
            loop = False
            break
        imagem_exibida = cv2.rotate(imagem, cv2.ROTATE_90_COUNTERCLOCKWISE)
        cv2.imshow("Imagem da camera:", imagem_exibida)
        contagem = contagem + 1
    valores_vistos = visualizar_valores(imagem)
    return valores_vistos

# --Declaração das variáveis a serem utilizadas no loop principal-- #
mao = False
loop = True
Eu = " "
Jogador = " "
X_ou_O_verificado = False
jogou = False

while loop:
    try:
        valores_quadrantes = valores_quadrantes
    except NameError:
        valores_quadrantes = []

    VERIFICA, imagem = camera.read()
    if not VERIFICA:
        print("Erro ao capturar imagem no loop.")

    # --Caso aperte esc o programa se encerra-- #
    if cv2.waitKey(5) == 27:
        camera.release()
        cv2.destroyAllWindows()
        loop = False
        break

    # --Gira a imagem pois ela está posicionada de lado-- #
    imagem_exibida = cv2.rotate(imagem, cv2.ROTATE_90_COUNTERCLOCKWISE)
    cv2.imshow("Imagem da camera:", imagem_exibida)

    # --Converte a imagem para preto e branco e identifica a quantidade de cada um a partir do limiar de luminosidade
    imagem_grayscale = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    limiar = 110
    _, imagem_binaria = cv2.threshold(imagem_grayscale , limiar, 255, cv2.THRESH_BINARY) #imagem_grayscale
    total_pixels = imagem_grayscale.shape[0] * imagem_grayscale.shape[1]
    total_pixels_brancos = cv2.countNonZero(imagem_binaria)
    total_pixels_pretos = total_pixels - total_pixels_brancos

    # --Verifica se alguém jogou de acordo com a diferença da quantidade de pixels brancos e pretos-- #
    if total_pixels_brancos <= 235000:
        print("Mão detectada")
        mao = True
        jogou = True
        time.sleep(0.25)
        continue
    else: 
        mao = False
        permitir_jogada()
    
    # --Identifica se deve jogar X ou O de acordo com a jogada realizada-- #
    if (X_ou_O_verificado == False) and jogou:
        proibir_jogada()
        valores_vistos = delay(10)
        print(valores_vistos)
        if "O" in valores_vistos:
            Jogador = "O"
            Eu = "X"
            board = valores_vistos
            jogou = True
            X_ou_O_verificado = True
        elif "X" in valores_vistos:
            Jogador = "X"
            Eu = "O" 
            board = valores_vistos
            jogou = True
            X_ou_O_verificado = True
        # --Ou não jogar se apenas foi identificado uma mão mas não houve jogada-- #
        else:
            jogou = False
            continue

    if jogou and X_ou_O_verificado:
        proibir_jogada() #Acende o led vermelho para não mexerem mais pois o robô se movimentará
        valores_vistos = delay(10) #Verifica a malha novamente
        #Verifica se houve alguma jogada de fato
        if valores_vistos != valores_quadrantes:
            Ganhador = analisar_vitoria(valores_vistos)
            if Ganhador or velha(valores_vistos):
                tchau(Ganhador)
                break
            
            board = valores_vistos.copy() #Define o tabuleiro para uso do minimax
            if loop == True:
                quadrante_escolhido = None
                print(valores_vistos)
                # Define a jogada que deverá ser executada
                best_action = bestaction(board, Eu)
            
                if best_action == 0:
                    quadrante_escolhido = a1
                if best_action == 1:
                    quadrante_escolhido = a2
                if best_action == 2:
                    quadrante_escolhido = a3
                if best_action == 3:
                    quadrante_escolhido = a4
                if best_action == 4:
                    quadrante_escolhido = a5
                if best_action == 5:
                    quadrante_escolhido = a6
                if best_action == 6:
                    quadrante_escolhido = a7
                if best_action == 7:
                    quadrante_escolhido = a8
                if best_action == 8:
                    quadrante_escolhido = a9
                
                # Joga X ou O na posição indicada pelo minimax
                if Eu == "X":
                    robo.draw_x(quadrante_escolhido, 20, 2)
                elif Eu == "O":
                    robo.draw_o(quadrante_escolhido, 12)
                time.sleep(1.3)
                #Volta a posição inicial e verifica a malha após a própria jogada
                robo.initial_position(p1)
                valores_vistos = delay(5)
                valores_quadrantes = valores_vistos.copy()
                Ganhador = analisar_vitoria(valores_vistos)
                if Ganhador or velha(valores_vistos):
                    tchau(Ganhador)
                    break
    
    # Torna a jogada possível novamente ao final da escolha 
    jogou = False
# Finaliza o protocolo com o robô após o uso.
robo.end_control()