from django.http import HttpResponse, HttpResponseRedirect 
from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import FileSystemStorage
from .models import tb_staff
from .models import tb_akses
from .models import tb_hasil_cluster
from .models import tb_penyakit
from .models import tb_data
from django.contrib import messages
from random import choice
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sqlalchemy

# Halaman Utama
def BASE(request):
    from sklearn.cluster import KMeans
    engine = sqlalchemy.create_engine('mysql+pymysql://root:@localhost:3306/db_marunggi')
    # select data dari database
    query="""SELECT nama_penyakit, SUM(total) AS Total, SUM(r1), SUM(r2), SUM(r3), SUM(r4), SUM(r5), SUM(r6), SUM(r7), SUM(r8), SUM(r9), SUM(r10), SUM(r11), SUM(r12) FROM cluster_tb_data GROUP BY nama_penyakit"""
    df = pd.read_sql_query(query,engine)
    X = df.iloc[:, [1,2,3,4,5,6,7,8,9,10,11,12,13]].values

    # Clustering k-means
    kmeans = KMeans(n_clusters = 2, init = 'k-means++', n_init=5, random_state=0)
    y_kmeans = kmeans.fit_predict(X)

    # Visualisasi data
    clusterCount = np.bincount(y_kmeans)
    label_cluster = ["Banyak Terjangkit", "Kurang Terjangkit"]    
    fig = go.Figure(data=([go.Pie(labels=label_cluster, values=clusterCount, pull=[0.2, 0])]))
    fig.update_layout(legend=dict(
        xanchor="left",
        x=0.01
    ),
        height=600
    )

    pie = fig.to_html()

    data = tb_data.objects.values_list('nama_penyakit', flat=True)
    random = choice(data)
    dataframe = pd.read_sql_query("""SELECT nama_penyakit, total, tanggal_input FROM cluster_tb_data WHERE tanggal_input <= CURRENT_DATE() AND nama_penyakit = '"""+random+"""'""",engine)
    dataframe = dataframe.sort_values(by="tanggal_input")
    dataframe = dataframe.drop(columns="nama_penyakit")
    count = len(dataframe)
    dataframe['hasil_prediksi'] = dataframe['total'].rolling(window=count).mean()
    dataframe = dataframe.iloc[:, [1, 0, 2]]              

    figure = px.line(dataframe,
            x="tanggal_input",
            y=['total','hasil_prediksi'],   
            height=500,
            width=1000,  
            title="Prediksi "+random                                
    )
    figure.update_traces(mode='lines+markers')
    figure.update_layout(
        legend_title_text='',
        xaxis=dict(
            title=dict(
                text='Tanggal'
            )
        ),
        yaxis=dict(
            title=dict(
                text='Banyak Kasus'
            )
        ),
    )
    line = figure.to_html()

    context = {'pie':pie,'line':line,'random':random}
    return render(request, 'home.html',context)
# Halaman kelola data
def DATA(request):
    # jika ada perintah method post
    if request.method == 'POST':
        uploaded_files = request.FILES['file']
        dateInput = request.POST['tanggal_input']
        if not dateInput:
            messages.add_message(request, messages.WARNING, 'Per. Tanggal input tidak boleh kosong')
            return render(request, 'kelola-data.html')        
        else:
            fs = FileSystemStorage()
            fs.save(uploaded_files.name, uploaded_files)
            # simpan file ke dalam local server
            file_name = uploaded_files.name 
            # proses data cleaning
            pd.set_option("display.max_rows", None)
            pd.set_option("display.max_columns", None)    
            df = pd.read_csv(r"D:/Yahya/xampp/htdocs/djangotest/data/" + file_name, delimiter=";")
            df['JENIS PENYAKIT'] = df['JENIS PENYAKIT'].str.lower()
            df['JENIS PENYAKIT'] = df['JENIS PENYAKIT'].str.title()        
            df = df.fillna(0)
            data_sebelum = df.to_html(classes="table table-stripped")
            df = df.drop_duplicates()
            df = df.drop(columns = "NO")
            df['tanggal_input'] = dateInput

            for x in df.index:
                if df.loc[x, "TOTAL"] == 0:
                    df.drop(x, inplace=True)
            df.rename(columns = {'JENIS PENYAKIT': 'nama_penyakit',"0-7 hr":'r1','8-28 hr':'r2','1 bl-1 th':'r3','1-4 th':'r4','5-9 th':'r5','10-14 th':'r6','15-19 th':'r7',' 20-44 th':'r8','45-54 th':'r9','55-59 th':'r10','60-69 th':'r11','> 70 th':'r12'}, inplace=True)
            df = df.reset_index(drop=True)
            data_sesudah = df.to_html(classes="table table-stripped")
            # simpan hasil data cleaning ke database
            engine = sqlalchemy.create_engine('mysql+pymysql://root:@localhost:3306/db_marunggi')
            df.to_sql(
                'cluster_tb_data', con=engine, index=False, if_exists='append'
            )
            messages.add_message(request, messages.SUCCESS, 'Data berhasil diinputkan')

            context = {'data1':data_sebelum,'data2':data_sesudah}
            return render(request, 'kelola-data.html', context)
    # jika ada perintah method get
    else:        
        return render(request, 'kelola-data.html')

