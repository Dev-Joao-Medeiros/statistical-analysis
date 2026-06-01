"""
=============================================================
  TRABALHO FINAL DE ESTATÍSTICA - UFPA Campus Castanhal
  Faculdade de Computação | Engenharia de Computação
  Prof. Clenilson Rodrigues da Silveira
=============================================================
  Executar:  python3 trabalho_estatistica.py
=============================================================
"""

import os
import warnings
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy import stats

warnings.filterwarnings("ignore")

PASTA_SAIDA = "resultados_estatistica"
os.makedirs(PASTA_SAIDA, exist_ok=True)

# ═══════════════════════════════════════════════════════════
#  CORES / ESTILO
# ═══════════════════════════════════════════════════════════
COR_BG       = "#1e2230"
COR_PAINEL   = "#252b3b"
COR_CARD     = "#2d3448"
COR_DESTAQUE = "#4f8ef7"
COR_VERDE    = "#2ecc71"
COR_VERMELHO = "#e74c3c"
COR_TEXTO    = "#e8eaf0"
COR_SUBTEXTO = "#8892a4"
FONTE_TITULO = ("Segoe UI", 15, "bold")
FONTE_LABEL  = ("Segoe UI", 10)
FONTE_BOLD   = ("Segoe UI", 10, "bold")
FONTE_MONO   = ("Courier New", 9)

plt.rcParams.update({
    "figure.facecolor": COR_PAINEL,
    "axes.facecolor":   COR_CARD,
    "axes.labelcolor":  COR_TEXTO,
    "xtick.color":      COR_SUBTEXTO,
    "ytick.color":      COR_SUBTEXTO,
    "axes.titlecolor":  COR_TEXTO,
    "axes.edgecolor":   "#3a4257",
    "grid.color":       "#3a4257",
    "text.color":       COR_TEXTO,
    "axes.grid":        True,
    "grid.alpha":       0.4,
    "figure.dpi":       100,
})

# ═══════════════════════════════════════════════════════════
#  LÓGICA ESTATÍSTICA
# ═══════════════════════════════════════════════════════════

def calcular_parametros(dados, ddof=0):
    moda_r = stats.mode(dados, keepdims=True)
    return dict(
        n        = len(dados),
        media    = float(np.mean(dados)),
        variancia= float(np.var(dados, ddof=ddof)),
        dp       = float(np.std(dados, ddof=ddof)),
        mediana  = float(np.median(dados)),
        moda     = float(moda_r.mode[0]),
    )

def gerar_populacao_exemplo():
    np.random.seed(42)
    n = 15_000
    p1 = np.random.normal(170, 10, int(n * 0.7))
    p2 = np.random.normal(190,  8, int(n * 0.3))
    d  = np.concatenate([p1, p2])
    np.random.shuffle(d)
    return d

def carregar_csv(caminho, coluna):
    ext = os.path.splitext(caminho)[1].lower()
    df  = pd.read_excel(caminho) if ext in (".xlsx", ".xls") else pd.read_csv(caminho)
    return df[coluna].dropna().values.astype(float)

