# Importaciones
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import joblib
import json

# Funciones
@st.cache_data # Mete en caché la carga de datos


def load_data():
    return pd.read_csv("data/clean/train_ready_for_modeling.csv")

df = load_data() # Carga de datos CSV


# Carga de modelo y filtros
def load_artifacts():
    model = joblib.load("model/best_xgb_model_final.pkl")
    encodings = joblib.load("model/target_encoding_maps.joblib")
    feature_order = joblib.load("model/feature_order.pkl")
    brand_model_options = joblib.load("model/brand_model_options.pkl")
    return model, encodings, feature_order, brand_model_options

model, target_encoding_maps, feature_order, brand_model_options = load_artifacts()  

# Carga de métricas
with open("metrics.json", "r") as f:
    metrics = json.load(f)
    
# Almacenamos las metricas
train_rmse = metrics["train_rmse"]
test_rmse = metrics["rmse"]
mae = metrics["mae"]
r2 = metrics["r2"]

# Layout

st.set_page_config(page_title="App de Regresión", layout="wide")


TARGET = "price"


with st.sidebar:
    st.title("Menú")

    section = st.sidebar.radio(
        "Selecciona una sección:",
        [
            "📊 Dashboard Analítico",
            "🔮 Predicción",
            "📈 Rendimiento del Modelo",
        ],
    )
    st.divider()
    st.subheader("Filtros")

    selected_brand = st.multiselect(
        "Marca",
        options=sorted(df["brand"].unique()),
        default=sorted(df["brand"].unique())
    )

    year_range = st.slider(
        "Año del modelo",
        int(df["model_year"].min()),
        int(df["model_year"].max()),
        (2010, 2024)
    )

    price_range = st.slider(
    "Rango de precio ($)",
    min_value=int(df["price"].min()),
    max_value=int(df["price"].max()),
    value=(
        int(df["price"].min()),
        int(df["price"].max())
    ),
    format="$%d"
)

    filtered_models = (
    df[df["brand"].isin(selected_brand)]["model"]
    .dropna()
    .unique()
    )

    selected_models = st.multiselect(
        "Modelo",
        options=sorted(filtered_models),
        default=sorted(filtered_models)
    )



# Secciones

