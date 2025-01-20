from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from .models import tb_staff
from .models import tb_akses
from .models import tb_hasil_cluster
from .models import tb_penyakit
from .models import tb_data
from .forms import LoginForm
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from random import choice
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sqlalchemy

def insert_break_after_40(text):
    if len(text) <= 40:
        return text    
    else:
        space_index = text.find(' ', 40)
        if space_index == -1:
            return text
        return text[:space_index] + '<br>' + text[space_index+1:]
 
def LOGIN(request):
    form = LoginForm(request.POST or None)
    msg = None
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            from django.http import Http404
            staff = tb_staff.objects.filter(username=username)
            try:
                tb_staff.objects.get(username=username)
                for s in staff:
                    if staff is not None and s.id_akses_id == 21:
                        checkpw = check_password(password,s.password)
                        if checkpw:
                            request.session['username'] = s.username
                            request.session['email'] = s.email
                            request.session['akses'] = s.id_akses_id
                            return redirect("dokteker")
                        else:
                            msg = 'Password salah'
                    elif staff is not None and s.id_akses_id == 22:                            
                        checkpw = check_password(password,s.password)
                        if checkpw:
                            request.session['username'] = s.username
                            request.session['email'] = s.email
                            request.session['akses'] = s.id_akses_id
                            return redirect("administrasi")
                        else:
                            msg = 'Password salah'
                    elif staff is not None and s.id_akses_id == 23:  
                        checkpw = check_password(password,s.password)
                        if checkpw:
                            request.session['username'] = s.username
                            request.session['email'] = s.email                          
                            request.session['akses'] = s.id_akses_id
                            return redirect("/")
                        else:
                            msg = 'Password salah'
            except tb_staff.DoesNotExist:
                raise Http404("Username tidak terdaftar") 
                
        else:
            msg = 'error validasi'        
    
    return render(request, 'login.html', {'form':form, 'msg':msg})

def LOGOUT(request):
    if request.session:
        request.session.flush()
        messages.add_message(request, messages.SUCCESS, "Anda telah berhasil logout")
        return redirect('login')    