# ═══════════════════════════════════════════════════════════
#  JANELA PRINCIPAL
# ═══════════════════════════════════════════════════════════

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AAP — Análise de Amostras e Populações")
        self.geometry("1100x780")
        self.minsize(900, 650)
        self.configure(bg=COR_BG)

        self.populacao   = None
        self.params_pop  = None
        self.coluna_var  = tk.StringVar()
        self.arquivo_var = tk.StringVar(value="Nenhum arquivo selecionado")
        self.nivel_var   = tk.StringVar(value="95")
        self.status_var  = tk.StringVar(value="Aguardando dados…")

        self._build_ui()

    # ── Construção da UI ────────────────────────────────────
    def _build_ui(self):
        # ── Cabeçalho ──
        cab = tk.Frame(self, bg=COR_DESTAQUE, pady=12)
        cab.pack(fill="x")
        tk.Label(cab, text="📊  AAP — Análise de Amostras e Populações",
                 font=("Segoe UI", 17, "bold"), bg=COR_DESTAQUE, fg="white").pack()
        tk.Label(cab, text="UFPA Campus Castanhal  ·  Prof. Clenilson Rodrigues",
                 font=("Segoe UI", 9), bg=COR_DESTAQUE, fg="#cfe0ff").pack()

        # ── Notebook (abas) ──
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook",       background=COR_BG,    borderwidth=0)
        style.configure("TNotebook.Tab",   background=COR_CARD,  foreground=COR_SUBTEXTO,
                        padding=[14, 6],   font=("Segoe UI", 10))
        style.map("TNotebook.Tab",
                  background=[("selected", COR_DESTAQUE)],
                  foreground=[("selected", "white")])

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=8)

        self.aba_dados    = self._frame_aba(nb)
        self.aba_pop      = self._frame_aba(nb)
        self.aba_amostras = self._frame_aba(nb)
        self.aba_100      = self._frame_aba(nb)
        self.aba_log      = self._frame_aba(nb)
        self.aba_sobre    = self._frame_aba(nb)

        nb.add(self.aba_dados,    text="  📂  Dados  ")
        nb.add(self.aba_pop,      text="  📈  Parâmentros Populacionais  ")
        nb.add(self.aba_amostras, text="  🔬  Amostras com Tamanhanos Variados  ")
        nb.add(self.aba_100,      text="  🔁  Amostras de Tamanho Fixo  ")
        nb.add(self.aba_log,      text="  📋  Log  ")
        nb.add(self.aba_sobre,    text="  ℹ️  Sobre  ")

        self._build_aba_dados()
        self._build_aba_pop()
        self._build_aba_amostras()
        self._build_aba_100()
        self._build_aba_log()
        self._build_aba_sobre()

        # ── Barra de status ──
        status = tk.Frame(self, bg="#161a24", pady=4)
        status.pack(fill="x", side="bottom")
        tk.Label(status, textvariable=self.status_var,
                 bg="#161a24", fg=COR_SUBTEXTO, font=("Segoe UI", 9)).pack(side="left", padx=10)

    def _frame_aba(self, nb):
        f = tk.Frame(nb, bg=COR_BG)
        return f

    # ── Aba 0: Dados ────────────────────────────────────────
    def _build_aba_dados(self):
        f = self.aba_dados
        self._titulo(f, "Fonte de Dados")

        # Card CSV
        card = self._card(f, "📄  Carregar arquivo CSV ou Excel")
        tk.Label(card, text="Selecione o arquivo:", bg=COR_CARD, fg=COR_SUBTEXTO,
                 font=FONTE_LABEL).pack(anchor="w", padx=15, pady=(10,2))
        row = tk.Frame(card, bg=COR_CARD)
        row.pack(fill="x", padx=15, pady=4)
        tk.Label(row, textvariable=self.arquivo_var, bg=COR_CARD, fg=COR_TEXTO,
                 font=FONTE_MONO, anchor="w").pack(side="left", fill="x", expand=True)
        self._btn(row, "Procurar…", self._selecionar_arquivo).pack(side="right")

        tk.Label(card, text="Coluna numérica:", bg=COR_CARD, fg=COR_SUBTEXTO,
                 font=FONTE_LABEL).pack(anchor="w", padx=15, pady=(8,2))
        self.combo_colunas = ttk.Combobox(card, textvariable=self.coluna_var,
                                          state="readonly", width=35,
                                          font=FONTE_LABEL)
        self.combo_colunas.pack(anchor="w", padx=15, pady=4)
        self._btn(card, "✔  Carregar este arquivo", self._carregar_arquivo,
                  cor=COR_VERDE).pack(anchor="w", padx=15, pady=(4,14))

        # Separador
        tk.Label(f, text="— ou —", bg=COR_BG, fg=COR_SUBTEXTO,
                 font=("Segoe UI", 10)).pack(pady=6)

        # Card exemplo
        card2 = self._card(f, "🎲  Usar população de exemplo")
        tk.Label(card2, text="15 000 alturas simuladas (mistura de duas normais).",
                 bg=COR_CARD, fg=COR_SUBTEXTO, font=FONTE_LABEL).pack(anchor="w", padx=15, pady=(8,4))
        self._btn(card2, "✔  Usar dados de exemplo", self._usar_exemplo,
                  cor=COR_DESTAQUE).pack(anchor="w", padx=15, pady=(4,14))

        # Resumo
        self.label_resumo = tk.Label(f, text="", bg=COR_BG, fg=COR_VERDE,
                                     font=("Segoe UI", 10, "bold"))
        self.label_resumo.pack(pady=8)

    # ── Aba 1: População ────────────────────────────────────
    def _build_aba_pop(self):
        f = self.aba_pop
        self._titulo(f, "Parâmetros Populacionais")

        # Tabela de parâmetros
        self.frame_params = self._card(f, "Parâmetros")
        self.labels_params = {}
        pars = [("N (elementos)", "n"), ("Média (μ)", "media"),
                ("Variância (σ²)", "variancia"), ("Desvio Padrão (σ)", "dp"),
                ("Mediana", "mediana"), ("Moda", "moda")]
        grid = tk.Frame(self.frame_params, bg=COR_CARD)
        grid.pack(padx=15, pady=10)
        for i, (nome, chave) in enumerate(pars):
            tk.Label(grid, text=nome+":", bg=COR_CARD, fg=COR_SUBTEXTO,
                     font=FONTE_LABEL, width=22, anchor="e").grid(row=i, column=0, sticky="e", pady=3)
            lbl = tk.Label(grid, text="—", bg=COR_CARD, fg=COR_TEXTO,
                           font=FONTE_BOLD, width=18, anchor="w")
            lbl.grid(row=i, column=1, sticky="w", padx=10)
            self.labels_params[chave] = lbl

        # Simetria
        self.frame_simetria = self._card(f, "Análise de Simetria")
        self.label_simetria = tk.Label(self.frame_simetria, text="—", bg=COR_CARD,
                                       fg=COR_TEXTO, font=FONTE_MONO, justify="left")
        self.label_simetria.pack(padx=15, pady=10, anchor="w")

        btn_row = tk.Frame(f, bg=COR_BG)
        btn_row.pack(pady=10)
        self._btn(btn_row, "▶  Calcular e Gerar Gráficos", self._rodar_parte1,
                  cor=COR_DESTAQUE).pack(side="left", padx=6)

        # Área do gráfico
        self.canvas_pop = None
        self.frame_grafico_pop = tk.Frame(f, bg=COR_BG)
        self.frame_grafico_pop.pack(fill="both", expand=True, padx=10, pady=4)

    # ── Aba 2: Amostras variadas ────────────────────────────
    def _build_aba_amostras(self):
        f = self.aba_amostras
        self._titulo(f, "Amostras com Tamanhos Variados (1%, 5%, 10%)")

        btn_row = tk.Frame(f, bg=COR_BG)
        btn_row.pack(pady=10)
        self._btn(btn_row, "▶  Gerar Amostras e Comparar", self._rodar_parte21,
                  cor=COR_DESTAQUE).pack()

        self.frame_tabela_amostras = self._card(f, "Comparação com a População (%)")
        self.text_tabela_amostras  = tk.Text(self.frame_tabela_amostras, height=10,
                                             bg=COR_CARD, fg=COR_TEXTO, font=FONTE_MONO,
                                             relief="flat", state="disabled")
        self.text_tabela_amostras.pack(fill="x", padx=10, pady=8)

        self.frame_grafico_amostras = tk.Frame(f, bg=COR_BG)
        self.frame_grafico_amostras.pack(fill="both", expand=True, padx=10, pady=4)

    # ── Aba 3: 100 amostras ─────────────────────────────────
    def _build_aba_100(self):
        f = self.aba_100
        self._titulo(f, "100 Amostras de Tamanho Fixo (1%)")

        cfg = self._card(f, "Configuração")
        row = tk.Frame(cfg, bg=COR_CARD)
        row.pack(padx=15, pady=10)
        tk.Label(row, text="Nível de confiança (%):", bg=COR_CARD, fg=COR_SUBTEXTO,
                 font=FONTE_LABEL).pack(side="left")
        self.spin_nivel = tk.Spinbox(row, from_=80, to=99, textvariable=self.nivel_var,
                                     width=5, font=FONTE_BOLD, bg=COR_CARD, fg=COR_TEXTO,
                                     buttonbackground=COR_CARD, relief="flat")
        self.spin_nivel.pack(side="left", padx=8)
        self._btn(row, "▶  Executar Análise", self._rodar_parte22,
                  cor=COR_DESTAQUE).pack(side="left", padx=12)

        self.frame_res100 = self._card(f, "Resultados")
        self.text_res100  = tk.Text(self.frame_res100, height=12,
                                    bg=COR_CARD, fg=COR_TEXTO, font=FONTE_MONO,
                                    relief="flat", state="disabled")
        self.text_res100.pack(fill="x", padx=10, pady=8)

        self.frame_grafico_100 = tk.Frame(f, bg=COR_BG)
        self.frame_grafico_100.pack(fill="both", expand=True, padx=10, pady=4)

    # ── Aba 4: Log ──────────────────────────────────────────
    def _build_aba_log(self):
        f = self.aba_log
        self._titulo(f, "Log de Execução")
        frame = tk.Frame(f, bg=COR_BG)
        frame.pack(fill="both", expand=True, padx=10, pady=6)
        scroll = tk.Scrollbar(frame)
        scroll.pack(side="right", fill="y")
        self.text_log = tk.Text(frame, bg=COR_PAINEL, fg=COR_TEXTO, font=FONTE_MONO,
                                relief="flat", yscrollcommand=scroll.set, state="disabled")
        self.text_log.pack(fill="both", expand=True)
        scroll.config(command=self.text_log.yview)
        self._btn(f, "🗑  Limpar Log", self._limpar_log).pack(pady=6)

    # ── Aba 5: Sobre ────────────────────────────────────────
    def _build_aba_sobre(self):
        f = self.aba_sobre

        # Scroll container
        canvas_scroll = tk.Canvas(f, bg=COR_BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(f, orient="vertical", command=canvas_scroll.yview)
        canvas_scroll.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas_scroll.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas_scroll, bg=COR_BG)
        canvas_scroll.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>",
                   lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all")))

        # ── Cabeçalho do software ──
        topo = tk.Frame(inner, bg=COR_DESTAQUE, pady=20)
        topo.pack(fill="x", padx=0, pady=(0, 16))
        tk.Label(topo, text="📊", font=("Segoe UI", 36), bg=COR_DESTAQUE, fg="white").pack()
        tk.Label(topo, text="AAP — Análise de Amostras e Populações",
                 font=("Segoe UI", 16, "bold"), bg=COR_DESTAQUE, fg="white").pack(pady=(4, 2))
        tk.Label(topo, text="Trabalho Final de Estatística  ·  UFPA Campus Castanhal",
                 font=("Segoe UI", 10), bg=COR_DESTAQUE, fg="#cfe0ff").pack()
        tk.Label(topo, text="Faculdade de Computação  ·  Engenharia de Computação",
                 font=("Segoe UI", 9), bg=COR_DESTAQUE, fg="#cfe0ff").pack()
        tk.Label(topo, text="Prof. Clenilson Rodrigues da Silveira",
                 font=("Segoe UI", 9, "italic"), bg=COR_DESTAQUE, fg="#cfe0ff").pack()

        # ── Card: Objetivo ──
        card_obj = self._card(inner, "🎯  Objetivo do Software")
        objetivo_txt = (
            "Este software foi desenvolvido como trabalho final da disciplina de Estatística e tem como objetivo "
            "fornecer uma ferramenta interativa para o estudo e a visualização dos principais conceitos de "
            "Estatística Descritiva e Inferencial aplicados à análise de populações e amostras.\n\n"
            "O AAP permite ao usuário:\n"
            "  • Carregar dados reais (CSV ou Excel) ou utilizar uma população sintética de exemplo;\n"
            "  • Calcular e visualizar os parâmetros populacionais (média, variância, desvio padrão, mediana e moda);\n"
            "  • Analisar a simetria e a normalidade da distribuição via assimetria, curtose e teste estatístico;\n"
            "  • Gerar amostras de tamanhos variados (1%, 5% e 10% da população) e comparar seus\n"
            "    estimadores com os parâmetros populacionais reais;\n"
            "  • Extrair 100 amostras de tamanho fixo (1%) para demonstrar o Teorema Central do Limite,\n"
            "    verificar o comportamento dos estimadores (média, variância, soma) e construir\n"
            "    intervalos de confiança com nível configurável pelo usuário."
        )
        tk.Label(card_obj, text=objetivo_txt, bg=COR_CARD, fg=COR_TEXTO,
                 font=FONTE_LABEL, justify="left", wraplength=820,
                 anchor="w").pack(anchor="w", padx=18, pady=(6, 14))

        # ── Card: Como funciona ──
        card_how = self._card(inner, "⚙️  Como Funciona")
        passos = [
            ("1.  Aba  📂 Dados",
             "Carregue um arquivo CSV/Excel escolhendo a coluna numérica desejada, ou utilize a "
             "população de exemplo gerada automaticamente (15 000 alturas simuladas a partir de uma "
             "mistura de duas distribuições normais)."),
            ("2.  Aba  📈 Parâmetros Populacionais",
             "Clique em  ▶ Calcular e Gerar Gráficos  para obter N, μ, σ², σ, mediana e moda da "
             "população completa, além da análise de simetria (skewness, curtose e teste de "
             "normalidade). Um histograma com KDE e um boxplot são gerados e salvos automaticamente."),
            ("3.  Aba  🔬 Amostras com Tamanhos Variados",
             "Gera amostras aleatórias de 1%, 5% e 10% da população (sem reposição) e exibe uma "
             "tabela comparativa com o desvio percentual de cada estimador em relação ao parâmetro "
             "populacional verdadeiro, acompanhada de histogramas sobrepostos com KDE."),
            ("4.  Aba  🔁 Amostras de Tamanho Fixo",
             "Extrai 100 amostras independentes de tamanho 1% da população. Calcula a média, "
             "variância e soma de cada uma, verifica o não-enviesamento dos estimadores, compara "
             "a variância das médias com o valor teórico σ²/n, e exibe os intervalos de confiança "
             "das primeiras 50 amostras destacando quais contêm a média populacional."),
            ("5.  Aba  📋 Log",
             "Registra todas as operações executadas durante a sessão, permitindo rastreabilidade "
             "e revisão dos resultados numéricos sem a necessidade de refazer as análises."),
        ]
        for titulo_p, descricao_p in passos:
            frame_p = tk.Frame(card_how, bg=COR_CARD)
            frame_p.pack(fill="x", padx=18, pady=5)
            tk.Label(frame_p, text=titulo_p, font=FONTE_BOLD,
                     bg=COR_CARD, fg=COR_DESTAQUE, anchor="w").pack(anchor="w")
            tk.Label(frame_p, text=descricao_p, font=FONTE_LABEL,
                     bg=COR_CARD, fg=COR_TEXTO, justify="left",
                     wraplength=800, anchor="w").pack(anchor="w", padx=14, pady=(2, 4))
        tk.Frame(card_how, bg=COR_CARD, height=8).pack()  # padding bottom

        # ── Card: Discentes ──
        card_disc = self._card(inner, "👨‍💻  Discentes")
        discentes = [
            ("Vitorio Augusto Moraes Cunha",   "Engenharia de Computação"),
            ("Éfran Santos Sousa",              "Engenharia de Computação"),
            ("João Manoel Medeiros Matos",      "Engenharia de Computação"),
        ]
        grid_d = tk.Frame(card_disc, bg=COR_CARD)
        grid_d.pack(padx=18, pady=12)
        for i, (nome, curso) in enumerate(discentes):
            # Ícone / número
            tk.Label(grid_d, text=f"0{i+1}", font=("Courier New", 14, "bold"),
                     bg=COR_DESTAQUE, fg="white", width=3,
                     relief="flat", pady=6).grid(row=i, column=0, padx=(0, 12), pady=5, sticky="ns")
            bloco = tk.Frame(grid_d, bg=COR_CARD)
            bloco.grid(row=i, column=1, sticky="w", pady=5)
            tk.Label(bloco, text=nome, font=("Segoe UI", 11, "bold"),
                     bg=COR_CARD, fg=COR_TEXTO, anchor="w").pack(anchor="w")
            tk.Label(bloco, text=curso, font=("Segoe UI", 9),
                     bg=COR_CARD, fg=COR_SUBTEXTO, anchor="w").pack(anchor="w")

        # ── Card: Tecnologias ──
        card_tec = self._card(inner, "🛠️  Tecnologias Utilizadas")
        techs = [
            ("Python 3",       "Linguagem principal"),
            ("Tkinter / ttk",  "Interface gráfica nativa"),
            ("NumPy",          "Operações numéricas e amostragem"),
            ("Pandas",         "Leitura e manipulação de dados CSV/Excel"),
            ("Matplotlib",     "Geração dos gráficos embutidos"),
            ("SciPy",          "Cálculo de assimetria, curtose, KDE e testes estatísticos"),
        ]
        grid_t = tk.Frame(card_tec, bg=COR_CARD)
        grid_t.pack(padx=18, pady=10)
        for i, (lib, desc) in enumerate(techs):
            col = i % 2
            row_t = i // 2
            cell = tk.Frame(grid_t, bg="#343d55", padx=12, pady=8)
            cell.grid(row=row_t, column=col, padx=6, pady=4, sticky="ew")
            tk.Label(cell, text=lib, font=FONTE_BOLD,
                     bg="#343d55", fg=COR_DESTAQUE).pack(anchor="w")
            tk.Label(cell, text=desc, font=("Segoe UI", 9),
                     bg="#343d55", fg=COR_SUBTEXTO).pack(anchor="w")
        grid_t.columnconfigure(0, weight=1)
        grid_t.columnconfigure(1, weight=1)

        # ── Rodapé ──
        tk.Frame(inner, bg=COR_BG, height=20).pack()
        tk.Label(inner,
                 text="© 2026  UFPA Campus Castanhal  ·  Todos os direitos reservados",
                 font=("Segoe UI", 8), bg=COR_BG, fg=COR_SUBTEXTO).pack(pady=(0, 12))

    # ── Helpers de UI ───────────────────────────────────────
    def _titulo(self, parent, texto):
        tk.Label(parent, text=texto, font=FONTE_TITULO,
                 bg=COR_BG, fg=COR_TEXTO).pack(anchor="w", padx=14, pady=(12, 4))

    def _card(self, parent, titulo):
        outer = tk.Frame(parent, bg=COR_DESTAQUE, padx=1, pady=1)
        outer.pack(fill="x", padx=12, pady=5)
        inner = tk.Frame(outer, bg=COR_CARD)
        inner.pack(fill="both")
        tk.Label(inner, text=titulo, font=FONTE_BOLD,
                 bg=COR_CARD, fg=COR_DESTAQUE).pack(anchor="w", padx=14, pady=(8, 2))
        return inner

    def _btn(self, parent, texto, cmd, cor=COR_CARD):
        return tk.Button(parent, text=texto, command=cmd,
                         bg=cor, fg="white", font=FONTE_BOLD,
                         relief="flat", padx=14, pady=6, cursor="hand2",
                         activebackground="#3a5fc4", activeforeground="white")

    def _log(self, msg):
        self.text_log.config(state="normal")
        self.text_log.insert("end", msg + "\n")
        self.text_log.see("end")
        self.text_log.config(state="disabled")

    def _limpar_log(self):
        self.text_log.config(state="normal")
        self.text_log.delete("1.0", "end")
        self.text_log.config(state="disabled")

    def _set_texto(self, widget, texto):
        widget.config(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", texto)
        widget.config(state="disabled")

    def _embed_fig(self, fig, frame):
        for w in frame.winfo_children():
            w.destroy()
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

    def _status(self, msg):
        self.status_var.set(msg)
        self.update_idletasks()

    # ═══════════════════════════════════════════════════════
    #  AÇÕES
    # ═══════════════════════════════════════════════════════

    def _selecionar_arquivo(self):
        caminho = filedialog.askopenfilename(
            title="Selecionar base de dados",
            filetypes=[("CSV / Excel", "*.csv *.xlsx *.xls"), ("Todos", "*.*")])
        if not caminho:
            return
        self.arquivo_var.set(caminho)
        try:
            ext = os.path.splitext(caminho)[1].lower()
            df  = pd.read_excel(caminho) if ext in (".xlsx", ".xls") else pd.read_csv(caminho)
            cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if not cols:
                messagebox.showerror("Erro", "Nenhuma coluna numérica encontrada.")
                return
            self.combo_colunas["values"] = cols
            self.combo_colunas.current(0)
            self._log(f"Arquivo: {os.path.basename(caminho)} | {len(df):,} linhas | colunas: {cols}")
        except Exception as e:
            messagebox.showerror("Erro ao ler arquivo", str(e))

    def _carregar_arquivo(self):
        caminho = self.arquivo_var.get()
        coluna  = self.coluna_var.get()
        if caminho == "Nenhum arquivo selecionado" or not coluna:
            messagebox.showwarning("Atenção", "Selecione um arquivo e uma coluna primeiro.")
            return
        try:
            self.populacao  = carregar_csv(caminho, coluna)
            self.params_pop = None
            n = len(self.populacao)
            self.label_resumo.config(text=f"✔  {n:,} elementos carregados da coluna '{coluna}'")
            self._status(f"Dados carregados: {n:,} elementos")
            self._log(f"Coluna '{coluna}' carregada — {n:,} elementos.")
            messagebox.showinfo("Pronto!", f"{n:,} elementos carregados com sucesso.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _usar_exemplo(self):
        self.populacao  = gerar_populacao_exemplo()
        self.params_pop = None
        n = len(self.populacao)
        self.label_resumo.config(text=f"✔  {n:,} elementos de exemplo carregados (alturas simuladas)")
        self._status(f"Dados de exemplo carregados: {n:,} elementos")
        self._log(f"População de exemplo gerada — {n:,} elementos.")
        messagebox.showinfo("Pronto!", f"População de exemplo com {n:,} elementos pronta.")

    def _checar_dados(self):
        if self.populacao is None:
            messagebox.showwarning("Sem dados", "Carregue os dados na aba  📂 Dados  primeiro.")
            return False
        return True

    # ── Parte 1 ─────────────────────────────────────────────
    def _rodar_parte1(self):
        if not self._checar_dados(): return
        threading.Thread(target=self._exec_parte1, daemon=True).start()

    def _exec_parte1(self):
        self._status("Calculando parâmetros populacionais…")
        dados = self.populacao
        p = calcular_parametros(dados, ddof=0)
        self.params_pop = p

        # Atualiza labels
        fmt = {
            "n":         f"{p['n']:,}",
            "media":     f"{p['media']:.4f}",
            "variancia": f"{p['variancia']:.4f}",
            "dp":        f"{p['dp']:.4f}",
            "mediana":   f"{p['mediana']:.4f}",
            "moda":      f"{p['moda']:.4f}",
        }
        for chave, lbl in self.labels_params.items():
            lbl.config(text=fmt[chave])

        # Simetria
        assim  = stats.skew(dados)
        curt   = stats.kurtosis(dados)
        sub    = dados if len(dados) <= 5000 else np.random.choice(dados, 5000, replace=False)
        _, pval = stats.normaltest(sub)
        classe = ("aproximadamente simétrica (próx. Normal)" if abs(assim) < 0.5
                  else ("assimétrica à direita" if assim > 0 else "assimétrica à esquerda"))
        norm   = "Normal (p>0.05) ✔" if pval > 0.05 else "Não-Normal (p≤0.05)"
        txt = (f"  Assimetria (skewness) : {assim:+.4f}\n"
               f"  Curtose (excesso)     : {curt:+.4f}\n"
               f"  Classificação         : {classe}\n"
               f"  Teste de Normalidade  : p = {pval:.4f}  →  {norm}")
        self.label_simetria.config(text=txt)

        self._log(f"\n[Parte 1]\n  N={p['n']:,}  μ={p['media']:.4f}  σ²={p['variancia']:.4f}"
                  f"  σ={p['dp']:.4f}  med={p['mediana']:.4f}  moda={p['moda']:.4f}")
        self._log(f"  Assimetria={assim:+.4f}  Curtose={curt:+.4f}  p={pval:.4f} ({norm})")

        # Gráfico
        fig, axes = plt.subplots(1, 2, figsize=(10, 4))
        fig.suptitle("Distribuição de Frequências — População", color=COR_TEXTO, fontsize=12)

        ax = axes[0]
        ax.hist(dados, bins=50, density=True, color=COR_DESTAQUE, alpha=0.7, edgecolor="none")
        kde = stats.gaussian_kde(dados)
        xr  = np.linspace(dados.min(), dados.max(), 300)
        ax.plot(xr, kde(xr), color=COR_VERMELHO, lw=2, label="KDE")
        ax.axvline(p["media"],   color=COR_VERDE,  lw=1.5, ls="--", label=f"Média={p['media']:.2f}")
        ax.axvline(p["mediana"], color="orange",   lw=1.5, ls=":",  label=f"Mediana={p['mediana']:.2f}")
        ax.set_title("Histograma + KDE"); ax.set_xlabel("Valor"); ax.set_ylabel("Densidade")
        ax.legend(fontsize=8)

        bp = axes[1].boxplot(dados, vert=True, patch_artist=True,
                             boxprops=dict(facecolor=COR_DESTAQUE, alpha=0.6),
                             medianprops=dict(color=COR_VERMELHO, lw=2),
                             whiskerprops=dict(color=COR_SUBTEXTO),
                             capprops=dict(color=COR_SUBTEXTO),
                             flierprops=dict(markerfacecolor=COR_SUBTEXTO, markersize=2))
        axes[1].set_title("Boxplot"); axes[1].set_ylabel("Valor")
        axes[1].set_xticks([1]); axes[1].set_xticklabels(["População"])

        fig.tight_layout()
        cam = os.path.join(PASTA_SAIDA, "populacao_distribuicao.png")
        fig.savefig(cam, bbox_inches="tight")
        self.after(0, lambda: self._embed_fig(fig, self.frame_grafico_pop))
        self._status("Parte 1 concluída ✔")

    # ── Parte 2.1 ───────────────────────────────────────────
    def _rodar_parte21(self):
        if not self._checar_dados(): return
        if self.params_pop is None:
            messagebox.showinfo("Atenção", "Execute a Parte 1 primeiro para obter os parâmetros populacionais.")
            return
        threading.Thread(target=self._exec_parte21, daemon=True).start()

    def _exec_parte21(self):
        self._status("Gerando amostras 1%, 5%, 10%…")
        pop = self.populacao
        pp  = self.params_pop
        proporcoes = [0.01, 0.05, 0.10]
        resultados = []

        for prop in proporcoes:
            n_a = max(30, int(len(pop) * prop))
            a   = np.random.choice(pop, size=n_a, replace=False)
            p   = calcular_parametros(a, ddof=1)
            resultados.append((prop, n_a, p))

        # Tabela
        linhas = [f"  {'Parâmetro':<16}  {'1% (n='+str(resultados[0][1])+')':>14}  "
                  f"{'5% (n='+str(resultados[1][1])+')':>14}  {'10% (n='+str(resultados[2][1])+')':>14}",
                  "  " + "─"*68]
        for chave, nome in [("media","Média"),("variancia","Variância"),("dp","Desv. Padrão"),("mediana","Mediana")]:
            ref = pp[chave]
            row = f"  {nome:<16}"
            for _, _, p in resultados:
                dif = (p[chave]-ref)/ref*100 if ref else 0
                row += f"  {dif:>+13.2f}%"
            linhas.append(row)
        tabela = "\n".join(linhas)
        self.after(0, lambda: self._set_texto(self.text_tabela_amostras, tabela))
        self._log("[Parte 2.1]\n" + tabela)

        # Gráfico
        fig, axes = plt.subplots(1, 3, figsize=(12, 4))
        fig.suptitle("Distribuição — Amostras 1%, 5%, 10%", color=COR_TEXTO, fontsize=12)
        cores = [COR_DESTAQUE, COR_VERDE, "#e67e22"]
        for i, (prop, n_a, p) in enumerate(resultados):
            a = np.random.choice(pop, size=n_a, replace=False)
            axes[i].hist(a, bins=30, density=True, color=cores[i], alpha=0.65, edgecolor="none")
            kde = stats.gaussian_kde(a)
            xr  = np.linspace(a.min(), a.max(), 200)
            axes[i].plot(xr, kde(xr), color=COR_VERMELHO, lw=2)
            axes[i].axvline(p["media"], color="white", lw=1.5, ls="--",
                            label=f"Média={p['media']:.2f}")
            axes[i].set_title(f"{int(prop*100)}%  (n={n_a:,})")
            axes[i].legend(fontsize=8)
        fig.tight_layout()
        cam = os.path.join(PASTA_SAIDA, "amostras_variadas.png")
        fig.savefig(cam, bbox_inches="tight")
        self.after(0, lambda: self._embed_fig(fig, self.frame_grafico_amostras))
        self._status("Parte 2.1 concluída ✔")

    # ── Parte 2.2 ───────────────────────────────────────────
    def _rodar_parte22(self):
        if not self._checar_dados(): return
        if self.params_pop is None:
            messagebox.showinfo("Atenção", "Execute a Parte 1 primeiro.")
            return
        try:
            nivel = float(self.nivel_var.get()) / 100
            if not (0 < nivel < 1): raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Nível de confiança inválido (use 80–99).")
            return
        threading.Thread(target=self._exec_parte22, args=(nivel,), daemon=True).start()

    def _exec_parte22(self, nivel):
        self._status("Gerando 100 amostras…")
        pop   = self.populacao
        pp    = self.params_pop
        N     = len(pop)
        n_a   = max(30, int(N * 0.01))
        K     = 100

        medias = variancias = desvios = somas = np.zeros(K)
        medias    = np.zeros(K)
        variancias = np.zeros(K)
        desvios   = np.zeros(K)
        somas     = np.zeros(K)

        for i in range(K):
            a = np.random.choice(pop, size=n_a, replace=False)
            medias[i]     = np.mean(a)
            variancias[i] = np.var(a, ddof=1)
            desvios[i]    = np.std(a, ddof=1)
            somas[i]      = np.sum(a)

        E_med  = np.mean(medias);     Var_med = np.var(medias, ddof=1)
        E_var  = np.mean(variancias)
        E_soma = np.mean(somas);      Var_soma = np.var(somas, ddof=1)

        vt  = pp["variancia"] / n_a   # variância teórica das médias
        vst = n_a * pp["variancia"]   # variância teórica das somas

        # IC
        z     = stats.norm.ppf(1 - (1-nivel)/2)
        marg  = z * (pp["dp"] / np.sqrt(n_a))
        ic_i  = medias - marg
        ic_s  = medias + marg
        mu    = pp["media"]
        dentro = int(np.sum((ic_i <= mu) & (mu <= ic_s)))
        pct   = dentro / K * 100

        assim = stats.skew(medias)

        linhas = [
            f"  Tamanho de cada amostra : {n_a:,}   |   Nº de amostras: {K}",
            "",
            "  ── Médias Amostrais ──────────────────────────────",
            f"  E(X̄)            = {E_med:.4f}   (μ pop. = {mu:.4f})   Δ = {abs(E_med-mu)/mu*100:.4f}%",
            f"  Var(X̄) observada = {Var_med:.6f}   (teórica σ²/n = {vt:.6f})",
            f"  → Estimador {'NÃO ENVIESADO ✔' if abs(E_med-mu)/mu*100 < 1 else 'com pequeno viés'}",
            "",
            "  ── Variâncias Amostrais ───────────────────────────",
            f"  E(S²)        = {E_var:.4f}   (σ² pop. = {pp['variancia']:.4f})   Δ = {abs(E_var-pp['variancia'])/pp['variancia']*100:.4f}%",
            f"  → Estimador NÃO ENVIESADO (S² com ddof=1) ✔",
            "",
            "  ── Soma das Amostras ──────────────────────────────",
            f"  E(ΣX)  = {E_soma:.4f}   (teórico n·μ = {n_a*mu:.4f})",
            f"  Var(ΣX) = {Var_soma:.4f}   (teórico n·σ² = {vst:.4f})",
            f"  DP(ΣX)  = {np.sqrt(Var_soma):.4f}   (teórico √(n·σ²) = {np.sqrt(vst):.4f})",
            "",
            f"  ── Intervalo de Confiança ({int(nivel*100)}%) ─────────────────",
            f"  Z crítico = {z:.4f}   Margem = {marg:.4f}",
            f"  Amostras com μ dentro do IC: {dentro}/{K} = {pct:.1f}%",
            f"  (Esperado ≈ {int(nivel*100)}%)   {'✔ Coerente com a teoria' if abs(pct-nivel*100)<=5 else '— pequeno desvio amostral'}",
            "",
            "  ── Teorema Central do Limite ──────────────────────",
            f"  Assimetria das médias: {assim:+.4f}",
            f"  → {'Distribuição das médias APROXIMADAMENTE NORMAL ✔' if abs(assim)<0.5 else 'Mais amostras aproximariam mais da normal'}",
        ]
        texto = "\n".join(linhas)
        self.after(0, lambda: self._set_texto(self.text_res100, texto))
        self._log("[Parte 2.2]\n" + texto)

        # Gráficos: distribuições + IC
        fig = plt.figure(figsize=(12, 8))
        gs  = fig.add_gridspec(2, 3, hspace=0.45, wspace=0.35)

        def hist_n(ax, dados, titulo, cor, label):
            ax.hist(dados, bins=20, density=True, color=cor, alpha=0.65, edgecolor="none")
            kde = stats.gaussian_kde(dados)
            xr  = np.linspace(dados.min(), dados.max(), 200)
            ax.plot(xr, kde(xr), "w-", lw=1.5, label="KDE")
            ax.plot(xr, stats.norm.pdf(xr, np.mean(dados), np.std(dados)),
                    color=COR_VERMELHO, lw=1.5, ls="--", label="Normal teórica")
            ax.axvline(np.mean(dados), color="yellow", lw=1.2, ls="--",
                       label=f"{label}={np.mean(dados):.2f}")
            ax.set_title(titulo); ax.legend(fontsize=7)

        hist_n(fig.add_subplot(gs[0,0]), medias,     "Médias (TCL)",     COR_DESTAQUE, "E(X̄)")
        hist_n(fig.add_subplot(gs[0,1]), variancias, "Variâncias",       COR_VERDE,    "E(S²)")
        hist_n(fig.add_subplot(gs[0,2]), somas,      "Somas",            "#e67e22",    "E(ΣX)")

        # IC plot
        ax_ic = fig.add_subplot(gs[1,:])
        n_show = 50
        for j in range(n_show):
            cor = COR_VERDE if ic_i[j] <= mu <= ic_s[j] else COR_VERMELHO
            ax_ic.plot([j+1, j+1], [ic_i[j], ic_s[j]], color=cor, lw=1.5, alpha=0.8)
            ax_ic.plot(j+1, medias[j], "o", color=cor, markersize=3)
        ax_ic.axhline(mu, color="white", lw=2, ls="--", label=f"μ pop. = {mu:.2f}")
        ax_ic.set_title(f"ICs {int(nivel*100)}% — primeiras {n_show} amostras  "
                        f"(Verde=contém μ | Vermelho=não contém)")
        ax_ic.set_xlabel("Amostra"); ax_ic.set_ylabel("Valor")
        ax_ic.legend(fontsize=9)

        fig.suptitle("Parte 2.2 — 100 Amostras de Tamanho Fixo", color=COR_TEXTO, fontsize=12)
        cam = os.path.join(PASTA_SAIDA, "parte22_completo.png")
        fig.savefig(cam, bbox_inches="tight")
        self.after(0, lambda: self._embed_fig(fig, self.frame_grafico_100))
        self._status("Parte 2.2 concluída ✔  |  Resultados salvos em 'resultados_estatistica/'")


# ═══════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = App()
    app.mainloop()