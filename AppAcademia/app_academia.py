"""
Academia Sport Fitness - Sistema de cadastro de clientes
Projeto de ADS | Python + tkinter (interface) + SQLite (banco de dados)

Login inicial do proprietário (administrador):
    usuário: admin
    senha:   admin123

Permissões:
    - Proprietário (admin): adiciona/remove clientes E funcionários.
    - Funcionário: apenas cadastra, edita e consulta clientes (não remove).
"""

import hashlib
import os
import re
import sqlite3
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

NOME_ACADEMIA = "Academia Sport Fitness"
ARQUIVO_BD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "academia_app.db")
PLANOS = ["Mensal", "Trimestral", "Semestral", "Anual"]

COR_PRINCIPAL = "#1f6feb"
COR_FUNDO = "#f4f6f8"


# ---------------------------------------------------------------------------
# BANCO DE DADOS
# ---------------------------------------------------------------------------
def gerar_hash(senha: str) -> str:
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


def conectar():
    con = sqlite3.connect(ARQUIVO_BD)
    con.row_factory = sqlite3.Row
    return con


def criar_banco():
    con = conectar()
    with con:
        con.execute(
            """CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                login TEXT NOT NULL UNIQUE,
                senha TEXT NOT NULL,
                perfil TEXT NOT NULL CHECK (perfil IN ('admin', 'funcionario'))
            )"""
        )
        con.execute(
            """CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf TEXT NOT NULL UNIQUE,
                telefone TEXT,
                email TEXT,
                plano TEXT NOT NULL,
                data_cadastro TEXT NOT NULL
            )"""
        )
        existe = con.execute("SELECT 1 FROM usuarios WHERE perfil = 'admin'").fetchone()
        if not existe:
            con.execute(
                "INSERT INTO usuarios (nome, login, senha, perfil) VALUES (?, ?, ?, 'admin')",
                ("Proprietário", "admin", gerar_hash("admin123")),
            )
    con.close()


def executar(sql, params=()):
    """Executa INSERT/UPDATE/DELETE e fecha a conexão."""
    con = conectar()
    try:
        with con:
            con.execute(sql, params)
    finally:
        con.close()


def consultar(sql, params=()):
    """Executa SELECT e devolve todas as linhas."""
    con = conectar()
    try:
        return con.execute(sql, params).fetchall()
    finally:
        con.close()


def autenticar(login, senha):
    linhas = consultar("SELECT * FROM usuarios WHERE login = ? AND senha = ?",
                       (login, gerar_hash(senha)))
    return linhas[0] if linhas else None


