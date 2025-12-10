import pandas as pd
import streamlit as st
import facebook
import requests
import matplotlib.pyplot as plt
import numpy as np
import altair as alt




st.markdown("""
    <style>
        /* Cambiar color de fondo */
        .stApp {
            background-color: #f4f4f9;
        }

        /* Estilo para títulos */
        h1, h2, h3 {
            color: #2c3e50;
            font-family: 'Poppins', sans-serif;
        }

        /* Tarjetas o contenedores personalizados */
        .card {
            background-color: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
            margin-bottom: 15px;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🔍 Metricas - Facebook Pages")

user_long_token = st.text_input("Introduce tu token de acceso (short-lived):", type="password")


if user_long_token:
    try:
        graph = facebook.GraphAPI(access_token=user_long_token, version="3.1")

        # 3️⃣ Inputs de fecha
        date_ini = st.date_input("Selecciona la fecha inicial")
        date_fin = st.date_input("Selecciona la fecha final")

        # 4️⃣ Obtener información de las páginas asociadas
        page_data = graph.get_object('/me/accounts')
        info = pd.DataFrame(page_data['data'])

        st.subheader("📋 Páginas asociadas a tu cuenta")
        st.dataframe(info['name'])

        # 5️⃣ Permitir seleccionar un número (por ejemplo, el índice de una fila)
        if not info.empty:
            indice = st.number_input(
                "Selecciona el número de fila que deseas usar:",
                min_value=0,
                max_value=len(info) - 1,
                step=1
            )
            if indice:
                st.write("Seleccionaste la página:")
                st.write(info['name'][indice])
                permanent_page_token = page_data['data'][indice]['access_token']
                page_id = page_data['data'][indice]['id']

                graph = facebook.GraphAPI(access_token=permanent_page_token, version=3.1)
                graph.get_object(id=page_id, fields='name')

                #fans = graph.get_connections(id = page_id, connection_name = 'insights', metric = 'page_fans', since = date_ini, until = date_fin)
                follow = graph.get_connections(id = page_id, connection_name = 'insights', metric = 'page_follows', since = date_ini, until = date_fin)
                #dataframe_facebook = pd.DataFrame(fans['data'][0]['values'])
                #dataframe_facebook.columns = ['Fans', 'Fecha']
                #dataframe_facebook['Fecha'] = pd.to_datetime(dataframe_facebook['Fecha'])
                #dataframe_facebook['Fecha'] = dataframe_facebook['Fecha'].dt.strftime('%Y-%m-%d')
                #df_fans = dataframe_facebook.set_index('Fecha')
                #df_fans['Nuevos Fans Netos'] = df_fans['Fans'].diff(periods=1)
                #df_fans['Nuevos Fans Netos'] = df_fans['Nuevos Fans Netos'].fillna(0)

                dataframe_facebook2 = pd.DataFrame(follow['data'][1]['values'])
                dataframe_facebook2.columns = ['Followers', 'Fecha']
                dataframe_facebook2['Fecha'] = pd.to_datetime(dataframe_facebook2['Fecha'])
                #dataframe_facebook2['Fecha'] = dataframe_facebook2['Fecha'].dt.strftime('%Y-%m-%d')
                df_fans2 = dataframe_facebook2.set_index('Fecha')
                df_fans2['Nuevos Followers Netos'] = df_fans2['Followers'].diff(periods=1)
                df_fans2['Nuevos Followers Netos'] = df_fans2['Nuevos Followers Netos'].fillna(0)
                
                #st.subheader("Fans asociados a tu cuenta")
                #st.dataframe(dataframe_facebook)

                st.subheader("Followers asociados a tu cuenta")
                st.dataframe(dataframe_facebook2)
                
                st.bar_chart(
                                df_fans2['Nuevos Followers Netos'],
                                y_label='Nuevos Followers Netos',
                                use_container_width=True
                            )
                

                posts = graph.get_connections(id=page_id, connection_name="feed", since=date_ini, until=date_fin)
                posteos = pd.DataFrame(posts['data'])
                posteos = posteos.iloc[:, :3]
                if not posteos.empty:
                    posteos.columns = ['Fecha', 'Mensaje', 'id']  # , 'stories']
                    posteos['Fecha'] = pd.to_datetime(posteos['Fecha'])
                    posteos['Fecha'] = posteos['Fecha'].dt.strftime('%Y-%m-%d')
                    imp=[]
                    imp_pg = []
                    react = []
                    sh = []
                    link = []
                    img = []
                    com = []
                    for i in posteos['id']:
                        impresion_post = graph.get_connections(id=str(i),connection_name='insights',metric='post_impressions_unique, post_impressions_paid_unique,post_reactions_by_type_total')
                        comments = graph.get_connections(id=str(i), connection_name="comments")
                        imp.append(impresion_post['data'][0]['values'][0]['value'])
                        imp_pg.append(impresion_post['data'][1]['values'][0]['value'])
                        react.append(sum(impresion_post['data'][2]['values'][0]['value'].values()))
                        com.append(len(comments['data']))
                        
                        try:
                            shar = graph.get_object(id=str(i),fields='shares')
                            sh.append(shar['shares']['count'])
                        except:
                            sh.append(0)

                        try:
                            lim = graph.get_object(id=str(i),fields='permalink_url, full_picture')
                            link.append(lim['permalink_url'])
                            img.append(lim['full_picture'])
                        except:
                            link.append('-')
                            img.append('-')
                            
                    posteos['Link'] = link         
                    posteos['Imagen'] = img        
                    posteos['Alcance'] = imp
                    posteos['Alcance Pagado'] = imp_pg
                    posteos['Reacciones'] = react
                    tp = []
                    for i in posteos['Alcance Pagado']:
                        if i == 0:
                            tp.append("Organico")
                        else:
                            tp.append("Pautado")
                    posteos["Comentarios"] = com        
                    posteos["Shares"] = sh
                    interpubli = []
                    for i in range(len(posteos["Shares"])):
                        ipubl = posteos['Shares'][i] + posteos['Comentarios'][i] + posteos['Reacciones'][i]
                        interpubli.append(ipubl)
                    posteos["Interacciones Publicas"] = interpubli
                    posteos["Tipo"] = tp    
                    st.subheader("📋 Post asociadas a tu cuenta")
                    #st.dataframe(posteos)
                    st.dataframe(
                                posteos,
                                column_config={
                                    "Imagen": st.column_config.ImageColumn(
                                        "Imagen",
                                        help="Vista previa",
                                        width="small"
                                    )
                                },
                                use_container_width=True
                            )


                    # ============================
                    # 🔽 Selección de Posteos
                    # ============================
                    
                    st.subheader("📌 Selecciona dos posteos para comparar")
                    
                    # Lista de IDs
                    post_ids = posteos["id"].tolist()
                    
                    post1 = st.selectbox("Selecciona Post 1:", post_ids, key="post1")
                    post2 = st.selectbox("Selecciona Post 2:", post_ids, key="post2")
                    
                    if post1 and post2 and post1 != post2:
                    
                        # Filtrar cada posteo
                        p1 = posteos[posteos["id"] == post1].iloc[0]
                        p2 = posteos[posteos["id"] == post2].iloc[0]
                    
                        # Extraer métricas relevantes
                        columnas_metricas = [
                            "Alcance", "Alcance Pagado", "Reacciones",
                            "Comentarios", "Shares"
                        ]
                    
                        df_comp = pd.DataFrame({
                            "Métrica": columnas_metricas,
                            "Post 1": [p1[col] for col in columnas_metricas],
                            "Post 2": [p2[col] for col in columnas_metricas],
                        })
                    
                        # Nueva columna: comparación
                        df_comp["Comparación (P1 / P2)"] = (
                            df_comp["Post 1"] / df_comp["Post 2"] - 1
                        ).round(2)
                    
                        st.subheader("📊 Comparación de Métricas")
                        st.dataframe(df_comp)
                    
                        # Gráfica comparativa
                        st.subheader("📈 Comparación visual")
                    
                        fig2, ax2 = plt.subplots(figsize=(8, 4))
                        x = np.arange(len(columnas_metricas))
                        width = 0.35
                    
                        ax2.bar(x - width/2, df_comp["Post 1"], width=width, label="Post 1")
                        ax2.bar(x + width/2, df_comp["Post 2"], width=width, label="Post 2")
                    
                        ax2.set_xticks(x)
                        ax2.set_xticklabels(columnas_metricas, rotation=45, ha="right")
                        ax2.set_ylabel("Cantidad")
                        ax2.set_title("Comparación de métricas entre dos posteos")
                        ax2.legend()
                    
                        st.pyplot(fig2)


                
                else:
                    st.write("No se encontraron publicaciones en el rango de fechas seleccionado.")


    except Exception as e:
        st.error(f"Ocurrió un error: {e}")

























