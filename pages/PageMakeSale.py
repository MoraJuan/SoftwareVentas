def update_cart_table(self):
        self.cart_table.rows.clear()
        total = 0

        for item in self.cart_items:
            self.cart_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(item["product_name"])),
                        ft.DataCell(ft.Text(str(item["quantity"]))),
                        ft.DataCell(ft.Text(f"${item['unit_price']:.2f}")),
                        ft.DataCell(ft.Text(f"${item['subtotal']:.2f}")),
                        ft.DataCell(
                            ft.IconButton(
                                ft.icons.DELETE,
                                on_click=lambda x, i=item: self.remove_from_cart(i)
                            )
                        ),
                    ]
                )
            )
            total += item["subtotal"]

        # Actualizar el texto del total
        self.total_text.value = f"Total: ${total:.2f}"
        self.page.update()