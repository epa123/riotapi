#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  riotapi.py
#  
#  Copyright 2015 Yan Pitangui <Yan Pitangui@DESKTOP-GK2ADKB>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

import requests

global apikey
apikey = '6f39b4c8-f156-4327-88c1-6e5be33013d3' #a apikey é necessária pra fazer qualquer coisa

#### FUNÇÕES DE PROCURA POR SUMMONER NAME/ID
def searchbysumm(invocador,regiao): #procura o nome do invocador e o ID
	invocador = invocador.replace(' ','')
	poss = ['BR','EUW','EUNE','NA','TR','OCE','CN','KR','LAN','RU','SEA','LAS']
	if regiao.upper() not in poss:
		return None
	url = 'https://%s.api.pvp.net/api/lol/%s/v1.4/summoner/by-name/%s?api_key=%s' %(regiao.lower(),regiao.lower(),invocador.lower(),apikey)
	jsrequest = requests.get(url)
	if jsrequest.status_code == 404:
		return None
	resposta = jsrequest.json()
	return resposta[invocador.lower()]['id'], resposta[invocador.lower()]['name'] #retorna o id do invocador e o nome real
	
def _searchbyid(lstsumid,regiao='br'): #busca o nome do invocador pelo ID 
	if type(lstsumid)== int or type(lstsumid)== str:
		lstsumid = [lstsumid]
	poss = ['BR','EUW','EUNE','NA','TR','OCE','CN','KR','LAN','RU','SEA','LAS']
	if regiao.upper() not in poss:
		return None
	strsum = ''
	for i in lstsumid:
		strsum+= str(i)+','
	url = 'https://{}.api.pvp.net/api/lol/{}/v1.4/summoner/{}?api_key={}'.format(regiao.lower(),regiao.lower(),strsum,apikey)
	jsrequest = requests.get(url)
	if jsrequest.status_code == 404:
		return None
	dicsaida = {}
	resposta = jsrequest.json()
	for i in resposta:
		dicsaida[i] = resposta[i]['name']
	return dicsaida
	#### FIM DAS FUNÇÕES DE PROCURA POR SUMMONER NAME/ID
	
	
#### FUNÇÕES DE DATABASE OU INTERNA
def _updatecmp(): #carrega todos os campeões de uma vez pra acelerar o processo de partida ativa
	champions = open('cmp.txt', 'w')
	urlbase = 'https://global.api.pvp.net/api/lol/static-data/br/v1.2/champion?api_key={}'.format(apikey)
	jsrequest = requests.get(urlbase)
	resposta = jsrequest.json()
	for i in resposta['data']:
		champions.writelines(str(resposta['data'][i]['id'])+','+resposta['data'][i]['name']+'\n')
	champions.close()
	print('Atualização dos indices de campeão realizada com sucesso!') 
	return

def carregacmp(): #carrega os campeões para um dicionário mais organizado
	champions = None
	while champions is None:
		try:
			champions = open('cmp.txt', 'r')
		except IOError:
			print('Ops... Parece que a tabela de campeões não foi criada')
			print('Tentando atualizar...')
			_updatecmp()
	linha = champions.readline().strip()
	dic = {}
	while linha!='':
		aux = linha.split(',')
		dic[aux[0]]=aux[1]
		linha = champions.readline().strip()
	return dic
#PROCURA DE INFORMAÇÃO DE SOLOQ
def getvarioselos(lstsumid,regiao= 'br'): #entrada: lista de summonersIDs, e a região a ser procurada, caso nada seja dado: padrão BR
	poss = ['BR','EUW','EUNE','NA','TR','OCE','CN','KR','LAN','RU','SEA','LAS']
	if regiao.upper() not in poss:
		return None
	strsum = ''
	for i in lstsumid:
		strsum+= str(i)+','
	url = 'https://%s.api.pvp.net/api/lol/%s/v2.5/league/by-summoner/%s/entry?api_key=%s' %(regiao.lower(),regiao.lower(),strsum,apikey)
	jsrequest = requests.get(url)
	dicsaida = {}
	if jsrequest.status_code in [400,401,429,500,503]: #erros de conexão, dados errados e api
		return None
	if jsrequest.status_code == 404: #caso todos sejam unranked atribui ao dic unranked
		aux = _searchbyid(lstsumid,regiao)
		#normalização movida para função externa
		for i in aux:
			dicsaida[str(i)]=['UNRANKED',0,0]
		return dicsaida
	resposta = jsrequest.json()
	for i in resposta:
		if resposta[i][0]["queue"]== "RANKED_SOLO_5x5": #procura pelo registro de soloq
			aux = resposta[i][0]['entries'][0]['playerOrTeamName']
			#normalização movida para função externa
			dicsaida[i] = [resposta[i][0]["tier"],resposta[i][0]['entries'][0]["division"],resposta[i][0]['entries'][0]["leaguePoints"]]
	for i in lstsumid:#CASO NÃO TODOS SEJAM UNRAKED DEVE SE FAZER UM PARSE ADICIONAL
		if str(i) not in dicsaida:
			dicsaida[str(i)]=['UNRANKED',0,0]
	return dicsaida
