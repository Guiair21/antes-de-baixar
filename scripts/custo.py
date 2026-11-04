#!/usr/bin/env python3
"""Converte tokens em proporção do limite semanal e do valor mensal de cada plano.

O limite em tokens não é publicado, então a conta usa uma calibração medida com /usage:
  python custo.py calibrar --plano NOME --tokens 250000 --pct 3.5
  python custo.py calcular --min 200000 --max 300000
"""
import argparse
import json
import pathlib

ARQ = pathlib.Path(__file__).with_name("planos.json")
SEMANAS_POR_MES = 52 / 12


def carregar():
    return json.loads(ARQ.read_text(encoding="utf-8"))


def calibrar(a):
    if a.tokens <= 0 or a.pct <= 0:
        raise SystemExit("tokens e pct precisam ser maiores que zero")
    d = carregar()
    if a.plano not in d:
        raise SystemExit(f"plano desconhecido: {a.plano}. Existentes: {', '.join(d)}")
    d[a.plano]["pct_semana_por_100k"] = round(a.pct / a.tokens * 100000, 4)
    ARQ.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{a.plano}: {d[a.plano]['pct_semana_por_100k']}% da semana a cada 100 mil tokens")


def calcular(a):
    for nome, p in carregar().items():
        c = p.get("pct_semana_por_100k")
        if not c:
            print(f"{nome}: não calibrado, sem proporção para mostrar")
            continue
        pmin, pmax = (a.min * c / 100000, a.max * c / 100000)
        semana = p["valor_mes"] / SEMANAS_POR_MES
        vmin, vmax = (semana * pmin / 100, semana * pmax / 100)
        print(f"{nome}: {pmin:.1f}% a {pmax:.1f}% da semana; {p['moeda']} {vmin:.2f} a {vmax:.2f} do valor pago")


ap = argparse.ArgumentParser()
sub = ap.add_subparsers(dest="cmd", required=True)
c1 = sub.add_parser("calibrar")
c1.add_argument("--plano", required=True)
c1.add_argument("--tokens", type=float, required=True)
c1.add_argument("--pct", type=float, required=True)
c2 = sub.add_parser("calcular")
c2.add_argument("--min", type=float, required=True)
c2.add_argument("--max", type=float, required=True)
a = ap.parse_args()
calibrar(a) if a.cmd == "calibrar" else calcular(a)