if section == "📊 Dashboard Analítico":
    st.markdown("""
    <style>
    .header {
        text-align: center;
        padding: 1rem;
        background-color: #0e1117;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .header h1 {
        color: white;
        margin: 0;
    }
    .header p {
        color: #a6a6a6;
        margin: 0;
    }
    </style>

    <div class="header">
        <h1>Dashboard Analítico</h1>
        <p>Análisis y predicción de precios de coches usados</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="block">', unsafe_allow_html=True)

    # Metemos los filtros en df_filtered
    
    df_filtered = df[
    (df["brand"].isin(selected_brand)) &
    (df["model"].isin(selected_models)) &
    (df["model_year"].between(year_range[0], year_range[1])) &
    (df["price"].between(price_range[0], price_range[1]))
    ]


    # KPIs
    
    st.markdown("### 📊 KPIs principales")

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    kpi1.metric("Precio medio", f"${df_filtered[TARGET].mean():,.0f}")
    kpi2.metric("Precio mediano", f"${df_filtered[TARGET].median():,.0f}")
    kpi3.metric("Nº vehículos", len(df_filtered))
    kpi4.metric("Desviación estándar", f"${df_filtered[TARGET].std():,.0f}")
    
    st.expander("Insight").write(
        """ 
        La diferencia entre el precio medio y mediano sugiere una distribución sesgada,
        probablemente debido a la presencia de coches de lujo con precios muy altos.
        """
    )

    # Gráfico de distribución de la variable objetivo


    g1, g2 = st.columns(2)

    # --- Gráfica 1: Distribución de precios ---
    with g1:
        fig, ax = plt.subplots(figsize=(5, 2))

        filtered_prices = df_filtered[df_filtered[TARGET] < 3000000][TARGET]
        ax.hist(filtered_prices, bins=40)

        ax.set_xlabel("Precio ($)")
        ax.set_ylabel("Frecuencia")
        ax.set_title("Distribución del precio de coches usados")
        ax.yaxis.set_major_formatter(
            mtick.FuncFormatter(lambda x, pos: f"{int(x/1000)}k")
        )
        ax.xaxis.set_major_formatter(
            mtick.FuncFormatter(lambda x, pos: f"{int(x/1000)}k")
        )

        st.pyplot(fig)

        with st.expander("Insight"):
            st.write(
                 """
            La mayoría de los coches usados se concentran por debajo de 500.000 $.
            Los valores extremos corresponden a vehículos premium o de alta gama.
            """
            )

    # --- Gráfica 2: Precio vs kilometraje ---
    with g2:
        fig, ax = plt.subplots(figsize=(5, 2))

        ax.scatter(df_filtered["milage"], df_filtered[TARGET], alpha=0.4)
        ax.set_xlabel("Kilometros (KM)")
        ax.set_ylabel("Precio ($)")
        ax.set_title("Kilometraje vs Precio")
        ax.yaxis.set_major_formatter(
            mtick.FuncFormatter(lambda x, pos: f"{int(x/1000)}k")
        )

        ax.xaxis.set_major_formatter(
            mtick.FuncFormatter(lambda x, pos: f"{int(x/1000)}k")
        )

        st.pyplot(fig)

        with st.expander("Insight"):
            st.write(
                "Existe una tendencia negativa entre el kilometraje y el precio: a mayor kilometraje, menor precio."
            )

    st.markdown('</div>', unsafe_allow_html=True)
    
    g3, g4 = st.columns(2)
    
    # --- Gráfica 3: Boxplot del precio ---
    with g3:
        fig, ax = plt.subplots(figsize=(5, 1.5))
        ax.set_xlabel("Precio ($)")
        ax.boxplot(df_filtered[TARGET], vert=False)
        ax.set_title("Boxplot del precio")
        ax.xaxis.set_major_formatter(
            mtick.FuncFormatter(lambda x, pos: f"{int(x/1000)}k")
        )
        st.pyplot(fig)

        with st.expander("Insight"):
            "Algunos coches tienen precios extremadamente altos, lo que indica la presencia de outliers en el dataset."
    st.markdown('</div>', unsafe_allow_html=True)


    # --- Gráfica 4: Año del modelo vs precio ---
    with g4:
        fig, ax = plt.subplots(figsize=(5, 1.5))

        ax.scatter(df_filtered["model_year"], df_filtered[TARGET], alpha=0.4)
        ax.set_xlabel("Año del modelo")
        ax.set_ylabel("Precio ($)")
        ax.set_title("Año del modelo vs Precio")
        ax.yaxis.set_major_formatter(
            mtick.FuncFormatter(lambda x, pos: f"{int(x/1000)}k")
        )

        st.pyplot(fig)
        
        st.markdown("")
        st.markdown("")
        
        with st.expander("Insight"):
            "Hay una clara tendencia positiva entre el año del modelo y el precio: los modelos más nuevos tienden a tener precios más altos."
    st.markdown('</div>', unsafe_allow_html=True)

    

elif section == "🔮 Predicción":
    st.title("Predicción de precio de coche")
    st.write("Introduce las características del coche y el modelo estimará el precio.")

    # Selectores dependientes
    brand = st.selectbox(
        "Marca",
        sorted(brand_model_options.keys())
    )

    models_for_brand = sorted(brand_model_options[brand].keys())

    model_car = st.selectbox(
        "Modelo",
        models_for_brand
    )

    ext_colors = brand_model_options[brand][model_car]["ext_col"]
    int_colors = brand_model_options[brand][model_car]["int_col"]

    # Fallbacks de seguridad
    if not ext_colors:
        ext_colors = sorted(target_encoding_maps["ext_col"]["mapping"].keys())

    if not int_colors:
        int_colors = sorted(target_encoding_maps["int_col"]["mapping"].keys())

    ext_col = st.selectbox("Color exterior", ext_colors)
    int_col = st.selectbox("Color interior", int_colors)

    model_year = st.number_input("Año", 1990, 2024, 2018)
    milage = st.number_input("Kilometraje", 0, 500000, 50000)
    horsepower = st.number_input("Caballos", 50, 1500, 150)
    engine_liters = st.number_input("Litros motor", 0.8, 8.0, 2.0)

    # booleanos
    turbo = st.checkbox("Turbo")
    clean_title = st.checkbox("Clean title (título limpio)")
    accident_none = st.checkbox("Accident: None reported")

    # fuel types
    fuel_E85 = st.checkbox("Fuel: E85 Flex Fuel")
    fuel_Gasoline = st.checkbox("Fuel: Gasoline")
    fuel_Hybrid = st.checkbox("Fuel: Hybrid")
    fuel_PlugIn = st.checkbox("Fuel: Plug-In Hybrid")
    fuel_Unknown = st.checkbox("Fuel: Unknown")

    # ----------------------------
    # PREPARAR INPUT
    # ----------------------------
    input_df = pd.DataFrame([{
        "brand": brand,
        "model": model_car,
        "model_year": model_year,
        "milage": milage,
        "ext_col": ext_col,
        "int_col": int_col,
        "horsepower": horsepower,
        "engine_liters": engine_liters,
        "turbo": turbo,
        "clean_title_Yes": clean_title,
        "accident_None reported": accident_none,
        "fuel_type_E85 Flex Fuel": fuel_E85,
        "fuel_type_Gasoline": fuel_Gasoline,
        "fuel_type_Hybrid": fuel_Hybrid,
        "fuel_type_Plug-In Hybrid": fuel_PlugIn,
        "fuel_type_Unknown": fuel_Unknown
    }])

    # ----------------------------
    # TARGET ENCODING
    # ----------------------------
    for col, enc in target_encoding_maps.items():
        input_df[col] = input_df[col].map(enc["mapping"]).fillna(enc["global_mean"])

    # ----------------------------
    # ORDENAR COLUMNAS
    # ----------------------------
    input_df = input_df.reindex(columns=feature_order, fill_value=0)

    # ----------------------------
    # PREDICCIÓN
    # ----------------------------
    if st.button("Predecir precio"):
        log_price_pred = model.predict(input_df)[0]
        price_pred = np.expm1(log_price_pred)
        st.metric("Precio estimado", f"${price_pred:,.0f}")



elif section == "📈 Rendimiento del Modelo":
    st.markdown(
        """
        <h1 style='text-align:center;'>📈 Rendimiento del Modelo</h1>
        <p style='text-align:center; color: grey;'>
        Evaluación del modelo de regresión seleccionado (XGBoost)
        </p>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # ---------- MÉTRICAS ----------
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("RMSE Train", f"{train_rmse:.4f}")
    col2.metric("RMSE Test", f"{test_rmse:.4f}")
    col3.metric("MAE", f"{mae:.4f}")
    col4.metric("R²", f"{r2:.4f}")

    st.divider()

    # ---------- OVERFITTING ----------
    overfitting = (test_rmse - train_rmse) / train_rmse * 100

    col_a, col_b = st.columns([1, 2])

    with col_a:
        st.metric(
            "Overfitting (%)",
            f"{overfitting:.2f}%",
            delta="OK" if overfitting < 5 else "Revisar"
        )

    with col_b:
        st.markdown(
            f"""
            **Interpretación del rendimiento**

            - El modelo presenta un **bajo nivel de sobreajuste**, con un overfitting del 
              **{overfitting:.2f}%**, inferior al umbral del 5%.
            - El coeficiente de determinación **R² = {r2:.2f}** indica que el modelo explica
              aproximadamente el **66% de la variabilidad** del precio.
            - El **MAE** refleja un error medio adecuado para un problema real de predicción de precios.
            """
        )

    st.divider()

    st.info(
        "Las métricas se obtuvieron tras validación cruzada y optimización del modelo XGBoost, "
        "asegurando una buena capacidad de generalización."
    )

    


