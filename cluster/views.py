from django.http import HttpResponse, HttpResponseRedirect 
from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import FileSystemStorage
from .models import tb_staff
from .forms import CreateForm
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sqlalchemy

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

        # Clustering k-means
        from sklearn.cluster import KMeans
        X = df.iloc[:, [1,2,3,4,5,6,7,8,9,10,11,12,13]].values

        kmeans = KMeans(n_clusters = 2, init = 'k-means++', random_state=42)
        y_kmeans = kmeans.fit_predict(X)

        # Visualisasi data
        clusterCount = np.bincount(y_kmeans)
        label_cluster = ["Banyak Terjangkit", "Kurang Terjangkit"]
        
        plt.pie(clusterCount, labels = label_cluster, autopct='%1.0f%%')
        plt.savefig('static/assets/images/output-'+ str(dateInput) +'.jpg')
        chart = plt.show()
        
        return render(request, 'kelola-data.html')
    # jika ada perintah method get
    else:        
        return render(request, 'kelola-data.html')

def MANAGE_USER(request):
    if request.method == 'POST':        
        if 'tambahuser' in request.POST:
            pass
           
    
    
    user = tb_staff.objects.raw('SELECT cluster_tb_staff.id, cluster_tb_staff.username, cluster_tb_akses.nama_akses FROM cluster_tb_staff CROSS JOIN cluster_tb_akses WHERE cluster_tb_staff.id_akses_id = cluster_tb_akses.id_akses')
    context = {'users': user, 'form1':CreateForm()}    
    return render(request, 'kelola-user.html', context)

def DELETE_USER(request, pk):
    user = get_object_or_404(tb_staff, pk=pk)
    user.delete()
    return redirect('KELOLA USER')
