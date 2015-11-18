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
apikey = '01b0e541-ea0b-44a6-8207-97fcabcb6b0e'
def searchbysumm(invocador,regiao):
	invocador = invocador.replace(' ','')
	poss = ['BR','EUW','EUNE','NA','TR','OCE','CN','KR','LAN','RU','SEA','LAS']
	if regiao.upper() not in poss:
		return None
	url = 'https://br.api.pvp.net/api/lol/%s/v1.4/summoner/by-name/%s?api_key=%s' %(regiao.lower(),invocador.lower(),apikey)
	jsrequest = requests.get(url)
	if jsrequest.status_code == 404:
		return None
	resposta = jsrequest.json()
	return resposta[invocador.lower()]['id'], resposta[invocador.lower()]['name'] #retorna o id do invocador e o nome real
	
def getelo(sumid,regiao):
	poss = ['BR','EUW','EUNE','NA','TR','OCE','CN','KR','LAN','RU','SEA','LAS']
	if regiao.upper() not in poss:
		return None
	url = 'https://%s.api.pvp.net/api/lol/%s/v2.5/league/by-summoner/%s/entry?api_key=%s'% (regiao.lower(),regiao.lower(), sumid, apikey)
	jsrequest = requests.get(url)
	if jsrequest.status_code in  [400,401,429,500,503]:
		return 'API DA RIOT ESTÁ OFFLINE',0,0
	resposta = jsrequest.json()
	if jsrequest.status_code == 404:
		return ('UNRANKED',0,0)
	return (str(resposta[str(sumid)][0]['tier']), str(resposta[str(sumid)][0]['entries'][0]['division']), str(resposta[str(sumid)][0]['entries'][0]['leaguePoints'])) #alterado para retorno de dados puros
	
	
	
def getvarioselos(lstsumid,regiao):
	poss = ['BR','EUW','EUNE','NA','TR','OCE','CN','KR','LAN','RU','SEA','LAS']
	if regiao.upper() not in poss:
		return None
	strsum = ''
	for i in lstsumid:
		strsum+= str(i)+','
	url = 'https://%s.api.pvp.net/api/lol/%s/v2.5/league/by-summoner/%s/entry?api_key=%s' %(regiao.lower(),regiao.lower(),strsum,apikey)
	jsrequest = requests.get(url)
	dicsaida = {}
	if jsrequest.status_code in [400,401,429,500,503]: #erros de conexão, pesquisa e api
		return None
	if jsrequest.status_code == 404: #caso todos sejam unranked atribui ao dic unranked
		for i in lstsumid:
			dicsaida[str(i)]=['UNRANKED',0,0,searchbysumm(i,regiao)]
		return dicsaida
	resposta = jsrequest.json()
	for i in resposta:
		if resposta[i][0]["queue"]== "RANKED_SOLO_5x5":
			dicsaida[i] = [resposta[i][0]["tier"],resposta[i][0]['entries'][0]["division"],resposta[i][0]['entries'][0]["leaguePoints"],resposta[i][0]['entries'][0]['playerOrTeamName']]
	for i in lstsumid:
		if str(i) not in dicsaida:
			dicsaida[str(lstsumid)]=['UNRANKED',0,0,resposta[i][0]['entries'][0]['playerOrTeamName']]
	return dicsaida
		
	
	
	
	
