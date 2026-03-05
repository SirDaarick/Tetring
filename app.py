import streamlit as st
import pandas as pd
import datetime

# Configuración de la página
st.set_page_config(page_title="Tetring: Generador de Horarios", layout="wide", page_icon="🟦")

# === VENTANA EMERGENTE (MODAL) DE INSTRUCCIONES ===
@st.dialog("ℹ️ ¿Cómo generar tu archivo CSV?")
def mostrar_instrucciones():
    st.write("Esta aplicación necesita un archivo `.csv` con la lista de todas las materias disponibles. Para evitar escribirlo a mano, utiliza **Gemini** o **ChatGPT**.")
    st.write("**Pasos a seguir:**")
    st.write("1. Toma capturas de pantalla de los horarios oficiales.")
    st.write("2. Sube las imágenes a la IA y envíale exactamente este prompt:")
    st.code("""Actúa como extractor de datos. Convierte los horarios de las imágenes en código CSV.
Columnas exactas: Grupo, Asignatura, Profesor, Edificio, Salón, Lun, Mar, Mie, Jue, Vie.
Formato de hora: HH:MM-HH:MM (ej. 07:00-08:30). Deja la celda completamente vacía si no hay clase ese día.""", language="text")
    st.write("3. Copia el texto devuelto, guárdalo en un bloc de notas como `materias.csv` y súbelo en el panel izquierdo.")

