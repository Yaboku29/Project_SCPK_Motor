import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="SCPK")
st.title("Pemilihan Motor Bekas")
st.subheader("Metode Simple Additive Weighting (SAW)")

df=pd.read_csv('bike_dataset.csv',usecols=lambda col: col!='links')
df=df.set_index('model_name')
data=df[(df['type_of_bike']=='Petrol Bike')]
data=data.drop(columns='type_of_bike')
selected_data=data.copy() # untuk data pilihan
# Using "with" notation
page = st.sidebar.radio ("Navigasi", ("Dataset Mentah","Semua Alternatif", "Alternatif Pilihan","CRUD"))
if page == "Dataset Mentah":
    raw_df = pd.read_csv('bike_dataset.csv')
    st.dataframe(raw_df)

elif page == "Semua Alternatif":
    tab1, tab2 = st.tabs(["Matriks Keputusan", "Kriteria"])
    with tab1:
        st.dataframe(data)
    with tab2:
        st.title("Kriteria SAW")
        col1, col2 = st.columns([4,1])
        with col1:
            w_price = st.number_input("Bobot Price", 0.0, 1.0, 0.16)
            w_cc = st.number_input("Bobot CC", 0.0, 1.0, 0.16)
            w_mileage = st.number_input("Bobot Mileage", 0.0, 1.0, 0.16)
            w_weight = st.number_input("Bobot Weight", 0.0, 1.0, 0.16)
            w_acs = st.number_input("Bobot Acceleration Speed", 0.0, 1.0, 0.16)
            w_tps = st.number_input("Bobot Top Speed", 0.0, 1.0, 0.16)

            total = w_price + w_cc + w_mileage + w_weight + w_acs + w_tps

            bobot={
                'price':w_price,
                'CC':w_cc,
                'mileage':w_mileage,
                'weight_in_kg':w_weight,
                'acceleration_speed':w_acs,
                'top_speed':w_tps
            }

            st.write("Total Bobot:", round(total, 2))

        with col2:
            at_price = st.selectbox("Atributte ",["Cost", "Benefit"], index=None, placeholder="Pilih", key="atPrice" )
            at_cc = st.selectbox("",["Cost", "Benefit"], index=None, placeholder="Pilih", key="atCC")
            at_milage = st.selectbox("",["Cost", "Benefit"], index=None, placeholder="Pilih", key="atMilage")
            at_weight = st.selectbox("",["Cost", "Benefit"], index=None, placeholder="Pilih", key="atWeight")
            at_acs = st.selectbox("",["Cost", "Benefit"], index=None, placeholder="Pilih", key="atAcs")
            at_tps = st.selectbox("",["Cost", "Benefit"], index=None, placeholder="Pilih", key="atTps")

            atribut = {
                "price": at_price,
                "CC": at_cc,
                "mileage": at_milage,
                "weight_in_kg": at_weight,
                "acceleration_speed": at_acs,
                "top_speed": at_tps
            }

    if st.button("Buat Alternatif Terbaik"):
        if abs(total - 1) > 0.001:
            st.error("Total bobot harus 1")
        elif None in atribut.values():
            st.error("Semua Atribut harus dipilih")
        else:
            tab3,tab4,tab5,tab6,tab7,tab8 = st.tabs(["Matriks Ternormalisasi","Nilai Preferensi","Tabel Ranking","Alternatif Terbaik","Top 3","Top 10"])
            with tab3:
                normalize_matrix=data.copy()
                # print(normalize_matrix)
                for col in atribut:# Pakai kolom (m)
                    if atribut[col].lower() == 'benefit':
                        normalize_matrix[col]=data[col]/data[col].max()
                    else:
                        normalize_matrix[col]=data[col].min()/data[col]
                st.dataframe(normalize_matrix)
            with tab4:
                preference_value={}
                for index,row in normalize_matrix.iterrows():
                    total=0
                    for k in normalize_matrix.columns:
                        total+=row[k] * bobot[k]
                    preference_value[index]=total
                df_preference_value=pd.DataFrame(preference_value.items(),columns=['model_name','preference_value'])
                df_preference_value=df_preference_value.set_index('model_name')
                st.dataframe(df_preference_value)
            with tab5:
                hasil_ranking=df_preference_value.sort_values(by='preference_value',ascending=False)
                hasil_ranking_data = hasil_ranking.reset_index()
                hasil_ranking_data.index = hasil_ranking_data.index + 1
                hasil_ranking_data.index.name = "Ranking"
                st.dataframe(hasil_ranking_data)
            with tab6:
                best_alt = hasil_ranking.index[0]
                st.write(best_alt)
                st.text(f"Motor Bekas Terbaik Adalah {best_alt}")
                
                df2=pd.read_csv('bike_dataset.csv')
                df2=df2.set_index('model_name')
                best_alt_data = df2.loc[best_alt]
                st.dataframe(best_alt_data)

                link_motor = best_alt_data['links']
                st.link_button(
                    "Lihat Detail Motor",
                    link_motor
                )
            with tab7:
                labels = [
                    f"{k} ({atribut[k]})"
                    for k in bobot.keys()
                ]
                fig, ax = plt.subplots()
                ax.pie(
                    bobot.values(),
                    labels=labels,
                    autopct='%1.1f%%'
                )
                ax.set_title("Bobot dan Atribut Kriteria")
                st.pyplot(fig)

                #grafik kedua
                top3 = hasil_ranking.head(3).index
                compare_data = normalize_matrix.loc[top3]
                fig, ax = plt.subplots(figsize=(12,6))
                x = np.arange(len(compare_data.columns))
                width = 0.25
                for i, motor in enumerate(compare_data.index):
                    ax.bar(
                        x + i*width,
                        compare_data.loc[motor],
                        width,
                        label=motor
                    )
                ax.set_xticks(x + width)
                ax.set_xticklabels(compare_data.columns)
                ax.set_title("Perbandingan Top 3 Motor")
                ax.set_ylabel("Nilai Normalisasi")
                ax.legend()
                st.pyplot(fig)

                st.subheader("Data Lengkap Top 3")
                top3_index = hasil_ranking.head(3).index
                top3_data = df2.loc[top3_index].copy()
                top3_data['preference_value'] = (
                    hasil_ranking.head(3)['preference_value']
                )  
                top3_data = top3_data.reset_index()
                top3_data.index = top3_data.index + 1
                top3_data.index.name = "Ranking"
                st.dataframe(top3_data)

            with tab8:
                #grafik ketiga
                top10 = hasil_ranking.head(10)
                fig, ax = plt.subplots(figsize=(12,6))

                ax.bar(
                    top10.index,
                    top10['preference_value']
                )

                ax.set_title("Top 10 Motor Berdasarkan Nilai SAW")
                ax.set_ylabel("Nilai Preferensi")

                plt.xticks(rotation=20)

                st.pyplot(fig)

                st.subheader("Data Lengkap Top 10")
                top10_index = hasil_ranking.head(10).index
                top10_data = df2.loc[top10_index].copy()
                top10_data['preference_value'] = (
                    hasil_ranking.head(10)['preference_value']
                )  
                top10_data = top10_data.reset_index()
                top10_data.index = top10_data.index + 1
                top10_data.index.name = "Ranking"
                st.dataframe(top10_data)
            
