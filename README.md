# Sistema de Irrigação Autônoma de Planta usando Raspberry Pi 4 

Projeto final de conclusão de curso ADS-IFBA

## Conteúdo

- [Tecnologia Utilizada](#tecnologia)
- [Pré-requisitos](#pré-requisitos)
- [Execução Aplicação](#execução)
- [Escopo](#escopo)

## Tecnologia Utilizada

- Biblioteca Prometheus_client

## Pré-requisitos

Estas são as instalações e configurações necessárias para executar o projeto.

Para executar este projeto é necessário instalar:

- Módulo Adafruit-ADS1x15 
- Obter o projeto do back-end e front-end

1. Após a instalação: 

   1.1 Habilite o I2C

        - Abra o termial, digite raspi-config -> interfacing Options -> I2C.
        - Reinicie o Raspberry Pi

## Execução Aplicação

1. Clonar repositório git utilizando o comando:

        git clone git@github.com:elayneargollo/tcc-raspberry.git

2. Vá ate a pasta do projeto

        cd tcc-raspberryPi

3. Execute o programa

        python raspberryPi.py

Após a execução a inicialização conseguirá acessar:

        - Logger de execução na raiz do projeto: irrigacao.log

## Escopo

A partir do cadastrado de plantas através de uma aplicação frontend, o raspberry irá acessar o banco de dados compartilhado com a aplicação de backend para atualizar os dados de sensores de acordo com os valores lidos em campo.

- RF1. Calibrar Sensor.

    - Cada sensor terá seu valor de calibração baseado nos valores mínimos e máximos em ambiente de solo completamente seco e completamente úmido.
        - Calibrar sensor para solo seco e guardar o log dos valores obtidos.
        - Calibrar sensor para solo úmido e guardar o log dos valores obtidos.

- RF2. Obter Concentração Mínima do solo

    - A partir do tipo de solo cadastrado na planta que está sendo monitorada pelo respectivo sensor, deve-se obter a concentração mínima de água necessária para manter a raiz saudável.
    - Este valor deve está entra a percentagem máxima e mínima (100% e 0%).
    - Cada solo téra seu valor de concentração.
    - Cada solo deve ter seu peso seco e seu peso úmido persistido.
    - Cada solo deve está associado a uma planta, um sensor e uma solenóide.

- RF3. Irrigar Automáticamente

    - Com os valores adquiridos após calibragem e concentração mínima deve-se irrigar automaticamente a planta se e somente se a valor lido pelo sensor for menor ou igual a concentração mínima.
    - Ligar ou desligar a solenóide de acordo com o valor lido.
    - Atualizar os dados do sensor.
    - Aguardar até a próxima leitura.

### Autora

<img style="border-radius: 50%;" src="https://avatars.githubusercontent.com/u/48841005?s=40&v=4" width="100px;" alt=""/>
 
Feito por Elayne Natália 👋🏽 

[![Linkedin Badge](https://img.shields.io/badge/-Elayne-blue?style=flat-square&logo=Linkedin&logoColor=white&link=https://www.linkedin.com/in/elayne/)](https://www.linkedin.com/in/elayne-nat%C3%A1lia/) 