def MANAGE_USER(request, id=0):
    valid_session = None        
    if request.method == 'POST':
        if 'tambahuser' in request.POST:
            akses = request.POST['id_akses']
            username = request.POST['username']
            email = request.POST['email']
            pass1 = request.POST['password1']
            pass2 = request.POST['password2']
            if akses == "0":                        
                messages.add_message(request, messages.WARNING,"pilih akses sistem")                
            elif tb_staff.objects.filter(username=username, email=email).exists():                
                messages.add_message(request, messages.WARNING,"username atau email telah terdaftar")
            elif pass1 != pass2:                        
                messages.add_message(request, messages.WARNING,"konfirmasi password tidak cocok")
            else:
                tb_staff.objects.create(email=email,username=username,id_akses_id=akses,password=pass1)
                messages.add_message(request, messages.SUCCESS,"Input data user berhasil")

        elif 'updateuser' in request.POST:
            id_akses = request.POST['id_akses']
            email = request.POST['email']
            user_lama = tb_staff.objects.filter(pk=id)
            if id_akses == "0":                        
                messages.add_message(request, messages.WARNING,"pilih akses sistem")
            for a in user_lama:                
                if a.email == email:
                    tb_staff.objects.filter(pk=id).update(email=email,id_akses_id=id_akses)
                elif tb_staff.objects.filter(email=email).exists():
                    messages.add_message(request, messages.WARNING,"email telah terdaftar")                            
        elif 'search' in request.POST:
            search = request.POST['keyword']
            search_query = f"%{search}%"      
            user = tb_staff.objects.raw("SELECT cluster_tb_staff.id, cluster_tb_staff.username, cluster_tb_akses.nama_akses FROM cluster_tb_akses CROSS JOIN cluster_tb_staff WHERE cluster_tb_staff.id_akses_id = cluster_tb_akses.id_akses AND cluster_tb_staff.username LIKE %s", [search_query])
            akses = tb_akses.objects.raw("SELECT * from cluster_tb_akses WHERE id_akses NOT LIKE '23'")
            context = {'users': user, 'akses': akses}    
            return render(request, 'kelola-user.html', context)
        
    request.session.modified = True    
    
    akses = tb_akses.objects.raw("SELECT * from cluster_tb_akses WHERE id_akses NOT LIKE '23'")
    user = tb_staff.objects.raw("SELECT cluster_tb_staff.id, cluster_tb_staff.username, cluster_tb_akses.nama_akses FROM cluster_tb_staff CROSS JOIN cluster_tb_akses ON cluster_tb_staff.id_akses_id = cluster_tb_akses.id_akses WHERE cluster_tb_staff.id_akses_id NOT LIKE 23")
    context = {'users': user, 'akses': akses, 'valid_session':valid_session}    
    return render(request, 'kelola-user.html', context)

def DELETE_USER(request, pk):
    user = get_object_or_404(tb_staff,pk=pk)
    user.delete()
    return render(request, 'kelola-user.html')

