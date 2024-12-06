from django.http import HttpResponse, HttpResponseRedirect 
from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import FileSystemStorage
from .models import tb_staff
from .models import tb_akses
from .models import tb_hasil_cluster
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sqlalchemy

# Halaman Utama
def BASE(request):
    return render(request, 'home.html')
# Halaman kelola data
def DATA(request):
    # jika ada perintah method post
    if request.method == 'POST':
        uploaded_files = request.FILES['file']
        dateInput = request.POST['tanggal_input']
        fs = FileSystemStorage()
        # simpan file ke dalam local server
        fs.save(uploaded_files.name, uploaded_files)
        file_name = uploaded_files.name 
        # proses data cleaning
        pd.set_option("display.max_rows", None)
        pd.set_option("display.max_columns", None)    
        df = pd.read_csv(r"D:/Yahya/xampp/htdocs/djangotest/data/" + file_name, delimiter=";")
        df = df.drop_duplicates()
        df = df.drop(columns = "NO")
        df = df.fillna(0)
        df['tanggal_input'] = dateInput

        for x in df.index:
            if df.loc[x, "TOTAL"] == 0:
                df.drop(x, inplace=True)
        df.rename(columns = {'JENIS PENYAKIT': 'nama_penyakit',"0-7 hr":'r1','8-28 hr':'r2','1 bl-1 th':'r3','1-4 th':'r4','5-9 th':'r5','10-14 th':'r6','15-19 th':'r7',' 20-44 th':'r8','45-54 th':'r9','55-59 th':'r10','60-69 th':'r11','> 70 th':'r12'}, inplace=True)
        df = df.reset_index(drop=True)
        # simpan hasil data cleaning ke database
        engine = sqlalchemy.create_engine('mysql+pymysql://root:@localhost:3306/db_marunggi')
        df.to_sql(
            'cluster_tb_data', con=engine, index=False, if_exists='append'
        )

        
        
        return render(request, 'kelola-data.html')
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
            if tb_staff.objects.filter(username=username, email=email).exists():                
                    request.session['invalid'] = 'username atau email sudah terdaftar'
                    valid_session = request.session['invalid']
            # elif pass1 != pass2:
            #     messages.error(request, "konfirmasi password tidak cocok")
            #     test = get_messages(request)
            #     return render(request, 'kelola-user.html', context, test)

            tb_staff.objects.create(username=username,password=pass1,email=email,id_akses_id=akses)            
        elif 'updateuser' in request.POST:
            id_akses = request.POST['id_akses']
            email = request.POST['email']
            tb_staff.objects.filter(pk=id).update(email=email,id_akses_id=id_akses)
        elif 'search' in request.POST:
            search = request.POST['keyword']
            search_query = f"%{search}%"      
            user = tb_staff.objects.raw('''SELECT cluster_tb_staff.id, cluster_tb_staff.username, cluster_tb_akses.nama_akses FROM cluster_tb_akses CROSS JOIN cluster_tb_staff WHERE cluster_tb_staff.id_akses_id = cluster_tb_akses.id_akses AND cluster_tb_staff.username LIKE %s''', [search_query])
            akses = tb_akses.objects.raw('SELECT * from cluster_tb_akses WHERE id_akses NOT LIKE "23"')
            context = {'users': user, 'akses': akses}    
            return render(request, 'kelola-user.html', context)
        
    request.session.modified = True    
    
    akses = tb_akses.objects.raw('SELECT * from cluster_tb_akses WHERE id_akses NOT LIKE "23"')
    user = tb_staff.objects.raw('SELECT cluster_tb_staff.id, cluster_tb_staff.username, cluster_tb_akses.nama_akses FROM cluster_tb_staff CROSS JOIN cluster_tb_akses ON cluster_tb_staff.id_akses_id = cluster_tb_akses.id_akses WHERE cluster_tb_staff.id_akses_id NOT LIKE 23')
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
        query='''SELECT nama_penyakit, SUM(total) AS Total, SUM(r1), SUM(r2), SUM(r3), SUM(r4), SUM(r5), SUM(r6), SUM(r7), SUM(r8), SUM(r9), SUM(r10), SUM(r11), SUM(r12), tanggal_input FROM cluster_tb_data WHERE tanggal_input <= ' '''+ date +''' ' GROUP BY nama_penyakit'''
        df = pd.read_sql_query(query,engine)
        X = df.iloc[:, [1,2,3,4,5,6,7,8,9,10,11,12,13]].values

        # Clustering k-means
        kmeans = KMeans(n_clusters = 2, init = 'k-means++', random_state=1234)
        y_kmeans = kmeans.fit_predict(X)
        # Visualisasi data
        import plotly.graph_objects as go
        clusterCount = np.bincount(y_kmeans)
        label_cluster = ["Banyak Terjangkit", "Kurang Terjangkit"]
        judul = 'Clustering Data Penyakit Per. '+date    
        fig = go.Figure(data=([go.Pie(labels=label_cluster, title=judul, values=clusterCount, pull=[0.2, 0])]))

        chart = fig.to_html()

        mapping = {0:'Banyak Terjangkit', 1:'Kurang Terjangkit'}
        y_kmeans = [mapping[i] for i in y_kmeans]

        df['cluster'] = y_kmeans
        df = df.drop(columns = ["Total", "SUM(r1)", "SUM(r2)", "SUM(r3)", "SUM(r4)", "SUM(r5)", "SUM(r6)", "SUM(r7)", "SUM(r8)", "SUM(r9)", "SUM(r10)", "SUM(r11)", "SUM(r12)"])
        df.columns = ['nama_penyakit','tanggal','hasil_klasifikasi']

        df.to_sql(
            'cluster_tb_hasil_cluster', con=engine, index=False, if_exists='append'
        )

        context = {'chart':chart,'kmeans':y_kmeans}
        return render(request, 'hasil-cluster.html', context)
        
    # select data dari database
    query='''SELECT nama_penyakit, SUM(total) AS Total, SUM(r1), SUM(r2), SUM(r3), SUM(r4), SUM(r5), SUM(r6), SUM(r7), SUM(r8), SUM(r9), SUM(r10), SUM(r11), SUM(r12) FROM cluster_tb_data GROUP BY nama_penyakit'''
    df = pd.read_sql_query(query,engine)
    X = df.iloc[:, [1,2,3,4,5,6,7,8,9,10,11,12,13]].values

    # Clustering k-means
    kmeans = KMeans(n_clusters = 2, init = 'k-means++', random_state=1234)
    y_kmeans = kmeans.fit_predict(X)

    # Visualisasi data
    import plotly.graph_objects as go
    clusterCount = np.bincount(y_kmeans)
    label_cluster = ["Banyak Terjangkit", "Kurang Terjangkit"]    
    fig = go.Figure(data=([go.Pie(labels=label_cluster, title='Clustering Data Penyakit',values=clusterCount, pull=[0.2, 0])]))

    chart = fig.to_html()

    cluster = tb_hasil_cluster.objects.all()
    context = {'chart':chart,'cluster':cluster}
    return render(request, 'hasil-cluster.html', context)

