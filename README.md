# Fake News Pipeline

## 📝 A propos

Ce projet analyse un flux continue d'article sur le climat pour y détecter de potentielles infox. 

*Projet de certification AIA : Bloc 4 - Construire, déployer et piloter des solutions d'IA @ [Jedha](https://www.jedha.co/)*

---

## ✨ Fonctionnalités
- Pipeline de données
- Interface web de suivi des contrôles

---

## 🔧 Prérequis
- Python 3.10
- Les dépendances python sont décrites dans le ```requirements.txt```
- Docker

---

## 🛠 Lancement en local

1. Cloner le répertoire :
```bash
git clone https://github.com/Olivier-52/fake-news-pipeline.git
```

2. Se rendre dans le repertoire Airflow (dag) :
```
cd fake-news-pipeline
```
3. **Pour les utilisateurs Linux uniquement** :  
   Il est **nécessaire** de créer un fichier `.env` afin d’éviter les erreurs de permissions sur les dossiers montés (`logs`, `dags`, etc.).  
   Exécutez la commande suivante une fois que vous êtes dans le dossier fake-news-pipeline :
```bash
echo -e "AIRFLOW_UID=$(id -u)" > .env
```
4. Lancer le docker-compose.yaml  :
```
docker-compose up
```
*Après le démarrage de l'application.*

5. Démarrer les DAG :

- Se connecter sur l'interface utilisateur [Airlow](http://localhost:8080/), avec le user : airflow, et mdp : airflow.

- Allez dans : Admin → Variables → "+" (Ajouter une variable)"

- Ajoutez les variables suivantes :

    - **API_ENDPOINT**= URL de l'API de génération des nouveaux articles. Application de génération d'article à classifier [disponible ici](https://huggingface.co/spaces/Olivier-52/Real_Time_Climate_Fake_News).

    - **PREDICT_ENDPOINT**= URL de l'API de prédiction avec le modèle. Application de prédiction [disponible ici](https://huggingface.co/spaces/Olivier-52/Climate_Fake_News_API).

    - **REFERENCE_STORE**= URL de stockage du fichier de référence pour générer les rapports de peformance et de drift du modèle. Une copie de celui-ci est disponible dans [le répertoire data du projet](/data).

- Lancer climate_news_api_dag pour déclencher le pipeline de récupération et de contrôle des articles.

5. Une fois le pipeline démarré, se rendre sur l'interface utilisateur [Streamlit](http://localhost:8501/) pour suivre les transactions.

---
## 🤝 Contributeur

[WissamHouzir](https://github.com/WissamHouzir),
[Thomas-L-debug](https://github.com/Thomas-L-debug),
[Olivier-52](https://github.com/Olivier-52)

---
