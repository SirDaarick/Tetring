import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="Generador de Horarios", layout="wide")

# Firma del creador
st.markdown("<h4 style='text-align: center; color: #888;'>Creado por Daarick</h4>", unsafe_allow_html=True)

st.title("Generador Automático de Horarios")

with st.expander("ℹ️ ¿Cómo usar esta herramienta y crear mi CSV?"):
    st.write("Esta aplicación necesita un archivo `.csv` con la lista de todas las materias disponibles. Para crearlo fácilmente sin tener que escribirlo a mano, puedes usar una Inteligencia Artificial como **Gemini** o **ChatGPT**.")
    st.write("**Pasos:**")
    st.write("1. Toma capturas de pantalla o fotos de los horarios en formato tabla o PDF que te da la escuela.")
    st.write("2. Ve a tu IA favorita, sube las imágenes y envíale exactamente este prompt:")
    
    st.code("""Actúa como un extractor de datos experto. Analiza las imágenes adjuntas que contienen horarios escolares y conviértelos en una tabla de datos. 
Devuélveme ÚNICAMENTE el código en formato CSV (separado por comas) sin ningún texto adicional, saludos o explicaciones.

Reglas obligatorias para el CSV:
1. Las columnas deben ser exactamente estas y en este orden: Grupo, Asignatura, Profesor, Edificio, Salón, Lun, Mar, Mie, Jue, Vie.
2. Las horas deben usar el formato HH:MM-HH:MM (por ejemplo: 07:00-08:30 o 13:00-14:30).
3. Si un día no hay clase para esa materia, deja la celda completamente vacía.
4. Asegúrate de capturar correctamente el Grupo (ejemplo: 6AM1, 6AV1).""", language="text")
    
    st.write("3. Copia el texto que te devuelva la IA, pégalo en el Bloc de notas y guárdalo como `materias.csv`.")
    st.write("4. Sube ese archivo aquí abajo, ajusta tus filtros, selecciona tus materias y ¡listo!")

st.write("Sube tu archivo CSV para ver las materias disponibles, selecciona las que necesites y genera todas las combinaciones posibles sin traslapes.")

