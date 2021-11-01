import os, sys
# import traceback
import sqlite3 # Installer avec 'pip install db-sqlite3'
import time
from datetime import datetime as dt


def log(msg, output=""):
	""" Afficher le log dans la sortie standard ou dans un fichier 
		Si rien n'est spécifié dans output : sortie standard
		Si un nom est spécifé un fichier avec ce nom sera créé """
	if output != "":
		logFile = open(output, 'a')
		print(str(dt.now()) + " -> " + str(msg), file=logFile)
		logFile.close()
	else:
		print(str(dt.now()) + " -> " + str(msg))


""" Utilitaires pour gérer une db sqlite """
class sqlite_database:
	""" Classe pour la gestion d'une base de données sqlite
		Paramètres:
			db_name = Nom de la DB
			GUI = Type d'interface graphique utilisée
				- None (Défaut)
				- tkinter

	"""

	def __init__(self, db_name, GUI=None):
		""" Constructeur """
		self.db = ""
		self.cursor = ""
		self.name = db_name
		self.GUI = GUI
		if self.GUI not in (None, "tkinter"):
			raise TypeError("Paramètre GUI incorrect")

	def open(self, returnFormat='list'):
		""" Méthode pour se connecter à la base de données """
		if os.path.exists("./" + self.name):
			# Si la db est inacessible, on réessaye 
			# for i in range(10):	
				# try:
			self.db = sqlite3.connect(self.name)
			if returnFormat == 'dict':
				self.db.row_factory = sqlite3.Row
			self.cursor = self.db.cursor()
			return True
				# except sqlite3.OperationalError as e: #sqlite3.OperationalError: database is locked:
				# 	if e == "database is locked":
				# 		time.sleep(0.2)
				# 	else:
				# 		print(traceback.format_exc())
				# 		return False

		else:
			if self.GUI == 'tkinter':
				showwarning("Base de données introuvable !", "La base de données est introuvable, le programme va se fermer !!")
			raise FileNotFoundError(f"fichier {self.name} inexistant")
			exit(1)



	def close(self,commit = False):
		""" Méthode pour fermer la base de données """
		if commit:
			self.commit()
		self.cursor.close()
		self.db.close()



	def execute(self,query):
		""" Méthode pour exécuter une requête """
		# Si la db est inacessible, on réessaye 
		# L'erreur est : sqlite3.OperationalError: database is locked
		for i in range(5):
			try:
				self.cursor.execute(query)
				return True
			except sqlite3.OperationalError as e: #sqlite3.OperationalError: database is locked:
				log(f"Error is : {e}")
				if e == "database is locked":
					log("Base de données verrouillée, attente ...")
					time.sleep(0.5)
				else:
					log(sys.exc_info())
					return False
	def exec(self,query, fetch = "all", return_format='list'):
		""" Méthode pour exécuter un requête et qui gère l'ouverture et la fermeture de la db automatiquement """
		# Si INSERT ou UPDATE -> commit
		if "SELECT" in query[:10]:
			commit = False
		else:
			commit = True

		# Exécution de la requête
		self.open(return_format)
		if self.execute(query):
			if (not commit) and fetch == "all":
				result = self.fetchall()
			elif (not commit) and fetch == "one":
				result = self.fetchone()
			self.close(commit)
			if not commit:
				if type(result) is None:
					return ["",]
				else:
					if return_format == 'dict':
						listResult = []
						for item in result:
							listResult.append(dict(item))
						return listResult
					else:
						return result



	def fetchall(self):
		""" Méthode pour le fetchall """
		return self.cursor.fetchall()


	def fetchone(self):
		""" Méthode pour le fetchone """
		return self.cursor.fetchone()


	def commit(self):
		""" Méthode pour exécuter le commit """
		self.db.commit()
