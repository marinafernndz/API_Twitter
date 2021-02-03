# -*- coding: utf-8 -*-
"""
Created on Fri Nov 27 13:55:24 2020

@author: marin
"""

import tweepy
import time
import networkx as nx
import matplotlib.pyplot as plt
consumer_key = 
consumer_secret = 
access_token = 
access_token_secret = 
auth = tweepy.OAuthHandler('consumer_key', 'consumer_secret')
auth.set_access_token('access_token', 'access_token_secret')

# Preparamos el módulo api de Tweepy (que es el que nos va a ayudar a hacer las "preguntas" a la API)
api = tweepy.API(auth)
# Importamos PyMongo
from pymongo import MongoClient

# Creamos una conexión con la BBDD
client = MongoClient()
           
#  Usamos una base de datos llamada test
db = client.test3

# Almacenamos cada tweet acompañado de nuestro hashtag en la colección tweet, y creamos un try and except
# para poder descargar más de los tweets permitidos por la API.
for tweet in tweepy.Cursor(api.search,q=("#salvadosultraderecha"),
                            tweet_mode= 'extended', lang="es",count=100).items():
      try:
          db.tweets.insert_one(tweet._json)
      except Exception as e:
          print(e)
          time.sleep(900)
          continue

# Definimos nuestro grafo.    
G = nx.DiGraph()

# Decidimos traernos cierta información de nuestros tweets como son el nombre de usuario, el nombre de usuario
# de la persona retwiteada , el nombre de usuario de la persona citada  y el nombre de usuario al que responde
# el tweet, siempre en el caso de que lo sean.

for result in db.tweets.find():
            uid = result['user']['screen_name']            
            G.add_node(uid) 
            if 'retweeted_status' in result:
                
                if G.has_edge(uid, result['retweeted_status']['user']['screen_name']):
                    G[uid][result['retweeted_status']['user']['screen_name']]['weight'] += 1.0
                else:
                     G.add_edge(uid, result['retweeted_status']['user']['screen_name'], weight = 1.0) 
            if 'quoted_status' in result:
                if G.has_edge(uid, result['quoted_status']['user']['screen_name']):
                    G[uid][result['quoted_status']['user']['screen_name']]['weight'] += 1.0
                else:
                    G.add_edge(uid, result['quoted_status']['user']['screen_name'], weight = 1.0)
                
            if  result['in_reply_to_screen_name'] != None:
                if G.has_edge(uid, result['in_reply_to_screen_name']):
                    G[uid][result['in_reply_to_screen_name']]['weight'] += 1.0
                else:
                    G.add_edge(uid, result['in_reply_to_screen_name'], weight = 1.0)
                    
# Dibujamos el grafo y lo exportamos.
nx.draw(G, with_labels=True)       
plt.show()
nx.write_graphml(G, "salvados_test_2.graphml")
        