def partidaativa(sumid,regiao): #a api da riot precisa da região e do summoner ID, por isso não é possivel o usuário chamá-la manualmente
	dicreg = {'br':'BR1', 'na':'NA1', 'lan':'LA1', 'las':'LA2', 'oce':'OC1', 'eune':'EUN1', 'tr':'TR1', 'ru':'RU', 'euw':'EUW1', 'kr':'KR'}
	if regiao.lower() not in dicreg:
		return None
	url = 'https://%s.api.pvp.net/observer-mode/rest/consumer/getSpectatorGameInfo/%s/%s?api_key=%s' %(regiao.lower(),dicreg[regiao.lower()],sumid,apikey) #formação da url
	jsrequest = requests.get(url) #chamada da url
	lstchampions = [] #declaração da lista de campeões que depois virará um dicionário
	lstsumid = [] #lista de summoners id que retornará um dicionário com elos
	
	if jsrequest.status_code !=200: #tratamento de erro
		return "O jogador não está em partida ativa ou a API da RIOT caiu"
	resposta = jsrequest.json() #transforma a resposta na classe JSON
	strretorno = 'INFORMAÇÕES DE PARTIDA\n'
	strretorno += 'MAPA: %s\t TIPO DE JOGO: %s\n' %(resposta["gameMode"], resposta['gameType'])
	if resposta['bannedChampions']!=[]:
			pass
	strretorno += '\t\tPARTICIPANTES\n'
	strtimevermelho = '\tTIME AZUL\n'
	strroxo ='\tTIME VERMELHO\n'
	#criação das listas de campeões e sumID
	for i in resposta['participants']:
		if i['championId'] not in lstchampions:
			lstchampions.append(i['championId'])
		if i not in lstsumid:
			lstsumid.append(i['summonerId'])
	dicsums = getvarioselos(lstsumid,regiao)
	#dicchampions = _getchampionname(lstchampions,regiao)
	#return 'aqui foi feito o dicionario de campeões'

	#começa a formar a string inteira de cada time
	for i in resposta['participants']:
		if i['teamId']==100:
			if dicsums[str(i['summonerId'])][0] == 'UNRANKED':
				strtimevermelho+= '{}\t'.format(dicsums[str(i['summonerId'])][3])
				strtimevermelho+= '{}\t'.format(dicsums[str(i['summonerId'])][0])
				#strtimevermelho+= 'Campeão: {}\n'.format(dicchampions[i['championId']])
			else:
				strtimevermelho+= '{}s   '.format(dicsums[str(i['summonerId'])][3])
				strtimevermelho+= '\t\t\t{}'.format(dicsums[str(i['summonerId'])][0])
				strtimevermelho+= ' \t{}'.format(dicsums[str(i['summonerId'])][1])
				strtimevermelho+= ' {} PDL\t'.format(dicsums[str(i['summonerId'])][2])
				#strtimevermelho+= 'Campeão: {}\n'.format(dicchampions[i['championId']])
		if i['teamId']==200:
			if dicsums[str(i['summonerId'])][0] == 'UNRANKED':
				strroxo+= '{}\t'.format(dicsums[str(i['summonerId'])][3])
				strroxo+= 	'{}\t'.format(dicsums[str(i['summonerId'])][0])
				#strroxo+= 'Campeão: {}\n'.format(dicchampions[i['championId']])
			else:
				strroxo+= '{}   '.format(dicsums[str(i['summonerId'])][3])
				strroxo+= '\t\t\t{}'.format(dicsums[str(i['summonerId'])][0])
				strroxo+= ' \t{}'.format(dicsums[str(i['summonerId'])][1])
				strroxo+= ' {} PDL\t'.format(dicsums[str(i['summonerId'])][2])
				#strroxo+= 'Campeão: {}\n'.format(dicchampions[i['championId']])
	strretorno+= strtimevermelho+strroxo
		
		
	return strretorno #pensando se retornarei uma string montada ou dados puros(matriz com nome de invocador, tier, divisão pdl e campeão)
	

def _getchampionname(cmpids,regiao): #só deve ser utilizada por outras funções, visto que ninguem terá o id do campeão manualmente
	strcmpid = ''
	dicsaida = {}
	for i in cmpids:
		url = 'https://global.api.pvp.net/api/lol/static-data/%s/v1.2/champion/%s?api_key=%s' % (regiao.lower(), str(i), apikey)
		jsrequest = requests.get(url)
		resposta = jsrequest.json()
		if i not in dicsaida:
			dicsaida[i]= resposta['name']
	return dicsaida
	


def main(args):
	while True:
		a = input('Qual o nome do invocador a ser pesquisado? ')
		b = input('Qual a região a ser pesquisada? ')
		valor = searchbysumm(a,b)
		print(partidaativa(valor[0],b))
	return 0

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))