# ---------------------------------------------------------------------------
# JANELA DE LOGIN
# ---------------------------------------------------------------------------
class TelaLogin(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{NOME_ACADEMIA} - Login")
        self.geometry("360x300")
        self.resizable(False, False)
        self.configure(bg=COR_FUNDO)

        tk.Label(self, text=NOME_ACADEMIA, font=("Segoe UI", 15, "bold"),
                 fg=COR_PRINCIPAL, bg=COR_FUNDO).pack(pady=(30, 5))
        tk.Label(self, text="Acesso ao sistema", bg=COR_FUNDO).pack(pady=(0, 20))

        quadro = tk.Frame(self, bg=COR_FUNDO)
        quadro.pack()
        tk.Label(quadro, text="Usuário:", bg=COR_FUNDO).grid(row=0, column=0, sticky="e", pady=5)
        tk.Label(quadro, text="Senha:", bg=COR_FUNDO).grid(row=1, column=0, sticky="e", pady=5)
        self.ent_login = ttk.Entry(quadro, width=25)
        self.ent_senha = ttk.Entry(quadro, width=25, show="*")
        self.ent_login.grid(row=0, column=1, padx=8)
        self.ent_senha.grid(row=1, column=1, padx=8)
        self.ent_login.focus()

        ttk.Button(self, text="Entrar", command=self.entrar).pack(pady=25)
        self.bind("<Return>", lambda e: self.entrar())

    def entrar(self):
        usuario = autenticar(self.ent_login.get().strip(), self.ent_senha.get())
        if not usuario:
            messagebox.showerror("Erro", "Usuário ou senha inválidos.")
            self.ent_senha.delete(0, tk.END)
            return
        self.destroy()
        TelaPrincipal(dict(usuario)).mainloop()


# ---------------------------------------------------------------------------
# JANELA PRINCIPAL
# ---------------------------------------------------------------------------
class TelaPrincipal(tk.Tk):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.eh_admin = usuario["perfil"] == "admin"
        papel = "Administrador" if self.eh_admin else "Funcionário"

        self.title(f"{NOME_ACADEMIA} - {papel}")
        self.geometry("820x520")
        self.minsize(700, 420)
        self.configure(bg=COR_FUNDO)

        topo = tk.Frame(self, bg=COR_PRINCIPAL)
        topo.pack(fill="x")
        tk.Label(topo, text=NOME_ACADEMIA, font=("Segoe UI", 14, "bold"),
                 fg="white", bg=COR_PRINCIPAL).pack(side="left", padx=15, pady=10)
        ttk.Button(topo, text="Sair", command=self.sair).pack(side="right", padx=15)
        tk.Label(topo, text=f"{usuario['nome']} ({papel})", fg="white",
                 bg=COR_PRINCIPAL).pack(side="right")

        # Administrador: abas Clientes + Funcionários. Funcionário: só Clientes.
        abas = ttk.Notebook(self)
        abas.pack(fill="both", expand=True, padx=10, pady=10)

        abas.add(AbaClientes(abas, self.eh_admin), text="  Clientes  ")
        if self.eh_admin:
            abas.add(AbaFuncionarios(abas), text="  Funcionários  ")

    def sair(self):
        self.destroy()
        TelaLogin().mainloop()


# ---------------------------------------------------------------------------
# ABA CLIENTES
# ---------------------------------------------------------------------------
class AbaClientes(tk.Frame):
    def __init__(self, master, eh_admin):
        super().__init__(master, bg=COR_FUNDO)
        self.eh_admin = eh_admin

        barra = tk.Frame(self, bg=COR_FUNDO)
        barra.pack(fill="x", pady=8, padx=8)
        tk.Label(barra, text="Buscar:", bg=COR_FUNDO).pack(side="left")
        self.var_busca = tk.StringVar()
        self.var_busca.trace_add("write", lambda *a: self.carregar())
        ttk.Entry(barra, textvariable=self.var_busca, width=28).pack(side="left", padx=6)

        ttk.Button(barra, text="Adicionar", command=self.adicionar).pack(side="left", padx=4)
        ttk.Button(barra, text="Editar", command=self.editar).pack(side="left", padx=4)
        if self.eh_admin:  # só o proprietário remove clientes
            ttk.Button(barra, text="Remover", command=self.remover).pack(side="left", padx=4)

        self.lbl_total = tk.Label(barra, bg=COR_FUNDO, fg="#555")
        self.lbl_total.pack(side="right")

        colunas = ("id", "nome", "cpf", "telefone", "plano", "data_cadastro")
        self.tabela = ttk.Treeview(self, columns=colunas, show="headings", selectmode="browse")
        titulos = {"id": "ID", "nome": "Nome", "cpf": "CPF", "telefone": "Telefone",
                   "plano": "Plano", "data_cadastro": "Cadastro"}
        larguras = {"id": 40, "nome": 220, "cpf": 110, "telefone": 110, "plano": 90, "data_cadastro": 90}
        for c in colunas:
            self.tabela.heading(c, text=titulos[c])
            self.tabela.column(c, width=larguras[c], anchor="w")
        rolagem = ttk.Scrollbar(self, orient="vertical", command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=rolagem.set)
        self.tabela.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=(0, 8))
        rolagem.pack(side="left", fill="y", pady=(0, 8), padx=(0, 8))
        self.carregar()

    def carregar(self):
        self.tabela.delete(*self.tabela.get_children())
        busca = f"%{self.var_busca.get().strip()}%"
        linhas = consultar(
            """SELECT * FROM clientes
               WHERE nome LIKE ? OR cpf LIKE ? OR telefone LIKE ?
               ORDER BY nome""", (busca, busca, busca))
        for l in linhas:
            self.tabela.insert("", "end", iid=str(l["id"]), values=(
                l["id"], l["nome"], l["cpf"], l["telefone"], l["plano"], l["data_cadastro"]))
        self.lbl_total.config(text=f"{len(linhas)} cliente(s)")

    def _selecionado(self):
        sel = self.tabela.selection()
        if not sel:
            messagebox.showinfo("Atenção", "Selecione um cliente na lista.")
            return None
        return int(sel[0])

    def adicionar(self):
        FormCliente(self, None, self.carregar)

    def editar(self):
        id_cli = self._selecionado()
        if id_cli:
            FormCliente(self, id_cli, self.carregar)

    def remover(self):
        id_cli = self._selecionado()
        if not id_cli:
            return
        nome = self.tabela.item(str(id_cli), "values")[1]
        if messagebox.askyesno("Confirmar", f"Remover o cliente '{nome}'?"):
            executar("DELETE FROM clientes WHERE id = ?", (id_cli,))
            self.carregar()


