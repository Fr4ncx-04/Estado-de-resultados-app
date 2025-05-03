import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# Configure page settings
st.set_page_config(
    page_title="GameVerse Studios - Sistema Contable",
    layout="wide"
)

# Custom CSS to improve appearance
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

# Application title
st.markdown('<div class="title">GameVerse Studios</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Sistema Contable Integral</div>', unsafe_allow_html=True)

# Navigation
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

# Módulo de transacciones actualizado
def modulo_transacciones_mejorado():
    with st.expander("Registrar Transacción", expanded=True):
        fecha = st.date_input("Fecha")
        tipo_transaccion = st.selectbox("Tipo de Transacción", [
            "Apertura de Cuentas",
            "Compra de Mercancía",
            "Venta de Mercancía",
            "Traspaso entre Cuentas"
        ])
        
        if tipo_transaccion == "Apertura de Cuentas":
            col1, col2 = st.columns(2)
            with col1:
                caja = st.number_input("Monto en Caja", min_value=0.0)
            with col2:
                bancos = st.number_input("Monto en Bancos", min_value=0.0)
            
            if st.button("Registrar Apertura"):
                asiento = generar_asiento_contable(
                    fecha=fecha.strftime("%d/%m/%Y"),
                    concepto="Apertura de cuentas",
                    cuentas_debe=[('Caja', caja), ('Bancos', bancos)],
                    cuentas_haber=[]
                )
                st.session_state.transacciones.append(asiento)
        
        elif tipo_transaccion == "Compra de Mercancía":
            monto = st.number_input("Monto Total Bancos", min_value=0.0)
            if monto > 0:
                neto = monto / 1.16
                iva = neto * 0.16
                
                if st.button("Registrar Compra"):
                    asiento = generar_asiento_contable(
                        fecha=fecha.strftime("%d/%m/%Y"),
                        concepto="Compra de mercancía",
                        cuentas_debe=[('Compras', neto), ('IVA Acreditable', iva)],
                        cuentas_haber=[('Bancos', monto)]
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

# Visualización del libro diario con formato específico
def mostrar_libro_diario():
    st.markdown("""
    <style>
        .libro-diario-table {
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
        }
        .libro-diario-table th, .libro-diario-table td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        .libro-diario-table tr:nth-child(even) {
            background-color: #f2f2f2;
        }
    </style>
    """, unsafe_allow_html=True)
    
    html = """
    <table class="libro-diario-table">
        <tr>
            <th>Fecha</th>
            <th>Cuentas</th>
            <th>Debe</th>
            <th>Haber</th>
            <th>Concepto</th>
        </tr>
    """
    
    for trans in st.session_state.transacciones:
        cuentas = trans['Cuentas'].split('\n')
        debe = trans['Debe'].split('\n')
        haber = trans['Haber'].split('\n')
        concepto = trans['Concepto']
        
        for i in range(len(cuentas)):
            html += f"""
            <tr>
                <td>{trans['Fecha'] if i == 0 else ''}</td>
                <td>{cuentas[i]}</td>
                <td>{debe[i]}</td>
                <td>{haber[i]}</td>
                <td>{concepto if i == 0 else ''}</td>
            </tr>
            """
    
    html += "</table>"
    st.markdown(html, unsafe_allow_html=True)
    
    # Cálculo de totales
    total_debe = sum(float(d.replace(",", "")) for trans in st.session_state.transacciones for d in trans['Debe'].split('\n'))
    total_haber = sum(float(h.replace(",", "")) for trans in st.session_state.transacciones for h in trans['Haber'].split('\n'))
    
    st.markdown(f"**Total Debe:** ${total_debe:,.2f}  \n**Total Haber:** ${total_haber:,.2f}")
    if total_debe != total_haber:
        st.error(f"Desbalance detectado: ${abs(total_debe - total_haber):,.2f}")

# Process journal entries to accounts (mayor)
def procesar_mayor():
    mayor = {}
    for trans in st.session_state.transacciones:
        cuentas = trans['Cuentas'].split('\n')
        debe = [float(d.replace(",", "")) for d in trans['Debe'].split('\n')]
        haber = [float(h.replace(",", "")) for h in trans['Haber'].split('\n')]
        
        for i, cuenta in enumerate(cuentas):
            if cuenta not in mayor:
                mayor[cuenta] = {'debe': 0.0, 'haber': 0.0}
            
            mayor[cuenta]['debe'] += debe[i]
            mayor[cuenta]['haber'] += haber[i]
    
    return mayor

# Generate balance (balanza de comprobación)
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

def arqueo_caja(monto):
    denominaciones = [
        1000, 500, 200, 100, 50, 20,  # Billetes
        20, 10, 5, 2, 1, 0.5  # Monedas
    ]
    
    desglose = {}
    monto_restante = round(monto, 2)
    
    for denom in sorted(denominaciones, reverse=True):
        if monto_restante >= denom:
            cantidad = int(monto_restante // denom)
            desglose[denom] = cantidad
            monto_restante = round(monto_restante - (cantidad * denom), 2)
    
    # Ajuste final para centavos
    if monto_restante > 0:
        if 0.5 in desglose:
            desglose[0.5] += 1
        else:
            desglose[0.5] = 1
        monto_restante -= 0.5
    
    return desglose

# Home page content
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
    mostrar_libro_diario()
    
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
        mayor = procesar_mayor()
        balanza, total_debe, total_haber = generar_balanza(mayor)
        balanza_df = pd.DataFrame(balanza)
        
        tab1, tab2 = st.tabs(["Libro Mayor", "Balanza"])
        with tab1:
            cuenta_seleccionada = st.selectbox("Seleccionar Cuenta", list(mayor.keys()))
            st.write(f"**Movimientos de {cuenta_seleccionada}**")
            # Mostrar movimientos específicos de la cuenta
        with tab2:
            st.dataframe(balanza_df, use_container_width=True)
            st.metric("Total Deudor", f"${total_debe:,.2f}")
            st.metric("Total Acreedor", f"${total_haber:,.2f}")
    else:
        st.warning("No hay datos para mostrar")

elif page == "Estado de Resultados":
    st.markdown('<div class="section-header">Estado de Resultados</div>', unsafe_allow_html=True)
    
    if st.session_state.transacciones:
        mayor = procesar_mayor()
        estado = generar_estado_resultados(mayor)
        
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

# En la página de Arqueo de Caja
elif page == "Arqueo de Caja":
    st.markdown('<div class="section-header">Arqueo de Caja</div>', unsafe_allow_html=True)
    
    monto = st.number_input("Ingrese el monto total en efectivo:", min_value=0.0, step=0.5, format="%.2f")
    
    if monto > 0:
        desglose = arqueo_caja(monto)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Desglose de Billetes")
            for denom in [1000, 500, 200, 100, 50, 20]:
                if denom in desglose and desglose[denom] > 0:
                    st.write(f"{desglose[denom]} billetes de ${denom:,.2f}")
        
        with col2:
            st.markdown("### Desglose de Monedas")
            for denom in [20, 10, 5, 2, 1, 0.5]:
                if denom in desglose and desglose[denom] > 0:
                    tipo = "monedas" if denom < 20 else "billetes"
                    st.write(f"{desglose[denom]} {tipo} de ${denom:,.2f}")
        
        total_calculado = sum(denom * cant for denom, cant in desglose.items())
        st.markdown(f"**Total verificado:** ${total_calculado:,.2f}")
        if abs(total_calculado - monto) <= 0.05:
            st.success("¡Arqueo correcto!")
        else:
            st.error(f"Discrepancia: ${abs(total_calculado - monto):,.2f}")