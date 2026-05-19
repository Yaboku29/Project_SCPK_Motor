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

# Using "with" notation
page = st.sidebar.radio ("Navigasi", ("Semua Data", "Data Pilihan"))
if page == "Semua Data":
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
            at_price = st.selectbox("Atributte ",["Cost", "Benefit"], key="atPrice")
            at_cc = st.selectbox("",["Cost", "Benefit"], key="atCC")
            at_milage = st.selectbox("",["Cost", "Benefit"], key="atMilage")
            at_weight = st.selectbox("",["Cost", "Benefit"], key="atWeight")
            at_acs = st.selectbox("",["Cost", "Benefit"], key="atAcs")
            at_tps = st.selectbox("",["Cost", "Benefit"], key="atTps")

            atribut = {
                "price": at_price,
                "CC": at_cc,
                "mileage": at_milage,
                "weight_in_kg": at_weight,
                "acceleration_speed": at_acs,
                "top_speed": at_tps
            }

if st.button("Buat Alternatif Terbaik"):
    if total == 1:
        tab3,tab4,tab5 = st.tabs(["Matriks Ternormalisasi","Nilai Preferensi","Alternatif Terbaik"])
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
            best_alt = hasil_ranking.index[0]
            st.text(f"Motor Bekas Terbaik Adalah {best_alt}")
            best_alt_data = data.loc[best_alt]
            st.dataframe(best_alt_data)
    else:
        st.error("Total bobot harus 1")
    
