#!/usr/bin/env python3
"""Headless checks for the standalone example, NOT all consuming applications.

Requires Python playwright and a local Chromium installation.
ASH_MARBLE_CHROMIUM selects the executable. Optional screenshots/results go to
ASH_MARBLE_ARTIFACT_DIR (keep that directory outside the repository).
"""
from __future__ import annotations

import itertools
import json
import os
from pathlib import Path
import shutil
import unittest

from playwright.sync_api import sync_playwright

REPO = Path(__file__).resolve().parents[1]
URL = (REPO / "examples/ash-marble-demo.html").as_uri()
BASE = json.loads((REPO / "tokens/design-tokens.json").read_text())
ASH = json.loads((REPO / "tokens/ash-marble.json").read_text())
WIDTHS = [1440, 980, 600, 390, 320]


def rgb(color: str) -> str:
    return "rgb(" + ", ".join(str(int(color[i:i + 2], 16)) for i in (1, 3, 5)) + ")"


class AshMarbleBrowser(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.playwright = sync_playwright().start()
        executable = os.environ.get("ASH_MARBLE_CHROMIUM") or shutil.which("google-chrome") or shutil.which("chromium")
        options = {"args": ["--no-sandbox", "--disable-dev-shm-usage"]}
        if executable:
            options["executable_path"] = executable
        cls.browser = cls.playwright.chromium.launch(**options)
        cls.results = {"browser": cls.browser.version, "stateCases": 0, "viewportCases": 0, "viewports": WIDTHS}
        cls.artifacts = Path(os.environ["ASH_MARBLE_ARTIFACT_DIR"]).resolve() if os.environ.get("ASH_MARBLE_ARTIFACT_DIR") else None
        if cls.artifacts:
            if cls.artifacts == REPO or REPO in cls.artifacts.parents:
                raise ValueError("Keep browser artifacts outside the repository")
            cls.artifacts.mkdir(parents=True, exist_ok=True)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.browser.close()
        cls.playwright.stop()
        if cls.artifacts:
            (cls.artifacts / "browser-results.json").write_text(json.dumps(cls.results, indent=2) + "\n")
        print("\nBrowser coverage:", json.dumps(cls.results))

    def setUp(self) -> None:
        self.context = self.browser.new_context(viewport={"width": 1440, "height": 1000}, color_scheme="light")
        self.errors = []
        self.remote = []
        self.context.on("request", lambda request: self.remote.append(request.url) if request.url.startswith(("http:", "https:")) else None)
        self.page = self.context.new_page()
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))
        self.page.on("console", lambda message: self.errors.append(message.text) if message.type == "error" else None)
        self.page.goto(URL)
        self.page.wait_for_function("document.getElementById('total-calls').textContent === '128,430'")

    def tearDown(self) -> None:
        self.context.close()
        self.assertEqual(self.errors, [], "Browser errors")
        self.assertEqual(self.remote, [], "Example requested remote resources")

    def load_state(self, palette="ash-marble", mode="auto", tone="pale", material="marble") -> None:
        self.page.evaluate("""state => {
          localStorage.clear();
          for (const [dimension,value] of Object.entries(state)) {
            if (dimension !== 'mode' || value !== 'auto') localStorage.setItem('sage-ash-marble-demo:' + dimension,value);
          }
        }""", {"palette": palette, "mode": mode, "tone": tone, "material": material})
        self.page.reload()
        self.page.wait_for_function("document.getElementById('total-calls').textContent === '128,430'")

    def snapshot(self) -> dict:
        return self.page.evaluate("""() => {
          const root=document.documentElement, card=document.querySelector('.card');
          const before=getComputedStyle(card,'::before');
          return {
            palette:root.dataset.palette, mode:root.dataset.themeMode, resolved:root.dataset.resolvedTheme,
            tone:root.dataset.ashTone, material:root.dataset.ashMaterial,
            page:getComputedStyle(document.body).backgroundColor,
            card:getComputedStyle(card).backgroundColor,
            hero:getComputedStyle(document.getElementById('total-calls')).color,
            secondary:getComputedStyle(document.getElementById('input-tokens')).color,
            change:getComputedStyle(document.getElementById('change-calls')).color,
            texture:!['none','normal'].includes(before.content) && before.display!=='none' && Number(before.opacity)>0,
            opacity:before.opacity, pointer:before.pointerEvents, overflow:getComputedStyle(card).overflow,
            disabled:[...document.querySelectorAll('[data-tone-choice],[data-material-choice]')].every(b=>b.disabled),
            values:[...document.querySelectorAll('.metric-value')].map(n=>n.textContent),
            scrollWidth:root.scrollWidth, viewport:innerWidth
          };
        }""")

    def test_01_complete_theme_and_viewport_matrix(self) -> None:
        for system, palette, mode, tone, material in itertools.product(["light", "dark"], ["sage", "ash-marble"], ["auto", "light", "dark"], ["pale", "gray"], ["marble", "flat"]):
            with self.subTest(system=system, palette=palette, mode=mode, tone=tone, material=material):
                self.page.emulate_media(color_scheme=system)
                self.load_state(palette, mode, tone, material)
                resolved = system if mode == "auto" else mode
                active = palette == "ash-marble" and resolved == "light"
                colors = ASH["tones"][tone] if active else BASE["colors"][resolved]
                initial = self.snapshot()
                self.assertEqual(initial["resolved"], resolved)
                self.assertEqual(initial["page"], rgb(colors["page"]))
                self.assertEqual(initial["card"], rgb(colors["surface-1"]))
                self.assertEqual(initial["hero"], rgb(ASH["accents"]["heroMetric"] if active else colors["ink-1"]))
                self.assertEqual(initial["secondary"], rgb(colors["ink-1"]))
                self.assertEqual(initial["change"], rgb(colors["ink-3"]))
                self.assertEqual(initial["texture"], active and material == "marble")
                self.assertEqual(initial["disabled"], not active)
                for dimension in ["palette", "tone", "material"]:
                    self.assertEqual(self.page.locator(f'[data-{dimension}-choice][aria-pressed="true"]').count(), 1)
                if active and material == "marble":
                    self.assertAlmostEqual(float(initial["opacity"]), ASH["material"]["marble"]["opacity"])
                    self.assertEqual(initial["pointer"], "none")
                    self.assertNotEqual(initial["overflow"], "hidden")
                type(self).results["stateCases"] += 1
                for width in WIDTHS:
                    self.page.set_viewport_size({"width": width, "height": 1000})
                    self.page.locator("details").evaluate_all("nodes => nodes.forEach(n=>n.open=true)")
                    current = self.snapshot()
                    self.assertLessEqual(current["scrollWidth"], width, "Overall horizontal overflow")
                    self.assertEqual(current["values"], initial["values"], "Display setting changed data")
                    geometry = self.page.evaluate("""() => {
                      const card=document.querySelector('.card'), shell=document.querySelector('.shell');
                      return {hero:getComputedStyle(document.getElementById('total-calls')).fontSize,
                        secondary:getComputedStyle(document.getElementById('input-tokens')).fontSize,
                        padding:getComputedStyle(card).padding, shell:shell.getBoundingClientRect().width,
                        card:card.getBoundingClientRect().width,
                        content:shell.clientWidth-parseFloat(getComputedStyle(shell).paddingLeft)-parseFloat(getComputedStyle(shell).paddingRight)};
                    }""")
                    self.assertEqual(geometry["hero"], "52px")
                    self.assertEqual(geometry["secondary"], "24px")
                    self.assertEqual(geometry["padding"], "16px 14px 14px" if width <= 600 else "16px 18px 14px")
                    if width == 1440:
                        self.assertEqual(geometry["shell"], 1240)
                        self.assertEqual(geometry["content"], 1176)
                        self.assertAlmostEqual(geometry["card"], 679.333, delta=.1)
                    else:
                        self.assertAlmostEqual(geometry["card"], geometry["content"], delta=.1)
                    type(self).results["viewportCases"] += 1
        self.page.emulate_media(color_scheme="light")
        self.load_state()
        if self.artifacts:
            for width in [1440, 320]:
                self.page.set_viewport_size({"width": width, "height": 1000})
                self.page.evaluate("window.scrollTo(0,0)")
                self.page.screenshot(path=str(self.artifacts / f"ash-pale-marble-{width}.png"), full_page=True)

    def test_02_data_contract_and_accessible_exact_values(self) -> None:
        self.assertEqual(self.page.locator("#trend-bars .column").count(), 7)
        self.assertEqual(self.page.locator("#trend-bars .bar").count(), 14)
        self.assertEqual(self.page.locator("#trend-dates span").all_text_contents(), [f"10-0{i}" for i in range(1, 8)])
        self.assertIn("12.7%", self.page.locator("#change-calls").inner_text())
        self.assertIn("99.2", self.page.locator("#success-rate").inner_text())
        rows = self.page.locator("#trend-rows tr").evaluate_all("rows=>rows.map(row=>[...row.cells].map(c=>c.textContent))")
        current = sum(int(row[2].replace(",", "")) for row in rows)
        prior = sum(int(row[3].replace(",", "")) for row in rows)
        self.assertEqual((current, prior), (128430, 114000))
        shares = self.page.locator("#distribution-rows tr").evaluate_all("rows=>rows.map(row=>[...row.cells].map(c=>c.textContent))")
        self.assertEqual(sum(int(row[1].replace(",", "")) for row in shares), current)
        self.assertAlmostEqual(sum(float(row[2].replace("%", "")) for row in shares), 100)
        heights = self.page.locator("#trend-bars .bar.current").evaluate_all("nodes=>nodes.map(n=>parseFloat(n.style.getPropertyValue('--h')))")
        self.assertEqual(heights, [int(row[2].replace(",", "")) / 25000 * 100 for row in rows])
        ticks = self.page.locator('.yaxis span').evaluate_all("nodes=>nodes.map(n=>{const r=n.getBoundingClientRect(),p=n.parentElement.getBoundingClientRect();return ((r.top+r.bottom)/2-p.top)/p.height;})")
        for actual, expected in zip(ticks, [0, .2, .4, .6, .8, 1]):
            self.assertAlmostEqual(actual, expected, delta=.001)
        self.assertEqual(self.page.locator('thead th:not([scope="col"])').count(), 0)
        self.assertEqual(self.page.locator('tbody th:not([scope="row"])').count(), 0)
        summary = self.page.locator("summary").first
        summary.focus()
        summary.press("Enter")
        self.assertTrue(self.page.locator("details").first.evaluate("n=>n.open"))
        self.assertIn("本期与上期对应日", self.page.locator("details").first.aria_snapshot())
        self.assertEqual(self.page.locator(".bar.prior").first.evaluate("n=>getComputedStyle(n).borderStyle"), "dashed")
        self.assertEqual(self.page.locator(".bar.current").first.evaluate("n=>getComputedStyle(n).borderStyle"), "solid")

    def test_03_keyboard_focus_persistence_auto_and_invalid_storage(self) -> None:
        self.page.locator("summary").first.focus()
        self.page.locator("summary").first.press("Enter")
        gray = self.page.locator('[data-tone-choice="gray"]')
        gray.focus()
        gray.press("Enter")
        self.assertEqual(gray.get_attribute("aria-pressed"), "true")
        self.assertEqual(gray.evaluate("n=>getComputedStyle(n).textDecorationLine"), "underline")
        self.assertTrue(gray.evaluate("n=>n===document.activeElement"))
        self.assertTrue(self.page.locator("details").first.evaluate("n=>n.open"))
        self.assertEqual(gray.evaluate("n=>getComputedStyle(n).outlineWidth"), "2px")
        self.page.locator('[data-material-choice="flat"]').focus()
        self.page.locator('[data-material-choice="flat"]').press("Space")
        self.page.reload()
        self.assertEqual(self.snapshot()["tone"], "gray")
        self.assertEqual(self.snapshot()["material"], "flat")
        theme = self.page.locator("#theme-mode")
        theme.focus()
        for expected in ["light", "dark", "auto"]:
            theme.press("Space")
            self.assertEqual(self.snapshot()["mode"], expected)
            self.assertTrue(theme.evaluate("n=>n===document.activeElement"))
        self.assertIsNone(self.page.evaluate("localStorage.getItem('sage-ash-marble-demo:mode')"))
        self.page.emulate_media(color_scheme="dark")
        # matchMedia change delivery is asynchronous; wait on state, not a sleep.
        self.page.wait_for_function("document.documentElement.dataset.resolvedTheme === 'dark'")
        self.assertEqual(self.snapshot()["resolved"], "dark")
        theme.press("Enter")
        self.assertEqual(self.snapshot()["resolved"], "light")
        self.page.emulate_media(color_scheme="light")
        self.page.emulate_media(color_scheme="dark")
        self.assertEqual(self.snapshot()["resolved"], "light", "Manual choice must win")
        self.page.evaluate("['palette','mode','tone','material'].forEach(d=>localStorage.setItem('sage-ash-marble-demo:'+d,'invalid'))")
        self.page.reload()
        restored = self.snapshot()
        self.assertEqual((restored["palette"], restored["mode"], restored["tone"], restored["material"]), ("ash-marble", "auto", "pale", "marble"))
        self.assertEqual(restored["resolved"], "dark")
        self.page.emulate_media(color_scheme="light")
        self.page.wait_for_function("document.documentElement.dataset.resolvedTheme === 'light'")
        gray.focus()
        self.page.emulate_media(color_scheme="dark")
        self.page.wait_for_function("document.activeElement.id === 'theme-mode'")
        self.assertTrue(theme.evaluate("n=>n===document.activeElement"), "System-disabled control needs predictable focus fallback")

    def test_04_storage_unavailable_and_script_unavailable(self) -> None:
        self.context.add_init_script("Object.defineProperty(window,'localStorage',{get(){throw new DOMException('blocked','SecurityError')}})")
        self.page.reload()
        self.assertIn("存储不可用", self.page.locator("#display-status").inner_text())
        self.page.locator('[data-tone-choice="gray"]').click()
        self.assertEqual(self.snapshot()["tone"], "gray")
        self.assertEqual(self.snapshot()["values"][0], "128,430")
        no_script = self.browser.new_context(java_script_enabled=False)
        try:
            page = no_script.new_page()
            page.goto(URL)
            self.assertIn("脚本不可用", page.locator("noscript").inner_text())
            self.assertEqual(page.locator("#total-calls").inner_text(), "—")
            self.assertEqual(page.locator("button:not(:disabled)").count(), 0)
        finally:
            no_script.close()

    def test_05_preferences_nested_control_guards_and_text_stress(self) -> None:
        self.page.emulate_media(reduced_motion="reduce")
        self.assertEqual(self.page.locator("body").evaluate("n=>getComputedStyle(n).transitionDuration"), "0s")
        self.assertEqual(self.page.locator("body").evaluate("n=>getComputedStyle(n).animationName"), "none")
        targets=self.page.locator('button:not(:disabled),summary').evaluate_all('nodes=>nodes.map(n=>n.getBoundingClientRect().height)')
        self.assertTrue(all(height >= 24 for height in targets), 'Small interactive target without a larger alternative')
        self.page.emulate_media(forced_colors="active")
        self.page.wait_for_function("document.getElementById('display-status').textContent.includes('强制颜色模式')")
        self.assertFalse(self.snapshot()["texture"])
        self.assertTrue(self.snapshot()["disabled"])
        self.assertEqual(self.page.locator('[data-tone-choice="pale"]').evaluate("n=>getComputedStyle(n).outlineWidth"), "1px")
        self.page.emulate_media(forced_colors="none")
        self.page.wait_for_function("!document.querySelector('[data-tone-choice]').disabled")
        guard = self.page.evaluate("""() => {
          const card=document.querySelector('.card');
          const button=document.createElement('button');button.textContent='Nested control';card.append(button);
          const misuse=document.createElement('button');misuse.className='ash-marble-card';misuse.textContent='Incorrect opt-in';card.append(misuse);
          const style=document.createElement('style');style.textContent='.review-popup{position:fixed}';document.head.append(style);
          const popup=document.createElement('div');popup.className='review-popup';popup.setAttribute('role','tooltip');card.append(popup);
          const dialog=document.createElement('dialog');document.body.append(dialog);
          const nativePosition=getComputedStyle(dialog).position;card.append(dialog);
          const result={background:getComputedStyle(button).backgroundColor,content:getComputedStyle(misuse,'::before').content,
            popupPosition:getComputedStyle(popup).position,dialogPosition:getComputedStyle(dialog).position,nativePosition};
          button.remove();misuse.remove();popup.remove();dialog.remove();style.remove();return result;
        }""")
        self.assertEqual(guard["background"], rgb(ASH["tones"]["pale"]["surface-1"]))
        self.assertEqual(guard["content"], "none")
        self.assertEqual(guard["popupPosition"], "fixed", "Texture recipe must not override host positioning")
        self.assertEqual(guard["dialogPosition"], guard["nativePosition"])
        self.page.locator("h1").evaluate("n=>n.textContent='长标题与标识符检查 / '+ 'very-long-identifier-'.repeat(12)")
        self.page.locator('[data-palette-choice="ash-marble"]').evaluate("n=>n.textContent='超长配色标签 '+ 'identifier'.repeat(10)")
        for width in WIDTHS:
            self.page.set_viewport_size({"width": width, "height": 1000})
            self.assertLessEqual(self.snapshot()["scrollWidth"], width)
        for width in WIDTHS:
            self.page.set_viewport_size({"width": width, "height": 1000})
            self.page.locator("body").evaluate("n=>n.style.zoom='2'")
            self.assertLessEqual(self.snapshot()["scrollWidth"], width, "200% page zoom overflow")
            self.page.locator("body").evaluate("n=>n.style.zoom='1'")
        # Independent text-only enlargement, not just a whole-page CSS zoom.
        for width in WIDTHS:
            self.page.set_viewport_size({"width": width, "height": 1000})
            self.page.evaluate("""() => {
              const nodes=[...document.querySelectorAll('body,body *')].map(n=>[n,n.style.fontSize,parseFloat(getComputedStyle(n).fontSize)]);
              for(const [node,,size] of nodes) node.style.fontSize=(size*2)+'px';
              window.restoreDemoText=()=>{for(const [node,inline] of nodes) node.style.fontSize=inline;};
            }""")
            self.assertLessEqual(self.snapshot()["scrollWidth"], width, "200% text-only overflow")
            self.page.evaluate("window.restoreDemoText()")
        self.page.set_viewport_size({"width": 320, "height": 1000})
        self.page.locator("summary").first.click()
        scroll = self.page.locator(".table-scroll").first
        self.assertGreater(scroll.evaluate("n=>n.scrollWidth"), scroll.evaluate("n=>n.clientWidth"))
        scroll.focus()
        self.assertTrue(scroll.evaluate("n=>n===document.activeElement"))
        if self.artifacts:
            self.load_state(mode="dark")
            self.page.evaluate("window.scrollTo(0,0)")
            self.page.screenshot(path=str(self.artifacts / "sage-dark-320.png"), full_page=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
