import flet as ft
from database.database import agregar_producto, actualizar_producto, obtener_producto_por_barcode, eliminar_producto


def show_modal_editar_producto(page, actualizar_lista_callback):
    # Campos del formulario
    codigo_barras = ft.TextField(
        label="Código de Barras",
        autofocus=True,
        on_change=lambda e: buscar_producto(e.control.value, page),
        on_submit=lambda e: buscar_producto(e.control.value, page)
    )
    nombre = ft.TextField(label="Nombre")
    marca = ft.TextField(label="Marca")
    precio = ft.TextField(label="Precio", keyboard_type="number")
    cantidad = ft.TextField(label="Cantidad", keyboard_type="number")
    categoria = ft.TextField(label="Categoría")
    
    error_text = ft.Text(color="red", visible=False)
    btn_eliminar = ft.ElevatedButton(
        "Eliminar Producto",
        icon=ft.Icons.DELETE,
        icon_color="white",
        color="white",
        bgcolor="red",
        visible=False
    )
    producto_actual = None

    def buscar_producto(codigo, page):
        nonlocal producto_actual
        if codigo:
            producto = obtener_producto_por_barcode(codigo)
            if producto:
                producto_actual = producto
                nombre.value = producto[1]
                marca.value = producto[2]
                precio.value = str(producto[3])
                cantidad.value = str(producto[4])
                categoria.value = producto[5]
                error_text.visible = False
                btn_eliminar.visible = True
            else:
                producto_actual = None
                nombre.value = ""
                marca.value = ""
                precio.value = ""
                cantidad.value = ""
                categoria.value = ""
                btn_eliminar.visible = False
            page.update()

    def guardar_producto(e):
        nonlocal producto_actual
        try:
            precio_val = float(precio.value)
            cantidad_val = int(cantidad.value)
        except ValueError:
            error_text.value = "Precio y cantidad deben ser números válidos"
            error_text.visible = True
            page.update()
            return
            
        if not all([codigo_barras.value, nombre.value, marca.value, categoria.value]):
            error_text.value = "Todos los campos son obligatorios"
            error_text.visible = True
            page.update()
            return

        if producto_actual:
            success = actualizar_producto(
                producto_actual[0],
                nombre.value,
                marca.value,
                precio_val,
                cantidad_val,
                categoria.value,
                codigo_barras.value
            )
        else:
            success = agregar_producto(
                nombre.value,
                marca.value,
                precio_val,
                cantidad_val,
                categoria.value,
                codigo_barras.value
            )
        
        if success:
            page.close(dialog)
            actualizar_lista_callback()
            if hasattr(page, 'nuevo_pedido'):
                page.nuevo_pedido(None)
        else:
            error_text.value = "Error: Código de barras ya existe"
            error_text.visible = True
            page.update()

    def confirmar_eliminar(e):
        page.open(confirm_dialog)

    def eliminar_producto_handler(e):
        if eliminar_producto(producto_actual[0]):
            page.close(confirm_dialog)
            # Cerrar también el diálogo de confirmación si está abierto
            if len(page.views) > 1:
                page.close(page.views[-1])
            actualizar_lista_callback()
        else:
            error_text.value = "Error al eliminar el producto"
            error_text.visible = True
            page.update()

    # Asignar el evento de click al botón eliminar
    btn_eliminar.on_click = confirmar_eliminar

    confirm_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirmar eliminación"),
        content=ft.Text(f"¿Estás seguro de eliminar el producto {nombre.value}?"),
        actions=[
            ft.TextButton("Sí", on_click=eliminar_producto_handler),
            ft.TextButton("No", on_click=lambda e: page.close(confirm_dialog)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Container(
            content=ft.Text("Crear/Editar Producto"),
            padding=ft.padding.only(left=50, right=50,bottom=20)
        ),
        content=ft.Column(
            controls=[
                ft.Row([
                    ft.Column([
                        codigo_barras,
                        nombre,
                        marca
                    ], expand=True),
                    ft.Column([
                        precio,
                        cantidad,
                        categoria
                    ], expand=True)
                ], expand=True),
                error_text,
                ft.Container(
                    content=btn_eliminar,
                    alignment=ft.alignment.center,
                    padding=10
                )
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True
        ),
        actions=[
            ft.ElevatedButton("Guardar", on_click=guardar_producto),
            ft.OutlinedButton("Cancelar", on_click=lambda e: page.close(dialog))
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        scrollable=True,
        content_padding=ft.padding.symmetric(horizontal=20, vertical=10),
        inset_padding=ft.padding.all(20)  # Aumenta el padding interno
    )
    
    def on_dialog_open(e):
        codigo_barras.focus()
    
    dialog.on_open = on_dialog_open
    page.open(dialog)