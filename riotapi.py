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
	if jsrequest.status_code in  [400,401,404,429,500,503]:
		return None
	resposta = jsrequest.json()
	if resposta[str(sumid)]== []:
		return (UNRANKED,0,0)
	return (str(resposta[str(sumid)][0]['tier']), str(resposta[str(sumid)][0]['entries'][0]['division']), str(resposta[str(sumid)][0]['entries'][0]['leaguePoints'])) #alterado para retorno de dados puros
	
def partidaativa(sumid,regiao): #a api da riot precisa da região e do summoner ID, por isso não é possivel o usuário chamá-la manualmente
	dicreg = {'br':'BR1', 'na':'NA1', 'lan':'LA1', 'las':'LA2', 'oce':'OC1', 'eune':'EUN1', 'tr':'TR1', 'ru':'RU', 'euw':'EUW1', 'kr':'KR'}
	if regiao.lower() not in dicreg:
		return None
	url = 'https://%s.api.pvp.net/observer-mode/rest/consumer/getSpectatorGameInfo/%s/%s?api_key=%s' %(regiao.lower(),dicreg[regiao.lower()],sumid,apikey)
	jsrequest = requests.get(url)
	if jsrequest.status_code !=200:
		return "O jogador não está em partida ativa ou a API da RIOT caiu"
	resposta = jsrequest.json()
	strretorno = 'INFORMAÇÕES DE PARTIDA\n'
	strretorno += 'MAPA: %s\t TIPO DE JOGO: %s\n' %(resposta["gameMode"], resposta['gameType'])
	if resposta['bannedChampions']!=[]:
			pass
	strretorno += '\t\tPARTICIPANTES\n'
	strtimevermelho = '\tTIME VERMELHO\n'
	strtimeroxo ='\tTIME ROXO\n'
	for i in resposta['participants']:
		if i['teamId']==100:
			if getelo(i['summonerId'],regiao)[0] == 'UNRANKED':
				strtimevermelho+= '%s\t' % i['summonerName']
				strtimevermelho+= '%s\t' % getelo(i['summonerId'],regiao.lower())[0]
				strtimevermelho+= 'Campeão: %s\n' % _getchampionname(i['championId'],regiao)
			else:
				strtimevermelho+= '%s' % i['summonerName']
				strtimevermelho+= ' %s' % getelo(i['summonerId'],regiao.lower())[0]
				strtimevermelho+= ' %s' % getelo(i['summonerId'] ,regiao.lower())[1]
				strtimevermelho+= ' %s PDL\t' % getelo(str(i['summonerId']),regiao.lower())[2]
				strtimevermelho+= 'Campeão: %s\n' % _getchampionname(i['championId'],regiao)
		if i['teamId']==200:
			if getelo(i['summonerId'],regiao)[0] == 'UNRANKED':
				strtimeroxo+= '%s\t' % i['summonerName']
				strtimeroxo+= '%s\t' % getelo(i['summonerId'],regiao.lower())[0]
				strtimeroxo+= 'Campeão: %s\n' % _getchampionname(i['championId'],regiao)
			else:
				strtimeroxo+= '%s' % i['summonerName']
				strtimeroxo+= ' %s' % getelo(i['summonerId'],regiao.lower())[0]
				strtimeroxo+= ' %s' % getelo(i['summonerId'] ,regiao.lower())[1]
				strtimeroxo+= ' %s PDL\t' % getelo(str(i['summonerId']),regiao.lower())[2]
				strtimeroxo+= 'Campeão: %s\n' % _getchampionname(i['championId'],regiao)
	strretorno+= strtimevermelho+strtimeroxo
		
		
	return strretorno #pensando se retornarei uma string montada ou dados puros(matriz com nome de invocador, tier, divisão pdl e campeão)
	

def _getchampionname(cmpid,regiao): #só deve ser utilizada por outras funções, visto que ninguem terá o id do campeão manualmente
	url = 'https://global.api.pvp.net/api/lol/static-data/%s/v1.2/champion/%s?api_key=%s' % (regiao.lower(), cmpid, apikey)
	jsrequest = requests.get(url)
	if jsrequest.status_code!=200:
		return None
	return jsrequest.json()['name']


def main(args):
	a = input('Qual o nome do invocador a ser pesquisado? ')
	b = input('Qual a região a ser pesquisada? ')
	valor = searchbysumm(a,b)
	print(partidaativa(valor[0],b))  
	return 0

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))
