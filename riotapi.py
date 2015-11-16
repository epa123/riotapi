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
apikey = 'da52e9a5-240d-4cac-9538-7ae90c298bb3'

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
	return resposta[invocador.lower()]['id'], resposta[invocador.lower()]['name']
	
def getelo(sumid,regiao,nome):
	poss = ['BR','EUW','EUNE','NA','TR','OCE','CN','KR','LAN','RU','SEA','LAS']
	if regiao.upper() not in poss:
		return None
	url = 'https://br.api.pvp.net/api/lol/%s/v2.5/league/by-summoner/%s/entry?api_key=%s'% (regiao.lower(), sumid, apikey)
	jsrequest = requests.get(url)
	if jsrequest.status_code in  [400,401,404,429,500,503]:
		return None
	resposta = jsrequest.json()
	if resposta[str(sumid)]== []:
		return None
	strretorno = 'Invocador: %s\n' % nome
	strretorno+= 'Liga: %s' % resposta[str(sumid)][0]['tier']
	strretorno+= ' %s' % resposta[str(sumid)][0]['entries'][0]['division']
	strretorno+= ' %s PDL' % resposta[str(sumid)][0]['entries'][0]['leaguePoints']
	return strretorno
	
	

def main(args):
	a = input('Qual o nome do invocador a ser pesquisado? ')
	b = input('Qual a região a ser pesquisada? ')
	valor = searchbysumm(a,b)
	print(getelo(valor[0],b,valor[1]))
	return 0

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))