class FormCliente(tk.Toplevel):
    """Janela de cadastro/edição de cliente."""

    def __init__(self, pai, id_cliente, ao_salvar):
        super().__init__(pai)
        self.id_cliente = id_cliente
        self.ao_salvar = ao_salvar
        self.title("Editar cliente" if id_cliente else "Novo cliente")
        self.resizable(False, False)
        self.configure(bg=COR_FUNDO, padx=20, pady=15)
        self.transient(pai)
        self.grab_set()

        self.campos = {}
        rotulos = [("nome", "Nome completo*"), ("cpf", "CPF* (11 números)"),
                   ("telefone", "Telefone"), ("email", "E-mail")]
        for i, (chave, rotulo) in enumerate(rotulos):
            tk.Label(self, text=rotulo, bg=COR_FUNDO).grid(row=i, column=0, sticky="e", pady=5)
            ent = ttk.Entry(self, width=32)
            ent.grid(row=i, column=1, padx=8)
            self.campos[chave] = ent

        tk.Label(self, text="Plano*", bg=COR_FUNDO).grid(row=4, column=0, sticky="e", pady=5)
        self.cmb_plano = ttk.Combobox(self, values=PLANOS, state="readonly", width=29)
        self.cmb_plano.current(0)
        self.cmb_plano.grid(row=4, column=1, padx=8)

        ttk.Button(self, text="Salvar", command=self.salvar).grid(row=5, column=0, columnspan=2, pady=15)

        if id_cliente:
            c = consultar("SELECT * FROM clientes WHERE id = ?", (id_cliente,))[0]
            for chave, ent in self.campos.items():
                ent.insert(0, c[chave] or "")
            self.cmb_plano.set(c["plano"])
        self.campos["nome"].focus()

    def salvar(self):
        nome = self.campos["nome"].get().strip()
        cpf = re.sub(r"\D", "", self.campos["cpf"].get())
        telefone = self.campos["telefone"].get().strip()
        email = self.campos["email"].get().strip()
        plano = self.cmb_plano.get()

        if not nome:
            return messagebox.showwarning("Atenção", "Informe o nome.", parent=self)
        if len(cpf) != 11:
            return messagebox.showwarning("Atenção", "O CPF deve ter 11 números.", parent=self)
        if email and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            return messagebox.showwarning("Atenção", "E-mail inválido.", parent=self)

        try:
            if self.id_cliente:
                executar("UPDATE clientes SET nome=?, cpf=?, telefone=?, email=?, plano=? WHERE id=?",
                         (nome, cpf, telefone, email, plano, self.id_cliente))
            else:
                executar("INSERT INTO clientes (nome, cpf, telefone, email, plano, data_cadastro) "
                         "VALUES (?, ?, ?, ?, ?, ?)",
                         (nome, cpf, telefone, email, plano, datetime.now().strftime("%d/%m/%Y")))
        except sqlite3.IntegrityError:
            return messagebox.showerror("Erro", "Já existe um cliente com esse CPF.", parent=self)

        self.ao_salvar()
        self.destroy()