elif page == "Alternatif Pilihan":
    tab1,tab2,tab3=st.tabs([
        "Matriks Keputusan",
        "Pilih Alternatif",
        "Kriteria"
    ])
    with tab1:
        st.dataframe(data)
    with tab2:
        jumlah=st.number_input(
            "Jumlah Alternatif",1,
            len(data),3
        )
        pilihan=st.multiselect(
            "Pilih motor",
            options=data.index.tolist(),
            max_selections=jumlah
        )
        if pilihan:
            selected_data=data.loc[pilihan]
            st.subheader("Alternatif yang Dipilih")
            st.dataframe(selected_data)
    with tab3:
        st.title("Kriteria SAW")
        col1, col2 = st.columns([4,1])
        with col1:
            w_price = st.number_input("Bobot Price", 0.0, 1.0, 0.16)
            w_cc = st.number_input("Bobot CC", 0.0, 1.0, 0.16)
            w_mileage = st.number_input("Bobot Mileage", 0.0, 1.0, 0.16)
            w_weight = st.number_input("Bobot Weight", 0.0, 1.0, 0.16)
            w_acs = st.number_input("Bobot Acceleration Speed", 0.0, 1.0, 0.16)
            w_tps = st.number_input("Bobot Top Speed", 0.0, 1.0, 0.16)

            total = w_price + w_cc + w_mileage + w_weight + w_acs + w_tps

            bobot={
                'price':w_price,
                'CC':w_cc,
                'mileage':w_mileage,
                'weight_in_kg':w_weight,
                'acceleration_speed':w_acs,
                'top_speed':w_tps
            }

            st.write("Total Bobot:", round(total, 2))

        with col2:
            at_price = st.selectbox("Atributte ",["Cost", "Benefit"], index=None, placeholder="Pilih", key="atPrice")
            at_cc = st.selectbox("",["Cost", "Benefit"], index=None, placeholder="Pilih", key="atCC")
            at_milage = st.selectbox("",["Cost", "Benefit"], index=None, placeholder="Pilih", key="atMilage")
            at_weight = st.selectbox("",["Cost", "Benefit"], index=None, placeholder="Pilih", key="atWeight")
            at_acs = st.selectbox("",["Cost", "Benefit"], index=None, placeholder="Pilih", key="atAcs")
            at_tps = st.selectbox("",["Cost", "Benefit"], index=None, placeholder="Pilih", key="atTps")

            atribut = {
                "price": at_price,
                "CC": at_cc,
                "mileage": at_milage,
                "weight_in_kg": at_weight,
                "acceleration_speed": at_acs,
                "top_speed": at_tps
            }

    if st.button("Buat Alternatif Terbaik"):
        if abs(total - 1) > 0.001:
            st.error("Total bobot harus 1")
        elif None in atribut.values():
            st.error("Semua Atribut harus dipilih")
        elif len(pilihan) == 0:
            st.error(f"Pilih tepat {jumlah} motor")
        elif len(pilihan) != jumlah:
            st.error(f"Pilih tepat {jumlah} motor")
        else:
            tab4,tab5,tab6,tab7 = st.tabs(["Matriks Ternormalisasi","Nilai Preferensi","Alternatif Terbaik","Grafik Perbandingan"])
            with tab4:
                normalize_matrix=selected_data.copy()
                # print(normalize_matrix)
                for col in atribut:# Pakai kolom (m)
                    if atribut[col].lower() == 'benefit':
                        normalize_matrix[col]=selected_data[col]/data[col].max()
                    else:
                        normalize_matrix[col]=selected_data[col].min()/data[col]
                st.dataframe(normalize_matrix)
            with tab5:
                preference_value={}
                for index,row in normalize_matrix.iterrows():
                    total=0
                    for k in normalize_matrix.columns:
                        total+=row[k] * bobot[k]
                    preference_value[index]=total
                df_preference_value=pd.DataFrame(preference_value.items(),columns=['model_name','preference_value'])
                df_preference_value=df_preference_value.set_index('model_name')
                st.dataframe(df_preference_value)
            with tab6:
                hasil_ranking=df_preference_value.sort_values(by='preference_value',ascending=False)
                best_alt = hasil_ranking.index[0]
                st.write(best_alt)
                st.text(f"Motor Bekas Terbaik Adalah {best_alt}")
                
                df2=pd.read_csv('bike_dataset.csv')
                df2=df2.set_index('model_name')
                best_alt_data = df2.loc[best_alt]
                st.dataframe(best_alt_data)

                link_motor = best_alt_data['links']
                st.link_button(
                    "Lihat Detail Motor",
                    link_motor
                )
            with tab7:
                #Grafik Distribusi Kriteria
                labels = [
                    f"{k} ({atribut[k]})"
                    for k in bobot.keys()
                ]
                fig, ax = plt.subplots()
                ax.pie(
                    bobot.values(),
                    labels=labels,
                    autopct='%1.1f%%'
                )
                ax.set_title("Bobot dan Atribut Kriteria")
                st.pyplot(fig)

                #Grafik Perbandingan Kriteria
                compare_data = normalize_matrix.loc[pilihan]
                fig, ax = plt.subplots(figsize=(12,6))
                x = np.arange(len(compare_data.columns))
                width = 0.8 / jumlah
                for i, motor in enumerate(compare_data.index):
                    ax.bar(
                        x + i*width,
                        compare_data.loc[motor],
                        width,
                        label=motor
                    )
                ax.set_xticks(x + width)
                ax.set_xticklabels(compare_data.columns)
                ax.set_title(f"Perbandingan {jumlah} Motor")
                ax.set_ylabel("Nilai Normalisasi")
                ax.legend(bbox_to_anchor=(1.02, 1),loc='upper left')
                st.pyplot(fig)
                
                #Grafik Nilai Preferensi
                fig, ax = plt.subplots(figsize=(12,6))
                ax.bar(
                    hasil_ranking.index,
                    hasil_ranking['preference_value']
                )
                ax.set_title(f"Top {jumlah} Motor Berdasarkan Nilai SAW")
                ax.set_ylabel("Nilai Preferensi")
                plt.xticks(rotation=20)
                st.pyplot(fig)

                # Tabel
                st.subheader(f"Data Lengkap {jumlah} Motor")
                pilihan_index = hasil_ranking.index
                pilihan_data = df2.loc[pilihan_index].copy()
                pilihan_data['preference_value'] = (
                    hasil_ranking.head(10)['preference_value']
                ) 
                pilihan_data = pilihan_data.reset_index()
                pilihan_data.index = pilihan_data.index + 1
                pilihan_data.index.name = "Ranking"
                st.dataframe(pilihan_data)
                
