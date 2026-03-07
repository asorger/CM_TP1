from dataclasses import field
import flet as ft
from sympy import sympify, N, sqrt, sin, cos, tan, asin, acos, atan, log, exp, factorial, Abs
from datetime import datetime
import duckdb
import os
 
PARQUET_FILE = "historico.parquet"
 
class HistoryItem(ft.Container):
    def __init__(self, index, timestamp, expression, result, delete_callback, copy_callback):
        super().__init__()
 
        self.index = index
        self.timestamp = timestamp
        self.expression = expression
        self.result = result
 
        self.content = ft.Column(
            controls=[
                ft.Text(expression, size=16, color=ft.Colors.WHITE),
                ft.Text(f"= {result}", size=18, color=ft.Colors.ORANGE),
                ft.Text(timestamp, size=12, color=ft.Colors.WHITE38),
                ft.Row(
                    [
                        ft.IconButton(icon=ft.Icons.COPY, icon_size=18, on_click=lambda e: copy_callback(self)),
                        ft.IconButton(icon=ft.Icons.DELETE, icon_size=18, on_click=lambda e: delete_callback(self)),
                    ],
                    alignment=ft.MainAxisAlignment.END
                )
            ],
            spacing=2
        )
 
        self.padding = 10
        self.border = ft.border.only(bottom=ft.BorderSide(1, ft.Colors.WHITE12))
 
 
@ft.control
class CalcButton(ft.Button):
    expand: int = field(default_factory=lambda: 1)
    height: int = 65
    border_radius: int = 12
    style = ft.ButtonStyle(
        shape=ft.RoundedRectangleBorder(radius=12),
        padding=0
    )
 
@ft.control
class DigitButton(CalcButton):
    bgcolor: ft.Colors = ft.Colors.WHITE_24
    color: ft.Colors = ft.Colors.WHITE
 
@ft.control
class ActionButton(CalcButton):
    bgcolor: ft.Colors = ft.Colors.ORANGE
    color: ft.Colors = ft.Colors.WHITE
 
@ft.control
class ExtraActionButton(CalcButton):
    bgcolor: ft.Colors = ft.Colors.BLUE_GREY_100
    color: ft.Colors = ft.Colors.BLACK
 
 
