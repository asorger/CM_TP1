from dataclasses import field
import flet as ft
from sympy import sympify, N, sqrt, sin

@ft.control
class CalcButton(ft.Button):
    expand: int = field(default_factory=lambda: 1)

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
        self.width = 350
        self.bgcolor = ft.Colors.BLACK
        self.border_radius = ft.BorderRadius.all(20)
        self.padding = 20
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
        self.content = ft.Column(
            controls=[
                ft.Row(controls=[self.text]),
                ft.Row([self.expression], alignment=ft.MainAxisAlignment.END),
                ft.Row([self.result], alignment=ft.MainAxisAlignment.END),
                ft.Row([
                    ExtraActionButton(content="CE", on_click=self.button_clicked),
                    ExtraActionButton(content="⬅️", on_click=self.button_clicked),
                    ExtraActionButton(content="(", on_click=self.button_clicked),
                    ExtraActionButton(content=")", on_click=self.button_clicked),
                ]),
                ft.Row([
                    ExtraActionButton(content="√", on_click=self.button_clicked),
                    ExtraActionButton(content="x²", on_click=self.button_clicked),
                    ExtraActionButton(content="1/x", on_click=self.button_clicked),
                    ExtraActionButton(content="sin", on_click=self.button_clicked),
                ]),
                ft.Row([
                    ExtraActionButton(content="AC", on_click=self.button_clicked),
                    ExtraActionButton(content="+/-", on_click=self.button_clicked),
                    ExtraActionButton(content="%", on_click=self.button_clicked),
                    ActionButton(content="/", on_click=self.button_clicked),
                ]),
                ft.Row([
                    DigitButton(content="7", on_click=self.button_clicked),
                    DigitButton(content="8", on_click=self.button_clicked),
                    DigitButton(content="9", on_click=self.button_clicked),
                    ActionButton(content="*", on_click=self.button_clicked),
                ]),
                ft.Row([
                    DigitButton(content="4", on_click=self.button_clicked),
                    DigitButton(content="5", on_click=self.button_clicked),
                    DigitButton(content="6", on_click=self.button_clicked),
                    ActionButton(content="-", on_click=self.button_clicked),
                ]),
                ft.Row([
                    DigitButton(content="1", on_click=self.button_clicked),
                    DigitButton(content="2", on_click=self.button_clicked),
                    DigitButton(content="3", on_click=self.button_clicked),
                    ActionButton(content="+", on_click=self.button_clicked),
                ]),
                ft.Row([
                    DigitButton(content="0", expand=2, on_click=self.button_clicked),
                    DigitButton(content=".", on_click=self.button_clicked),
                    ActionButton(content="=", on_click=self.button_clicked),
                ]),
            ]
        )

    def text_changed(self, e):
        allowed = "0123456789+-*/(). "
        new_text = "".join(c for c in self.text.value if c in allowed)
        if new_text != self.text.value:
            self.text.value = new_text
            self.update()

    def calculate_from_text(self, e):
        try:
            result = N(sympify(self.text.value))
            self.result.value = self.format_with_spaces(result)
        except:
            self.result.value = "Erro"
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

        if data == "⬅️":
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
    calc = CalculatorApp()
    page.add(calc)

ft.run(main)