#####
		
	
	
	
#função de informação de partida ativa
def partidaativa(sumid,regiao='br'): #a api da riot precisa da região e do summoner ID, por isso não é possivel o usuário chamá-la manualmente
	#declarar os ids das filas, mapas e regiões
	idfilas = {'4':'RANKED_SOLO_5x5', '14':'NORMAL_5x5_DRAFT', '0':'CUSTOM', '8':'NORMAL_3x3', '2':'NORMAL_5x5_BLIND',
	 '41':'RANKED_TEAM_3x3', '42':'RANKED_TEAM_5x5', '65':'ARAM_5x5', '52':'BOT_TT_3x3', '31':'BOT_5x5_INTRO',
	 '32':'BOT_5x5_BEGINNER', '33':'BOT_5x5_INTERMEDIATE', '61':'GROUP_FINDER_5x5'}
	idmapas = { '1':"Summoner's Rift", '2':"Summoner's Rift", '3':'The Proving Grounds', '4':'Twisted Treeline', '8':'The Crystal Scar',
	'10':'Twisted Treeline', '11':"Summoner's Rift", '12':'Howling Abyss', '14':"Butcher's Bridge"}
	dicreg = {'br':'BR1', 'na':'NA1', 'lan':'LA1', 'las':'LA2', 'oce':'OC1', 'eune':'EUN1', 'tr':'TR1', 'ru':'RU', 'euw':'EUW1', 'kr':'KR'}
	if regiao.lower() not in dicreg: #se a região não está no dicionário retornar None
		return None
	url = 'https://%s.api.pvp.net/observer-mode/rest/consumer/getSpectatorGameInfo/%s/%s?api_key=%s' %(regiao.lower(),dicreg[regiao.lower()],sumid,apikey) #formação da url
	jsrequest = requests.get(url) #chamada da url
	lstsumid = [] #lista de summoners id que retornará um dicionário com elos
	if jsrequest.status_code !=200: #tratamento de erro
		return "O jogador não está em partida ativa ou a API da RIOT caiu"
	resposta = jsrequest.json() #transforma a resposta na classe JSON
	iddomapa = str(resposta['mapId'])
	iddafila = str(resposta['gameQueueConfigId'])
	if resposta['bannedChampions']!=[]:
			pass
	#criação das listas de campeões e sumID
	for i in resposta['participants']:
		if i not in lstsumid:
			lstsumid.append(i['summonerId'])
	dicsums = getvarioselos(lstsumid,regiao) #guarda as informações importantes do summoner no dicionário
	dicchampions = carregacmp() #carregar o dicionário de campeões inteiro é mais rapido que procurar campeões um por um
	#começa a formar a string inteira de cada
	lstsaida = []
	lstmapa = [idmapas.get(iddomapa,'Desconhecido'),idfilas.get(iddafila,'Desconhecido')]
	lstsaida.append(lstmapa)
	lstazul = []
	lstvermelho = []
	participantes = resposta['participants']
	for i in participantes:
		aux = []
		if i['teamId']==100:
			aux = dicsums[str(i['summonerId'])]
			aux.append(dicchampions[str(i['championId'])])
			aux = [i['summonerName']] + aux 
			lstazul.append(aux)
		elif i['teamId']==200:
			aux = dicsums[str(i['summonerId'])]
			aux.append(dicchampions[str(i['championId'])])
			aux = [i['summonerName']] + aux 
			lstvermelho.append(aux)
	lstsaida.append(lstazul)
	lstsaida.append(lstvermelho)
	return lstsaida #retorna uma matriz com todos os dados(que julguei úteis por hora).
	
	
def normaliza(strentr,plen): #recebe o summoner name e o retorna com 16 caracteres, preenchendo o que falta com espaços ao final.
	strentr = str(strentr)
	while len(strentr)!=plen:
		strentr+= ' '
	return strentr
	

def main(args):
	a = input('Qual o nome de invocador deseja procurar? ')
	b = input('Qual a região? ')
	valor = searchbysumm(a,b)
	print(partidaativa(valor[0],b))
	return 0

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))
