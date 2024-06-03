import socket
import re
import time
import ast
import math 

class robot():
    socketRobo = None
    @classmethod #Herança de classes
    def connect_to_robot(cls, host, port):
        socketRobo = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Instancia socket
        socketRobo.connect((host, port)) #Efetua conexão com o robô
        cls.socketRobo = socketRobo
        return cls

    def set_speed(self, speed=30):
        self.socketRobo.sendall("1;1;EXECSPD {}".format(speed).encode())  #Seta a velocidade do robô
        data = self.socketRobo.recv(1024)
        print(f"Received {data!r}")
        print("A velocidade do robô foi definida em {}".format(speed))

    def start_control(self):
        self.socketRobo.sendall(b"1;1;CNTLON")  #Inicia controle
        data = self.socketRobo.recv(1024) #Aguarda reasposta
        print(f"Received {data!r}") #Printa resposta

        self.socketRobo.sendall(b"1;1;EXECACCEL 30") #Seta aceleração do robô
        data = self.socketRobo.recv(1024)
        print(f"Received {data!r}")

        self.socketRobo.sendall(b"1;1;EXECMvTune 2") #Seta o robô no modo aprimorado para velocidade
        data = self.socketRobo.recv(1024)
        print(f"Received {data!r}")

        #A PARTIR DAQUI O ROBÔ ESTÁ HÁPTO A SER MOVIMENTADO
    def servo_on(self): #Liga o robô na programação desejada
        self.socketRobo.sendall(b"1;1;SRVON") #Habilita os servos
        data = self.socketRobo.recv(1024)
        print(f"Received {data!r}")

    def servo_off(self): #Desliga os servos e para o robô
        self.socketRobo.sendall(b"1;1;SRVOFF") #Desabilita os servos
        data = self.socketRobo.recv(1024)
        print(f"Received {data!r}")
        self.socketRobo.sendall(b"1; 0;STOP") #Para o robô
        data = self.socketRobo.recv(1024)
        print(f"Received {data!r}")

    def reset(self): #Função que reinicia o controlador do robô
        str_commands = ["1;0;STOP","1;1;SLOTINIT",
                    "1;1;STATE","1;2;STATE",
                    "1;3;STATE","1;4;STATE",
                    "1;5;STATE","1;6;STATE",
                    "1;7;STATE","1;8;STATE"]
        for list_commands in str_commands:
            self.socketRobo.sendall('{}'.format(list_commands).encode()) #reinicia o robô
            data = self.socketRobo.recv(1024)
            print(f"Received {data!r}")

    def end_control(self):
        self.socketRobo.sendall(b"1;1;CNTLOFF") #desliga o controle
        data = self.socketRobo.recv(1024)
        print(f"Received {data!r}")
        self.socketRobo.close()

    def open_hand(self): #Abre a garra do robô
        str_commands = ["1;1EXECHCLOSE 1"]
        for list_commands in str_commands:
            self.socketRobo.sendall('{}'.format(list_commands).encode()) #reinicia o robô
            data = self.socketRobo.recv(1024)
            print(f"Received {data!r}")

    def close_hand(self): #Abre a garra do robô
        str_commands = ["1;1EXECHOPEN 1"]
        for list_commands in str_commands:
            self.socketRobo.sendall('{}'.format(list_commands).encode()) #reinicia o robô
            data = self.socketRobo.recv(1024)
            print(f"Received {data!r}")


    def movimentmvs_list(self, pos):  # pos agora é esperado ser uma lista
    # A conversão para float é redundante se já garantimos que pos contém floats
        command = "1;1;EXECPPOS=({}, {}, {}, {}, {}, {})".format(*pos)  # Desempacota a lista diretamente
        self.socketRobo.sendall(command.encode())  # Envia os vetores
        data = self.socketRobo.recv(1024)
        print(f"Received {data!r}")
        self.socketRobo.sendall(b"1;1;EXECMVS PPOS")  # Manda o robô para a posição
        data = self.socketRobo.recv(1024)
        print(f"Received {data!r}")

    def movimentmvs(self, pos): #função que determina o movimento do robô de acordo com a posição da mão
        positions = pos.split(",")
        self.socketRobo.sendall("1;1;EXECPPOS=({}, {}, {}, {}, {}, {})".format((float(positions[0])), float(positions[1]), float(positions[2]),
                                                                                float(positions[3]), float(positions[4]), float(positions[5])).encode()) # Envia os vetores
        data = self.socketRobo.recv(1024)
        print(f"Received {data!r}")
        self.socketRobo.sendall(b"1;1;EXECMVS PPOS") #Manda o robô para a posição
        data = self.socketRobo.recv(1024)
        print(f"Received {data!r}")

    def movimentmov(self, pos): #função que determina o movimento do robô de acordo com a posição da mão
        positions = pos.split(",")
        self.socketRobo.sendall("1;1;EXECPPOS=({}, {}, {}, {}, {}, {})".format((float(positions[0])), float(positions[1]), float(positions[2]),
                                                                                float(positions[3]), float(positions[4]), float(positions[5])).encode()) # Envia os vetores
        data = self.socketRobo.recv(1024)
        print(f"Received {data!r}")
        self.socketRobo.sendall(b"1;1;EXECMOV PPOS") #Manda o robô para a posição
        data = self.socketRobo.recv(1024)
        print(f"Received {data!r}")

    
    def movimentmvc(self, pos:str, radius): 
        # função que determina o movimento do robô de acordo com a posição da mão
        positions = pos.split(",") 
        
        # Calcula as novas posições dos pontos P1, P2 e P3
        p1_x = float(positions[0]) - (radius * math.sqrt(2))
        p1_y = float(positions[1])
        p1_z = float(positions[2])
        
        p2_x = float(positions[0]) + radius
        p2_y = float(positions[1]) + radius
        p2_z = float(positions[2])
        
        p3_x = float(positions[0]) + radius
        p3_y = float(positions[1]) - radius
        p3_z = float(positions[2])
        
        # Envia os vetores para o robô
        self.socketRobo.sendall("1;1;EXECP1=({}, {}, {}, {}, {}, {})".format(p1_x, p1_y, p1_z,float(positions[3]),float(positions[4]),float(positions[5])).encode())
        data = self.socketRobo.recv(1024)
        print(f"Received {data!r}")
        
        self.socketRobo.sendall("1;1;EXECP2=({}, {}, {}, {}, {}, {})".format(p2_x, p2_y, p2_z,float(positions[3]),float(positions[4]),float(positions[5])).encode())
        data = self.socketRobo.recv(1024)
        print(f"Received {data!r}")
        
        self.socketRobo.sendall("1;1;EXECP3=({}, {}, {}, {}, {}, {})".format(p3_x, p3_y, p3_z,float(positions[3]),float(positions[4]),float(positions[5])).encode())
        data = self.socketRobo.recv(1024)
        print(f"Received {data!r}")

        # Envia comando para mover o robô para a posição determinada pelos pontos P1, P2 e P3
        self.socketRobo.sendall(b"1;1;EXECMVC P1, P2, P3")
        
        # Recebe e imprime os dados recebidos
        data = self.socketRobo.recv(1024)
        print(f"Received {data!r}")

    def get_poss(self):
        self.socketRobo.sendall(b"1;1;VALP_CURR")  # Envia o comando desejado
        data = self.socketRobo.recv(1024)
        data_str = str(data, 'utf-8')  # Converte os bytes recebidos para uma string UTF-8
        match = re.search(r'\((.*?)\)', data_str)
        if match:
            content_inside_brackets = match.group(1)
            coordenates = content_inside_brackets.split(",")
            print(coordenates[0], coordenates[1],coordenates[2],coordenates[3],coordenates[4],coordenates[5])
            time.sleep(3)

    def verify_pos(self):
        self.socketRobo.sendall(b"1;1;VALP_CURR")  # Envia o comando desejado
        data = self.socketRobo.recv(1024)
        data_str = str(data, 'utf-8')  # Converte os bytes recebidos para uma string UTF-8
        match = re.search(r'\((.*?)\)', data_str)
        if match:
            content_inside_brackets = match.group(1)
            coordenates = content_inside_brackets.split(",")
            print(f"Received {data_str!r}")
            time.sleep(5)

    def initial_position(self, pos):
        self.movimentmvs(pos)
        time.sleep(3)
    
    def draw_mesh(self,p1_aerial:int,p1,p2,p2_aerial,p3_aerial,p3,p4,p4_aerial,p5_aerial,p5,p6,p6_aerial,p7_aerial,p7,p8,p8_aerial):
        
        #Desenho da primeira linha
        '''
            |
            |
            |
        '''
        self.movimentmvs(p1_aerial)
        time.sleep(2)
        self.movimentmvs(p1)
        time.sleep(0.5)
        self.movimentmvs(p2)
        time.sleep(1.0)
        self.movimentmvs(p2_aerial)
        time.sleep(0.5)



        #Desenho da segunda linha
        '''
            |  |
            |  |
            |  |
        '''
        self.movimentmov(p3_aerial)
        time.sleep(0.5)
        self.movimentmvs(p3)
        time.sleep(0.5)
        self.movimentmvs(p4)
        time.sleep(1.0)
        self.movimentmvs(p4_aerial)
        time.sleep(0.5)


        #Desenho da terceira linha
        '''
        ____|__|____
            |  |
            |  |
        '''
        self.movimentmvs(p6_aerial)
        time.sleep(1)
        self.movimentmvs(p6)
        time.sleep(0.5)
        self.movimentmvs(p5)
        time.sleep(1.0)
        self.movimentmvs(p5_aerial)
        time.sleep(0.5)


        #Desenho da Quarta linha
        '''
           p1  p3
      p5____|__|____p6
      p7____|__|____p8
            |  |
           p2  p4
        
        '''
        self.movimentmvs(p7_aerial)
        time.sleep(0.5)
        self.movimentmvs(p7)
        time.sleep(0.5)
        self.movimentmvs(p8)
        time.sleep(1.0)
        self.movimentmvs(p8_aerial)
        time.sleep(0.5)



    def draw_x(self, pos:str, height:int, font_size:int):
        positions = [float(p.strip()) for p in pos.split(",")]  # Converte cada item para float e remove espaços extras

        # Cria a posição aérea aumentando a coordenada Z
        p1_aerea = positions.copy()
        p1_aerea[2] += height  # Adiciona a altura especificada ao eixo Z
        # Ajusta as coordenadas X e Y para criar o ponto 1 do "X"
        p1 = positions.copy()
        p1[0] -= 5 * font_size  # Ajusta X
        p1[1] -= 5 * font_size  # Ajusta Y
        # Primeiro, move para a posição aérea
        self.movimentmvs_list(p1_aerea)
        time.sleep(3)
        # Depois, move para a posição final
        self.movimentmvs_list(p1)
        time.sleep(0.3)

        # Cria a posição aérea aumentando a coordenada Z
        p2_aerea = positions.copy()
        p2_aerea[2] += height  # Adiciona a altura especificada ao eixo Z
        # Ajusta as coordenadas X e Y para criar o ponto 2 do "X"
        p2 = positions.copy()
        p2[0] += 5 * font_size  # Ajusta X
        p2[1] += 5 * font_size  # Ajusta Y
        # Primeiro, move para a posição aérea
        # Depois, move para a posição final
        self.movimentmvs_list(p2)
        time.sleep(1)
        self.movimentmvs_list(p2_aerea)
        time.sleep(0.3)

        # Cria a posição aérea aumentando a coordenada Z
        p3_aerea = positions.copy()
        p3_aerea[2] += height  # Adiciona a altura especificada ao eixo Z
        # Ajusta as coordenadas X e Y para criar o ponto 3 do "X"
        p3 = positions.copy()
        p3[0] -= 5 * font_size  # Ajusta X
        p3[1] += 5 * font_size  # Ajusta Y
        # Primeiro, move para a posição aérea
        self.movimentmvs_list(p3_aerea)
        time.sleep(1)
        # Depois, move para a posição final
        self.movimentmvs_list(p3)
        time.sleep(0.3)

        # Cria a posição aérea aumentando a coordenada Z
        p4_aerea = positions.copy()
        p4_aerea[2] += height  # Adiciona a altura especificada ao eixo Z
        # Ajusta as coordenadas X e Y para criar o ponto 4 do "X"
        p4 = positions.copy()
        p4[0] += 5 * font_size  # Ajusta X
        p4[1] -= 5 * font_size  # Ajusta Y
        # Primeiro, move para a posição aérea
        # Depois, move para a posição final
        self.movimentmvs_list(p4)
        time.sleep(1)
        self.movimentmvs_list(p4_aerea)
        time.sleep(0.3)
    
    def draw_o(self, pos:str, height:int):
        positions = [float(p.strip()) for p in pos.split(",")]  # Converte cada item para float e remove espaços extras

        # Cria a posição aérea aumentando a coordenada Z
        p1_aerea = positions.copy()
        p1_aerea[2] += height  # Adiciona a altura especificada ao eixo Z
        p1 = positions.copy()
        self.movimentmvs_list(p1_aerea)
        time.sleep(2)
        # Depois, move para a posição final
        self.movimentmvc(pos, 12)
        
