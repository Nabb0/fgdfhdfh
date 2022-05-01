import matplotlib.pyplot as plt
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import contextily
import geopandas as gpd
import pandas as pd
import io
import os
import csv
from flask import Flask, render_template, request, Response, redirect, url_for
app = Flask(__name__)
matplotlib.use('Agg')

# Dichiarazioni dei geodataframe
dati = pd.read_json("/workspace/EasyMilano/static/file/dati.json")

quartieri = gpd.read_file('/workspace/EasyMilano/static/file/ds964_nil_wm-20220405T093028Z-001.zip')

mezzi_superficie = gpd.read_file('/workspace/EasyMilano/static/file/tpl_percorsi.geojson')

uffici_postali = gpd.read_file('/workspace/EasyMilano/static/file/ds555_uffici_postali_milano_final.geojson')

civici = gpd.read_file('/workspace/EasyMilano/static/file/ds634_civici_coordinategeografiche_20220401_final.geojson')
stradario = pd.read_csv('/workspace/EasyMilano/static/file/stradario (2).csv')

comandi_polizialocale = gpd.read_file('/workspace/EasyMilano/static/file/geocoded_comandi-decentrati-polizia-locale__final.geojson')

scuole = pd.read_csv('/workspace/EasyMilano/static/file/CITTA_METROPOLITANA_MILANO_-_Scuole_di_ogni_ordine_e_grado.csv')
metro = gpd.read_file('/workspace/EasyMilano/static/file/tpl_metropercorsi.geojson')

#converto entrambi in int64 dopo che dava errore, uno era string e l'altro int
civici = civici.astype({"CODICE_VIA": int}, errors='raise') 
stradario = stradario.astype({"CODICE_VIA": int}, errors='raise') 

vie_milano = pd.merge(civici, stradario, on='CODICE_VIA', how='inner')

# home e registrazione


@app.route('/', methods=['GET'])
def home():

    return render_template('home.html')

#_______________________________________________________________________



                        #register

                   
# _____________________________________________________________________
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        name = request.form.get("name")
        surname = request.form.get("surname")
        psw = request.form.get("pwd")
        cpsw = request.form.get("cpwd")
        email = request.form.get("email")
        via = request.form.get("via")
        civico = request.form.get('civico')
        df = pd.read_json("./static/file/dati.json")
        if cpsw== psw:
            df= df.append({'name': [name],'surname':[surname],'via':[via],'civico':[civico] ,'email' : [email],'psw':[psw]},ignore_index=True)
            df.to_json("./static/file/dati.json")
            return render_template('login.html', name = name, surname = surname, psw = psw , via = via, df = df, email = email, civico = civico)
        else:
            return 'le password non corrispondono'
    else:
        return render_template('register.html')
#_______________________________________________________________________



                             #login


#_______________________________________________________________________
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        log_email = request.form.get('email')
        log_pwd = request.form.get('pwd')
        df = pd.read_json("./static/file/dati.json")



        for _, r in df.iterrows():
            if log_email != r['email'] and log_pwd != r['pwd']:  
                return '<h1>Errore</h1>'

        return render_template("ok.html")
    else:
        return render_template('login.html')
#_______________________________________________________________________
#quartieri
#_______________________________________________________________________
@app.route('/quartieri', methods=['GET'])
def quartieriFunzione ():
    return render_template('quartieriFunzione.html')




@app.route('/selezione', methods=['GET'])
def selezione():
 global lista_qt,scelta
 lista_qt= quartieri.NIL.to_list() # DEVO PER FORZA TRASFORMARE IN LISTA
 scelta = request.args["radio"]


 if scelta=="1":
    return render_template('scelta.html',quartieri=lista_qt)
 elif scelta=="2":
    return render_template('scelta.html',quartieri=lista_qt)
 elif scelta=="3":
    return render_template('scelta.html',quartieri=lista_qt)
 elif scelta=="4":
  return render_template()

@app.route('/visualizzaqt', methods=['GET'])
def visualizzaqt():
 global quartiere
 nome_quartiere=request.args["quartiere"]
 quartiere=quartieri[quartieri.NIL.str.contains(nome_quartiere)]
 quartiere2=quartieri[quartieri.NIL.str.contains(nome_quartiere)]

 
 if scelta=="3":
    area = quartiere2.geometry.area/10**6
    return render_template('Lunghezzaqt.html',area=area) 
 else:
  return render_template('mappafinaleqt.html') 
 


@app.route('/mappa', methods=['GET'])
def mappa():
 if scelta=="1":
    fig, ax = plt.subplots(figsize = (12,8))
    quartiere.to_crs(epsg=3857).plot(ax=ax, alpha=0.5,edgecolor='k')
    contextily.add_basemap(ax=ax)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')    
 else:
    fig, ax = plt.subplots(figsize = (12,8))
    QtConfinanati=quartieri[quartieri.touches(quartiere.geometry.squeeze())]
    QtConfinanati.to_crs(epsg=3857).plot(ax=ax,facecolor='r')
    quartiere.to_crs(epsg=3857).plot(ax=ax, alpha=0.5,edgecolor='k')
    contextily.add_basemap(ax=ax)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')    
#_______________________________________________________________________
#poste
#_______________________________________________________________________
@app.route('/poste', methods=['GET'])
def posteFunzione():
    return render_template('posteFunzione.html')

@app.route('/selezione2', methods=['GET'])
def selezione2():
 global lista_qt,scelta
 lista_qt= quartieri.NIL.to_list() # DEVO PER FORZA TRASFORMARE IN LISTA
 scelta = request.args["radio"]
 if scelta=="1":
    return render_template()
 elif scelta=="2":
    return render_template()
 elif scelta=="3":
  return render_template("mappafinaleqt.html")
 elif scelta=="4":
  return render_template()

@app.route('/mappaposte', methods=['GET'])
def mappaposte():
#fare il elif di prima
    

    fig, ax = plt.subplots(figsize = (12,8))
    
    uffici_postali.to_crs(epsg=3857).plot(ax=ax,color  = 'r')
    quartieri.to_crs(epsg=3857).plot(ax=ax, alpha= 0.5)
    contextily.add_basemap(ax=ax)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')    


    




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3245, debug=True)