elif page == "CRUD":
    tabs1,tabs2,tabs3 = st.tabs(["Input Data", "Edit Data", "Hapus Data"]);

    dfcrud = pd.read_csv("bike_dataset.csv")    
    dfc=dfcrud[(dfcrud['type_of_bike']=='Petrol Bike')]
    
    with tabs1:
        with st.form("tambah_motor"):
            model = st.text_input("Nama Motor")
            price = st.number_input("Harga", min_value=1000)
            cc = st.number_input("CC", min_value=50.0)
            mileage = st.number_input("Mileage" , min_value=1)
            tob = st.text_input("Type", value="Petrol Bike", disabled=True)
            weight = st.number_input("Weight", min_value=100)
            links = st.text_input("Links", placeholder="https://", value="https://")
            accel = st.number_input("Acceleration Speed", min_value=1.0)
            topsp = st.number_input("Top Speed", min_value=20)

            if st.form_submit_button("Tambah"):
                if model.strip() == "":
                    st.error("Nama motor wajib diisi")
                elif len(model.strip()) < 3:
                    st.error("Nama motor minimal 3 karakter")
                elif model in df["model_name"].values:
                    st.error("Motor sudah ada di dataset")
                elif price < 1000:
                    st.error("Harga tidak masuk akal")
                elif cc < 50:
                    st.error("CC minimal 50")
                elif mileage < 1:
                    st.error("Mileage harus lebih dari 0")
                elif weight < 100:
                    st.error("Berat motor tidak masuk akal")
                elif links.strip() == "":
                    st.error("Link wajib diisi")
                elif not (
                    links.startswith("http://")
                    or links.startswith("https://")
                ):
                    st.error("Link harus diawali http:// atau https://")
                elif "." not in links:
                    st.error("Format link tidak valid")
                elif accel <= 0:
                    st.error("Acceleration Speed harus lebih dari 0")
                elif accel > 30:
                    st.error("Acceleration Speed tidak masuk akal")
                elif topsp < 20:
                    st.error("Top Speed tidak masuk akal")
                elif topsp > 500:
                    st.error("Top Speed tidak masuk akal")
                else:
                    dfc.loc[len(dfc)] = {
                        "model_name": model,
                        "price": price,
                        "CC" : cc,
                        "mileage" : mileage,
                        "type_of_bike" : tob,
                        "weight_in_kg" : weight,
                        "links" : links,
                        "acceleration_speed" : accel,
                        "top_speed" : topsp
                    }
                    dfc.to_csv(
                        "bike_dataset.csv",
                        index=False
                    )
                    st.success("Motor ditambahkan")
                    st.rerun()

    with tabs2:

        motor_pilih = st.selectbox(
            "Pilih Motor",
            dfc["model_name"]
        )

        with st.form("edit_motor"):

            row = dfc[dfc["model_name"] == motor_pilih].iloc[0]

            model_name = st.text_input(
                "Model",
                value=row["model_name"]
            )

            price = st.number_input(
                "Harga",
                min_value=1,
                value=int(row["price"])
            )

            cc = st.number_input(
                "CC",
                min_value=1.0,
                value=max(1.0, float(row["CC"]))
            )

            mileage = st.number_input(
                "Mileage",
                min_value=1,
                value=int(row["mileage"])
            )

            tob = st.text_input(
                "Type",
                value=row["type_of_bike"],
                disabled=True
            )

            weight = st.number_input(
                "Weight",
                min_value=1,
                value=int(row["weight_in_kg"])
            )

            links = st.text_input(
                "Links",
                value=row["links"]
            )

            accel = st.number_input(
                "Acceleration Speed",
                min_value=1.0,
                value=float(row["acceleration_speed"])
            )

            topsp = st.number_input(
                "Top Speed",
                min_value=1,
                value=int(row["top_speed"])
            )

            if st.form_submit_button("Edit"):

                if links.strip() == "":
                    st.error("Link wajib diisi")

                elif not (
                    links.startswith("http://")
                    or links.startswith("https://")
                ):
                    st.error("Link harus diawali http:// atau https://")

                else:

                    idx = dfc[dfc["model_name"] == motor_pilih].index[0]

                    dfc.loc[idx, "model_name"] = model_name
                    dfc.loc[idx, "price"] = price
                    dfc.loc[idx, "CC"] = cc
                    dfc.loc[idx, "mileage"] = mileage
                    dfc.loc[idx, "weight_in_kg"] = weight
                    dfc.loc[idx, "links"] = links
                    dfc.loc[idx, "acceleration_speed"] = accel
                    dfc.loc[idx, "top_speed"] = topsp

                    dfc.to_csv(
                        "bike_dataset.csv",
                        index=False
                    )

                    st.success("Data berhasil diperbarui")
                    st.rerun()
    with tabs3:

        motor_hapus = st.selectbox(
            "Pilih Motor yang Akan Dihapus",
            dfc["model_name"]
        )

        st.warning(
            f"Motor yang akan dihapus: {motor_hapus}"
        )

        if st.button("Hapus Motor"):

            dfc = dfc[
                dfc["model_name"] != motor_hapus
            ]

            dfc.to_csv(
                "bike_dataset.csv",
                index=False
            )

            st.success(
                f"{motor_hapus} berhasil dihapus"
            )
            st.rerun()