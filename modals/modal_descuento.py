import flet as ft
from functools import partial
    
def show_modal_descuento(page, sale, actualizar_sidebar):
    """Muestra el modal para aplicar descuento al total de la venta"""
    
    porcentaje_input = ft.TextField(
        label="Porcentaje de descuento",
        value=f"{sale.descuento_porcentaje:.2f}" if sale.descuento_porcentaje else "",
        keyboard_type="number",
        suffix_text="%",
        autofocus=True,
        input_filter=ft.InputFilter(r'^\d*\.?\d*$'),  # Acepta números y decimales
        border_color='#EBEBEB',
        border_radius=7
    )
    

    def aplicar_descuento(e):
        try:
            if not porcentaje_input.value:
                raise ValueError("Ingrese un porcentaje")
                
            porcentaje = float(porcentaje_input.value)
            sale.aplicar_descuento(porcentaje)
            
            page.close(dialog)
            actualizar_sidebar()  # Esto ahora recalculará automáticamente
            
        except ValueError as err:
            page.update()

    # Diálogo principal
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Container(
            content=ft.Text("Aplicar Descuento"),

        ),
        content= porcentaje_input,
        actions=[
            ft.ElevatedButton(
                "Aplicar",
                bgcolor='#FFCDFA',
                color=ft.Colors.BLACK,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=7)
                ),
                on_click=aplicar_descuento
            ),
            ft.OutlinedButton(
                "Cancelar",
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=7)
                ),
                on_click=lambda e: page.close(dialog)
            )
        ],
    )

    # Función al abrir el diálogo
    def on_dialog_open(e):
        porcentaje_input.focus()

    dialog.on_open = on_dialog_open
    page.open(dialog)   