def HASIL_CLUSTER(request):
    from sklearn.cluster import KMeans
    engine = sqlalchemy.create_engine('mysql+pymysql://root:@localhost:3306/db_marunggi')
    if request.method == 'POST':
        date = request.POST['tanggal']
        if not date:
            messages.add_message(request, messages.WARNING,"Per. Tanggal input tidak boleh kosong")                    
        else:
            query="""SELECT nama_penyakit, SUM(total) AS Total, SUM(r1), SUM(r2), SUM(r3), SUM(r4), SUM(r5), SUM(r6), SUM(r7), SUM(r8), SUM(r9), SUM(r10), SUM(r11), SUM(r12), tanggal_input FROM cluster_tb_data WHERE tanggal_input <= '"""+ date +"""' GROUP BY nama_penyakit"""
            df = pd.read_sql_query(query,engine)

            # Clustering k-means
            X = df.iloc[:, [1,2,3,4,5,6,7,8,9,10,11,12,13]].values
            kmeans = KMeans(n_clusters = 2, init = 'k-means++', n_init=5, random_state=0)
            y_kmeans = kmeans.fit_predict(X)
            # Visualisasi data
            import plotly.graph_objects as go
            clusterCount = np.bincount(y_kmeans)
            label_cluster = ["Kurang Terjangkit", "Banyak Terjangkit"]
            judul = 'Clustering Data Penyakit Per. '+date    
            fig = go.Figure(data=([go.Pie(labels=label_cluster, title=judul, values=clusterCount, pull=[0.2, 0])]))
            fig.update_layout(
                height=600
            )
            chart = fig.to_html()

            mapping = {0:'Kurang Terjangkit', 1:'Banyak Terjangkit'}
            y_kmeans = [mapping[i] for i in y_kmeans]

            df['cluster'] = y_kmeans
            df = df.drop(columns = ["Total", "SUM(r1)", "SUM(r2)", "SUM(r3)", "SUM(r4)", "SUM(r5)", "SUM(r6)", "SUM(r7)", "SUM(r8)", "SUM(r9)", "SUM(r10)", "SUM(r11)", "SUM(r12)"])
            df.columns = ['nama_penyakit','tanggal','hasil_klasifikasi']

            df.to_sql(
                'cluster_tb_hasil_cluster', con=engine, index=True, index_label='id', if_exists='replace'
            )

            banyak = tb_hasil_cluster.objects.filter(hasil_klasifikasi="Banyak Terjangkit",tanggal__lte=date)
            kurang = tb_hasil_cluster.objects.filter(hasil_klasifikasi="Kurang Terjangkit",tanggal__lte=date) 

            context = {'banyak':banyak,'kurang':kurang,'chart':chart}
            return render(request, 'hasil-cluster.html', context)
        
    # select data dari database
    query="""SELECT nama_penyakit, SUM(total) AS Total, SUM(r1), SUM(r2), SUM(r3), SUM(r4), SUM(r5), SUM(r6), SUM(r7), SUM(r8), SUM(r9), SUM(r10), SUM(r11), SUM(r12) FROM cluster_tb_data GROUP BY nama_penyakit"""
    df = pd.read_sql_query(query,engine)
    X = df.iloc[:, [1,2,3,4,5,6,7,8,9,10,11,12,13]].values

    # Clustering k-means
    kmeans = KMeans(n_clusters = 2, init = 'k-means++', n_init=5, random_state=0)
    y_kmeans = kmeans.fit_predict(X)

    # Visualisasi data
    import plotly.graph_objects as go
    clusterCount = np.bincount(y_kmeans)
    label_cluster = ["Kurang Terjangkit", "Banyak Terjangkit"]    
    fig = go.Figure(data=([go.Pie(labels=label_cluster, title='Clustering Data Penyakit',values=clusterCount, pull=[0.2, 0])]))
    fig.update_layout(
        height=600
    )

    chart = fig.to_html()

    banyak = tb_hasil_cluster.objects.filter(hasil_klasifikasi="Banyak Terjangkit")
    kurang = tb_hasil_cluster.objects.filter(hasil_klasifikasi="Kurang Terjangkit") 
        
    context = {'banyak':banyak,'kurang':kurang,'chart':chart}
    return render(request, 'hasil-cluster.html', context)

def HASIL_PREDIKSI(request):
    list_penyakit = tb_penyakit.objects.all()
    engine = sqlalchemy.create_engine('mysql+pymysql://root:@localhost:3306/db_marunggi')
    if request.method == 'POST':        
        date = request.POST.get('tanggal')
        penyakit = request.POST.get('penyakit')
        if not date:
            messages.add_message(request, messages.WARNING,"Per. Tanggal input tidak boleh kosong", extra_tags="date")                    
        elif penyakit == "0":
            messages.add_message(request, messages.WARNING,"Pilih penyakit yang ingin ada cek", extra_tags="penyakit")                    
        else:
            df = pd.read_sql_query("""SELECT nama_penyakit, total, tanggal_input FROM cluster_tb_data WHERE tanggal_input <= '"""+ date +"""' AND nama_penyakit = '"""+penyakit+"""'""",engine)
            df = df.sort_values(by="tanggal_input")
            df = df.drop(columns="nama_penyakit")
            count = len(df)
            df['hasil_prediksi'] = df['total'].rolling(window=count).mean()
            df = df.iloc[:, [1, 0, 2]]              

            fig = px.line(df,
                x="tanggal_input",
                y=['total','hasil_prediksi'],
                title='Prediksi '+penyakit,                         
            )
            fig.update_traces(mode='lines+markers')
            fig.update_layout(
                legend_title_text='',
                xaxis=dict(
                    title=dict(
                        text='Tanggal'
                    )
                ),
                yaxis=dict(
                    title=dict(
                        text='Banyak Kasus'
                    )
                ),
            )
            chart = fig.to_html()
            
            context = {'list':list_penyakit,'chart':chart}
            return render(request, 'hasil-prediksi.html', context)
        
    context = {'list':list_penyakit}
    return render(request, 'hasil-prediksi.html',context)