# Halaman Utama
def HOME(request):
    usersession = request.session.get('username')
    userakses = request.session.get('akses')
    #Autentikasi user    
    if usersession is None:
        messages.add_message(request, messages.WARNING, "Login terlebih dahulu")
        return redirect('login')
    elif userakses != 23:
        messages.add_message(request, messages.WARNING, "Akses gagal")
        return redirect('login')

    from sklearn.cluster import KMeans
    engine = sqlalchemy.create_engine('mysql+pymysql://root:@localhost:3306/db_marunggi')
    # select data dari database
    query="""SELECT nama_penyakit, SUM(total) AS Total, SUM(r1), SUM(r2), SUM(r3), SUM(r4), SUM(r5), SUM(r6), SUM(r7), SUM(r8), SUM(r9), SUM(r10), SUM(r11), SUM(r12) FROM cluster_tb_data GROUP BY nama_penyakit"""
    df = pd.read_sql_query(query,engine)
    X = df.iloc[:, [1,2,3,4,5,6,7,8,9,10,11,12,13]].values

    # Clustering k-means
    kmeans = KMeans(n_clusters = 2, init = 'k-means++', n_init=5, random_state=0)
    y_kmeans = kmeans.fit_predict(X)

    # Visualisasi data pie chart
    clusterCount = np.bincount(y_kmeans)
    label_cluster = ["Sedikit Terjangkit", "Banyak Terjangkit"]    
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
    dataframe['hasil_prediksi'] = dataframe['total'].expanding().mean()
    dataframe = dataframe.iloc[:, [1, 0, 2]]              

    # Visualisasi data line chart
    figure = px.line(dataframe,   
            x="tanggal_input",
            y=['total','hasil_prediksi'],   
            height=600, 
            width=970,           
            title="<b>Prediksi "+random +"</b>"                               
    )
    figure.update_traces(mode='lines+markers')
    newnames = {'total':insert_break_after_40(random), 'hasil_prediksi': 'Hasil prediksi'}
    figure.for_each_trace(lambda t: t.update(name = newnames[t.name],
                                        legendgroup = newnames[t.name],
                                        hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])))
    figure.update_layout(
        legend_title_text='',
        title={        
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
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
    line = figure.to_html(div_id="d-block")

    
    context = {'pie':pie,'line':line,'random':random,'session':usersession}
    return render(request, 'admin/home.html', context)

# Halaman kelola data
def DATA(request):
    usersession = request.session.get('username')
    userakses = request.session.get('akses')
    engine = sqlalchemy.create_engine('mysql+pymysql://root:@localhost:3306/db_marunggi')
    if usersession is None:
        messages.add_message(request, messages.WARNING, "Login terlebih dahulu")
        return redirect('login')
    elif userakses != 23:
        messages.add_message(request, messages.WARNING, "Akses gagal")
        return redirect('login')

    # jika ada perintah method post
    if request.method == 'POST':
        if 'importSubmit' in request.POST:
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
                df = pd.read_csv(r"D:/Yahya/xampp/htdocs/django/data/" + file_name, delimiter=";")
                df['JENIS PENYAKIT'] = df['JENIS PENYAKIT'].str.lower()
                df['JENIS PENYAKIT'] = df['JENIS PENYAKIT'].str.title()
                df = df.fillna(0)
                df = df.convert_dtypes()
                data_sebelum = df.to_html(classes="table table-stripped")
                df = df.drop_duplicates()
                df = df.drop(columns = "NO")
                df['tanggal_input'] = dateInput

                for x in df.index:
                    if df.loc[x, "TOTAL"] == 0:
                        df.drop(x, inplace=True)
                df = df.reset_index(drop=True)
                data_sesudah = df.to_html(classes="table table-stripped")
                df.rename(columns = {'JENIS PENYAKIT':'nama_penyakit',"0-7 hr":'r1','8-28 hr':'r2','1 bl-1 th':'r3','1-4 th':'r4','5-9 th':'r5','10-14 th':'r6','15-19 th':'r7',' 20-44 th':'r8','45-54 th':'r9','55-59 th':'r10','60-69 th':'r11','> 70 th':'r12'}, inplace=True)
                # simpan hasil data cleaning ke database
                df.to_sql(
                    'cluster_tb_data', con=engine, index=False, if_exists='append'
                )
                messages.add_message(request, messages.SUCCESS, 'Data berhasil diinputkan')

                context = {'data1':data_sebelum,'data2':data_sesudah, 'session':usersession}
                return render(request, 'admin/kelola-data.html', context)
        if 'cekSubmit' in request.POST:
            bulanInput = request.POST['bulan_input']  
            if not bulanInput:
                messages.add_message(request, messages.WARNING, 'Pilih bulan data yang ingin dicek')
                return render(request, 'kelola-data.html')        
            else:
                query = """SELECT nama_penyakit,r1,r2,r3,r4,r5,r6,r7,r8,r9,r10,r11,r12,total,tanggal_input FROM cluster_tb_data WHERE tanggal_input BETWEEN '"""+bulanInput+"""-01' AND '"""+bulanInput+"""-31'"""
                df = pd.read_sql_query(query,engine)
                df.rename(columns = {'nama_penyakit':'JENIS PENYAKIT','r1':"0-7 hr",'r2':'8-28 hr','r3':'1 bl-1 th','r4':'1-4 th','r5':'5-9 th','r6':'10-14 th','r7':'15-19 th','r8':' 20-44 th','r9':'45-54 th','r10':'55-59 th','r11':'60-69 th','r12':'> 70 th'}, inplace=True)
                data_cek = df.to_html(classes="table table-stripped")
                context = {'cek':data_cek, 'session':usersession}
                return render(request, 'admin/kelola-data.html', context)
    # jika ada perintah method get
    else:        
        return render(request, 'admin/kelola-data.html', {'session':usersession})

def MANAGE_USER(request, id=0):
    usersession = request.session.get('username')
    userakses = request.session.get('akses')
    if usersession is None:
        messages.add_message(request, messages.WARNING, "Login terlebih dahulu")
        return redirect('login')
    elif userakses != 23:
        messages.add_message(request, messages.WARNING, "Akses gagal")
        return redirect('login')
    
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
                passinput = make_password(pass1,salt=None)
                tb_staff.objects.create(email=email,username=username,id_akses_id=akses,password=passinput)
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
            context = {'users': user, 'akses': akses, 'session':usersession}    
            return render(request, 'admin/kelola-user.html', context)
    
    akses = tb_akses.objects.all()
    user = tb_staff.objects.raw("SELECT cluster_tb_staff.id, cluster_tb_staff.username, cluster_tb_akses.nama_akses FROM cluster_tb_staff CROSS JOIN cluster_tb_akses ON cluster_tb_staff.id_akses_id = cluster_tb_akses.id_akses WHERE cluster_tb_staff.id_akses_id NOT LIKE 23")
    context = {'users': user, 'akses': akses, 'session':usersession}    
    return render(request, 'admin/kelola-user.html', context)

def DELETE_USER(request, pk):
    user = get_object_or_404(tb_staff,pk=pk)
    user.delete()
    return redirect('kelola-user', id=0)

def HASIL_CLUSTER(request):
    usersession = request.session.get('username')
    userakses = request.session.get('akses')
    if usersession is None:
        messages.add_message(request, messages.WARNING, "Login terlebih dahulu")
        return redirect('login')
    elif userakses != 23:
        messages.add_message(request, messages.WARNING, "Akses gagal")
        return redirect('login')

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
            clusterCount = np.bincount(y_kmeans)
            label_cluster = ["Sedikit Terjangkit", "Banyak Terjangkit"]
            judul = 'Clustering Data Penyakit Per. '+date    
            fig = go.Figure(data=([go.Pie(labels=label_cluster, title=judul, values=clusterCount, pull=[0.2, 0])]))
            fig.update_layout(
                height=600
            )
            chart = fig.to_html()

            mapping = {0:'Sedikit Terjangkit', 1:'Banyak Terjangkit'}
            y_kmeans = [mapping[i] for i in y_kmeans]

            df['cluster'] = y_kmeans
            df = df.drop(columns = ["Total", "SUM(r1)", "SUM(r2)", "SUM(r3)", "SUM(r4)", "SUM(r5)", "SUM(r6)", "SUM(r7)", "SUM(r8)", "SUM(r9)", "SUM(r10)", "SUM(r11)", "SUM(r12)"])
            df.columns = ['nama_penyakit','tanggal','hasil_klasifikasi']

            df.to_sql(
                'cluster_tb_hasil_cluster', con=engine, index=True, index_label='id', if_exists='replace'
            )

            banyak_date = tb_hasil_cluster.objects.filter(hasil_klasifikasi="Banyak Terjangkit",tanggal__lte=date)
            kurang_date = tb_hasil_cluster.objects.filter(hasil_klasifikasi="Sedikit Terjangkit",tanggal__lte=date) 

            context = {'banyak':banyak_date,'kurang':kurang_date,'chart':chart, 'session':usersession}
            return render(request, 'admin/hasil-cluster.html', context)
        
    # select data dari database
    else:
        query="""SELECT nama_penyakit, SUM(total) AS Total, SUM(r1), SUM(r2), SUM(r3), SUM(r4), SUM(r5), SUM(r6), SUM(r7), SUM(r8), SUM(r9), SUM(r10), SUM(r11), SUM(r12) FROM cluster_tb_data GROUP BY nama_penyakit"""
        df = pd.read_sql_query(query,engine)
        X = df.iloc[:, [1,2,3,4,5,6,7,8,9,10,11,12,13]].values

        # Clustering k-means
        kmeans = KMeans(n_clusters = 2, init = 'k-means++', n_init=5, random_state=0)
        y_kmeans = kmeans.fit_predict(X)

        # Visualisasi data
        clusterCount = np.bincount(y_kmeans)
        label_cluster = ["Sedikit Terjangkit", "Banyak Terjangkit"]    
        fig = go.Figure(data=([go.Pie(labels=label_cluster, title='Clustering Data Penyakit',values=clusterCount, pull=[0.2, 0])]))
        fig.update_layout(
            height=600
        )

        chart = fig.to_html()

        banyak = tb_hasil_cluster.objects.filter(hasil_klasifikasi="Banyak Terjangkit")
        kurang = tb_hasil_cluster.objects.filter(hasil_klasifikasi="Sedikit Terjangkit") 
            
        context = {'banyak':banyak,'kurang':kurang,'chart':chart, 'session':usersession}
        return render(request, 'admin/hasil-cluster.html', context)

def HASIL_PREDIKSI(request):
    usersession = request.session.get('username')
    userakses = request.session.get('akses')
    if usersession is None:
        messages.add_message(request, messages.WARNING, "Login terlebih dahulu")
        return redirect('login')
    elif userakses != 23:
        messages.add_message(request, messages.WARNING, "Akses gagal")
        return redirect('login')

    list_penyakit = tb_data.objects.raw("SELECT id_data, nama_penyakit FROM cluster_tb_data GROUP BY nama_penyakit")
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
            df['hasil_prediksi'] = df['total'].expanding().mean()
            df = df.iloc[:, [1, 0, 2]]              

            fig = px.line(df,
                x="tanggal_input",
                y=['total','hasil_prediksi'],
                title='<b>Prediksi '+penyakit+"</b>",                         
            )
            fig.update_traces(mode='lines+markers')
            newnames = {'total':insert_break_after_40(penyakit), 'hasil_prediksi': 'Hasil prediksi'}
            fig.for_each_trace(lambda t: t.update(name = newnames[t.name],
                                                legendgroup = newnames[t.name],
                                                hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])))
            fig.update_layout(
                legend_title_text='',
                title=dict(font=dict(size=12)),
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

            df['nama_penyakit'] = penyakit 
            df = df.drop(columns="total")
            df = df.iloc[:, [2,0,1]]
            df.to_sql(
                'cluster_tb_hasil_prediksi', engine, index=False, index_label='id', if_exists='append'
            )
            
            context = {'list':list_penyakit,'chart':chart, 'session':usersession}
            return render(request, 'admin/hasil-prediksi.html', context)
        
    context = {'list':list_penyakit, 'session':usersession}
    return render(request, 'admin/hasil-prediksi.html',context)

def DOKTER_APOTEKER(request):
    usersession = request.session.get('username')
    userakses = request.session.get('akses')
    if usersession is None:
        messages.add_message(request, messages.WARNING, "Login terlebih dahulu")
        return redirect('login')
    elif userakses != 21:
        messages.add_message(request, messages.WARNING, "Akses gagal")
        return redirect('login')

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
    label_cluster = ["Sedikit Terjangkit", "Banyak Terjangkit"]     
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
    dataframe['hasil_prediksi'] = dataframe['total'].expanding().mean()
    dataframe = dataframe.iloc[:, [1, 0, 2]]              

    figure = px.line(dataframe,
            x="tanggal_input",
            y=['total','hasil_prediksi'],   
            height=500,
            width=1000,  
            title="<b>Prediksi "+random +"</b>"                               
    )
    figure.update_traces(mode='lines+markers')
    newnames = {'total':random, 'hasil_prediksi': 'Hasil prediksi'}
    figure.for_each_trace(lambda t: t.update(name = newnames[t.name],
                                        legendgroup = newnames[t.name],
                                        hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])))
    figure.update_layout(
        legend_title_text='',
        title={        
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
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

    context = {'pie':pie,'line':line,'random':random, 'session':usersession}
    return render(request, 'dokteker/home.html', context)

def DA_HASIL_CLUSTER(request):
    usersession = request.session.get('username')
    userakses = request.session.get('akses')
    if usersession is None:
        messages.add_message(request, messages.WARNING, "Login terlebih dahulu")
        return redirect('login')
    elif userakses != 21:
        messages.add_message(request, messages.WARNING, "Akses gagal")
        return redirect('login')

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
            clusterCount = np.bincount(y_kmeans)
            label_cluster = ["Sedikit Terjangkit", "Banyak Terjangkit"]
            judul = 'Clustering Data Penyakit Per. '+date    
            fig = go.Figure(data=([go.Pie(labels=label_cluster, title=judul, values=clusterCount, pull=[0.2, 0])]))
            fig.update_layout(
                height=600
            )
            chart = fig.to_html()

            mapping = {0:'Sedikit Terjangkit', 1:'Banyak Terjangkit'}
            y_kmeans = [mapping[i] for i in y_kmeans]

            df['cluster'] = y_kmeans
            df = df.drop(columns = ["Total", "SUM(r1)", "SUM(r2)", "SUM(r3)", "SUM(r4)", "SUM(r5)", "SUM(r6)", "SUM(r7)", "SUM(r8)", "SUM(r9)", "SUM(r10)", "SUM(r11)", "SUM(r12)"])
            df.columns = ['nama_penyakit','tanggal','hasil_klasifikasi']

            df.to_sql(
                'cluster_tb_hasil_cluster', con=engine, index=True, index_label='id', if_exists='replace'
            )

            banyak = tb_hasil_cluster.objects.filter(hasil_klasifikasi="Banyak Terjangkit",tanggal__lte=date)
            kurang = tb_hasil_cluster.objects.filter(hasil_klasifikasi="Sedikit Terjangkit",tanggal__lte=date) 

            context = {'banyak':banyak,'kurang':kurang,'chart':chart,'session':usersession}
            return render(request, 'dokteker/hasil-cluster.html', context)
        
    # select data dari database
    query="""SELECT nama_penyakit, SUM(total) AS Total, SUM(r1), SUM(r2), SUM(r3), SUM(r4), SUM(r5), SUM(r6), SUM(r7), SUM(r8), SUM(r9), SUM(r10), SUM(r11), SUM(r12) FROM cluster_tb_data GROUP BY nama_penyakit"""
    df = pd.read_sql_query(query,engine)
    X = df.iloc[:, [1,2,3,4,5,6,7,8,9,10,11,12,13]].values

    # Clustering k-means
    kmeans = KMeans(n_clusters = 2, init = 'k-means++', n_init=5, random_state=0)
    y_kmeans = kmeans.fit_predict(X)

    # Visualisasi data
    clusterCount = np.bincount(y_kmeans)
    label_cluster = ["Sedikit Terjangkit", "Banyak Terjangkit"]    
    fig = go.Figure(data=([go.Pie(labels=label_cluster, title='Clustering Data Penyakit',values=clusterCount, pull=[0.2, 0])]))
    fig.update_layout(
        height=600
    )

    chart = fig.to_html()

    banyak = tb_hasil_cluster.objects.filter(hasil_klasifikasi="Banyak Terjangkit")
    kurang = tb_hasil_cluster.objects.filter(hasil_klasifikasi="Sedikit Terjangkit") 
        
    context = {'banyak':banyak,'kurang':kurang,'chart':chart,'session':usersession}
    return render(request, 'dokteker/hasil-cluster.html', context)

def DA_HASIL_PREDIKSI(request):
    usersession = request.session.get('username')
    userakses = request.session.get('akses')
    if usersession is None:
        messages.add_message(request, messages.WARNING, "Login terlebih dahulu")
        return redirect('login')
    elif userakses != 21:
        messages.add_message(request, messages.WARNING, "Akses gagal")
        return redirect('login')

    list_penyakit = tb_data.objects.raw("SELECT id_data, nama_penyakit FROM cluster_tb_data GROUP BY nama_penyakit")
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
            df['hasil_prediksi'] = df['total'].expanding().mean()
            df = df.iloc[:, [1, 0, 2]]              

            fig = px.line(df,
                x="tanggal_input",
                y=['total','hasil_prediksi'],
                title='<b>Prediksi '+penyakit+"</b>",                         
            )
            fig.update_traces(mode='lines+markers')
            newnames = {'total':penyakit, 'hasil_prediksi': 'Hasil prediksi'}
            fig.for_each_trace(lambda t: t.update(name = newnames[t.name],
                                                legendgroup = newnames[t.name],
                                                hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])))
            fig.update_layout(
                legend_title_text='',
                title=dict(font=dict(size=12)),
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

            df['nama_penyakit'] = penyakit 
            df = df.drop(columns="total")
            df = df.iloc[:, [2,0,1]]
            df.to_sql(
                'cluster_tb_hasil_prediksi', engine, index=False, index_label='id', if_exists='append'
            )
            
            context = {'list':list_penyakit,'chart':chart,'session':usersession}
            return render(request, 'dokteker/hasil-prediksi.html', context)
        
    context = {'list':list_penyakit,'session':usersession}
    return render(request, 'dokteker/hasil-prediksi.html',context)

def ADMINISTRASI(request):
    usersession = request.session.get('username')
    userakses = request.session.get('akses')
    if usersession is None:
        messages.add_message(request, messages.WARNING, "Login terlebih dahulu")
        return redirect('login')
    elif userakses != 22:
        messages.add_message(request, messages.WARNING, "Akses gagal")
        return redirect('login')
    
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
    label_cluster = ["Sedikit Terjangkit", "Banyak Terjangkit"]     
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
    dataframe['hasil_prediksi'] = dataframe['total'].expanding().mean()
    dataframe = dataframe.iloc[:, [1, 0, 2]]              

    figure = px.line(dataframe,
            x="tanggal_input",
            y=['total','hasil_prediksi'],   
            height=500,
            width=1000,  
            title="<b>Prediksi "+random +"</b>"                               
    )
    figure.update_traces(mode='lines+markers')
    newnames = {'total':random, 'hasil_prediksi': 'Hasil prediksi'}
    figure.for_each_trace(lambda t: t.update(name = newnames[t.name],
                                        legendgroup = newnames[t.name],
                                        hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])))
    figure.update_layout(
        legend_title_text='',
        title={        
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
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

    context = {'pie':pie,'line':line,'random':random,'session':usersession}
    return render(request, 'administrasi/home.html', context)

def SA_DATA(request):
    usersession = request.session.get('username')
    userakses = request.session.get('akses')
    if usersession is None:
        messages.add_message(request, messages.WARNING, "Login terlebih dahulu")
        return redirect('login')
    elif userakses != 22:
        messages.add_message(request, messages.WARNING, "Akses gagal")
        return redirect('login')
    
    engine = sqlalchemy.create_engine('mysql+pymysql://root:@localhost:3306/db_marunggi')
    # jika ada perintah method post
    if request.method == 'POST':
        if 'importSubmit' in request.POST:
            uploaded_files = request.FILES['file']
            dateInput = request.POST['tanggal_input']
            if not dateInput:
                messages.add_message(request, messages.WARNING, 'Per. Tanggal input tidak boleh kosong')
                return render(request, 'administrasi/kelola-data.html')        
            else:
                fs = FileSystemStorage()
                fs.save(uploaded_files.name, uploaded_files)
                # simpan file ke dalam local server
                file_name = uploaded_files.name 
                # proses data cleaning
                pd.set_option("display.max_rows", None)
                pd.set_option("display.max_columns", None)
                df = pd.read_csv(r"D:/Yahya/xampp/htdocs/django/data/" + file_name, delimiter=";")
                df['JENIS PENYAKIT'] = df['JENIS PENYAKIT'].str.lower()
                df['JENIS PENYAKIT'] = df['JENIS PENYAKIT'].str.title()
                df = df.fillna(0)
                df = df.convert_dtypes()
                data_sebelum = df.to_html(classes="table table-stripped")
                df = df.drop_duplicates()
                df = df.drop(columns = "NO")
                df['tanggal_input'] = dateInput

                for x in df.index:
                    if df.loc[x, "TOTAL"] == 0:
                        df.drop(x, inplace=True)
                df = df.reset_index(drop=True)
                data_sesudah = df.to_html(classes="table table-stripped")
                df.rename(columns = {'JENIS PENYAKIT':'nama_penyakit',"0-7 hr":'r1','8-28 hr':'r2','1 bl-1 th':'r3','1-4 th':'r4','5-9 th':'r5','10-14 th':'r6','15-19 th':'r7',' 20-44 th':'r8','45-54 th':'r9','55-59 th':'r10','60-69 th':'r11','> 70 th':'r12'}, inplace=True)
                # simpan hasil data cleaning ke database
                df.to_sql(
                    'cluster_tb_data', con=engine, index=False, if_exists='append'
                )
                messages.add_message(request, messages.SUCCESS, 'Data berhasil diinputkan')

                context = {'data1':data_sebelum,'data2':data_sesudah, 'session':usersession}
                return render(request, 'administrasi/kelola-data.html', context)
        if 'cekSubmit' in request.POST:
            bulanInput = request.POST['bulan_input']  
            if not bulanInput:
                messages.add_message(request, messages.WARNING, 'Pilih bulan data yang ingin dicek')
                return render(request, 'administrasi/kelola-data.html')        
            else:
                query = """SELECT nama_penyakit,r1,r2,r3,r4,r5,r6,r7,r8,r9,r10,r11,r12,total,tanggal_input FROM cluster_tb_data WHERE tanggal_input BETWEEN '"""+bulanInput+"""-01' AND '"""+bulanInput+"""-31'"""
                df = pd.read_sql_query(query,engine)
                df.rename(columns = {'nama_penyakit':'JENIS PENYAKIT','r1':"0-7 hr",'r2':'8-28 hr','r3':'1 bl-1 th','r4':'1-4 th','r5':'5-9 th','r6':'10-14 th','r7':'15-19 th','r8':' 20-44 th','r9':'45-54 th','r10':'55-59 th','r11':'60-69 th','r12':'> 70 th'}, inplace=True)
                data_cek = df.to_html(classes="table table-stripped")
                context = {'cek':data_cek, 'session':usersession}
                return render(request, 'administrasi/kelola-data.html', context)
    # jika ada perintah method get
    else:        
        return render(request, 'administrasi/kelola-data.html', {'session':usersession})

def SA_HASIL_CLUSTER(request):
    usersession = request.session.get('username')
    userakses = request.session.get('akses')
    if usersession is None:
        messages.add_message(request, messages.WARNING, "Login terlebih dahulu")
        return redirect('login')
    elif userakses != 22:
        messages.add_message(request, messages.WARNING, "Akses gagal")
        return redirect('login')
    
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
            clusterCount = np.bincount(y_kmeans)
            label_cluster = ["Sedikit Terjangkit", "Banyak Terjangkit"]
            judul = 'Clustering Data Penyakit Per. '+date    
            fig = go.Figure(data=([go.Pie(labels=label_cluster, title=judul, values=clusterCount, pull=[0.2, 0])]))
            fig.update_layout(
                height=600
            )
            chart = fig.to_html()

            mapping = {0:'Sedikit Terjangkit', 1:'Banyak Terjangkit'}
            y_kmeans = [mapping[i] for i in y_kmeans]

            df['cluster'] = y_kmeans
            df = df.drop(columns = ["Total", "SUM(r1)", "SUM(r2)", "SUM(r3)", "SUM(r4)", "SUM(r5)", "SUM(r6)", "SUM(r7)", "SUM(r8)", "SUM(r9)", "SUM(r10)", "SUM(r11)", "SUM(r12)"])
            df.columns = ['nama_penyakit','tanggal','hasil_klasifikasi']

            df.to_sql(
                'cluster_tb_hasil_cluster', con=engine, index=True, index_label='id', if_exists='replace'
            )

            banyak = tb_hasil_cluster.objects.filter(hasil_klasifikasi="Banyak Terjangkit",tanggal__lte=date)
            kurang = tb_hasil_cluster.objects.filter(hasil_klasifikasi="Sedikit Terjangkit",tanggal__lte=date) 

            context = {'banyak':banyak,'kurang':kurang,'chart':chart,'session':usersession}
            return render(request, 'administrasi/hasil-cluster.html', context)
        
    # select data dari database
    query="""SELECT nama_penyakit, SUM(total) AS Total, SUM(r1), SUM(r2), SUM(r3), SUM(r4), SUM(r5), SUM(r6), SUM(r7), SUM(r8), SUM(r9), SUM(r10), SUM(r11), SUM(r12) FROM cluster_tb_data GROUP BY nama_penyakit"""
    df = pd.read_sql_query(query,engine)
    X = df.iloc[:, [1,2,3,4,5,6,7,8,9,10,11,12,13]].values

    # Clustering k-means
    kmeans = KMeans(n_clusters = 2, init = 'k-means++', n_init=5, random_state=0)
    y_kmeans = kmeans.fit_predict(X)

    # Visualisasi data
    clusterCount = np.bincount(y_kmeans)
    label_cluster = ["Sedikit Terjangkit", "Banyak Terjangkit"]    
    fig = go.Figure(data=([go.Pie(labels=label_cluster, title='Clustering Data Penyakit',values=clusterCount, pull=[0.2, 0])]))
    fig.update_layout(
        height=600
    )

    chart = fig.to_html()

    banyak = tb_hasil_cluster.objects.filter(hasil_klasifikasi="Banyak Terjangkit")
    kurang = tb_hasil_cluster.objects.filter(hasil_klasifikasi="Sedikit Terjangkit") 
        
    context = {'banyak':banyak,'kurang':kurang,'chart':chart,'session':usersession}
    return render(request, 'administrasi/hasil-cluster.html', context)

def SA_HASIL_PREDIKSI(request):
    usersession = request.session.get('username')
    userakses = request.session.get('akses')
    if usersession is None:
        messages.add_message(request, messages.WARNING, "Login terlebih dahulu")
        return redirect('login')
    elif userakses != 22:
        messages.add_message(request, messages.WARNING, "Akses gagal")
        return redirect('login')
    
    list_penyakit = tb_data.objects.raw("SELECT id_data, nama_penyakit FROM cluster_tb_data GROUP BY nama_penyakit")
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
            df['hasil_prediksi'] = df['total'].expanding().mean()
            df = df.iloc[:, [1, 0, 2]]   
                     
            fig = px.line(df,
                x="tanggal_input",
                y=['total','hasil_prediksi'],
                title='<b>Prediksi '+penyakit+"</b>",                         
            )
            fig.update_traces(mode='lines+markers')
            newnames = {'total':penyakit, 'hasil_prediksi': 'Hasil prediksi'}
            fig.for_each_trace(lambda t: t.update(name = newnames[t.name],
                                                legendgroup = newnames[t.name],
                                                hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])))
            fig.update_layout(
                legend_title_text='',
                title=dict(font=dict(size=12)),
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

            df['nama_penyakit'] = penyakit 
            df = df.drop(columns="total")
            df = df.iloc[:, [2,0,1]]
            df.to_sql(
                'cluster_tb_hasil_prediksi', engine, index=False, index_label='id', if_exists='append'
            )
        
            context = {'list':list_penyakit,'chart':chart,'session':usersession}
            return render(request, 'administrasi/hasil-prediksi.html', context)
        
    context = {'list':list_penyakit,'session':usersession}
    return render(request, 'administrasi/hasil-prediksi.html',context)        