uploaded_file = st.file_uploader("Sube tu archivo CSV de materias", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df = df.fillna('')
    
    # === SISTEMA DE LIMPIEZA DE DATOS (Evita los duplicados) ===
    df['Grupo'] = df['Grupo'].astype(str).str.strip()
    df['Asignatura'] = df['Asignatura'].astype(str).str.strip()
    df = df.drop_duplicates()
    df = df.drop_duplicates(subset=['Grupo', 'Asignatura'], keep='first')
    # ===============================================================

    columnas_requeridas = ['Asignatura', 'Grupo', 'Profesor', 'Lun', 'Mar', 'Mie', 'Jue', 'Vie']
    if not all(col in df.columns for col in columnas_requeridas):
        st.error(f"El CSV debe contener las siguientes columnas: {', '.join(columnas_requeridas)}")
    else:
        # Clasificar cada fila estrictamente por la letra de su grupo
        def clasificar_turno(grupo):
            g = str(grupo).upper()
            if 'M' in g: return 'Matutino'
            if 'V' in g: return 'Vespertino'
            return 'Otro'
            
        df['Turno_Calc'] = df['Grupo'].apply(clasificar_turno)

        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            st.subheader("⏱️ Selecciona tu turno:")
            turno = st.radio(
                "Filtrar materias por turno:",
                ["Matutino", "Vespertino", "Mixto"],
                horizontal=True,
                help="Solo usará grupos con 'M' (Matutino) o 'V' (Vespertino). Mixto mostrará todos separados por turno."
            )
            
        with col2:
            st.subheader("⏰ Delimita tu horario:")
            rango_horario = st.slider(
                "Muestra horarios dentro de estas horas:",
                min_value=datetime.time(6, 0),
                max_value=datetime.time(22, 0),
                value=(datetime.time(7, 0), datetime.time(22, 0)),
                format="HH:mm",
                step=datetime.timedelta(minutes=30)
            )
            
        with col3:
            st.subheader("🛡️ Protección de RAM:")
            max_resultados = st.selectbox(
                "Mostrar solo los X mejores horarios:",
                [50, 100, 200, 500],
                index=0,
                help="Limita cuántas tablas se dibujan en pantalla para evitar que tu navegador se congele."
            )
            
        hora_inicio_limit, hora_fin_limit = rango_horario
        
        start_limit_slot = hora_inicio_limit.hour * 2 + (1 if hora_inicio_limit.minute >= 30 else 0)
        end_limit_slot = hora_fin_limit.hour * 2 + (1 if hora_fin_limit.minute >= 30 else 0)

        st.markdown("---")
        st.subheader("📚 Selecciona las materias obligatorias:")
        
        # === NUEVA LÓGICA DE SELECCIÓN ESTRICTA (Sin cambiar nombres) ===
        materias_seleccionadas = [] # Guardará un par: (Turno_Deseado, Nombre_Materia)
        
        if turno == "Mixto":
            col_mat, col_vesp = st.columns(2)
            
            with col_mat:
                st.markdown("#### ☀️ Turno Matutino")
                mat_subjects = sorted(df[df['Turno_Calc'] == 'Matutino']['Asignatura'].unique())
                if not mat_subjects:
                    st.info("No hay materias matutinas.")
                for materia in mat_subjects:
                    if str(materia).strip():
                        if st.checkbox(materia, key=f"mat_{materia}"):
                            materias_seleccionadas.append(('Matutino', materia))
                            
            with col_vesp:
                st.markdown("#### 🌙 Turno Vespertino")
                vesp_subjects = sorted(df[df['Turno_Calc'] == 'Vespertino']['Asignatura'].unique())
                if not vesp_subjects:
                    st.info("No hay materias vespertinas.")
                for materia in vesp_subjects:
                    if str(materia).strip():
                        if st.checkbox(materia, key=f"vesp_{materia}"):
                            materias_seleccionadas.append(('Vespertino', materia))
        else:
            # Si eligió solo Matutino o solo Vespertino
            materias_unicas = sorted(df[df['Turno_Calc'] == turno]['Asignatura'].unique())
            cols = st.columns(3)
            for i, materia in enumerate(materias_unicas):
                if str(materia).strip():
                    if cols[i % 3].checkbox(materia, key=materia):
                        materias_seleccionadas.append((turno, materia))
        
        st.markdown("---")
        
        if st.button("🚀 Generar Horarios"):
            if not materias_seleccionadas:
                st.warning("⚠️ Por favor, selecciona al menos una materia para continuar.")
            else:
                with st.spinner('Filtrando clases y calculando combinaciones...'):
                    
                    # Guardamos el estado exacto de la búsqueda para el control de la página
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
                            if not time_str or time_str == 'X':
                                continue
                            try:
                                start, end = time_str.split('-')
                                sh, sm = map(int, start.split(':'))
                                eh, em = map(int, end.split(':'))
                                start_idx = sh * 2 + (1 if sm >= 30 else 0)
                                end_idx = eh * 2 + (1 if em >= 30 else 0)
                                for s in range(start_idx, end_idx):
                                    slots.add(day_idx * 100 + s)
                            except:
                                pass
                        return slots

                    df_final['all_slots'] = df_final.apply(parse_slots, axis=1)
                    
                    def esta_en_rango(slots):
                        if not slots: return True 
                        for s in slots:
                            time_idx = s % 100
                            if time_idx < start_limit_slot or time_idx >= end_limit_slot:
                                return False
                        return True
                        
                    df_final = df_final[df_final['all_slots'].apply(esta_en_rango)]
                    
                    subjects_data = []
                    es_posible = True
                    
                    # === FILTRO ESTRICTO ===
                    # Busca la materia EXACTA asegurándose que el grupo corresponda al turno solicitado
                    for turno_req, subj in materias_seleccionadas:
                        rows = df_final[(df_final['Asignatura'] == subj) & (df_final['Turno_Calc'] == turno_req)].to_dict('records')
                        if not rows:
                            st.error(f"❌ La materia '{subj}' no tiene grupos disponibles en el turno {turno_req} dentro del horario que elegiste ({hora_inicio_limit.strftime('%H:%M')} a {hora_fin_limit.strftime('%H:%M')}).")
                            es_posible = False
                            break
                        subjects_data.append(rows)
                    
                    if es_posible:
                        valid_schedules = []
                        MAX_BUSQUEDA = 20000 
                        
                        subjects_data.sort(key=len)
                        
                        def backtrack(subj_idx, current_schedule, occupied_slots):
                            if len(valid_schedules) >= MAX_BUSQUEDA:
                                return
                                
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
                            st.error("❌ No se encontraron combinaciones posibles sin traslapes para las materias y el rango de horario seleccionados.")
                        else:
                            scored_schedules = []
                            for sched in valid_schedules:
                                total_free_hours = 0
                                day_slots = {i: [] for i in range(5)}
                                for row in sched:
                                    for slot in row['all_slots']:
                                        day_slots[slot // 100].append(slot % 100)
                                for day_idx, times in day_slots.items():
                                    if times:
                                        total_free_hours += ((max(times) - min(times) + 1) - len(times)) * 0.5
                                scored_schedules.append({'classes': sched, 'free_hours': total_free_hours})

                            scored_schedules.sort(key=lambda x: x['free_hours'])
                            
                            st.session_state['horarios_completos'] = scored_schedules
                            st.session_state['max_resultados_render'] = max_resultados
                            
                            total_encontrados = len(scored_schedules)
                            
                            mensaje_exito = f"✅ ¡Éxito! Se calcularon **{total_encontrados}** combinaciones posibles."
                            if total_encontrados >= 20000:
                                mensaje_exito += " *(Se alcanzó el límite de búsqueda seguro del servidor).* "
                                
                            st.success(mensaje_exito)

# ==========================================
# VISUALIZACIÓN Y FILTROS INTELIGENTES
# ==========================================
if 'horarios_completos' in st.session_state:
    st.markdown("---")
    
    estado_actual = {
        'materias': sorted(materias_seleccionadas) if 'materias_seleccionadas' in locals() else [],
        'turno': turno if 'turno' in locals() else "Matutino",
        'horario': rango_horario if 'rango_horario' in locals() else ()
    }
    
    if st.session_state.get('estado_busqueda') != estado_actual:
        st.warning("⚠️ **ATENCIÓN:** Has modificado las casillas o los filtros. Por favor, haz clic nuevamente en el botón **'🚀 Generar Horarios'** para actualizar las tablas de abajo.")
    else:
        st.subheader("🔎 Resultados y Filtros Adicionales")
        
        todos_los_profesores = set()
        for sched in st.session_state['horarios_completos']:
            for row in sched['classes']:
                if row['Profesor'].strip():
                    todos_los_profesores.add(row['Profesor'])
                    
        lista_profesores_ordenada = sorted(list(todos_los_profesores))
        
        profesores_seleccionados = st.multiselect(
            "Filtrar todas las combinaciones por profesor(es) específico(s):", 
            options=lista_profesores_ordenada,
            placeholder="Escribe para buscar o selecciona de la lista..."
        )
        
        horarios_filtrados = []
        for sched in st.session_state['horarios_completos']:
            prof_names_in_sched = [row['Profesor'] for row in sched['classes']]
            
            matches_all = True
            for prof in profesores_seleccionados:
                if prof not in prof_names_in_sched:
                    matches_all = False
                    break
                    
            if matches_all:
                horarios_filtrados.append(sched)
                
        if not horarios_filtrados:
            st.error("No se encontraron horarios que incluyan a todos los profesores seleccionados simultáneamente.")
        else:
            max_render = st.session_state['max_resultados_render']
            total_filtrados = len(horarios_filtrados)
            
            horarios_a_mostrar = horarios_filtrados[:max_render]
            
            if profesores_seleccionados:
                mensaje = f"Se encontraron **{total_filtrados}** opciones con los profesores seleccionados."
            else:
                mensaje = f"Mostrando la base de datos de **{total_filtrados}** opciones disponibles."
                
            if total_filtrados > max_render:
                mensaje += f" Mostrando el Top **{max_render}** más óptimas en pantalla."
                
            st.info(mensaje)
            
            # La tabla final usará el nombre original limpio sin (Vespertinos) agregados al nombre
            cols_to_show = ['Grupo', 'Asignatura', 'Profesor', 'Edificio', 'Salón', 'Lun', 'Mar', 'Mie', 'Jue', 'Vie']
            
            for idx, sched in enumerate(horarios_a_mostrar, 1):
                with st.expander(f"🏅 Opción {idx} - Horas libres totales: {sched['free_hours']} hrs", expanded=(idx==1)):
                    df_visual = pd.DataFrame(sched['classes'])[cols_to_show]
                    
                    st.dataframe(df_visual, use_container_width=True, hide_index=True)
                    
                    col_espacio, col_boton = st.columns([4, 1])
                    with col_boton:
                        csv_data = df_visual.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Descargar (CSV)",
                            data=csv_data,
                            file_name=f"mi_horario_opcion_{idx}.csv",
                            mime="text/csv",
                            key=f"btn_descarga_{idx}"
                        )