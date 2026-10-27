#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
contraste.py - Calcula a razão de contraste WCAG entre duas cores e sugere a
cor de texto mais próxima (mesmo matiz) que atinge o mínimo exigido.

Uso:
    python contraste.py "#999999" "#ffffff"
    python contraste.py "rgb(120,120,120)" white --alvo 7
    python contraste.py "#aaa" "#fff" --grande          # texto grande: mínimo 3:1
    python contraste.py "#aaa" "#fff" --json

Critérios WCAG 2.2 / ABNT NBR 17225:
    1.4.3  (AA)  4.5:1 texto normal | 3:1 texto grande (>= 24px, ou >= 18.66px em negrito)
    1.4.6  (AAA) 7:1 texto normal   | 4.5:1 texto grande
    1.4.11 (AA)  3:1 componentes de interface, bordas de campos, ícones e gráficos

Também é importado por scan.py (somente biblioteca padrão).
"""

import argparse
import colorsys
import json
import re
import sys

NAMED = {
    "white": "#ffffff", "black": "#000000", "red": "#ff0000", "green": "#008000",
    "blue": "#0000ff", "gray": "#808080", "grey": "#808080", "silver": "#c0c0c0",
    "yellow": "#ffff00", "orange": "#ffa500", "purple": "#800080", "navy": "#000080",
    "teal": "#008080", "maroon": "#800000", "olive": "#808000", "lime": "#00ff00",
    "aqua": "#00ffff", "cyan": "#00ffff", "fuchsia": "#ff00ff", "magenta": "#ff00ff",
    "pink": "#ffc0cb", "brown": "#a52a2a", "darkgray": "#a9a9a9", "darkgrey": "#a9a9a9",
    "lightgray": "#d3d3d3", "lightgrey": "#d3d3d3", "gold": "#ffd700",
    "whitesmoke": "#f5f5f5", "gainsboro": "#dcdcdc", "dimgray": "#696969",
    "dimgrey": "#696969", "lightblue": "#add8e6", "lightgreen": "#90ee90",
    "coral": "#ff7f50", "tomato": "#ff6347", "salmon": "#fa8072", "khaki": "#f0e68c",
    "beige": "#f5f5dc", "ivory": "#fffff0", "snow": "#fffafa", "crimson": "#dc143c",
    "indigo": "#4b0082", "violet": "#ee82ee", "skyblue": "#87ceeb",
    "steelblue": "#4682b4", "slategray": "#708090", "darkblue": "#00008b",
    "darkgreen": "#006400", "darkred": "#8b0000",
}


def _opaque(alpha):
    alpha = alpha.strip()
    if alpha.endswith("%"):
        return float(alpha[:-1]) >= 100
    return float(alpha) >= 1


def _channel(value):
    value = value.strip()
    if value.endswith("%"):
        num = float(value[:-1]) * 2.55
    else:
        num = float(value)
    return max(0, min(255, int(round(num))))


def parse_color(value):
    """Converte uma cor CSS em (r, g, b) 0-255.

    Retorna None se a cor não for reconhecida ou for translúcida (nesse caso o
    contraste depende do que está atrás e não pode ser calculado isoladamente).
    """
    if not value:
        return None
    v = re.sub(r"\s*!important\s*$", "", value.strip().lower())
    v = NAMED.get(v, v)
    try:
        m = re.fullmatch(r"#([0-9a-f]{3,8})", v)
        if m:
            h = m.group(1)
            if len(h) in (3, 4):
                if len(h) == 4 and h[3] != "f":
                    return None
                h = "".join(c * 2 for c in h[:3])
            elif len(h) == 8:
                if h[6:] != "ff":
                    return None
                h = h[:6]
            elif len(h) != 6:
                return None
            return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
        m = re.fullmatch(
            r"rgba?\(\s*([\d.]+%?)[\s,]+([\d.]+%?)[\s,]+([\d.]+%?)(?:\s*[,/]\s*([\d.]+%?))?\s*\)", v)
        if m:
            if m.group(4) is not None and not _opaque(m.group(4)):
                return None
            return tuple(_channel(x) for x in m.group(1, 2, 3))
        m = re.fullmatch(
            r"hsla?\(\s*([\d.]+)(?:deg)?[\s,]+([\d.]+)%[\s,]+([\d.]+)%(?:\s*[,/]\s*([\d.]+%?))?\s*\)", v)
        if m:
            if m.group(4) is not None and not _opaque(m.group(4)):
                return None
            h = float(m.group(1)) % 360 / 360
            s = float(m.group(2)) / 100
            l = float(m.group(3)) / 100
            r, g, b = colorsys.hls_to_rgb(h, l, s)
            return (round(r * 255), round(g * 255), round(b * 255))
    except ValueError:
        return None
    return None


def to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def relative_luminance(rgb):
    def lin(c):
        c = c / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(fg, bg):
    l1, l2 = relative_luminance(fg), relative_luminance(bg)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def _with_lightness(h, l, s):
    r, g, b = colorsys.hls_to_rgb(h, max(0.0, min(1.0, l)), s)
    return (round(r * 255), round(g * 255), round(b * 255))


def suggest(fg, bg, target=4.5):
    """Menor ajuste de luminosidade (mantendo matiz e saturação) da cor do
    texto para atingir `target` contra o fundo. Retorna (r, g, b) ou None."""
    if contrast_ratio(fg, bg) >= target:
        return fg
    h, l, s = colorsys.rgb_to_hls(*(c / 255 for c in fg))
    best = None
    for direction in (-1, 1):
        room = l if direction < 0 else 1 - l
        if contrast_ratio(_with_lightness(h, l + direction * room, s), bg) < target:
            continue
        lo, hi = 0.0, room
        for _ in range(40):
            mid = (lo + hi) / 2
            if contrast_ratio(_with_lightness(h, l + direction * mid, s), bg) >= target:
                hi = mid
            else:
                lo = mid
        delta = hi
        cand = _with_lightness(h, l + direction * delta, s)
        while contrast_ratio(cand, bg) < target and delta < room:
            delta = min(room, delta + 0.002)
            cand = _with_lightness(h, l + direction * delta, s)
        if contrast_ratio(cand, bg) >= target and (best is None or delta < best[0]):
            best = (delta, cand)
    return best[1] if best else None


def main():
    parser = argparse.ArgumentParser(description="Razão de contraste WCAG entre duas cores.")
    parser.add_argument("texto", help="cor do texto/primeiro plano (hex, rgb(), hsl() ou nome)")
    parser.add_argument("fundo", help="cor do fundo")
    parser.add_argument("--alvo", type=float, help="razão mínima desejada (padrão 4.5, ou 3 com --grande)")
    parser.add_argument("--grande", action="store_true", help="texto grande (>= 24px ou >= 18.66px negrito)")
    parser.add_argument("--json", action="store_true", help="saída em JSON")
    args = parser.parse_args()

    fg, bg = parse_color(args.texto), parse_color(args.fundo)
    if fg is None or bg is None:
        print("Cor não reconhecida ou translúcida: use cores opacas (hex, rgb(), hsl() ou nomes CSS).", file=sys.stderr)
        sys.exit(2)

    target = args.alvo or (3.0 if args.grande else 4.5)
    ratio = contrast_ratio(fg, bg)
    sug = suggest(fg, bg, target)
    result = {
        "texto": to_hex(fg),
        "fundo": to_hex(bg),
        "razao": round(ratio, 2),
        "aa_texto_normal": ratio >= 4.5,
        "aa_texto_grande": ratio >= 3.0,
        "aa_componentes": ratio >= 3.0,
        "aaa_texto_normal": ratio >= 7.0,
        "aaa_texto_grande": ratio >= 4.5,
        "alvo": target,
        "sugestao": to_hex(sug) if sug else None,
        "razao_sugestao": round(contrast_ratio(sug, bg), 2) if sug else None,
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    def ok(flag):
        return "APROVADO" if flag else "REPROVADO"

    print("Cor do texto:  {}".format(result["texto"]))
    print("Cor do fundo:  {}".format(result["fundo"]))
    print("Contraste:     {:.2f}:1".format(ratio))
    print("AA  texto normal (4.5:1) ........ {}".format(ok(result["aa_texto_normal"])))
    print("AA  texto grande (3:1) .......... {}".format(ok(result["aa_texto_grande"])))
    print("AA  componentes/ícones (3:1) .... {}".format(ok(result["aa_componentes"])))
    print("AAA texto normal (7:1) .......... {}".format(ok(result["aaa_texto_normal"])))
    if ratio >= target:
        print("Já atinge o alvo de {}:1.".format(target))
    elif sug:
        print("Sugestão (mesmo tom) para {}:1 -> {} ({:.2f}:1)".format(
            target, result["sugestao"], result["razao_sugestao"]))
    else:
        print("Não há variação de luminosidade deste tom que atinja {}:1; troque a cor do fundo.".format(target))


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    main()