# === INYECCIÓN DE CSS: MIDNIGHT ACADEMIC & ANIMACIÓN TETRIS ===
st.markdown("""
    <style>
    /* Fondo animado de Tetris aplicado al contenedor principal de Streamlit */
    [data-testid="stAppViewContainer"] {
        background-color: #0b1120;
        background-image: url("data:image/svg+xml,%3Csvg width='120' height='120' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%236366f1' fill-opacity='0.04'%3E%3Cpath d='M20 20 h20 v60 h-20 z M40 60 h20 v20 h-20 z'/%3E%3Cpath d='M80 20 h40 v20 h-40 z M100 40 h20 v40 h-20 z'/%3E%3C/g%3E%3C/svg%3E");
        animation: tetris-fall 30s linear infinite;
    }
    
    @keyframes tetris-fall {
        0% { background-position: 0px -1000px; }
        100% { background-position: 0px 1000px; }
    }

    /* Título principal profesional pero con identidad */
    .main-header { 
        font-size: 2.8rem; 
        font-weight: 800; 
        color: #e2e8f0; 
        margin-bottom: 0px; 
        letter-spacing: -1px;
    }
    .sub-header { 
        font-size: 1.1rem; 
        color: #64748b; 
        margin-bottom: 30px; 
    }
    
    /* Botón principal sutilmente estructurado */
    div.stButton > button:first-child {
        background-color: #3730a3;
        color: white;
        border-radius: 6px; 
        border: 1px solid #4f46e5;
        padding: 10px 24px;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.2s ease;
        width: 100%;
    }
    div.stButton > button:first-child:hover {
        background-color: #4f46e5;
        border-color: #6366f1;
        transform: translateY(-2px);
    }
    
    /* Estilo específico para el botón de instrucciones (Top Right) */
    .btn-instrucciones button {
        background-color: transparent !important;
        border: 1px solid #64748b !important;
        color: #cbd5e1 !important;
        margin-top: 15px;
    }
    .btn-instrucciones button:hover {
        background-color: #1e293b !important;
        color: #f8fafc !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# ENCABEZADO SUPERIOR (Título a la izq, Botón a la der)
# ==========================================
col_titulo, col_boton = st.columns([4, 1])

with col_titulo:
    st.markdown("<div class='main-header'>Tetring: Generador de Horarios</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Organiza y optimiza tus clases sin empalmes. Desarrollado por Daarick.</div>", unsafe_allow_html=True)

with col_boton:
    st.markdown("<div class='btn-instrucciones'>", unsafe_allow_html=True)
    if st.button("ℹ️ Cómo usar"):
        mostrar_instrucciones()
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# BARRA LATERAL (SIDEBAR) - PANEL DE CONTROL
# ==========================================
with st.sidebar:
    st.markdown("### ⚙️ Panel de Control")
    uploaded_file = st.file_uploader("📂 Base de datos (CSV)", type="csv")
    
    st.markdown("---")
    st.markdown("### 🎛️ Filtros Globales")
    
    turno = st.radio(
        "Modalidad de Turno:",
        ["Matutino", "Vespertino", "Mixto"],
        help="Limita los grupos según la nomenclatura oficial ('M' o 'V')."
    )
    
    rango_horario = st.slider(
        "Franja Horaria:",
        min_value=datetime.time(6, 0),
        max_value=datetime.time(22, 0),
        value=(datetime.time(7, 0), datetime.time(22, 0)),
        format="HH:mm",
        step=datetime.timedelta(minutes=30)
    )
    
    max_resultados = st.selectbox(
        "Límite de Renderizado:",
        [50, 100, 200, 500],
        index=0,
        help="Protección de memoria. Límite de opciones a mostrar en pantalla."
    )

# ==========================================
# ÁREA PRINCIPAL
# ==========================================
if uploaded_file is None:
    st.info("👈 **Para comenzar, carga tu archivo `materias.csv` en el panel izquierdo.**")
else:
    df = pd.read_csv(uploaded_file)
    df = df.fillna('')
    
    # Limpieza de datos
    df['Grupo'] = df['Grupo'].astype(str).str.strip()
    df['Asignatura'] = df['Asignatura'].astype(str).str.strip()
    df = df.drop_duplicates()
    df = df.drop_duplicates(subset=['Grupo', 'Asignatura'], keep='first')

    columnas_requeridas = ['Asignatura', 'Grupo', 'Profesor', 'Lun', 'Mar', 'Mie', 'Jue', 'Vie']
    if not all(col in df.columns for col in columnas_requeridas):
        st.error(f"Error de formato. El CSV requiere estas columnas: {', '.join(columnas_requeridas)}")
    else:
        def clasificar_turno(grupo):
            g = str(grupo).upper()
            if 'M' in g: return 'Matutino'
            if 'V' in g: return 'Vespertino'
            return 'Otro'
            
        df['Turno_Calc'] = df['Grupo'].apply(clasificar_turno)

        hora_inicio_limit, hora_fin_limit = rango_horario
        start_limit_slot = hora_inicio_limit.hour * 2 + (1 if hora_inicio_limit.minute >= 30 else 0)
        end_limit_slot = hora_fin_limit.hour * 2 + (1 if hora_fin_limit.minute >= 30 else 0)

        st.markdown("### 📚 Selecciona tus materias")
        
        materias_seleccionadas = []
        
        if turno == "Mixto":
            col_mat, col_vesp = st.columns(2)
            with col_mat:
                st.markdown("##### ☀️ Turno Matutino")
                mat_subjects = sorted(df[df['Turno_Calc'] == 'Matutino']['Asignatura'].unique())
                for materia in mat_subjects:
                    if str(materia).strip() and st.checkbox(materia, key=f"mat_{materia}"):
                        materias_seleccionadas.append(('Matutino', materia))
                        
            with col_vesp:
                st.markdown("##### 🌙 Turno Vespertino")
                vesp_subjects = sorted(df[df['Turno_Calc'] == 'Vespertino']['Asignatura'].unique())
                for materia in vesp_subjects:
                    if str(materia).strip() and st.checkbox(materia, key=f"vesp_{materia}"):
                        materias_seleccionadas.append(('Vespertino', materia))
        else:
            materias_unicas = sorted(df[df['Turno_Calc'] == turno]['Asignatura'].unique())
            cols = st.columns(3)
            for i, materia in enumerate(materias_unicas):
                if str(materia).strip() and cols[i % 3].checkbox(materia, key=materia):
                    materias_seleccionadas.append((turno, materia))
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🚀 Generar Horarios"):
            if not materias_seleccionadas:
                st.warning("⚠️ Selecciona al menos una materia para continuar.")
            else:
                with st.spinner('Procesando combinaciones óptimas...'):
                    st.session_state['estado_busqueda'] = {
                        'materias': sorted(materias_seleccionadas),
                        'turno': turno,
                        'horario': rango_horario
                    }

                    df_final = df.copy()
                    
                    def parse_slots(row):
                        slots = set()
                        for day_idx, day in enumerate(['Lun', 'Mar', 'Mie', 'Jue', 'Vie']):
                            time_str = row[day]
                            if not time_str or time_str == 'X': continue
                            try:
                                start, end = time_str.split('-')
                                sh, sm = map(int, start.split(':'))
                                eh, em = map(int, end.split(':'))
                                start_idx = sh * 2 + (1 if sm >= 30 else 0)
                                end_idx = eh * 2 + (1 if em >= 30 else 0)
                                for s in range(start_idx, end_idx):
                                    slots.add(day_idx * 100 + s)
                            except: pass
                        return slots

                    df_final['all_slots'] = df_final.apply(parse_slots, axis=1)
                    
                    def esta_en_rango(slots):
                        if not slots: return True 
                        for s in slots:
                            time_idx = s % 100
                            if time_idx < start_limit_slot or time_idx >= end_limit_slot: return False
                        return True
                        
                    df_final = df_final[df_final['all_slots'].apply(esta_en_rango)]
                    
                    subjects_data = []
                    es_posible = True
                    
                    for turno_req, subj in materias_seleccionadas:
                        rows = df_final[(df_final['Asignatura'] == subj) & (df_final['Turno_Calc'] == turno_req)].to_dict('records')
                        if not rows:
                            st.error(f"❌ La materia '{subj}' no tiene grupos disponibles de {hora_inicio_limit.strftime('%H:%M')} a {hora_fin_limit.strftime('%H:%M')}.")
                            es_posible = False
                            break
                        subjects_data.append(rows)
                    
                    if es_posible:
                        valid_schedules = []
                        MAX_BUSQUEDA = 20000 
                        subjects_data.sort(key=len)
                        
                        def backtrack(subj_idx, current_schedule, occupied_slots):
                            if len(valid_schedules) >= MAX_BUSQUEDA: return
                            if subj_idx == len(materias_seleccionadas):
                                valid_schedules.append(current_schedule.copy())
                                return
                            for row in subjects_data[subj_idx]:
                                if not row['all_slots'].intersection(occupied_slots):
                                    current_schedule.append(row)
                                    backtrack(subj_idx + 1, current_schedule, occupied_slots.union(row['all_slots']))
                                    current_schedule.pop()

                        backtrack(0, [], set())
                        
                        if not valid_schedules:
                            st.error("❌ No existen combinaciones posibles sin empalmes con estos parámetros.")
                        else:
                            scored_schedules = []
                            for sched in valid_schedules:
                                total_free_hours = 0
                                day_slots = {i: [] for i in range(5)}
                                for row in sched:
                                    for slot in row['all_slots']:
                                        day_slots[slot // 100].append(slot % 100)
                                for day_idx, times in day_slots.items():
                                    if times: total_free_hours += ((max(times) - min(times) + 1) - len(times)) * 0.5
                                scored_schedules.append({'classes': sched, 'free_hours': total_free_hours})

                            scored_schedules.sort(key=lambda x: x['free_hours'])
                            
                            st.session_state['horarios_completos'] = scored_schedules
                            st.session_state['max_resultados_render'] = max_resultados

# ==========================================
# RENDERIZADO DE RESULTADOS
# ==========================================
if 'horarios_completos' in st.session_state:
    estado_actual = {
        'materias': sorted(materias_seleccionadas) if 'materias_seleccionadas' in locals() else [],
        'turno': turno if 'turno' in locals() else "Matutino",
        'horario': rango_horario if 'rango_horario' in locals() else ()
    }
    
    if st.session_state.get('estado_busqueda') != estado_actual:
        st.warning("⚠️ Has modificado los parámetros. Haz clic en **'Generar Horarios'** para recalcular.")
    else:
        st.markdown("---")
        
        col_met1, col_met2, col_met3 = st.columns(3)
        col_met1.metric(label="Opciones Viables", value=len(st.session_state['horarios_completos']))
        col_met2.metric(label="Materias Asignadas", value=len(materias_seleccionadas))
        col_met3.metric(label="Opción Óptima (Horas Libres)", value=f"{st.session_state['horarios_completos'][0]['free_hours']} hrs")

        st.markdown("### 🔎 Filtrar por Catedrático")
        
        todos_los_profesores = set()
        for sched in st.session_state['horarios_completos']:
            for row in sched['classes']:
                if row['Profesor'].strip(): todos_los_profesores.add(row['Profesor'])
                    
        profesores_seleccionados = st.multiselect(
            "Selecciona los profesores requeridos:", 
            options=sorted(list(todos_los_profesores))
        )
        
        horarios_filtrados = []
        for sched in st.session_state['horarios_completos']:
            prof_names = [row['Profesor'] for row in sched['classes']]
            if all(prof in prof_names for prof in profesores_seleccionados):
                horarios_filtrados.append(sched)
                
        if not horarios_filtrados:
            st.error("Ninguna de las combinaciones viables incluye a todos estos profesores juntos.")
        else:
            max_render = st.session_state['max_resultados_render']
            horarios_a_mostrar = horarios_filtrados[:max_render]
            
            st.success(f"Mostrando {min(len(horarios_filtrados), max_render)} de {len(horarios_filtrados)} horarios disponibles.")
            
            cols_to_show = ['Grupo', 'Asignatura', 'Profesor', 'Edificio', 'Salón', 'Lun', 'Mar', 'Mie', 'Jue', 'Vie']
            
            for idx, sched in enumerate(horarios_a_mostrar, 1):
                with st.expander(f"🏅 Opción {idx} | Horas libres totales: {sched['free_hours']} hrs", expanded=(idx==1)):
                    df_visual = pd.DataFrame(sched['classes'])[cols_to_show]
                    st.dataframe(df_visual, use_container_width=True, hide_index=True)
                    
                    _, col_btn = st.columns([4, 1])
                    with col_btn:
                        csv_data = df_visual.to_csv(index=False).encode('utf-8')
                        st.download_button("📥 Descargar CSV", data=csv_data, file_name=f"tetring_horario_{idx}.csv", key=f"dl_{idx}")