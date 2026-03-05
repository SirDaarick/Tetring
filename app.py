import streamlit as st
import pandas as pd
import datetime

# Configuración de la página (Debe ser la primera línea)
st.set_page_config(page_title="Generador de Horarios", layout="wide", page_icon="📅")

# === INYECCIÓN DE CSS PARA MEJORAR EL DISEÑO ===
st.markdown("""
    <style>
    /* Estilo del título principal */
    .main-header { font-size: 2.8rem; font-weight: 800; color: #7B113A; text-align: center; margin-bottom: 0px; }
    .sub-header { font-size: 1.2rem; color: #555; text-align: center; margin-bottom: 30px; }
    
    /* Botones profesionales con animación */
    div.stButton > button:first-child {
        background-color: #7B113A;
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: bold;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        width: 100%;
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.2);
        background-color: #5A0C2A;
    }
    
    /* Tarjetas de expansores más limpias */
    .streamlit-expanderHeader {
        font-weight: bold !important;
        font-size: 16px !important;
        color: #2C3E50 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Título de la App
st.markdown("<div class='main-header'>Generador Automático de Horarios</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Optimiza tus tiempos, evita empalmes y encuentra tu semestre ideal. <br><span style='font-size: 0.9em; color: #888;'>Desarrollado por Daarick</span></div>", unsafe_allow_html=True)

# ==========================================
# BARRA LATERAL (SIDEBAR) - PANEL DE CONTROL
# ==========================================
with st.sidebar:
    st.markdown("### ⚙️ Panel de Control")
    uploaded_file = st.file_uploader("📂 Sube tu archivo CSV", type="csv")
    
    st.markdown("---")
    st.markdown("### 🎛️ Filtros Globales")
    
    turno = st.radio(
        "⏱️ Selecciona tu turno:",
        ["Matutino", "Vespertino", "Mixto"],
        help="Solo usará grupos con 'M' (Matutino) o 'V' (Vespertino)."
    )
    
    rango_horario = st.slider(
        "⏰ Delimita tu horario:",
        min_value=datetime.time(6, 0),
        max_value=datetime.time(22, 0),
        value=(datetime.time(7, 0), datetime.time(22, 0)),
        format="HH:mm",
        step=datetime.timedelta(minutes=30)
    )
    
    max_resultados = st.selectbox(
        "🛡️ Protección de RAM (Top Resultados):",
        [50, 100, 200, 500],
        index=0,
        help="Limita cuántas tablas se dibujan en pantalla."
    )
    
    st.markdown("---")
    with st.expander("ℹ️ ¿Cómo armar mi CSV?"):
        st.write("Sube capturas de tus horarios a una IA (Gemini/ChatGPT) y usa este prompt:")
        st.code("""Actúa como extractor de datos. Convierte los horarios de las imágenes en CSV.
Columnas exactas: Grupo, Asignatura, Profesor, Edificio, Salón, Lun, Mar, Mie, Jue, Vie.
Formato hora: HH:MM-HH:MM. Celdas vacías si no hay clase.""", language="text")

# ==========================================
# ÁREA PRINCIPAL - SELECCIÓN Y RESULTADOS
# ==========================================
if uploaded_file is None:
    st.info("👈 **Para comenzar, sube tu archivo `materias.csv` en el Panel de Control a tu izquierda.**")
else:
    df = pd.read_csv(uploaded_file)
    df = df.fillna('')
    
    # Limpieza de datos (Evita los duplicados)
    df['Grupo'] = df['Grupo'].astype(str).str.strip()
    df['Asignatura'] = df['Asignatura'].astype(str).str.strip()
    df = df.drop_duplicates()
    df = df.drop_duplicates(subset=['Grupo', 'Asignatura'], keep='first')

    columnas_requeridas = ['Asignatura', 'Grupo', 'Profesor', 'Lun', 'Mar', 'Mie', 'Jue', 'Vie']
    if not all(col in df.columns for col in columnas_requeridas):
        st.error(f"El CSV debe contener estas columnas: {', '.join(columnas_requeridas)}")
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

        st.markdown("### 📚 Selecciona las materias a cursar")
        
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
        
        st.markdown("<br>", unsafe_allow_html=True) # Espacio visual
        
        if st.button("🚀 GENERAR HORARIOS INTELIGENTES"):
            if not materias_seleccionadas:
                st.warning("⚠️ Selecciona al menos una materia.")
            else:
                with st.spinner('Procesando algoritmo de combinaciones...'):
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
                            st.error(f"❌ '{subj}' no tiene grupos disponibles de {hora_inicio_limit.strftime('%H:%M')} a {hora_fin_limit.strftime('%H:%M')}.")
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
                            st.error("❌ Imposible generar horario sin empalmes con estos parámetros.")
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
# RENDERIZADO DE RESULTADOS (FUERA DEL BOTÓN)
# ==========================================
if 'horarios_completos' in st.session_state:
    estado_actual = {
        'materias': sorted(materias_seleccionadas) if 'materias_seleccionadas' in locals() else [],
        'turno': turno if 'turno' in locals() else "Matutino",
        'horario': rango_horario if 'rango_horario' in locals() else ()
    }
    
    if st.session_state.get('estado_busqueda') != estado_actual:
        st.warning("⚠️ **ATENCIÓN:** Has modificado los filtros. Haz clic en **'GENERAR HORARIOS INTELIGENTES'** para actualizar.")
    else:
        st.markdown("---")
        
        # Métrica Visual Superior
        col_met1, col_met2, col_met3 = st.columns(3)
        col_met1.metric(label="Combinaciones Encontradas", value=len(st.session_state['horarios_completos']))
        col_met2.metric(label="Materias Seleccionadas", value=len(materias_seleccionadas))
        col_met3.metric(label="Mejor Opción (Horas Libres)", value=f"{st.session_state['horarios_completos'][0]['free_hours']} hrs")

        st.markdown("### 🔎 Filtro de Profesores")
        
        todos_los_profesores = set()
        for sched in st.session_state['horarios_completos']:
            for row in sched['classes']:
                if row['Profesor'].strip(): todos_los_profesores.add(row['Profesor'])
                    
        profesores_seleccionados = st.multiselect(
            "Priorizar opciones que incluyan a estos profesores:", 
            options=sorted(list(todos_los_profesores))
        )
        
        horarios_filtrados = []
        for sched in st.session_state['horarios_completos']:
            prof_names = [row['Profesor'] for row in sched['classes']]
            if all(prof in prof_names for prof in profesores_seleccionados):
                horarios_filtrados.append(sched)
                
        if not horarios_filtrados:
            st.error("No hay combinaciones que incluyan a todos esos profesores juntos.")
        else:
            max_render = st.session_state['max_resultados_render']
            horarios_a_mostrar = horarios_filtrados[:max_render]
            
            st.success(f"Mostrando {min(len(horarios_filtrados), max_render)} de {len(horarios_filtrados)} opciones disponibles.")
            
            cols_to_show = ['Grupo', 'Asignatura', 'Profesor', 'Edificio', 'Salón', 'Lun', 'Mar', 'Mie', 'Jue', 'Vie']
            
            for idx, sched in enumerate(horarios_a_mostrar, 1):
                with st.expander(f"🏅 Opción {idx} | Horas libres totales: {sched['free_hours']} hrs", expanded=(idx==1)):
                    df_visual = pd.DataFrame(sched['classes'])[cols_to_show]
                    st.dataframe(df_visual, use_container_width=True, hide_index=True)
                    
                    _, col_btn = st.columns([4, 1])
                    with col_btn:
                        csv_data = df_visual.to_csv(index=False).encode('utf-8')
                        st.download_button("📥 Descargar CSV", data=csv_data, file_name=f"horario_opcion_{idx}.csv", key=f"dl_{idx}")