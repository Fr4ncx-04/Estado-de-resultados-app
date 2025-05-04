import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# configuracion de la pagina
st.set_page_config(
    page_title="GameVerse Studios - Sistema Contable",
    layout="wide"
)

# configuracion de la apariencia
st.markdown("""
<style>
    .title {
        text-align: center;
        font-size: 42px;
        font-weight: bold;
        margin-bottom: 20px;
        color: #1E3A8A;
    }
    .subtitle {
        text-align: center;
        font-size: 24px;
        margin-bottom: 30px;
        color: #2563EB;
    }
    .section-header {
        font-size: 24px;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 15px;
        color: #1E3A8A;
        padding-bottom: 5px;
        border-bottom: 2px solid #2563EB;
    }
    .card {
        background-color: #F3F4F6;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .highlight {
        background-color: #DBEAFE;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .result-box {
        background-color: #EFF6FF;
        border: 1px solid #BFDBFE;
        border-radius: 8px;
        padding: 15px;
        margin-top: 20px;
    }
    .warning {
        color: #DC2626;
        font-weight: bold;
    }
    .success {
        color: #059669;
        font-weight: bold;
    }
    .table-container {
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# tutulo de la pagina
st.markdown('<div class="title">GameVerse Studios</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Sistema Contable Integral</div>', unsafe_allow_html=True)

# navegacion
st.sidebar.title("Navegación")
page = st.sidebar.radio("Seleccione una opción:", 
                    ["Inicio", "Libro Diario", "Mayor y Balanza", "Estado de Resultados", "Arqueo de Caja"])

# Variables de estado
if 'transacciones' not in st.session_state:
    st.session_state.transacciones = []
if 'saldo_caja' not in st.session_state:
    st.session_state.saldo_caja = 0.0
if 'saldo_bancos' not in st.session_state:
    st.session_state.saldo_bancos = 0.0

# Funciones auxiliares
def calcular_iva(monto, tasa=0.16):
    return monto * tasa

def generar_asiento_contable(fecha, concepto, cuentas_debe, cuentas_haber):
    # Calcular totales
    total_debe = sum(monto for _, monto in cuentas_debe)
    total_haber = sum(monto for _, monto in cuentas_haber)
    
    # Validar balance
    if abs(total_debe - total_haber) > 0.01:
        raise ValueError("El asiento no está balanceado")
    
    # Construir estructura del asiento
    asiento = {
        'Fecha': fecha,
        'Cuentas': [],
        'Debe': [],
        'Haber': [],
        'Concepto': concepto
    }
    
    # Procesar cuentas en Debe
    for cuenta, monto in cuentas_debe:
        asiento['Cuentas'].append(cuenta)
        asiento['Debe'].append(f"{monto:,.2f}")
        asiento['Haber'].append("0.00")
    
    # Procesar cuentas en Haber
    for cuenta, monto in cuentas_haber:
        asiento['Cuentas'].append(cuenta)
        asiento['Debe'].append("0.00")
        asiento['Haber'].append(f"{monto:,.2f}")
    
    # Unir con saltos de línea
    asiento['Cuentas'] = '\n'.join(asiento['Cuentas'])
    asiento['Debe'] = '\n'.join(asiento['Debe'])
    asiento['Haber'] = '\n'.join(asiento['Haber'])
    
    return asiento

# Ejemplo de uso para apertura de cuentas
asiento_apertura = generar_asiento_contable(
    fecha="10/04/2025",
    concepto="Apertura de cuentas",
    cuentas_debe=[("Caja", 8512990.00), ("Bancos", 481000.00)],
    cuentas_haber=[("Capital Social", 8512990.00 + 481000.00)]  # Contrapartida automática
)

# Módulo de transacciones
def modulo_transacciones_mejorado():
    with st.expander("Registrar Transacción", expanded=True):
        fecha = st.date_input("Fecha")
        tipo = st.selectbox("Tipo de Transacción", [
            "Apertura de Cuentas",          # 1
            "Compra de Mercancía",          # 2
            "Descuento Pronto Pago Compras",# 3
            "Venta al Contado",             # 4
            "Descuento Pronto Pago Ventas", # 5
            "Devolución de Compras",        # 6
            "Devolución de Ventas",         # 7
            "Rebajas en Compras",           # 8
            "Rebajas en Ventas",            # 9
            "Pago Gastos Generales"         # 10
        ])
        
        if tipo == "Apertura de Cuentas":
            caja   = st.number_input("Monto en Caja", min_value=0.0)
            bancos = st.number_input("Monto en Bancos", min_value=0.0)
            if st.button("Registrar"):
                total = caja + bancos
                asiento = generar_asiento_contable(
                    fecha=fecha.strftime("%d/%m/%Y"),
                    concepto="Apertura de cuentas",
                    cuentas_debe=[("Caja", caja), ("Bancos", bancos)],
                    cuentas_haber=[("Capital Social", total)]
                )
                st.session_state.transacciones.append(asiento)

        elif tipo == "Compra de Mercancía":
            compras = st.number_input("Monto Compras", min_value=0.0)
            if st.button("Registrar"):
                neto = compras
                iva  = neto * 0.16
                total = neto + iva
                asiento = generar_asiento_contable(
                    fecha=fecha.strftime("%d/%m/%Y"),
                    concepto="Compra de mercancía",
                    cuentas_debe=[("Compras", neto), ("IVA Acreditable", iva)],
                    cuentas_haber=[("Bancos", total)]
                )
                st.session_state.transacciones.append(asiento)

        elif tipo == "Descuento Pronto Pago Compras":
            recibido = st.number_input("Monto Bancos (10% Pronto Pago)", min_value=0.0)
            if st.button("Registrar"):
                neto = recibido / 1.16
                iva  = neto * 0.16
                descuento = recibido
                asiento = generar_asiento_contable(
                    fecha=fecha.strftime("%d/%m/%Y"),
                    concepto="Descuento Pronto Pago Compras 10%",
                    cuentas_debe=[("Bancos", recibido)],
                    cuentas_haber=[("Descuentos s/compras", neto), ("IVA Acreditable", iva)]
                )
                st.session_state.transacciones.append(asiento)

        elif tipo == "Venta al Contado":
            recibido = st.number_input("Monto Bancos", min_value=0.0)
            if st.button("Registrar"):
                neto = recibido / 1.16
                iva  = neto * 0.16
                asiento = generar_asiento_contable(
                    fecha=fecha.strftime("%d/%m/%Y"),
                    concepto="Venta de mercancía al contado",
                    cuentas_debe=[("Bancos", recibido)],
                    cuentas_haber=[("Ventas", neto), ("IVA Trasladado", iva)]
                )
                st.session_state.transacciones.append(asiento)

        elif tipo == "Descuento Pronto Pago Ventas":
            descuento = st.number_input("Monto Descuento (Excluyendo IVA)", min_value=0.0)
            if st.button("Registrar"):
                iva = descuento * 0.16
                total = descuento + iva
                asiento = generar_asiento_contable(
                    fecha=fecha.strftime("%d/%m/%Y"),
                    concepto="Descuento Pronto Pago Ventas",
                    cuentas_debe=[("Descuentos s/ventas", descuento), ("IVA Trasladado", iva)],
                    cuentas_haber=[("Bancos", total)]
                )
                st.session_state.transacciones.append(asiento)

        elif tipo == "Devolución de Compras":
            monto = st.number_input("Monto Bancos Devolución", min_value=0.0)
            if st.button("Registrar"):
                neto = monto / 1.16
                iva  = neto * 0.16
                asiento = generar_asiento_contable(
                    fecha=fecha.strftime("%d/%m/%Y"),
                    concepto="Devolución de compras",
                    cuentas_debe=[
                        ("Bancos", monto),
                    ],
                    cuentas_haber=[
                        ("Devoluciones s/compras", neto),
                        ("IVA Acreditable", iva)
                    ]
                )
                st.session_state.transacciones.append(asiento)

        elif tipo == "Devolución de Ventas":
            monto = st.number_input("Monto Bancos Devolución", min_value=0.0)
            if st.button("Registrar"):
                neto = monto / 1.16
                iva  = neto * 0.16
                asiento = generar_asiento_contable(
                    fecha=fecha.strftime("%d/%m/%Y"),
                    concepto="Devolución de ventas",
                    cuentas_debe=[("Devoluciones s/ventas", neto), ("IVA Trasladado", iva)],
                    cuentas_haber=[("Bancos", monto)]
                )
                st.session_state.transacciones.append(asiento)

        elif tipo == "Rebajas en Compras":
            monto = st.number_input("Monto Rebaja (bancos)", min_value=0.0)
            if st.button("Registrar"):
                neto = monto / 1.16
                iva  = neto * 0.16
                asiento = generar_asiento_contable(
                    fecha=fecha.strftime("%d/%m/%Y"),
                    concepto="Rebajas en compras",
                    cuentas_debe=[
                        ("Bancos", monto),
                    ],
                    cuentas_haber=[
                        ("Rebajas s/compras", neto),
                        ("IVA Acreditable", iva)
                    ]
                )
                st.session_state.transacciones.append(asiento)

        elif tipo == "Rebajas en Ventas":
            monto = st.number_input("Monto Rebaja (bancos)", min_value=0.0)
            if st.button("Registrar"):
                neto = monto / 1.16
                iva  = neto * 0.16
                asiento = generar_asiento_contable(
                    fecha=fecha.strftime("%d/%m/%Y"),
                    concepto="Rebajas en ventas",
                    cuentas_debe=[("Rebajas s/ventas", neto), ("IVA Trasladado", iva)],
                    cuentas_haber=[("Bancos", monto)]
                )
                st.session_state.transacciones.append(asiento)

        elif tipo == "Pago Gastos Generales":
            pago = st.number_input("Monto Gastos (bancos)", min_value=0.0)
            if st.button("Registrar"):
                neto = pago / 1.16
                iva  = neto * 0.16
                asiento = generar_asiento_contable(
                    fecha=fecha.strftime("%d/%m/%Y"),
                    concepto="Pago Gastos Generales",
                    cuentas_debe=[("Gastos Generales", neto), ("IVA Acreditable", iva)],
                    cuentas_haber=[("Bancos", pago)]
                )
                st.session_state.transacciones.append(asiento)

def registrar_compra(fecha, monto_total):
    neto = monto_total / 1.16
    iva = neto * 0.16
    
    return generar_asiento_contable(
        fecha=fecha,
        concepto="Compra de mercancía",
        cuentas_debe=[
            ("Compras", neto),
            ("IVA Acreditable", iva)
        ],
        cuentas_haber=[
            ("Bancos", monto_total)
        ]
    )

# Ejemplo de compra de $2,320.00
transaccion_compra = registrar_compra("10/04/2025", 2320.00)

# Visualización del libro diario
def mostrar_libro_diario_mejorado():
    filas = []
    total_debe = 0.0
    total_haber = 0.0

    for trans in st.session_state.transacciones:
        fecha = trans.get('Fecha', '')
        cuentas = trans.get('Cuentas', '').split('\n')
        debe   = trans.get('Debe',   '').split('\n')
        haber  = trans.get('Haber',  '').split('\n')

        for cuenta, d_str, h_str in zip(cuentas, debe, haber):
            # Convertimos a float
            try:
                d = float(d_str.replace(",", "")) if d_str else 0.0
            except:
                d = 0.0
            try:
                h = float(h_str.replace(",", "")) if h_str else 0.0
            except:
                h = 0.0

            filas.append({
                'Fecha': fecha,
                'Cuenta': cuenta,
                'Debe': d,
                'Haber': h
            })

            total_debe  += d
            total_haber += h

    #Crear el DataFrame
    if filas:
        diario_df = pd.DataFrame(filas)
        st.dataframe(diario_df, use_container_width=True, hide_index=True)
    else:
        st.warning("No hay transacciones para mostrar en el Diario")
        return

    #Mostrar métricas de totales
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Debe",  f"${total_debe:,.2f}")
    with col2:
        st.metric("Total Haber", f"${total_haber:,.2f}")

    #Balance
    if abs(total_debe - total_haber) < 0.01:
        st.success("✅ Libro balanceado")
    else:
        st.error(f"❌ Desbalance: ${abs(total_debe - total_haber):,.2f}")
        
def obtener_df_diario():
    """Construye un DataFrame con columnas [Fecha, Cuenta, Debe, Haber] idéntico
        al que se muestra en pantalla."""
    filas = []
    for trans in st.session_state.transacciones:
        fecha   = trans.get('Fecha', '')
        cuentas = trans.get('Cuentas',   '').split('\n')
        debe    = trans.get('Debe',      '').split('\n')
        haber   = trans.get('Haber',     '').split('\n')
        for c, d_str, h_str in zip(cuentas, debe, haber):
            try:
                d = float(d_str.replace(",", "")) if d_str else 0.0
            except:
                d = 0.0
            try:
                h = float(h_str.replace(",", "")) if h_str else 0.0
            except:
                h = 0.0
            filas.append({
                "Fecha":  fecha,
                "Cuenta": c,
                "Debe":   d,
                "Haber":  h
            })
    return pd.DataFrame(filas)


def procesar_mayor_mejorado():
    """Agrupa el DataFrame diario por cuenta y devuelve un dict con saldos."""
    df = obtener_df_diario()
    if df.empty:
        return {}
    grp = df.groupby("Cuenta")[["Debe", "Haber"]].sum().reset_index()
    mayor = {
        row["Cuenta"]: {"debe": row["Debe"], "haber": row["Haber"]}
        for _, row in grp.iterrows()
    }
    return mayor


def mostrar_mayor_y_balanza():
    mayor = procesar_mayor_mejorado()
    if not mayor:
        st.warning("No hay datos para Libro Mayor")
        return
    
    #generar apariencia mayor
    mayor_rows = []
    for cuenta, sal in mayor.items():
        mayor_rows.append({
            "Cuenta": cuenta,
            "Total Debe":   sal["debe"],
            "Total Haber":  sal["haber"],
            "Saldo Deudor": max(sal["debe"] - sal["haber"], 0),
            "Saldo Acreedor": max(sal["haber"] - sal["debe"], 0)
        })
    mayor_df = pd.DataFrame(mayor_rows)
    st.markdown("### Libro Mayor")
    st.dataframe(mayor_df, use_container_width=True, hide_index=True)

    # Generar la balanza de comprobación
    balanza = mayor_df[["Cuenta", "Saldo Deudor", "Saldo Acreedor"]]
    total_deudor  = balanza["Saldo Deudor"].sum()
    total_acreedor= balanza["Saldo Acreedor"].sum()

    st.markdown("### Balanza de Comprobación")
    st.dataframe(balanza, use_container_width=True, hide_index=True)
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Deudor",   f"${total_deudor:,.2f}")
    with col2:
        st.metric("Total Acreedor", f"${total_acreedor:,.2f}")
    if abs(total_deudor - total_acreedor) < 0.01:
        st.success("✅ Balanza balanceada")
    else:
        st.error(f"❌ Desbalance en balanza: ${abs(total_deudor - total_acreedor):,.2f}")

# Generar balanza de comprobación
def generar_balanza(mayor):
    balanza = []
    total_debe = 0
    total_haber = 0
    
    for cuenta, saldos in mayor.items():
        saldo_deudor = max(saldos['debe'] - saldos['haber'], 0)
        saldo_acreedor = max(saldos['haber'] - saldos['debe'], 0)
        
        balanza.append({
            'Cuenta': cuenta,
            'Debe': saldos['debe'],
            'Haber': saldos['haber'],
            'Saldo Deudor': saldo_deudor,
            'Saldo Acreedor': saldo_acreedor
        })
        
        total_debe += saldo_deudor
        total_haber += saldo_acreedor
    
    return balanza, total_debe, total_haber

def generar_estado_resultados(mayor):
    # Extraer valores reales del mayor
    ventas = mayor.get('Ventas', {'haber': 0})['haber']
    descuentos_ventas = mayor.get('Descuentos s/ventas', {'debe': 0})['debe']
    devoluciones_ventas = mayor.get('Devoluciones s/ventas', {'debe': 0})['debe']
    rebajas_ventas = mayor.get('Rebajas s/ventas', {'debe': 0})['debe']
    
    compras = mayor.get('Compras', {'debe': 0})['debe']
    descuentos_compras = mayor.get('Descuentos s/compras', {'haber': 0})['haber']
    devoluciones_compras = mayor.get('Devoluciones s/compras', {'haber': 0})['haber']
    rebajas_compras = mayor.get('Rebajas s/compras', {'haber': 0})['haber']

    # Cálculos según especificación
    ventas_netas = ventas + descuentos_ventas + devoluciones_ventas + rebajas_ventas
    compras_totales = compras
    compras_netas = compras + descuentos_compras + devoluciones_compras + rebajas_compras
    total_mercancia = compras_netas
    costo_ventas = compras_netas + (compras_netas * 0.0003)  # 0.03%
    utilidad_bruta = ventas_netas - costo_ventas
    perdida_operacion = utilidad_bruta

    return {
        'ventas_netas': ventas_netas,
        'compras_totales': compras_totales,
        'compras_netas': compras_netas,
        'total_mercancia': total_mercancia,
        'costo_ventas': costo_ventas,
        'utilidad_bruta': utilidad_bruta,
        'perdida_operacion': perdida_operacion
    }

def obtener_ultimo_saldo_caja():
    for trans in reversed(st.session_state.transacciones):
        cuentas = trans['Cuentas'].split('\n')
        debe    = trans['Debe'].split('\n')
        haber   = trans['Haber'].split('\n')
        for c, d_str, h_str in zip(cuentas, debe, haber):
            if c == 'Caja':
                try:
                    return float(d_str.replace(',', ''))
                except:
                    return 0.0
    return 0.0

def arqueo_caja(monto):
    """
    Devuelve un desglose en un único dict {denominación: cantidad},
    garantizando al menos 1 unidad de cada denom y completando el resto greedy.
    """
    # Lista de todas las denominaciones, de mayor a menor
    denom = [1000, 500, 200, 100, 50, 20, 10, 5, 2, 1, 0.5]
    desglose = {d: 1 for d in denom}
    usado = sum(d for d in denom)  
    if usado > monto:
        return arqueo_caja_greedy(monto, denom)

    restante = round(monto - usado, 2)

    for d in denom:
        extra = int(restante // d)
        if extra:
            desglose[d] += extra
            restante = round(restante - extra * d, 2)
        if restante < 0.01:
            break

    return desglose

def arqueo_caja_greedy(monto, denom):
    desglose = {}
    restante = monto
    for d in denom:
        cnt = int(restante // d)
        if cnt:
            desglose[d] = cnt
            restante = round(restante - cnt * d, 2)
        if restante < 0.01:
            break
    return desglose

# Home page
if page == "Inicio":
    st.markdown('<div class="section-header">Bienvenido al Sistema Contable de GameVersito Studios</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Módulos Disponibles")
        st.write("• Libro Diario: Registro cronológico de transacciones")
        st.write("• Mayor y Balanza: Agrupación de transacciones por cuenta")
        st.write("• Estado de Resultados: Reporte de ingresos y gastos")
        st.write("• Arqueo de Caja: Verificación física del efectivo")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Saldos Actuales")
        st.metric("Saldo en Caja", f"${st.session_state.saldo_caja:,.2f}")
        st.metric("Saldo en Bancos", f"${st.session_state.saldo_bancos:,.2f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.plotly_chart(px.bar(
        x=['Caja', 'Bancos'],
        y=[st.session_state.saldo_caja, st.session_state.saldo_bancos],
        title="Liquidez Actual",
        labels={'x': 'Cuenta', 'y': 'Saldo'},
        color=['Caja', 'Bancos']
    ), use_container_width=True)

# Libro Diario page
elif page == "Libro Diario":
    st.markdown('<div class="section-header">Libro Diario</div>', unsafe_allow_html=True)
    modulo_transacciones_mejorado()
    mostrar_libro_diario_mejorado()
    
    if st.session_state.transacciones:
        diario_df = pd.DataFrame(st.session_state.transacciones)
        st.dataframe(diario_df, use_container_width=True, hide_index=True)
        
        # Cálculo de totales
        total_debe = sum(float(d.replace(",", "")) 
                    for trans in st.session_state.transacciones 
                    for d in trans['Debe'].split('\n'))
        total_haber = sum(float(h.replace(",", "")) 
                    for trans in st.session_state.transacciones 
                    for h in trans['Haber'].split('\n'))
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Debe", f"${total_debe:,.2f}")
        with col2:
            st.metric("Total Haber", f"${total_haber:,.2f}")
        
        if total_debe == total_haber:
            st.success("✅ Libro balanceado")
        else:
            st.error(f"❌ Desbalance: ${abs(total_debe - total_haber):,.2f}")
    else:
        st.warning("No hay transacciones registradas")

# Mayor y Balanza page
elif page == "Mayor y Balanza":
    st.markdown('<div class="section-header">Libro Mayor y Balanza</div>', unsafe_allow_html=True)

    if st.session_state.transacciones:
        # Obtén el dict de saldos por cuenta:
        mayor_dict = procesar_mayor_mejorado()

        # 2) Usa ese dict para generar la balanza:
        balanza, total_debe, total_haber = generar_balanza(mayor_dict)
        balanza_df = pd.DataFrame(balanza)

        # Muestra ambas pestañas:
        tab1, tab2 = st.tabs(["Libro Mayor", "Balanza"])
        with tab1:
            st.subheader("Libro Mayor")
            mayor_rows = []
            for cuenta, sal in mayor_dict.items():
                mayor_rows.append({
                    "Cuenta": cuenta,
                    "Total Debe":    sal["debe"],
                    "Total Haber":   sal["haber"],
                    "Saldo Deudor":  max(sal["debe"] - sal["haber"], 0),
                    "Saldo Acreedor":max(sal["haber"] - sal["debe"], 0)
                })
            mayor_df = pd.DataFrame(mayor_rows)
            st.dataframe(mayor_df, use_container_width=True, hide_index=True)

        with tab2:
            st.subheader("Balanza de Comprobación")
            st.dataframe(balanza_df, use_container_width=True, hide_index=True)
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Deudor",   f"${total_debe:,.2f}")
            with col2:
                st.metric("Total Acreedor", f"${total_haber:,.2f}")

    else:
        st.warning("No hay datos para mostrar")

elif page == "Estado de Resultados":
    st.markdown('<div class="section-header">Estado de Resultados</div>', unsafe_allow_html=True)
    
    if st.session_state.transacciones:
        mayor_dict = procesar_mayor_mejorado()
        estado = generar_estado_resultados(mayor_dict)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            st.markdown("### GameVersito Studios")
            st.markdown("### Estado de Resultados")
            st.markdown("---")
            
            st.markdown("**Ventas Netas**")
            st.write(f"${estado['ventas_netas']:,.2f}")
            
            st.markdown("**Compras Totales**")
            st.write(f"${estado['compras_totales']:,.2f}")
            
            st.markdown("**Compras Netas**")
            st.write(f"${estado['compras_netas']:,.2f}")
            
            st.markdown("**Total Mercancía**")
            st.write(f"${estado['total_mercancia']:,.2f}")
            
            st.markdown("**Costo de Ventas**")
            st.write(f"${estado['costo_ventas']:,.2f}")
            
            st.markdown("**Utilidad Bruta**")
            st.write(f"${estado['utilidad_bruta']:,.2f}")
            
            st.markdown("**Resultado Operativo**")
            st.write(f"${estado['perdida_operacion']:,.2f}")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            fig = px.pie(
                names=['Ventas Netas', 'Costo Ventas', 'Utilidad Bruta'],
                values=[estado['ventas_netas'], estado['costo_ventas'], estado['utilidad_bruta']],
                title='Composición del Resultado'
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No hay transacciones registradas")

# Arqueo de Caja page
elif page == "Arqueo de Caja":
    st.markdown('<div class="section-header">Arqueo de Caja</div>', unsafe_allow_html=True)

    metodo = st.radio("Selecciona método de monto:", [
        "Ingresar manualmente",
        "Usar último saldo de Caja"
    ])
    if metodo == "Usar último saldo de Caja":
        monto = obtener_ultimo_saldo_caja()
        st.markdown(f"**Usando último saldo de Caja:** ${monto:,.2f}")
    else:
        monto = st.number_input("Monto total en efectivo:", min_value=0.0, step=0.5, format="%.2f")

    if monto > 0:
        desglose = arqueo_caja(monto)
        monedas = {d: c for d, c in desglose.items() if d < 20}
        billetes= {d: c for d, c in desglose.items() if d >= 20}

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Monedas")
            for d, c in sorted(monedas.items()):
                st.write(f"{c} × ${d:.2f} = ${c*d:,.2f}")
            total_m = sum(d*c for d, c in monedas.items())
            st.markdown(f"**Total Monedas:** ${total_m:,.2f}")
        with col2:
            st.markdown("### Billetes")
            for d, c in sorted(billetes.items()):
                st.write(f"{c} × ${d:.2f} = ${c*d:,.2f}")
            total_b = sum(d*c for d, c in billetes.items())
            st.markdown(f"**Total Billetes:** ${total_b:,.2f}")

        # Verificación final
        total_calc = total_m + total_b
        st.markdown(f"**Total Arqueo:** ${total_calc:,.2f}")
        if abs(total_calc - monto) < 0.01:
            st.success("✅ Arqueo correcto, sin discrepancias y usando todas las denominaciones.")
        else:
            st.error(f"❌ Discrepancia de ${abs(total_calc - monto):,.2f}")