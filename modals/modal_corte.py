import flet as ft
import csv
import io
import os
from datetime import datetime
from database.database import (
        obtener_ventas_por_empleado_hoy,
        obtener_total_ventas_hoy,
        obtener_inventario_actual,
        exportar_ventas_csv,
        exportar_inventario_csv
    )

def show_modal_corte(page):
    """
    Muestra un modal con el corte de caja del día.
    
    Args:
        page: Instancia de la página de Flet
    """
    
    # Obtener datos
    ventas_por_empleado = obtener_ventas_por_empleado_hoy()
    total_ventas = obtener_total_ventas_hoy()
    inventario = obtener_inventario_actual()
    
    # Configuramos un FilePicker global para la función
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)
    page.update()
    
    # Variable para almacenar los datos del CSV actual
    csv_data = {"contenido": "", "nombre": ""}
    
    def on_save_result(e: ft.FilePickerResultEvent):
        """Callback que se ejecuta después de seleccionar una ubicación para guardar"""
        if e.path:
            try:
                # Guardar el archivo con los datos almacenados en csv_data
                with open(e.path, "w", newline='', encoding='utf-8') as f:
                    f.write(csv_data["contenido"])
                
                # Mostrar mensaje de éxito
                page.open(ft.SnackBar(
                    content=ft.Text(f"Archivo guardado con éxito"),
                    action="OK"
                ))
                page.close(dlg_modal)
                page.update()
            except Exception as ex:
                # Mostrar mensaje de error
                page.open(ft.SnackBar(
                    content=ft.Text(f"Error al guardar el archivo: {str(ex)}"),
                    action="OK"
                ))
                page.update()
    
    # Asignar el callback al FilePicker
    file_picker.on_result = on_save_result
    
    def handle_download(e, tipo_reporte):
        """Función para manejar la descarga de reportes"""
        try:
            # Generar fecha para el nombre
            fecha = datetime.now().strftime("%d_%m_%Y")
            
            # Preparar los datos según el tipo de reporte
            if tipo_reporte == "ventas":
                datos = exportar_ventas_csv()
                nombre_archivo = f"ventas_del_dia_{fecha}.csv"
            else:  # inventario
                datos = exportar_inventario_csv()
                nombre_archivo = f"inventario_actual_{fecha}.csv"
            
            # Convertir datos a CSV
            output = io.StringIO()
            writer = csv.writer(output)
            for fila in datos:
                writer.writerow(fila)
            
            # Almacenar los datos del CSV para usarlos en el callback
            csv_data["contenido"] = output.getvalue()
            csv_data["nombre"] = nombre_archivo
            
            # Llamar a save_file para abrir el diálogo
            file_picker.save_file(
                dialog_title="Guardar archivo CSV",
                file_name=nombre_archivo,
                allowed_extensions=["csv"]
            )
            
        except Exception as ex:
            page.open(ft.SnackBar(
                content=ft.Text(f"Error: {str(ex)}"),
                action="OK"
            ))
            page.update()
    
    # Crear tablas
    def crear_tabla_ventas():
        tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Empleado", weight="bold")),
                ft.DataColumn(ft.Text("Total vendido", weight="bold")),
            ],
            rows=[]
        )
        
        for empleado, total in ventas_por_empleado:
            tabla.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(empleado)),
                        ft.DataCell(ft.Text(f"${total:.2f}")),
                    ]
                )
            )
        
        return ft.Container(
            content=ft.Column(
                controls=[tabla],
                scroll=ft.ScrollMode.AUTO,
                expand=True
            ),
            expand=True
        )
    
    def crear_tabla_inventario():
        tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Producto", weight="bold")),
                ft.DataColumn(ft.Text("Marca", weight="bold")),
                ft.DataColumn(ft.Text("Cantidad", weight="bold")),
                ft.DataColumn(ft.Text("Precio", weight="bold")),
            ],
            rows=[]
        )
        
        for producto in inventario:
            # Destacar productos con bajo stock (menos de 3)
            bajo_stock = producto[3] < 3
            color_texto = ft.Colors.RED if bajo_stock else None
            
            tabla.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(producto[1], color=color_texto)),
                        ft.DataCell(ft.Text(producto[2])),
                        ft.DataCell(ft.Text(str(producto[3]), color=color_texto)),
                        ft.DataCell(ft.Text(f"${producto[4]:.2f}")),
                    ],
                    color=ft.Colors.RED_50 if bajo_stock else None
                )
            )
        
        return ft.Container(
            content=ft.Column(
                controls=[tabla],
                scroll=ft.ScrollMode.AUTO,
                expand=True
            ),
            expand=True
        )
    
    # Crear tabs
    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(
                text="Ventas del día",
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text("Corte de Caja", size=24, weight="bold"),
                            ft.Text(datetime.now().strftime("%d/%m/%Y"), 
                                   size=18, weight="bold")
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Container(
                            content=crear_tabla_ventas(),
                            expand=True
                        ),
                        ft.Container(height=20),
                        ft.Row([
                            ft.Text("Total en caja:", size=20),
                            ft.Text(f"${total_ventas:.2f}", size=24, weight="bold")
                        ], alignment=ft.MainAxisAlignment.END),
                        ft.Container(height=20),
                        ft.FilledButton(
                            "Exportar ventas a CSV",
                            icon=ft.Icons.DOWNLOAD,
                            style=ft.ButtonStyle(
                                bgcolor='#FFCDFA',
                                color=ft.Colors.BLACK,
                                shape=ft.RoundedRectangleBorder(radius=7)
                            ),
                            on_click=lambda e: handle_download(e, "ventas")
                        )
                    ]),
                    padding=20,
                    width=800,
                )
            ),
            ft.Tab(
                text="Inventario",
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text("Inventario Actual", size=24, weight="bold"),
                            ft.Text(datetime.now().strftime("%d/%m/%Y"), 
                                   size=18, weight="bold")
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        
                        ft.Row([
                            ft.Text("* Los productos con bajo stock (menos de 3) se muestran en rojo",
                                  size=14, color=ft.Colors.RED)
                        ]),
                        
                        ft.Container(
                            content=crear_tabla_inventario(),
                            expand=True,
                        ),
                        
                        ft.FilledButton(
                            "Exportar inventario a CSV",
                            icon=ft.Icons.DOWNLOAD,
                            style=ft.ButtonStyle(
                                bgcolor='#FFCDFA',
                                color=ft.Colors.BLACK,
                                shape=ft.RoundedRectangleBorder(radius=7)
                            ),
                            on_click=lambda e: handle_download(e, "inventario")
                        )
                    ]),
                    padding=20,
                    expand=True
                )
            )
        ]
    )
    
    # Crear el modal
    dlg_modal = ft.AlertDialog(
        modal=True,
        content=ft.Container(
            width=700,
            content=tabs
        ),
        actions=[
            ft.ElevatedButton(
                "Cerrar",
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.GREY_300,
                    color=ft.Colors.BLACK,
                    shape=ft.RoundedRectangleBorder(radius=7)
                ),
                on_click=lambda e: page.close(dlg_modal)
            )
        ],
        actions_alignment=ft.MainAxisAlignment.END
    )
    
    # Mostrar el diálogo
    page.open(dlg_modal)