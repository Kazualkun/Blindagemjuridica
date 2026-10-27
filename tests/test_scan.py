"""Testes do scanner da skill blindagem-juridica.

Rodar a partir da raiz do repositório:
    python -m unittest discover -s tests -v
"""

import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "blindagem-juridica", "scripts")
FIXTURES = os.path.join(ROOT, "tests", "fixtures")
sys.path.insert(0, SCRIPTS)

from contraste import contrast_ratio, parse_color, suggest  # noqa: E402
from scan import Scanner, cnpj_valid  # noqa: E402


def rules(scanner):
    return {f["regra"] for f in scanner.findings}


class TestContraste(unittest.TestCase):
    def test_razao_preto_branco(self):
        self.assertAlmostEqual(contrast_ratio((0, 0, 0), (255, 255, 255)), 21.0, places=2)

    def test_parse(self):
        self.assertEqual(parse_color("#fff"), (255, 255, 255))
        self.assertEqual(parse_color("rgb(0, 0, 0)"), (0, 0, 0))
        self.assertEqual(parse_color("white"), (255, 255, 255))
        self.assertIsNone(parse_color("rgba(0,0,0,.5)"))  # translúcida: não calculável

    def test_sugestao_atinge_alvo(self):
        fg, bg = parse_color("#aaaaaa"), parse_color("#ffffff")
        sug = suggest(fg, bg, 4.5)
        self.assertIsNotNone(sug)
        self.assertGreaterEqual(contrast_ratio(sug, bg), 4.5)


class TestCNPJ(unittest.TestCase):
    def test_numerico(self):
        self.assertTrue(cnpj_valid("11.222.333/0001-81"))
        self.assertFalse(cnpj_valid("11.222.333/0001-00"))
        self.assertFalse(cnpj_valid("00.000.000/0000-00"))

    def test_alfanumerico_exemplo_serpro(self):
        self.assertTrue(cnpj_valid("12.ABC.345/01DE-35"))
        self.assertFalse(cnpj_valid("12.ABC.345/01DE-36"))


class TestLojaProblematica(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sc = Scanner(os.path.join(FIXTURES, "loja-problematica"), max_per_rule=50).run()
        cls.rules = rules(cls.sc)

    def assertRule(self, rule):
        self.assertIn(rule, self.rules, "regra esperada não disparou: " + rule)

    def test_documentos(self):
        for r in ("privacidade-ausente", "reembolso-ausente", "clausula-abusiva"):
            self.assertRule(r)

    def test_cookies_e_rastreadores(self):
        for r in ("cookies-sem-consentimento", "banner-sem-rejeitar", "consentimento-tacito",
                  "rastreador-publicidade", "gravacao-sessao", "pixel-advanced-matching", "consent-mode-ausente"):
            self.assertRule(r)
        self.assertIn("Google Analytics", self.sc.p["rastreadores"])

    def test_formularios(self):
        for r in ("checkbox-pre-marcado", "consentimento-agrupado", "dado-sensivel-formulario",
                  "dado-verificar-necessidade", "formulario-sem-aviso"):
            self.assertRule(r)

    def test_acessibilidade(self):
        for r in ("img-sem-alt", "html-sem-lang", "zoom-bloqueado", "campo-sem-rotulo",
                  "botao-icone-sem-nome", "clique-sem-teclado", "link-sem-href", "contraste-insuficiente"):
            self.assertRule(r)

    def test_publicidade(self):
        for r in ("avatar-gerado", "prova-social-aleatoria", "promessa-critico", "escassez", "preco-de-por"):
            self.assertRule(r)

    def test_direitos_autorais(self):
        for r in ("imagem-banco-pago", "imagem-hotlink", "imagem-origem-desconhecida", "fonte-comercial"):
            self.assertRule(r)

    def test_empresa_e_lgpd(self):
        for r in ("cnpj-invalido", "form-http", "sem-canal-titular", "senha-sem-hash",
                  "storage-dado-pessoal", "env-nao-ignorado", "promocao-sorteio"):
            self.assertRule(r)

    def test_texto_da_politica_nao_vira_rastreador(self):
        # o documento de termos não pode ser tratado como código de rastreamento
        self.assertTrue(all(f.get("arquivo") != "termos.html" or f["item"] in (2, 4) for f in self.sc.findings
                            if f["regra"].startswith(("rastreador", "consentimento-tacito"))))


class TestSiteLimpo(unittest.TestCase):
    def test_sem_achados_graves(self):
        sc = Scanner(os.path.join(FIXTURES, "site-limpo")).run()
        graves = [f for f in sc.findings if f["severidade"] in ("critico", "alto", "medio")]
        self.assertEqual(graves, [], graves)
        self.assertEqual(sc.p["empresa"]["cnpj_validos"], ["11.222.333/0001-81"])


class TestCLI(unittest.TestCase):
    def test_json(self):
        out = subprocess.run([sys.executable, os.path.join(SCRIPTS, "scan.py"),
                              os.path.join(FIXTURES, "site-limpo"), "--format", "json"],
                             capture_output=True, text=True, encoding="utf-8", check=True).stdout
        self.assertIn('"perfil"', out)


if __name__ == "__main__":
    unittest.main()
