"""Acciones del recorrido web de SauceDemo (Page Object Model)."""

from playwright.sync_api import Page


class SauceDemoPage:
    URL = "https://www.saucedemo.com/"

    def __init__(self, page: Page) -> None:
        self.page = page

    def elemento(self, nombre: str):
        # SauceDemo identifica sus controles con el atributo data-test.
        return self.page.locator(f'[data-test="{nombre}"]')

    def abrir(self) -> None:
        self.page.goto(self.URL)

    def iniciar_sesion(self, usuario: str, clave: str) -> None:
        self.elemento("username").fill(usuario)
        self.elemento("password").fill(clave)
        self.elemento("login-button").click()

    def seleccionar_productos(self) -> None:
        self.elemento("add-to-cart-sauce-labs-backpack").click()
        self.elemento("add-to-cart-sauce-labs-bike-light").click()

    def abrir_carrito(self) -> None:
        self.elemento("shopping-cart-link").click()

    def iniciar_checkout(self) -> None:
        self.elemento("checkout").click()

    def completar_datos(self, nombre: str, apellido: str, codigo_postal: str) -> None:
        self.elemento("firstName").fill(nombre)
        self.elemento("lastName").fill(apellido)
        self.elemento("postalCode").fill(codigo_postal)
        self.elemento("continue").click()

    def finalizar(self) -> None:
        self.elemento("finish").click()