# Robotic Tic Tac Toe

Projeto de manuseio de um braço robótico permitindo-o jogar o "Jogo da Velha" contra um jogador real utilizando uma câmera para visualização, um canetão para as jogadas em uma lousa branca e o algoritmo minimax para as escolhas autônomas.

## Sumário

- [Descrição](#descrição)
- [Pré-requisitos](#pré-requisitos)
- [Configuração do Ambiente](#config)
- [Contribuição](#contribuição)
- [Licença](#licença)
- [Autores e Agradecimentos](#autores-e-agradecimentos)
- [Recursos Adicionais](#recursos-adicionais)

## Descrição

O projeto consiste no manuseio de um braço robótico controlado via protocolo Socket enviando-o qual movimento deve executar e em quais coordenadas. Para a visualização e identificação da malha e suas jogadas foi utilizado uma câmera juntamente com uma rede neural, cujo torna-se responsável pela identificação do que é X ou O. Para a decisão das escolhas que o robô deve tomar foi utilizado o algoritmo minimax. Este funciona simulando e visualizando todas as possíveis jogadas e atribuindo um valor a elas de acordo com os seus nodos terminais, sendo uma pontuação positiva caso vitória, nula caso empate e negativa caso enfrente a derrota. Após simular todas as possibilidades ele escolhe a jogada simulada que obteve a maior pontuação e envia-a para a execução da jogada por parte do robô. Para controles de segurança foi utilizado 2 LEDS de controle, um verde e um vermelho que sinalizam quando a jogada é permitida e proibida respectivamente. 

## Pré-requisitos

- keras: 2.6.0
- python: 3.10.0
- tensorflow: 2.9.1
- pip (gerenciador de pacotes)
- Acesso a um broker MQTT (como Mosquitto, HiveMQ, etc.)


## Config

É recomendável criar um ambiente virtual para isolar as dependências do projeto. Os comandos variam conforme o sistema operacional.

**Para Windows:**

```bash
#Criação do ambiente virtual
python -m venv <NOME_DO_SEU_PROJETO>

#Ativação do ambiente virtual
<NOME_DO_SEU_PROJETO>\Scripts\activate

pip install -r requirements.txt
```
**Para Linux/Ubuntu:**

```bash
#Criação do ambiente virtual
python3 -m venv <NOME_DO_SEU_PROJETO>

#Ativação do ambiente virtual
source <NOME_DO_SEU_PROJETO>/bin/activate

pip install -r requirements.txt
```