@ft.control
class CalculatorApp(ft.Container):
    def init(self):
        self.reset()
        self.expand = True
        self.bgcolor = ft.Colors.BLACK
        self.border_radius = ft.BorderRadius.all(20)
        self.padding = 10
        self.history = []
        self.history_index = 1
        self.history_visible = False
 
        self.history_btn = ft.IconButton(
            icon=ft.Icons.HISTORY,
            icon_size=28,
            on_click=self.toggle_history
        )
 
        self.scientific_btn = ft.IconButton(
            icon=ft.Icons.SCIENCE,
            icon_size=28,
            on_click=self.toggle_scientific
        )
 
        self.history_panel = ft.Container(
            visible=False,
            bgcolor=ft.Colors.BLACK12,
            padding=10,
            border_radius=10,
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                height=300,
                spacing=8
            )
        )
 
        self.expression = ft.Text(value="", color=ft.Colors.WHITE54, size=16)
        self.text = ft.TextField(
            value="",
            color=ft.Colors.WHITE,
            text_size=20,
            hint_text="Insira expressão...",
            on_change=self.text_changed,
            on_submit=self.calculate_from_text,
            text_align=ft.TextAlign.RIGHT
        )
        self.result = ft.Text(value="0", color=ft.Colors.WHITE, size=20)
 
        self.scientific_visible = False
 
        self.scientific_panel_row1 = ft.Row(
            visible=False,
            spacing=8,
            controls=[
                ExtraActionButton(content="√", bgcolor=ft.Colors.DEEP_ORANGE_400, color=ft.Colors.WHITE, on_click=self.button_clicked),
                ExtraActionButton(content="1/x", bgcolor=ft.Colors.DEEP_ORANGE_400, color=ft.Colors.WHITE, on_click=self.button_clicked),
                ExtraActionButton(content="x²", bgcolor=ft.Colors.DEEP_ORANGE_400, color=ft.Colors.WHITE, on_click=self.button_clicked),
                ExtraActionButton(content="log", bgcolor=ft.Colors.DEEP_ORANGE_400, color=ft.Colors.WHITE, on_click=self.button_clicked),
            ]
        )
 
        self.scientific_panel_row2 = ft.Row(
            visible=False,
            spacing=8,
            controls=[
                ExtraActionButton(content="exp", bgcolor=ft.Colors.DEEP_ORANGE_400, color=ft.Colors.WHITE, on_click=self.button_clicked),
                ExtraActionButton(content="!", bgcolor=ft.Colors.DEEP_ORANGE_400, color=ft.Colors.WHITE, on_click=self.button_clicked),
                ExtraActionButton(content="sin", bgcolor=ft.Colors.DEEP_ORANGE_400, color=ft.Colors.WHITE, on_click=self.button_clicked),
                ExtraActionButton(content="cos", bgcolor=ft.Colors.DEEP_ORANGE_400, color=ft.Colors.WHITE, on_click=self.button_clicked),
            ]
        )
 
        self.scientific_panel_row3 = ft.Row(
            visible=False,
            spacing=8,
            controls=[
                ExtraActionButton(content="tan", bgcolor=ft.Colors.DEEP_ORANGE_400, color=ft.Colors.WHITE, on_click=self.button_clicked),
                ExtraActionButton(content="asin", bgcolor=ft.Colors.DEEP_ORANGE_400, color=ft.Colors.WHITE, on_click=self.button_clicked),
                ExtraActionButton(content="acos", bgcolor=ft.Colors.DEEP_ORANGE_400, color=ft.Colors.WHITE, on_click=self.button_clicked),
                ExtraActionButton(content="atan", bgcolor=ft.Colors.DEEP_ORANGE_400, color=ft.Colors.WHITE, on_click=self.button_clicked),
                ExtraActionButton(content="abs", bgcolor=ft.Colors.DEEP_ORANGE_400, color=ft.Colors.WHITE, on_click=self.button_clicked),
            ]
        )
 
        self.calc_keyboard = ft.Column(
            expand=True,
            spacing=8,
            controls=[
                ft.Row([self.text], expand=False),
                ft.Row([self.expression], alignment=ft.MainAxisAlignment.END, expand=False),
                ft.Row([self.result], alignment=ft.MainAxisAlignment.END, expand=False),
 
                ft.Row([
                    ExtraActionButton(content="CE", on_click=self.button_clicked),
                    ExtraActionButton(content="⌫", on_click=self.button_clicked),
                    ExtraActionButton(content="(", on_click=self.button_clicked),
                    ExtraActionButton(content=")", on_click=self.button_clicked),
                ], expand=True),
 
                self.scientific_panel_row1,
                self.scientific_panel_row2,
                self.scientific_panel_row3,
 
                ft.Row([
                    ExtraActionButton(content="AC", on_click=self.button_clicked),
                    ExtraActionButton(content="+/-", on_click=self.button_clicked),
                    ExtraActionButton(content="%", on_click=self.button_clicked),
                    ActionButton(content="/", on_click=self.button_clicked),
                ], expand=True),
 
                ft.Row([
                    DigitButton(content="7", on_click=self.button_clicked),
                    DigitButton(content="8", on_click=self.button_clicked),
                    DigitButton(content="9", on_click=self.button_clicked),
                    ActionButton(content="*", on_click=self.button_clicked),
                ], expand=True),
 
                ft.Row([
                    DigitButton(content="4", on_click=self.button_clicked),
                    DigitButton(content="5", on_click=self.button_clicked),
                    DigitButton(content="6", on_click=self.button_clicked),
                    ActionButton(content="-", on_click=self.button_clicked),
                ], expand=True),
 
                ft.Row([
                    DigitButton(content="1", on_click=self.button_clicked),
                    DigitButton(content="2", on_click=self.button_clicked),
                    DigitButton(content="3", on_click=self.button_clicked),
                    ActionButton(content="+", on_click=self.button_clicked),
                ], expand=True),
 
                ft.Row([
                    DigitButton(content="0", expand=2, on_click=self.button_clicked),
                    DigitButton(content=".", on_click=self.button_clicked),
                    ActionButton(content="=", on_click=self.button_clicked),
                ], expand=True),
            ]
        )
 
        self.content = ft.Column(
            expand=True,
            spacing=10,
            controls=[
                ft.Row([self.history_btn, self.scientific_btn], alignment=ft.MainAxisAlignment.END),
                self.history_panel,
                self.calc_keyboard
            ]
        )
 
    def toggle_scientific(self, e):
        self.scientific_visible = not self.scientific_visible
        self.scientific_panel_row1.visible = self.scientific_visible
        self.scientific_panel_row2.visible = self.scientific_visible
        self.scientific_panel_row3.visible = self.scientific_visible
        self.update()
 
    def did_mount(self):
        self.load_history()
 
    def save_history(self):
        simple_list = [
            {
                "index": item.index,
                "timestamp": item.timestamp,
                "expression": item.expression,
                "result": item.result
            }
            for item in self.history
        ]
 
        try:
            con = duckdb.connect()
            con.execute("CREATE TABLE IF NOT EXISTS hist (idx INTEGER, ts TEXT, expr TEXT, res TEXT)")
            con.execute("DELETE FROM hist")
 
            for h in simple_list:
                con.execute(
                    "INSERT INTO hist VALUES (?, ?, ?, ?)",
                    [h["index"], h["timestamp"], h["expression"], h["result"]]
                )
 
            con.execute(f"COPY hist TO '{PARQUET_FILE}' (FORMAT PARQUET)")
            con.close()
        except Exception as e:
            print("Erro DuckDB:", e)
 
    def load_history(self):
        if os.path.exists(PARQUET_FILE):
            try:
                con = duckdb.connect()
                rows = con.execute(
                    f"SELECT * FROM read_parquet('{PARQUET_FILE}')"
                ).fetchall()
                con.close()
 
                for row in rows:
                    item = HistoryItem(
                        index=row[0],
                        timestamp=row[1],
                        expression=row[2],
                        result=row[3],
                        delete_callback=self.delete_history_item,
                        copy_callback=self.copy_history_item
                    )
                    self.history.append(item)
 
                if len(self.history) > 0:
                    self.history_index = self.history[0].index + 1
 
            except Exception as e:
                print("Erro a ler Parquet/DuckDB:", e)
 
        self.refresh_history_panel()
 
    def toggle_history(self, e):
        self.history_visible = not self.history_visible
        self.history_btn.icon = ft.Icons.CALCULATE if self.history_visible else ft.Icons.HISTORY
        self.history_panel.visible = self.history_visible
        self.calc_keyboard.visible = not self.history_visible
        self.update()
 
    def add_to_history(self, expression, result):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
 
        item = HistoryItem(
            index=self.history_index,
            timestamp=timestamp,
            expression=expression,
            result=result,
            delete_callback=self.delete_history_item,
            copy_callback=self.copy_history_item
        )
 
        self.history_index += 1
        self.history.insert(0, item)
 
        if len(self.history) > 10:
            self.history.pop()
 
        self.save_history()
        self.refresh_history_panel()
 
    def refresh_history_panel(self):
        self.history_panel.content.controls = self.history
        self.update()
 
    def delete_history_item(self, item):
        self.history.remove(item)
        self.save_history()
        self.refresh_history_panel()
 
    def copy_history_item(self, item):
        self.page.set_clipboard(item.result)
 
    def text_changed(self, e):
        allowed = "0123456789+-*/(). "
        new_text = "".join(c for c in self.text.value if c in allowed)
        if new_text != self.text.value:
            self.text.value = new_text
            self.update()
 
    def calculate_from_text(self, e):
        expression = self.text.value
        try:
            result = N(sympify(expression))
            formatted = self.format_with_spaces(result)
            self.result.value = formatted
            self.add_to_history(expression, formatted)
        except:
            self.result.value = "Erro"
        self.text.value = ""
        self.update()
 
    def format_with_spaces(self, value):
        try:
            num = float(value)
            if num.is_integer():
                return f"{int(num):,}".replace(",", " ")
            else:
                inteiro, decimal = str(num).split(".")
                inteiro = f"{int(inteiro):,}".replace(",", " ")
                return inteiro + "." + decimal
        except:
            return value
 
    def button_clicked(self, e):
        data = e.control.content
 
        if data == "AC":
            self.text.value = ""
            self.result.value = "0"
            self.update()
            return
 
        if data == "CE":
            self.text.value = ""
            self.update()
            return
 
        if data == "⌫":
            self.text.value = self.text.value[:-1]
            self.update()
            return
 
        if data == "√":
            self.text.value = f"sqrt({self.text.value})"
            self.update()
            return
 
        if data == "x²":
            self.text.value += "**2"
            self.update()
            return
 
        if data == "1/x":
            self.text.value = f"1/({self.text.value})"
            self.update()
            return
 
        if data == "sin":
            self.text.value = f"sin({self.text.value})"
            self.update()
            return
 
        if data == "%":
            if self.text.value.strip() != "":
                self.text.value = f"({self.text.value})/100"
                self.update()
            return
 
        if data == "log":
            self.text.value = f"log({self.text.value})"
            self.update()
            return
 
        if data == "exp":
            self.text.value = f"exp({self.text.value})"
            self.update()
            return
 
        if data == "!":
            self.text.value = f"factorial({self.text.value})"
            self.update()
            return
 
        if data == "cos":
            self.text.value = f"cos({self.text.value})"
            self.update()
            return
 
        if data == "tan":
            self.text.value = f"tan({self.text.value})"
            self.update()
            return
 
        if data == "asin":
            self.text.value = f"asin({self.text.value})"
            self.update()
            return
 
        if data == "acos":
            self.text.value = f"acos({self.text.value})"
            self.update()
            return
 
        if data == "atan":
            self.text.value = f"atan({self.text.value})"
            self.update()
            return
 
        if data == "abs":
            self.text.value = f"Abs({self.text.value})"
            self.update()
            return
 
        if data == "=":
            self.calculate_from_text(None)
            return
 
        self.text.value += data
        self.update()
 
    def reset(self):
        self.operator = "+"
        self.operand1 = 0
        self.new_operand = True
 
 
def main(page: ft.Page):
    page.title = "Calc App"
    page.expand = True
    page.padding = 0
    page.spacing = 0
 
    calc = CalculatorApp()
    page.add(calc)
 
if __name__ == "__main__":
    ft.app(target=main)