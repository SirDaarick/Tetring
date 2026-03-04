import streamlit as st
import pandas as pd

st.set_page_config(page_title="Generador de Horarios", layout="wide")

st.title("Generador Automático de Horarios")
st.write("Sube tu archivo CSV para ver las materias disponibles, selecciona las que necesites y genera todas las combinaciones posibles sin traslapes.")

# 1. Subir el archivo CSV
uploaded_file = st.file_uploader("Sube tu archivo CSV de materias", type="csv")

if uploaded_file is not None:
    # Cargar y limpiar los datos
    df = pd.read_csv(uploaded_file)
    df = df.fillna('')
    
    # Validar que existan las columnas mínimas necesarias
    columnas_requeridas = ['Asignatura', 'Grupo', 'Profesor', 'Lun', 'Mar', 'Mie', 'Jue', 'Vie']
    if not all(col in df.columns for col in columnas_requeridas):
        st.error(f"El CSV debe contener las siguientes columnas: {', '.join(columnas_requeridas)}")
    else:
        st.markdown("---")
        st.subheader("📚 Selecciona las materias obligatorias:")
        
        # Obtener materias únicas y ordenadas alfabéticamente
        materias_unicas = sorted(df['Asignatura'].unique())
        
        # Mostrar casillas de verificación en 3 columnas
        materias_seleccionadas = []
        cols = st.columns(3)
        for i, materia in enumerate(materias_unicas):
            if materia.strip(): # Evitar nombres vacíos
                if cols[i % 3].checkbox(materia):
                    materias_seleccionadas.append(materia)
        
        st.markdown("---")
        
        # Botón para generar los horarios
        if st.button("🚀 Generar Horarios"):
            if not materias_seleccionadas:
                st.warning("⚠️ Por favor, selecciona al menos una materia para continuar.")
            else:
                with st.spinner('Calculando combinaciones posibles...'):
                    # Filtrar el dataframe con las materias elegidas
                    df_filtrado = df[df['Asignatura'].isin(materias_seleccionadas)].copy()
                    
                    # Convertir los textos de horas a "bloques" de 30 mins
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

                    df_filtrado['all_slots'] = df_filtrado.apply(parse_slots, axis=1)
                    
                    # Agrupar las filas por materia
                    subjects_data = []
                    for subj in materias_seleccionadas:
                        subjects_data.append(df_filtrado[df_filtrado['Asignatura'] == subj].to_dict('records'))
                    
                    # Lógica de backtracking
                    valid_schedules = []
                    def backtrack(subj_idx, current_schedule, occupied_slots):
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
                        st.error("❌ No se encontraron combinaciones posibles sin traslapes para las materias seleccionadas.")
                    else:
                        # Calcular horas libres y ordenar
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
                        
                        # Guardar en el estado de la sesión
                        st.session_state['horarios_generados'] = scored_schedules
                        st.success(f"✅ ¡Éxito! Se encontraron **{len(scored_schedules)}** combinaciones posibles.")

# ==========================================
# VISUALIZACIÓN Y FILTROS INTELIGENTES
# ==========================================
if 'horarios_generados' in st.session_state:
    st.markdown("---")
    st.subheader("🔎 Resultados y Filtros")
    
    # 1. Obtener la lista de todos los profesores únicos disponibles en los horarios generados
    todos_los_profesores = set()
    for sched in st.session_state['horarios_generados']:
        for row in sched['classes']:
            # Solo agregamos si el campo de profesor no está vacío
            if row['Profesor'].strip():
                todos_los_profesores.add(row['Profesor'])
                
    lista_profesores_ordenada = sorted(list(todos_los_profesores))
    
    # 2. Crear el buscador multiselect (Autocompletado + Etiquetas con cruz)
    profesores_seleccionados = st.multiselect(
        "Filtrar por profesor(es) específico(s):", 
        options=lista_profesores_ordenada,
        placeholder="Escribe para buscar o selecciona de la lista..."
    )
    
    # 3. Lógica para aplicar el filtro
    horarios_filtrados = []
    for sched in st.session_state['horarios_generados']:
        prof_names_in_sched = [row['Profesor'] for row in sched['classes']]
        
        # Verificar que TODOS los profesores seleccionados estén en este horario
        matches_all = True
        for prof in profesores_seleccionados:
            if prof not in prof_names_in_sched:
                matches_all = False
                break
                
        if matches_all:
            horarios_filtrados.append(sched)
            
    # 4. Mostrar resultados
    if not horarios_filtrados:
        st.error("No se encontraron horarios que incluyan a todos los profesores seleccionados simultáneamente.")
    else:
        if profesores_seleccionados:
            st.info(f"Mostrando **{len(horarios_filtrados)}** opciones que incluyen a los profesores seleccionados.")
        else:
            st.info(f"Mostrando las **{len(horarios_filtrados)}** combinaciones disponibles.")
        
        # Columnas a mostrar en la tabla final
        cols_to_show = ['Grupo', 'Asignatura', 'Profesor', 'Edificio', 'Salón', 'Lun', 'Mar', 'Mie', 'Jue', 'Vie']
        
        for idx, sched in enumerate(horarios_filtrados, 1):
            with st.expander(f"🏅 Opción {idx} - Horas libres totales: {sched['free_hours']} hrs", expanded=(idx==1)):
                df_visual = pd.DataFrame(sched['classes'])[cols_to_show]
                st.dataframe(df_visual, use_container_width=True, hide_index=True)