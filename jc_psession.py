# différentes importations nécessaires à la création du programme
import streamlit as st 
import pandas as pd
from datetime import date
from numpy_financial import pmt,ipmt,ppmt
from PIL import Image
import datetime
import numpy as np
import matplotlib.pyplot as plt

# établissement du titre 

st.markdown('<p class="font3"> Calculateur hypothécaire</p>', unsafe_allow_html=True)

st.markdown(""" <style>

.font1 {

        font-size:35px ;

        font-family: 'Cooper Black';

        color: #FF9633;

        text-align: center;

        border: 3px solid green;
        }
        
.font2 {

        font-size:40px ;

        font-family: 'Cooper Black';

        color: gold;

        text-align: center;

        border: 3px solid blue;
        }
.font3 {

        font-size:40px ;

        font-family: 'Cooper Black';

        color: #f80504;

        text-align: center;

        border: 4px solid green;
        }

</style> """,

unsafe_allow_html=True)

#téléchargement d'une photo de maison afin qu'elle soit visible dans le programme
image = Image.open("maison_projet.jpg")
st.image(image, caption= " Maison contemporaine ", width=None, use_column_width=None, clamp=False, channels="RGB", output_format="auto")

# établissement sous-titre
st.write("""
Cette application vous permettra de calculer le montant mensuel de votre hypothèque ainsi que le tableau d'amortissement.
""")

# définition de la fonction me permettant de déterminer le montant de paiement hypothécaire

prix_maison = st.sidebar.number_input("Quelle est la valeur de la maison?", step = 5000, value = 300000)

mise_fonds = st.sidebar.number_input("Quelle est votre mise de fonds?", step = 1000, value = 20000)

montant = prix_maison - mise_fonds

annee = st.sidebar.number_input("Combien de temps est votre hypothèque en année ?", step = 1, value = 25)

interet = st.sidebar.number_input("Quel est le taux d'intérêt de votre hypothèque ? ( ex : 5 = 5%) ", step = 0.1, value = 2.5)

nb_p_annee = st.sidebar.selectbox(
    "Combien est-ce qu'il y a de paiements par année ? ( 12 = mensuel , 24 = bi-mensuel , 52 = hebdomadaire )",
    ( 12 , 24, 52))
pmt1 = -pmt((interet/100)/nb_p_annee, annee * nb_p_annee , montant)

# informations
st.write(f' ##### Le montant de votre paiement hypothécaire est : ', ("{0:,.2f}".format(pmt1)) , '$')
st.write(" ##### Voici le tableau d'amortissement de l'hypotheque:")

# date de début qui sera également dans les sidebar
date_debut = st.sidebar.date_input( " quelle est la date de début de vos paiements ? ", value = date(2021, 1, 1))

# montage du tableau d'amortissement
if nb_p_annee == 12:
    rng = pd.date_range(date_debut, periods=annee * nb_p_annee, freq='MS') # pour paiement mensuel
elif nb_p_annee == 24:
    rng = pd.date_range(date_debut, periods=annee * nb_p_annee, freq='SM') # pour paiement bi-mensuel
elif nb_p_annee == 52:
    rng = pd.date_range(date_debut, periods=annee * nb_p_annee, freq='W') # pour paiement hebdomadaire

rng.name = "date de paiement"
df = pd.DataFrame(index=rng, columns=['Paiement', 'Montant principal', 'Intérêt payé', 'Balance'], dtype='float')
df.reset_index(inplace=True)
df.index += 1
df.index.name = "Période"
df['date de paiement'] = pd.to_datetime(df['date de paiement']).dt.date # fonction pour corriger affichage des dates

# définition des montants qui seront présent dans les colonnes
df["Paiement"] = pmt1  # formule est plus haut pour établir le montant du paiement hypothécaire
ppmt1= -ppmt((interet/100)/nb_p_annee , df.index , annee * nb_p_annee, montant)
df["Montant principal"] = ppmt1
ipmt1 = -ipmt((interet/100)/nb_p_annee, df.index , annee * nb_p_annee, montant)
df["Intérêt payé"] = ipmt1
df = df.round(2)

# création de la dernière colonne ( balance restante)
df["Balance"] = 0
df.loc[1, "Balance"] = montant - df.loc[1, "Montant principal"]

for temps in range(2,len(df)+1):
    balance_precedente = df.loc[temps-1, "Balance"]
    principal_paye = df.loc[temps, "Montant principal"]
    
    if balance_precedente == 0:
        df.loc[temps, ["Paiement", "Montant principal", "Intérêt payé", "Balance"]] ==0
        continue
    elif principal_paye <= balance_precedente :
        df.loc[temps, "Balance"] = balance_precedente - principal_paye

# création du tableau sur streamlit
st.dataframe(df)


#création du graphique 1 : paiements
st.write("### Représentation graphiques des éléments du tableau d'amortissement")

st.markdown("""
Ce graphique propose l'évolution du montant payé en principal et en intérêt :
""")
fig1, ax1 = plt.subplots(facecolor = 'skyblue')
#x1 = annee
y1 = ppmt1
y2 = ipmt1
y3 = [pmt1]*len(ppmt1)

ax1.plot(y1, color = 'purple',label = "Partie capital")
ax1.plot(y2, color = 'goldenrod', label = "Partie intérêts")
ax1.plot(y3, color = 'darkolivegreen', linestyle ="--",label = "Paiement périodique total")

# titre et nom des axes ( x,y ) du graphique 
ax1.set_title(' Évolution des paiements ')
ax1.set_xlabel('Périodes', color = 'k')
ax1.set_ylabel('Paiements', color = 'k')
ax1.legend()
ax1.grid(color='lightgrey', linestyle='--', linewidth=0.5)
st.pyplot(fig1)

#création du graphique 2 : amortissement

st.markdown("""
Ce graphique propose l'évolution du solde de l'hypothèque au fil du temps :
""")
fig2, ax2 = plt.subplots(facecolor = 'skyblue')

y4 = df["Balance"]

ax2.bar(list(range(len(y4))), y4, color = 'y')


# titre et nom des axes ( x,y ) du graphique 
ax2.set_title(' Amortissement du montant hypothécaire')
ax2.set_xlabel('Périodes', color = 'k')
ax2.set_ylabel("Solde de l'hypothèque", color = 'k')
ax2.legend()
ax2.grid(color='lightgrey', linestyle='--', linewidth=0.5)
st.pyplot(fig2)

# petit message pour la fin du programme
st.title("Bienvenue dans votre maison!")