# ---------------------------------------------------------------------------
# ABA FUNCIONÁRIOS (somente administrador)
# ---------------------------------------------------------------------------
class AbaFuncionarios(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=COR_FUNDO)

        barra = tk.Frame(self, bg=COR_FUNDO)
        barra.pack(fill="x", pady=8, padx=8)
        ttk.Button(barra, text="Adicionar", command=self.adicionar).pack(side="left", padx=4)
        ttk.Button(barra, text="Remover", command=self.remover).pack(side="left", padx=4)

        self.tabela = ttk.Treeview(self, columns=("id", "nome", "login"), show="headings",
                                   selectmode="browse")
        for c, t, w in [("id", "ID", 40), ("nome", "Nome", 260), ("login", "Usuário (login)", 160)]:
            self.tabela.heading(c, text=t)
            self.tabela.column(c, width=w, anchor="w")
        self.tabela.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.carregar()

    def carregar(self):
        self.tabela.delete(*self.tabela.get_children())
        for f in consultar("SELECT id, nome, login FROM usuarios "
                           "WHERE perfil='funcionario' ORDER BY nome"):
            self.tabela.insert("", "end", iid=str(f["id"]), values=(f["id"], f["nome"], f["login"]))

    def adicionar(self):
        FormFuncionario(self, self.carregar)

    def remover(self):
        sel = self.tabela.selection()
        if not sel:
            return messagebox.showinfo("Atenção", "Selecione um funcionário na lista.")
        nome = self.tabela.item(sel[0], "values")[1]
        if messagebox.askyesno("Confirmar", f"Remover o funcionário '{nome}'?"):
            executar("DELETE FROM usuarios WHERE id = ? AND perfil = 'funcionario'", (int(sel[0]),))
            self.carregar()


class FormFuncionario(tk.Toplevel):
    def __init__(self, pai, ao_salvar):
        super().__init__(pai)
        self.ao_salvar = ao_salvar
        self.title("Novo funcionário")
        self.resizable(False, False)
        self.configure(bg=COR_FUNDO, padx=20, pady=15)
        self.transient(pai)
        self.grab_set()

        self.campos = {}
        itens = [("nome", "Nome completo*", False), ("login", "Usuário (login)*", False),
                 ("senha", "Senha* (mín. 4)", True)]
        for i, (chave, rotulo, oculto) in enumerate(itens):
            tk.Label(self, text=rotulo, bg=COR_FUNDO).grid(row=i, column=0, sticky="e", pady=5)
            ent = ttk.Entry(self, width=30, show="*" if oculto else "")
            ent.grid(row=i, column=1, padx=8)
            self.campos[chave] = ent
        ttk.Button(self, text="Salvar", command=self.salvar).grid(row=3, column=0, columnspan=2, pady=15)
        self.campos["nome"].focus()

    def salvar(self):
        nome = self.campos["nome"].get().strip()
        login = self.campos["login"].get().strip()
        senha = self.campos["senha"].get()
        if not nome or not login:
            return messagebox.showwarning("Atenção", "Preencha nome e usuário.", parent=self)
        if len(senha) < 4:
            return messagebox.showwarning("Atenção", "A senha deve ter ao menos 4 caracteres.", parent=self)
        try:
            executar("INSERT INTO usuarios (nome, login, senha, perfil) VALUES (?, ?, ?, 'funcionario')",
                     (nome, login, gerar_hash(senha)))
        except sqlite3.IntegrityError:
            return messagebox.showerror("Erro", "Esse usuário (login) já existe.", parent=self)
        self.ao_salvar()
        self.destroy()


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    criar_banco()
    TelaLogin().mainloop()
