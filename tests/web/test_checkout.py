"""Recorrido web equivalente a selección, carrito y compra del onboarding."""

import os
from pathlib import Path

from playwright.sync_api import Page, expect

from pages.saucedemo_page import SauceDemoPage


def test_compra_simulada(page: Page) -> None:
    tienda = SauceDemoPage(page)

    tienda.abrir()
    tienda.iniciar_sesion(
        os.getenv("SAUCE_USER", "standard_user"),
        os.getenv("SAUCE_PASSWORD", "secret_sauce"),
    )

    tienda.seleccionar_productos()
    expect(tienda.elemento("shopping-cart-badge")).to_have_text("2")

    tienda.abrir_carrito()
    expect(page.get_by_text("Sauce Labs Backpack", exact=True)).to_be_visible()
    expect(page.get_by_text("Sauce Labs Bike Light", exact=True)).to_be_visible()

    tienda.iniciar_checkout()
    tienda.completar_datos("Prueba", "QA", "00000")
    tienda.finalizar()

    expect(tienda.elemento("complete-header")).to_have_text(
        "Thank you for your order!"
    )

    Path("evidencias").mkdir(exist_ok=True)
    page.screenshot(path="evidencias/compra_saucedemo.png", full_page=True)