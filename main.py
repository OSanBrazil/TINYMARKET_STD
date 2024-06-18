# Importa bibliotecas
import sys
import tkinter.font
from tkinter import *
from tkinter import ttk
import sqlite3
from pathlib import Path
from datetime import datetime
from tkinter import messagebox
import re
import locale
import os

# Determina o país/região para usar a função locale.currency
locale.setlocale(locale.LC_ALL, "pt_BR")

# Ativa ou desativa modo debug
debug_mode = False


# Funções
# ---------------------------------------------------------------------------------------------------------------------
# Associa todos os botões à tecla <ENTER>
def associa_botoes(widget):
    if isinstance(widget, Button):
        widget.bind('<Return>', lambda event, b=widget: on_enter_key_pressed(b))
    for child in widget.winfo_children():
        associa_botoes(child)


def seta_aparencia_de_widgets():
    seta_aparencias(janela)


def seta_estado_inicial_do_app():
    tabs[2].destroy()
    venda()

    if Path("historico.txt").exists():
        with open("historico.txt", "r") as f:
            historico_de_caixa = f.read()
    else:
        historico_de_caixa = ""
    text_historico_de_caixa.config(state="normal")
    text_historico_de_caixa.insert("1.0", historico_de_caixa)
    text_historico_de_caixa.config(state="disabled")


def seta_aparencias(widget):
    msg("Muda a aparência dos widgets")
    frames_visible = checkbox_frames_visible_ischecked.get()
    if isinstance(widget, Frame):
        if frames_visible:
            widget.config(borderwidth=1, relief="raised")
        else:
            widget.config(borderwidth=0, relief="flat")
    big_buttons = checkbox_bigbuttons_ischecked.get()
    if isinstance(widget, Button):
        if big_buttons:
            widget.config(height=alt_botao_img * 2)
        else:
            widget.config(height=alt_botao_img)
    if isinstance(widget, Frame):
        widget.config(padx=padx_padrao * 2, pady=pady_padrao)
    for child in widget.winfo_children():
        seta_aparencias(child)


def debug_mode_changed():
    global debug_mode
    debug_mode = checkbox_debugmode_ischecked.get()
    if debug_mode:
        msg("MODO DEBUG ATIVADO!")
    else:
        print(">" + datetime.now().strftime("%H:%M:%S:%f") + " MODO DEBUG DESATIVADO.")


def msg(mensagem):
    if debug_mode:
        print(">" + datetime.now().strftime("%H:%M:%S:%f") + " " + mensagem)


def msg_erro(id_erro):
    if id_erro == 0:
        messagebox.showwarning("", "Não são permitidos campos vazios!")
    if id_erro == 1:
        messagebox.showwarning("", "O CPF deve ter 11 dígitos!")
    if id_erro == 3:
        messagebox.showwarning("", "CPF digitado é inválido!")
    if id_erro == 4:
        messagebox.showwarning("", "Número do TELEFONE incompleto!")
    if id_erro == 5:
        messagebox.showwarning("", "Código de barras ou produto não consta do cadastro de Produtos!")
    if id_erro == 6:
        messagebox.showwarning("", "Formato de e-mail inválido!")
    if id_erro == 7:
        messagebox.showwarning("", "O CPF informado jé existe no cadastro de Clientes!")
    if id_erro == 8:
        messagebox.showwarning("", "Já existe um produto com o mesmo cóigo de barras!")


# Tecla <ENTER> pressionada

def on_enter_key_pressed(b):
    b.invoke()


def venda():
    MainTabControl.select(0)

    campos_de_entrada_tab0[0].focus_set()
    # Preenche os campos informativos com os dados do cliente selecionado


def produtos():
    MainTabControl.select(1)
    campos_de_entrada_tab1[0].focus_set()


def estoque():
    MainTabControl.select(2)


def clientes():
    MainTabControl.select(2)
    campos_de_entrada_tab3[0].focus_set()


def opcoes():
    MainTabControl.select(3)


def informa_comprador():
    msg("Preenche os dados do cliente no terminal de caixa")
    linha = grid_Clientes.focus()
    if not linha:
        messagebox.showwarning("", "Selecione antes um cliente na aba CLIENTES!")
        return
    msg(f"Linha selecionada: {linha}")
    valores = grid_Clientes.item(linha)["values"]
    msg(f"Conteúdo da linha: {valores}")
    valor = valores[1]
    msg(f"Conteúdo do campo Nome {valor}")
    rotulos_tab0[7].config(text=valor)
    valor = valores[3]
    msg(f"Conteúdo do campo CPF {valor}")
    rotulos_tab0[9].config(text=valor)


def inicia_venda():
    MainTabControl.select(0)
    CaixaTabControl.select(0)
    if not messagebox.askyesno("", "Iniciar NOVA VENDA?"):
        return
    msg("Iniciando nova venda")
    global dinheiro
    global troco
    global total_da_compra
    dinheiro = 0
    troco = 0
    campos_de_entrada_tab0[0].focus_set()
    grid_fita_de_caixa.delete(*grid_fita_de_caixa.get_children())
    grid_fita_de_caixa.insert("", END, values=[""])
    grid_fita_de_caixa.insert("", END,
                              values=["                         MERCADINHO TINYMARKET                          "])
    grid_fita_de_caixa.insert("", END, values=[""])
    grid_fita_de_caixa.insert("", END,
                              values=["CÓD. PRODUTO                          FABR.      PREÇO   QTE  SUBTOTAL"])
    grid_fita_de_caixa.insert("", END, values=[""])
    for i in range(3):
        campos_de_entrada_tab0[i].config(state="normal")
    btn_finaliza_venda_produto.config(state="normal")
    btn_exclui_venda_produto.config(state="normal")
    btn_registra_venda_produto.config(state="normal")
    btn_comprador.config(state="normal")
    rotulo_display_tab0[0].config(text="CAIXA ABERTO")
    rotulo_display_tab0[1].config(text="")
    rotulo_display_tab0[2].config(text="")
    for n in range(1 - 9, 2):
        rotulos_tab0[n].config(text="")
    return


def entrada_produto_tabvenda_changed(e):
    msg("Entrada produtos no tab venda mudou")
    produto = filtra_produto_venda()
    msg(f"Resultado do filtro: {produto}")
    if not produto:
        for n in range(1, 6, 2):
            rotulos_tab0[n].config(text="")
        return
    produto = produto[0]
    rotulos_tab0[1].config(text=f"{produto[1]}")
    rotulos_tab0[3].config(text=f"{produto[3]}")
    rotulos_tab0[5].config(text=f"{produto[4]}")


def entrada_produto_confirma(e):
    msg("Produto da pesquisa aceito")
    campos_de_entrada_tab0[0].insert(0, rotulos_tab0[3].cget("text"))
    campos_de_entrada_tab0[1].delete(0, END)
    campos_de_entrada_tab0[1].insert(0, rotulos_tab0[1].cget("text"))
    campos_de_entrada_tab0[2].delete(0, END)
    campos_de_entrada_tab0[2].insert(0, "1")
    campos_de_entrada_tab0[2].focus_set()
    InfoTabControl.select(0)
    CaixaTabControl.select(0)
    calcula_subtotal_venda(rotulos_tab0[5].cget("text"))


def entrada_qtde_confirma(e):
    msg("Quantidade produto aceita")
    btn_registra_venda_produto.focus_set()


def formata_qtde_tab_venda(e):
    msg("Formatando quantidade tab venda")
    qtde = campos_de_entrada_tab0[2].get()
    campos_de_entrada_tab0[2].delete(0, END)
    qtde = re.sub("[^0-9]", "", qtde)
    qtde = qtde[:3]
    campos_de_entrada_tab0[2].insert(0, qtde)
    calcula_subtotal_venda(rotulos_tab0[5].cget("text"))


def formata_qtde_final_tab_venda(e):
    msg("Formatando quantidade tab venda na sáida do campo")
    qtde = campos_de_entrada_tab0[2].get()
    if qtde == "" or int(qtde) < 1:
        qtde = "1"
        campos_de_entrada_tab0[2].delete(0, END)
        campos_de_entrada_tab0[2].insert(0, qtde)
    calcula_subtotal_venda(rotulos_tab0[5].cget("text"))


def formata_cod_barras_tabvenda(e):
    msg("Formatando código de barras no tab venda")
    cod_barras = campos_de_entrada_tab0[0].get()
    campos_de_entrada_tab0[0].delete(0, END)
    cod_barras = re.sub("[^0-9]", "", cod_barras)
    cod_barras = cod_barras[:13]
    campos_de_entrada_tab0[0].insert(0, cod_barras)
    produto = filtra_produto_venda()
    msg(f"Resultado do filtro: {produto}")
    if not produto:
        return
    produto = produto[0]
    rotulos_tab0[1].config(text=f"{produto[1]}")
    rotulos_tab0[3].config(text=f"{produto[3]}")
    rotulos_tab0[5].config(text=f"{produto[4]}")
    if len(cod_barras) >= 13:
        entrada_produto_confirma(0)


def filtra_produto_venda():
    cod_barras = campos_de_entrada_tab0[0].get()
    if cod_barras == "":
        cod_barras = "*"
    produto = campos_de_entrada_tab0[1].get()
    if produto == "":
        produto = "*"
    dados = curs.execute(f"SELECT * FROM produtos WHERE produto LIKE '%{produto}%' OR "
                         f"cod_barras='{cod_barras}'").fetchall()
    msg("Filtrando Produtos...")
    return dados


def calcula_subtotal_venda(preco):
    qtde = campos_de_entrada_tab0[2].get()
    if qtde == "":
        qtde = "0"
    qtde = int(qtde)
    preco = (re.sub("[^0-9]", "", preco))
    if not preco:
        return
    preco = int(preco)
    subtotal = qtde * preco
    subtotalf = (subtotal / 100)
    subtotalf_str = locale.currency(subtotalf, grouping=True).replace("R$ ", "")
    qtde_str = str(qtde).rjust(3, "0")
    rotulo_display_tab0[0].config(text=f"SUBTOTAL: R$ {subtotalf_str}")
    return qtde_str, subtotalf_str


def registra_venda_produto():
    msg("Registra venda do produto")
    dados = filtra_produto_venda()
    if not dados:
        msg_erro(5)
        return
    n = -1
    texto = ""
    preco = ""
    for item in dados[0]:
        item = str(item)
        n += 1
        if n == 0:
            item = item.rjust(4, "0")[:4]
        if n == 3 or n > 4: continue
        if n == 1:
            item = item.ljust(32, " ")[:32]
        if n == 2:
            item = item.ljust(7, " ")[:7]
        if n == 4:
            preco = item

        if n > 3:
            item = item.rjust(8, " ")
        texto += item + " "
    qtde_str, subtotalf_str = calcula_subtotal_venda(preco)
    texto += f"x {qtde_str} {subtotalf_str.rjust(9, " ")}"
    msg("Inserindo linha no grid Caixa:")
    msg(texto)
    grid_fita_de_caixa.insert("", "end", values=[texto])
    grid_fita_de_caixa.yview_moveto(1)
    calcula_total()
    for n in range(2):
        campos_de_entrada_tab0[n].delete(0, END)
    campos_de_entrada_tab0[0].focus_set()


def exclui_venda_produto():
    msg("Excluindo produto da venda")
    linha = grid_fita_de_caixa.focus()
    if not linha:
        messagebox.showwarning("", "Nenhum produto selecionado.")
        return
    msg(f"Linha selecionada: {linha}")
    if not messagebox.askyesno("Atenção!", "Excluir registro?"):
        return
    grid_fita_de_caixa.delete(linha)
    campos_de_entrada_tab0[0].focus_set()


def calcula_total():
    msg("Calculando Total")
    global total_da_compra
    total = 0
    totalf_str = ""
    for line in grid_fita_de_caixa.get_children():
        for value in grid_fita_de_caixa.item(line)["values"]:
            msg(f"value: {value}")
            if not value:
                continue
            subtotal_item = value[len(value) - 9:]
            msg(f"subtotal_item: {subtotal_item}")
            if not subtotal_item[6] == ",":
                continue
            subtotal_item = subtotal_item.replace(",", "").replace(".", "")
            msg(subtotal_item)
            total += int(subtotal_item)
            totalf = total / 100
            totalf_str = locale.currency(totalf, grouping=True)  # .replace("R$ ", "")
            rotulo_display_tab0[1].config(text=f"TOTAL: {totalf_str}")
            if total == 0:
                rotulo_display_tab0[1].config(text="")
            msg(totalf_str)
            total_da_compra = total
    return total, totalf_str


def finaliza_venda():
    global dinheiro
    global troco
    global total_da_compra
    msg("Finalizando venda...")
    for i in range(3):
        campos_de_entrada_tab0[i].config(state="disabled")
    btn_finaliza_venda_produto.config(state="disabled")
    btn_exclui_venda_produto.config(state="disabled")
    btn_registra_venda_produto.config(state="disabled")
    btn_comprador.config(state="disabled")
    total, totalf_str = calcula_total()
    dinheiro_str = formata_reais(dinheiro)
    troco_str = formata_reais(troco)
    rotulo_display_tab0[0].config(text="VENDA FINALIZADA")
    rotulo_display_tab0[2].config(text=f"TROCO: {troco_str}")

    if total == 0:
        rotulo_display_tab0[0].config(text="CAIXA FECHADO")
        rotulo_display_tab0[1].config(text="")
        rotulo_display_tab0[2].config(text="")
        for n in range(1 - 9, 2):
            rotulos_tab0[n].config(text="")
        return
    atualiza_qtde_estoque()
    grid_fita_de_caixa.insert("", "end", values=[""])
    grid_fita_de_caixa.insert("", "end", values=[f"TOTAL: {totalf_str}"])
    grid_fita_de_caixa.insert("", "end", values=[f"DINHEIRO: {dinheiro_str}"])
    grid_fita_de_caixa.insert("", "end", values=[f"TROCO: {troco_str}"])
    grid_fita_de_caixa.insert("", "end", values=[""])
    if nota_com_cpf:
        nome = rotulos_tab0[7].cget("text")
        cpf = rotulos_tab0[9].cget("text")
        grid_fita_de_caixa.insert("", "end", values=[f"CLIENTE: {nome[:30]}  CPF: {cpf}"])
    grid_fita_de_caixa.insert("", "end", values=["DATA/HORA DA COMPRA: "
                                                 + datetime.now().strftime("%x às %X")])
    grid_fita_de_caixa.yview_moveto(1)
    value = []
    # Escreve fita de caixa no componente Text de histórico e armazena em string para impressão
    str_nota_caixa = ""
    for line in grid_fita_de_caixa.get_children():
        for value in grid_fita_de_caixa.item(line)["values"]:
            if not value:
                continue
        value = value.rjust(75, " ") + "\n"
        str_nota_caixa += value
    text_historico_de_caixa.config(state="normal")
    text_historico_de_caixa.insert(END, str_nota_caixa)
    text_historico_de_caixa.config(state="disabled")
    text_historico_de_caixa.see("end")
    # Imprime fita de caixa
    if checkbox_printer_enabled_ischecked.get():
        msg("Imprimindo Fita de Caixa")
        with open("impressao.txt", "w") as f:
            f.write(str_nota_caixa)
        os.startfile("impressao.txt", "print")

    # Adiciona fita gerada ao arquivo "historico.txt" (append)
    msg("Salvando fita de histórico no hdd (appending)")
    with open("historico.txt", "a") as f:
        f.write(str_nota_caixa)


# Prepara para finalizar a venda
def prepara_finalizar_venda():
    global nota_com_cpf
    total, totalf = calcula_total()
    if total == 0:
        finaliza_venda()
        return
    if rotulos_tab0[9].cget("text") == "":
        nota_com_cpf = False
        entrada_dinheiro()
        return
    if not messagebox.askyesno("Atenção!", "Incluir CPF do cliente na nota?"):
        nota_com_cpf = False
    else:
        nota_com_cpf = True
    entrada_dinheiro()


# Abre o formulário de diálogo da entrada de dinheiro
def entrada_dinheiro():
    def formata_preco_entrada_dinheiro(e):
        msg("Formatando preço no tab dinheiro")
        preco = campo_valor_dinheiro.get()
        campo_valor_dinheiro.delete(0, END)
        preco = re.sub("[^0-9]", "", preco)
        if preco == "":
            return
        preco = preco[:8]
        precof = (int(preco) / 100)
        preco_str = locale.currency(precof, grouping=True).replace("R$ ", "")
        campo_valor_dinheiro.insert(0, preco_str)

    def fecha_dialogo():
        global dinheiro
        global troco
        global total_da_compra
        dialogo_pagto.destroy()
        dialogo_pagto.update()
        if dinheiro < total_da_compra:
            return
        troco = dinheiro - total_da_compra
        finaliza_venda()

    def enter_pressionado(e):
        global dinheiro
        dinheiro_str = campo_valor_dinheiro.get()
        dinheiro = int(dinheiro_str.replace(".", "").replace(",", ""))

        if dinheiro < total_da_compra:
            return
        fecha_dialogo()

    dialogo_pagto = Toplevel(tabs[0])
    dialogo_pagto.geometry("480x240+120+120")
    dialogo_pagto.resizable(False, False)
    dialogo_pagto.iconbitmap("images/main_icon.ico")
    rotulo_valor_dinheiro = Label(dialogo_pagto)
    rotulo_valor_dinheiro.config(font="None, 32", text="Entrada de Dinheiro:", pady=pady_padrao * 12)
    campo_valor_dinheiro = Entry(dialogo_pagto)
    campo_valor_dinheiro.config(width=9, font="Consolas, 52", bg="Black", fg="Lime", justify="right")
    rotulo_valor_dinheiro.pack()
    campo_valor_dinheiro.pack(pady=pady_padrao * 12)
    campo_valor_dinheiro.focus_set()
    campo_valor_dinheiro.insert(0, "0,00")
    campo_valor_dinheiro.bind("<KeyRelease>", formata_preco_entrada_dinheiro)
    campo_valor_dinheiro.bind("<Return>", enter_pressionado)
    dialogo_pagto.grab_set()
    dialogo_pagto.protocol("WM_DELETE_WINDOW", fecha_dialogo)


def formata_reais(valor):
    valorf = (int(valor) / 100)
    valor_str = locale.currency(valorf, grouping=True)
    return valor_str


def atualiza_qtde_estoque():
    msg("Atualizando quantidades do estoque na tabela de Produtos")
    for line in grid_fita_de_caixa.get_children():
        for value in grid_fita_de_caixa.item(line)["values"]:
            if not value:
                continue
            msg(value)
            if not value[len(value) - 3] == ",":
                msg(f"pulou {value}")
                continue
            cod_item = value[0:4]
            qtde_item = value[57:60]

            msg(f"Item cód: {cod_item} - Qtde vendida: {qtde_item}")
            qtde_item = int(qtde_item)
            cod_item = int(cod_item)
            curs.execute(
                f"UPDATE produtos SET qtde_estoque = qtde_estoque - {qtde_item} WHERE id = {cod_item}")
    conexao.commit()
    limpa_grid_produtos()
    preenche_grid_produtos()


def formata_cpf_tab_clientes(e):
    msg("Verificando formatação do CPF")
    texto_do_campo = campos_de_entrada_tab3[2].get()
    campos_de_entrada_tab3[2].delete(0, END)
    texto_do_campo = re.sub("[^0-9]", "", texto_do_campo)
    texto_do_campo = texto_do_campo[:11]
    campos_de_entrada_tab3[2].insert(0, formata_cpf(texto_do_campo))


def formata_telefone_tab_clientes(e):
    msg("Verificando formatação do TELEFONE")
    texto_do_campo = campos_de_entrada_tab3[3].get()
    campos_de_entrada_tab3[3].delete(0, END)
    texto_do_campo = re.sub("[^0-9]", "", texto_do_campo)
    texto_do_campo = texto_do_campo[:11]
    campos_de_entrada_tab3[3].insert(0, formata_telefone(texto_do_campo))


def formata_cod_barras_tab_produtos(e):
    msg("Formatando código de barras no tab produtos")
    cod_barras = campos_de_entrada_tab1[2].get()
    campos_de_entrada_tab1[2].delete(0, END)
    cod_barras = re.sub("[^0-9]", "", cod_barras)
    cod_barras = cod_barras[:13]
    campos_de_entrada_tab1[2].insert(0, cod_barras)


def formata_preco_tab_produtos(e):
    msg("Formatando preço no tab produtos")
    preco = campos_de_entrada_tab1[3].get()
    campos_de_entrada_tab1[3].delete(0, END)
    preco = re.sub("[^0-9]", "", preco)
    if preco == "":
        return
    preco = preco[:8]
    precof = (int(preco) / 100)
    preco_str = locale.currency(precof, grouping=True).replace("R$ ", "")
    campos_de_entrada_tab1[3].insert(0, preco_str)


def formata_qtde_tab_produtos(e):
    msg("Formatando quantidade no tab produtos")
    qtde = campos_de_entrada_tab1[4].get()
    campos_de_entrada_tab1[4].delete(0, END)
    qtde = re.sub("[^0-9]", "", qtde)
    qtde = qtde[:6]
    campos_de_entrada_tab1[4].insert(0, qtde)


def formata_cpf(cpf):
    msg("Formatando CPF")
    if cpf == "":
        return cpf
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"


def formata_telefone(telefone):
    msg("Formatando telefone")
    if telefone == "":
        return telefone
    return f"({telefone[:2]}){telefone[2:7]}-{telefone[7:11]}"


def valida_digitos_cpf(cpf):
    cpf = re.sub("[^0-9]", "", cpf)
    cpf_fornecido = cpf
    if len(cpf) < 11:
        return False
    cpf = cpf[:9]
    if debug_mode:
        msg("ATENÇÃO!")
        msg("Modo DEBUG desativa verificação de CPF! CPF's não verificados são aceitos sem restrição.")
        return True
    soma = 0
    for i in range(9):
        soma += (i + 1) * int(cpf[i])
    d1 = str(soma % 11 % 10)
    cpf += d1
    soma = 0
    for i in range(1, 10):
        soma += i * int(cpf[i])
    d2 = str(soma % 11 % 10)
    cpf += d2
    if cpf_fornecido == cpf:
        return True
    else:
        return False


def sair():
    if not messagebox.askyesno("Atenção!", "Deseja mesmo sair?"):
        return
    prepara_saida()
    sys.exit()


def prepara_saida():
    msg("Preparações necessárias antes de fechar o aplicativo")
    return
    # historico_de_caixa = text_historico_de_caixa.get("1.0", "end-1c")
    # with open("historico.txt", "w") as f:
    #     f.write(historico_de_caixa)


# Preenche o Grid de Produtos com os dados da tabela correspondente
def preenche_grid_produtos():
    msg("Preenchendo Grid Produtos...")
    dados = curs.execute("SELECT * FROM produtos").fetchall()
    for linha in dados:
        valor_estoque = int(re.sub("[^0-9]", "", linha[4])) * linha[5]
        valor_estoque = locale.currency(valor_estoque / 100, grouping=True).replace("R$ ", "")
        linha += (valor_estoque,)
        grid_Produtos.insert("", "end", values=linha)


# Preenche o Grid de Clientes com os dados da tabela correspondente
def preenche_grid_clientes():
    msg("Preenchendo Grid Clientes...")
    dados = curs.execute("SELECT * FROM clientes").fetchall()
    for linha in dados:
        grid_Clientes.insert("", "end", values=linha)


def apaga_cliente():
    msg("Apaga Cliente")
    linha = grid_Clientes.focus()
    if not linha:
        messagebox.showwarning("", "Nenhum cliente selecionado.")
        return
    msg(f"Linha selecionada: {linha}")
    valores = grid_Clientes.item(linha)["values"]
    msg(f"Conteúdo da linha: {valores}")
    valor = valores[0]
    msg(f"Conteúdo do primeiro campo {valor}")
    if not messagebox.askyesno("Atenção!", "Apagar registro?"):
        return
    grid_Clientes.delete(linha)
    curs.execute(f"DELETE FROM clientes WHERE id='{valor}'")
    conexao.commit()


def apaga_produto():
    msg("Apaga Produto")
    linha = grid_Produtos.focus()
    if not linha:
        messagebox.showwarning("", "Nenhum produto selecionado.")
        return
    msg(f"Linha selecionada: {linha}")
    valores = grid_Produtos.item(linha)["values"]
    msg(f"Conteúdo da linha: {valores}")
    valor = valores[0]
    msg(f"Conteúdo do primeiro campo {valor}")
    if not messagebox.askyesno("Atenção!", "Apagar registro?"):
        return
    grid_Produtos.delete(linha)
    curs.execute(f"DELETE FROM produtos WHERE id='{valor}'")
    conexao.commit()


def atualiza_produto():
    msg("Atualiza Produto")
    linha = grid_Produtos.focus()
    if not linha:
        messagebox.showwarning("", "Nenhum produto selecionado.")
        return
    if not messagebox.askyesno("Atenção!", "Atualizar registro?"):
        return
    valores = grid_Produtos.item(linha)["values"]
    cod_item = valores[0]
    msg(f"Alteração confirmada. Item código {cod_item}")
    houve_alteracao = False
    campos = ("produto", "fabricante", "cod_barras", "preco", "qtde_estoque")
    for i in range(len(campos)):
        new_value = campos_de_entrada_tab1[i].get()
        if new_value:
            houve_alteracao = True
        if i == 2:
            if new_value:
                messagebox.showwarning("", f"O campo {campos[i]} não é passível de alteração!")
            continue
        if not new_value:
            continue
        msg(f"Campo a ser alterado: {campos[i]}/Novo valor a alterar: {new_value}")
        curs.execute(
            f"UPDATE produtos SET {campos[i]} = '{new_value}' WHERE id = {cod_item}")
    conexao.commit()
    limpa_grid_produtos()
    preenche_grid_produtos()
    if houve_alteracao:
        messagebox.showinfo("", "Campos informados alterados com sucesso!")
    else:
        messagebox.showinfo("", "Nenhum campo foi alterado.")


def atualiza_cliente():
    msg("Atualiza Cliente")
    linha = grid_Clientes.focus()
    if not linha:
        messagebox.showwarning("", "Nenhum cliente selecionado.")
        return
    if not messagebox.askyesno("Atenção!", "Atualizar registro?"):
        return
    valores = grid_Clientes.item(linha)["values"]
    cod_item = valores[0]
    msg(f"Alteração confirmada. Item código {cod_item}")
    houve_alteracao = False
    campos = ("nome", "endereco", "cpf", "telefone", "email")
    for i in range(len(campos)):
        new_value = campos_de_entrada_tab3[i].get()
        if new_value:
            houve_alteracao = True
        if i == 2:
            if new_value:
                messagebox.showwarning("", f"O campo {campos[i]} não é passível de alteração!")
            continue
        if not new_value:
            continue
        msg(f"Campo a ser alterado: {campos[i]}/Novo valor a alterar: {new_value}")
        curs.execute(
            f"UPDATE clientes SET {campos[i]} = '{new_value}' WHERE id = {cod_item}")
    conexao.commit()
    limpa_grid_clientes()
    preenche_grid_clientes()
    if houve_alteracao:
        messagebox.showinfo("", "Campos informados alterados com sucesso!")
    else:
        messagebox.showinfo("", "Nenhum campo foi alterado.")


def limpa_campos_venda(e):
    for n in range(2):
        campos_de_entrada_tab0[n].delete(0, END)


def limpa_produtos():
    limpa_grid_produtos()
    for i in range(5):
        campos_de_entrada_tab1[i].delete(0, "end")
    campos_de_entrada_tab1[0].focus_set()
    preenche_grid_produtos()


def limpa_clientes():
    limpa_grid_clientes()
    for i in range(5):
        campos_de_entrada_tab3[i].delete(0, "end")
    campos_de_entrada_tab3[0].focus_set()
    preenche_grid_clientes()


def limpa_grid_produtos():
    grid_Produtos.delete(*grid_Produtos.get_children())


def limpa_grid_clientes():
    grid_Clientes.delete(*grid_Clientes.get_children())


def pesquisa_produto():
    msg("Pesquisa Produtos")
    item = []
    for i in range(5):
        valor = campos_de_entrada_tab1[i].get()
        item.append(valor)
    filtra_grid_produtos(item[0], item[1], item[2], item[3], item[4])


def pesquisa_cliente():
    msg("Pesquisa Clientes")
    item = []
    for i in range(5):
        valor = campos_de_entrada_tab3[i].get()
        item.append(valor)
    filtra_grid_clientes(item[0], item[1], item[2], item[3], item[4])


def filtra_grid_produtos(item1, item2, item3, item4, item5):
    msg("Filtrando Grid Produtos...")
    dados = curs.execute(f"SELECT * FROM produtos WHERE produto LIKE '%{item1}%' AND fabricante LIKE '%{item2}%'"
                         f" AND cod_barras LIKE '%{item3}%' AND preco LIKE '%{item4}%'"
                         f" AND qtde_estoque LIKE '%{item5}%'").fetchall()
    msg("Preenchendo Grid Produtos...")
    limpa_grid_produtos()
    for linha in dados:
        valor_estoque = int(re.sub("[^0-9]", "", linha[4])) * linha[5]
        valor_estoque = locale.currency(valor_estoque / 100, grouping=True).replace("R$ ", "")
        linha += (valor_estoque,)
        grid_Produtos.insert("", "end", values=linha)


def filtra_grid_clientes(item1, item2, item3, item4, item5):
    msg("Filtrando Grid Clientes...")
    dados = (curs.execute(f"SELECT * FROM clientes WHERE nome LIKE '%{item1}%'"
                          f" AND endereco LIKE '%{item2}%' AND cpf LIKE '%{item3}%'"
                          f" AND telefone LIKE '%{item4}%' AND email LIKE '%{item5}%'")
             .fetchall())
    msg("Preenchendo Grid Clientes...")
    limpa_grid_clientes()
    for linha in dados:
        grid_Clientes.insert("", "end", values=linha)


# Insere os dados digitados nos campos Entry na tabela "produtos"
def registra_produto():
    msg("Registra Produtos")
    produto_registrado = campos_de_entrada_tab1[0].get()
    fabricante_registrado = campos_de_entrada_tab1[1].get()
    cod_barras_registrado = campos_de_entrada_tab1[2].get()
    preco_registrado = campos_de_entrada_tab1[3].get()
    qtde_estoque_registrada = campos_de_entrada_tab1[4].get()
    if (produto_registrado == "" or fabricante_registrado == "" or cod_barras_registrado == "" or preco_registrado == ""
            or qtde_estoque_registrada == ""):
        msg("Não são permitidos campos vazios!")
        msg_erro(0)
        return

    if debug_mode:
        msg("ATENÇÃO!")
        msg("Modo DEBUG desativa verificação de duplicidade de CÓDIGO DE BARRAS! CÓDIGOS's duplicados são aceitos sem restrição.")
    else:
        dados = curs.execute(f"SELECT * FROM produtos WHERE cod_barras='{cod_barras_registrado}'").fetchall()
        if dados:
            msg("Já existe um produto com o mesmo cóigo de barras!")
            msg_erro(8)
            return

    curs.execute(f"INSERT INTO produtos (produto, fabricante, cod_barras, preco, qtde_estoque) VALUES"
                 f" ('{produto_registrado}','{fabricante_registrado}','{cod_barras_registrado}','{preco_registrado}'"
                 f",{qtde_estoque_registrada})")
    conexao.commit()
    dados = curs.execute("SELECT * FROM produtos WHERE ROWID IN ( SELECT max( ROWID ) FROM produtos )").fetchall()
    for linha in dados:
        grid_Produtos.insert("", "end", values=linha)
        grid_Produtos.yview_moveto(1)
    msg(f"Produto registrado")
    limpa_produtos()


# Insere os dados digitados nos campos Entry na tabela "clientes"
def registra_cliente():
    nome_registrado = campos_de_entrada_tab3[0].get()
    endereco_registrado = campos_de_entrada_tab3[1].get()
    cpf_registrado = campos_de_entrada_tab3[2].get()
    telefone_registrado = campos_de_entrada_tab3[3].get()
    email_registrado = campos_de_entrada_tab3[4].get()
    if nome_registrado == "" or endereco_registrado == "" or cpf_registrado == "" or telefone_registrado == "" \
            or email_registrado == "":
        msg("Não são permitidos campos vazios!")
        msg_erro(0)
        return
    if not valida_digitos_cpf(cpf_registrado):
        msg("CPF inválido!")
        msg_erro(3)
        return
    if len(cpf_registrado) < 14:
        msg("CPF deve ter 11 dígitos!")
        msg_erro(1)
        return
    if len(telefone_registrado) < 14:
        msg("TELEFONE deve ter 11 dígitos!")
        msg_erro(4)
        return
    if not "@" in email_registrado or email_registrado[0] == "@" or email_registrado[len(email_registrado) - 1] == "@":
        msg("Formato de e-mail inválido!")
        msg_erro(6)
        return
    if debug_mode:
        msg("ATENÇÃO!")
        msg("Modo DEBUG desativa verificação de duplicidade de CPF! CPF's duplicados são aceitos sem restrição.")
    else:
        dados = curs.execute(f"SELECT * FROM clientes WHERE cpf='{cpf_registrado}'").fetchall()
        if dados:
            msg("CPF já existe no cadastro de Clientes!")
            msg_erro(7)
            return
    curs.execute(f"INSERT INTO clientes (nome, endereco, cpf, telefone, email) VALUES"
                 f" ('{nome_registrado}','{endereco_registrado}','{cpf_registrado}','{telefone_registrado}','{email_registrado}')")
    conexao.commit()
    dados = curs.execute("SELECT * FROM clientes WHERE ROWID IN ( SELECT max( ROWID ) FROM clientes )").fetchall()
    for linha in dados:
        grid_Clientes.insert("", "end", values=linha)
        grid_Clientes.yview_moveto(1)
    msg(f"Cliente registrado")
    limpa_clientes()


# ---------------------------------------------------------------------------------------------------------------------

# Cria Janela
janela = Tk()
janela.geometry("1280x720+24+24")
janela.minsize(1280, 640)
janela.title("TINYMARKET - ETE")
# Seta o ícone da janela
janela.iconbitmap("images/main_icon.ico")
janela.protocol("WM_DELETE_WINDOW", sair)

# Cria a base de dados e as tabelas, se não existirem
# Obs: Utiliza o SQLite3
meu_arquivo = Path("controle_de_estoque.db")
criartabelas = not meu_arquivo.exists()
msg("criartabelas = " + str(criartabelas))
if criartabelas:
    msg("Criando banco de dados...")
else:
    msg("Banco de dados já existe")
conexao = sqlite3.connect("controle_de_estoque.db")
curs = conexao.cursor()
if criartabelas:
    curs.execute("CREATE TABLE clientes(id INTEGER PRIMARY"
                 " KEY AUTOINCREMENT, nome TEXT, endereco TEXT, cpf TEXT, telefone TEXT, email TEXT)")
    curs.execute("CREATE TABLE produtos(id INTEGER PRIMARY"
                 " KEY AUTOINCREMENT, produto TEXT, fabricante TEXT, cod_barras TEXT, preco TEXT, qtde_estoque INTEGER)")
    msg("Tabelas criadas")

# Cria o Menu Principal e os Submenus
main_menu = Menu(janela)
janela.config(menu=main_menu)
padx_padrao = 3
pady_padrao = 2

dinheiro = 0
troco = 0
total_da_compra = 0
nota_com_cpf = False

# Variáveis que determinam os tamanhos dos botões com e sem ícones
lar_botao_padrao = 16
lar_botao_img = 115
alt_botao_padrao = 1
alt_botao_img = 18

arquivo_menu = Menu(main_menu, tearoff=0)
main_menu.add_cascade(label="Arquivo", menu=arquivo_menu)
# arquivo_menu.add_command(label="Estoque", command=estoque)
arquivo_menu.add_command(label="Clientes", command=clientes)
arquivo_menu.add_command(label="Opções", command=opcoes)
arquivo_menu.add_command(label="Sair", command=sair)
produtos_menu = Menu(main_menu, tearoff=0)
main_menu.add_cascade(label="Produtos", menu=produtos_menu)
produtos_menu.add_command(label="Venda", command=venda)
produtos_menu.add_command(label="Cadastrar/Consultar", command=produtos)
caixa_menu = Menu(main_menu, tearoff=0)
main_menu.add_cascade(label="Caixa", menu=caixa_menu)
caixa_menu.add_command(label="Iniciar Nova Venda", command=inicia_venda)

# Cria as abas no tabControl e insere os títulos e ícones das abas
style = ttk.Style()
style.configure("Custom.TNotebook", tabposition="wn")
MainTabControl = ttk.Notebook(janela, style="Custom.TNotebook")
myTabs = ["VENDA", "PRODUTOS", "ESTOQUE", "CLIENTES", "OPÇÕES"]
myTabsImages = ["venda.png", "produtos.png", "estoque.png", "clientes.png", "opcoes.png"]
imagens_dos_tabs = []
n = 0
tabs = []
for names in myTabs:
    tabs.append(ttk.Frame(MainTabControl))
    imagens_dos_tabs.append(PhotoImage(file="images/" + myTabsImages[n]))
    MainTabControl.add(tabs[n], text=f"", image=imagens_dos_tabs[n])
    Label(tabs[n], text=" " + names, font=("", 30, "bold"),
          fg="teal", bg="ghostwhite", anchor=W).pack(fill=X, anchor=W, pady=pady_padrao)
    n += 1
MainTabControl.pack(expand=True, fill="both")
# Carrega as imagens de botões
icone_trash = PhotoImage(file="images/trash.png")
icone_search = PhotoImage(file="images/search.png")
icone_confirm = PhotoImage(file="images/confirm.png")
icone_confirm_red = PhotoImage(file="images/confirm_red.png")
icone_clear = PhotoImage(file="images/clear.png")
icone_update = PhotoImage(file="images/update.png")

# Cria os campos de entrada e botões na aba Venda

quadro_um_tab0 = Frame(tabs[0])
quadro_dois_tab0 = Frame(tabs[0])
quadro_tres_tab0 = Frame(tabs[0])

display_nome = ("*", "*", "*")
rotulo_display_tab0 = []
n = 0
for lines in display_nome:

    rotulo_display = Label(quadro_um_tab0, text=lines, padx=padx_padrao, pady=pady_padrao, anchor="center")
    if lines:
        rotulo_display.config(font=("Consolas", 24), fg="Lime", bg="Black")
    rotulo_display.pack(side=TOP, anchor=W, fill="x")
    rotulo_display_tab0.append(rotulo_display)

campos_nome = ("Cód. Barras:", "Produto:", "Qtde.:")
campos_tamanho = (15, 40, 5)
campos_de_entrada_tab0 = []
n = 0
for entries in campos_nome:
    rotulo = Label(quadro_um_tab0, text=entries, padx=padx_padrao, pady=pady_padrao, font=("", 12))
    rotulo.pack(side=TOP, anchor=W)
    entrada = Entry(quadro_um_tab0, width=campos_tamanho[n], font=("", 12))
    campos_de_entrada_tab0.append(entrada)
    if n == 0:
        entrada.config(justify="center")
        entrada.bind("<KeyRelease>", formata_cod_barras_tabvenda)
        entrada.bind("<FocusIn>", limpa_campos_venda)
    if n == 1:
        entrada.bind("<KeyRelease>", entrada_produto_tabvenda_changed)
        entrada.bind("<Return>", entrada_produto_confirma)
        entrada.bind("<FocusIn>", limpa_campos_venda)
    if n == 2:
        entrada.config(justify="center")
        entrada.bind("<KeyRelease>", formata_qtde_tab_venda)
        entrada.bind("<Return>", entrada_qtde_confirma)
        entrada.bind("<FocusOut>", formata_qtde_final_tab_venda)
    entrada.pack(padx=padx_padrao, pady=pady_padrao, side=TOP, anchor=W)
    n += 1

btn_registra_venda_produto = (Button(quadro_um_tab0, text="REGISTRA",
                                     image=icone_confirm, compound=LEFT,
                                     width=lar_botao_img * 2, height=alt_botao_img, command=registra_venda_produto))
btn_exclui_venda_produto = (Button(quadro_um_tab0, text="EXCLUI",
                                   image=icone_clear, compound=LEFT,
                                   width=lar_botao_img * 2, height=alt_botao_img, command=exclui_venda_produto))
btn_finaliza_venda_produto = (Button(quadro_um_tab0, text="FINALIZA",
                                     image=icone_confirm_red, compound=LEFT,
                                     width=lar_botao_img * 2, height=alt_botao_img, command=prepara_finalizar_venda))
btn_registra_venda_produto.pack(padx=padx_padrao, pady=pady_padrao * 6, side=LEFT, anchor=NW)
btn_exclui_venda_produto.pack(padx=padx_padrao, pady=pady_padrao * 6, anchor=E)
btn_finaliza_venda_produto.pack(padx=padx_padrao, pady=pady_padrao * 2, anchor=E)
InfoTabControl = ttk.Notebook(quadro_dois_tab0)
myTabs = ["Compra", "Cliente"]
n = 0
tabs_info = []
for names in myTabs:
    tabs_info.append(ttk.Frame(InfoTabControl))
    InfoTabControl.add(tabs_info[n], text=myTabs[n])
    n += 1
InfoTabControl.pack(expand=True, fill="both")
campos_nome = (
    "Descrição do Produto", "", "Código de Barras:", "", "Preço Unitário:", "", "Nome do Cliente:", "", "CPF:", "")
rotulos_tab0 = []
n = 0
for rotulos in campos_nome:
    if rotulos == "Nome do Cliente:":
        n += 1
    if rotulos == "":
        rotulo = Label(tabs_info[n], text=rotulos, padx=padx_padrao, pady=pady_padrao, font=("", 20),
                       fg="DarkBlue", bg="LightGray", anchor=E)
    else:
        rotulo = Label(tabs_info[n], text=rotulos, padx=padx_padrao, pady=pady_padrao, font=("", 9),
                       anchor=E)
    rotulos_tab0.append(rotulo)
    rotulo.pack(side=TOP, anchor=W, fill="x")
btn_comprador = Button(tabs_info[1], text="  INCLUI", image=icone_search, compound=LEFT, width=lar_botao_img * 2,
                       height=alt_botao_img,
                       command=informa_comprador)
btn_comprador.pack(padx=padx_padrao, pady=pady_padrao, side=RIGHT)
estilo = ttk.Style()
estilo.configure("meuestilo.Treeview", font=("Consolas", 12))
estilo.configure("meuestilo.Treeview.Heading", font=("Consolas", 15, "bold"))

CaixaTabControl = ttk.Notebook(quadro_tres_tab0)
myTabs = ["Venda", "Histórico"]
n = 0
tabs_caixa = []
for names in myTabs:
    tabs_caixa.append(ttk.Frame(CaixaTabControl))
    CaixaTabControl.add(tabs_caixa[n], text=myTabs[n])
    n += 1
CaixaTabControl.pack(expand=True, fill="both")
grid_fita_de_caixa = ttk.Treeview(tabs_caixa[0], columns=["caixa"], show="headings",
                                  selectmode="browse"
                                  , height=80)
grid_fita_de_caixa.config(style="meuestilo.Treeview")
grid_fita_de_caixa.heading(0, text="----------------- CAIXA -----------------")
grid_fita_de_caixa.column(0, width=640, anchor=E)
grid_fita_de_caixa.pack(side=BOTTOM, anchor=NW, expand=True, padx=padx_padrao * 4, pady=pady_padrao * 4)
text_historico_de_caixa = Text(tabs_caixa[1])
text_historico_de_caixa.pack(padx=padx_padrao * 4, pady=pady_padrao * 4, expand=True, fill="both")
text_historico_de_caixa.config(width=80, state="disabled")
quadro_tres_tab0.pack(side=LEFT, expand=False, fill="x", anchor=NW)
quadro_dois_tab0.pack(side=TOP, expand=True, fill="x", anchor=NW)
quadro_um_tab0.pack(side=TOP, expand=True, fill="x", anchor=NW)

# Cria os campos de entrada e botões na aba Produtos
campos_de_entrada_tab1 = []
campos_nome = ("Produto:", "Fabricante:", "Cód. Barras:", "Preço R$:", "Qtde. Estoque:")
campos_tamanho = (40, 30, 15, 12, 7, 12)
quadro_um_tab1 = Frame(tabs[1])
quadro_dois_tab1 = Frame(tabs[1])
n = 0
for entries in campos_nome:
    # if entries == "Qtde. Estoque":
    #    break
    rotulo = Label(quadro_um_tab1, text=entries, padx=padx_padrao, pady=pady_padrao)
    rotulo.pack(side=LEFT)
    entrada = Entry(quadro_um_tab1, width=campos_tamanho[n])
    campos_de_entrada_tab1.append(entrada)
    if entries == "Cód. Barras:":
        entrada.config(justify="center")
        entrada.bind("<KeyRelease>", formata_cod_barras_tab_produtos)
    if entries == "Preço R$:":
        entrada.config(justify="right")
        entrada.bind("<KeyRelease>", formata_preco_tab_produtos)
    if entries == "Qtde. Estoque:":
        entrada.bind("<KeyRelease>", formata_qtde_tab_produtos)
    entrada.pack(padx=padx_padrao, pady=pady_padrao, side=LEFT)
    n += 1

botao_registra_produto = Button(quadro_um_tab1, text="  REGISTRAR", image=icone_confirm, compound=LEFT,
                                width=lar_botao_img, height=alt_botao_img, command=registra_produto)
botao_limpa_produtos = Button(quadro_dois_tab1, text="  LIMPAR", image=icone_clear, compound=LEFT, width=lar_botao_img,
                              height=alt_botao_img,
                              command=limpa_produtos)
botao_pesquisa_produto = Button(quadro_dois_tab1, text="  PESQUISAR", image=icone_search, compound=LEFT,
                                width=lar_botao_img, height=alt_botao_img, command=pesquisa_produto)
botao_atualiza_produto = Button(quadro_dois_tab1, text="  ATUALIZAR", image=icone_update, compound=LEFT,
                                width=lar_botao_img, height=alt_botao_img, command=atualiza_produto)
botao_apaga_produto = Button(quadro_dois_tab1, text="  APAGAR", image=icone_trash, compound=LEFT,
                             width=lar_botao_img, height=alt_botao_img, command=apaga_produto)
botao_registra_produto.pack(padx=padx_padrao, pady=pady_padrao)
botao_limpa_produtos.pack(padx=padx_padrao, pady=pady_padrao, side=LEFT)
botao_pesquisa_produto.pack(padx=padx_padrao, pady=pady_padrao, side=LEFT)
botao_atualiza_produto.pack(padx=padx_padrao, pady=pady_padrao, side=LEFT)
botao_apaga_produto.pack(padx=padx_padrao, pady=pady_padrao, side=LEFT)
quadro_um_tab1.pack(pady=pady_padrao, anchor=E)
quadro_dois_tab1.pack(pady=pady_padrao, anchor=E)

# Cria um Grid (TreeView) na aba Produtos
colunas = ("id", "produto", "fabricante", "cod_barras", "preco", "qtde_estoque", "valor_estoque")
colunas_nome = ("ID", "PRODUTO", "FABRICANTE", "CÓD.BARRAS", "PREÇO UNIT. R$", "QTD.ESTOQUE", "VALOR ESTOQUE R$")
colunas_tamanho = (4, 30, 18, 15, 11, 8, 11)
grid_Produtos = ttk.Treeview(tabs[1], columns=colunas, show="headings", selectmode="browse")
grid_Produtos.pack(expand=True, fill=BOTH, padx=padx_padrao, pady=pady_padrao)
n = 0
for items in colunas:
    grid_Produtos.heading(items, text=colunas_nome[n])
    grid_Produtos.column(n, width=colunas_tamanho[n] * 12)
    if n > 2:
        grid_Produtos.column(n, anchor=E)
    if items == "cod_barras":
        grid_Produtos.column(n, anchor=CENTER)
    n += 1
grid_Produtos.column(0, anchor=E, stretch=NO)
preenche_grid_produtos()

# Cria os campos de entrada e botões na aba Clientes
campos_de_entrada_tab3 = []
campos_nome = ("Nome:", "Endereço:", "CPF:", "Telefone:", "E-mail")
campos_tamanho = (32, 40, 14, 14, 28)
quadro_um_tab3 = Frame(tabs[3])
quadro_dois_tab3 = Frame(tabs[3])
n = 0
for entries in campos_nome:
    rotulo = Label(quadro_um_tab3, text=entries, padx=padx_padrao, pady=pady_padrao)
    rotulo.pack(side=LEFT)
    entrada = Entry(quadro_um_tab3, width=campos_tamanho[n])
    campos_de_entrada_tab3.append(entrada)
    entrada.pack(padx=padx_padrao, pady=pady_padrao, side=LEFT)
    if n == 2:
        entrada.config(justify="center", validate="key")
        entrada.bind("<KeyRelease>", formata_cpf_tab_clientes)
    if n == 3:
        entrada.config(justify="center", validate="key")
        entrada.bind("<KeyRelease>", formata_telefone_tab_clientes)
    n += 1
botao_registra_cliente = Button(quadro_um_tab3, text="  REGISTRAR", image=icone_confirm, compound=LEFT,
                                width=lar_botao_img, height=alt_botao_img, command=registra_cliente)
botao_limpa_clientes = Button(quadro_dois_tab3, text="  LIMPAR", image=icone_clear, compound=LEFT, width=lar_botao_img,
                              height=alt_botao_img,
                              command=limpa_clientes)
botao_pesquisa_cliente = Button(quadro_dois_tab3, text="  PESQUISAR", image=icone_search, compound=LEFT,
                                width=lar_botao_img, height=alt_botao_img, command=pesquisa_cliente)
botao_atualiza_cliente = Button(quadro_dois_tab3, text="  ATUALIZAR", image=icone_update, compound=LEFT,
                                width=lar_botao_img, height=alt_botao_img, command=atualiza_cliente)
botao_apaga_cliente = Button(quadro_dois_tab3, text="  APAGAR", image=icone_trash, compound=LEFT,
                             width=lar_botao_img, height=alt_botao_img, command=apaga_cliente)
botao_registra_cliente.pack(padx=padx_padrao, pady=pady_padrao)
botao_limpa_clientes.pack(padx=padx_padrao, pady=pady_padrao, side=LEFT)
botao_pesquisa_cliente.pack(padx=padx_padrao, pady=pady_padrao, side=LEFT)
botao_atualiza_cliente.pack(padx=padx_padrao, pady=pady_padrao, side=LEFT)
botao_apaga_cliente.pack(padx=padx_padrao, pady=pady_padrao, side=LEFT)
quadro_um_tab3.pack(pady=pady_padrao, anchor=E)
quadro_dois_tab3.pack(pady=pady_padrao, anchor=E)

colunas = ("id", "nome", "endereco", "cpf", "telefone", "e-mail")
colunas_nome = ("ID", "NOME COMPLETO", "ENDEREÇO", "CPF", "TELEFONE", "E-MAIL")
colunas_tamanho = (4, 32, 38, 16, 14, 28)
grid_Clientes = ttk.Treeview(tabs[3], columns=colunas, show="headings", selectmode="browse")
grid_Clientes.pack(expand=True, fill=BOTH, padx=padx_padrao, pady=pady_padrao)
n = 0
for items in colunas:
    grid_Clientes.heading(items, text=colunas_nome[n])
    grid_Clientes.column(n, width=colunas_tamanho[n] * 8)
    n += 1
grid_Clientes.column(0, anchor=E, stretch=NO)
grid_Clientes.column(3, anchor=CENTER, stretch=NO)
grid_Clientes.column(4, anchor=CENTER, stretch=NO)
preenche_grid_clientes()

# Associa a tecla <ENTER> à função on_enter_key_pressed para cada botão
n = 0
msg("Associando <ENTER> aos botões")
associa_botoes(MainTabControl)

# Cria os widgets da aba Opções
quadro_um_tab4 = Frame(tabs[4])
quadro_um_tab4.pack(anchor=NW, fill="x")
checkbox_debugmode_ischecked = BooleanVar(value=True)
checkbox_frames_visible_ischecked = BooleanVar()
checkbox_bigbuttons_ischecked = BooleanVar(value=True)
checkbox_printer_enabled_ischecked = BooleanVar(value=True)
checkb_debug_mode = Checkbutton(quadro_um_tab4, text="Modo DEBUG", command=debug_mode_changed,
                                variable=checkbox_debugmode_ischecked)
checkb_frames_visible_mode = Checkbutton(quadro_um_tab4, text="Bordas visíveis (relevo)",
                                         command=seta_aparencia_de_widgets,
                                         variable=checkbox_frames_visible_ischecked)
checkb_bigbuttons_mode = Checkbutton(quadro_um_tab4, text="Botões grandes", command=seta_aparencia_de_widgets,
                                     variable=checkbox_bigbuttons_ischecked)
checkb_printer_mode = Checkbutton(quadro_um_tab4, text="Impressora ativada",
                                  variable=checkbox_printer_enabled_ischecked)
checkb_debug_mode.pack(anchor=W, padx=padx_padrao * 2, pady=pady_padrao * 2)
checkb_frames_visible_mode.pack(anchor=W, padx=padx_padrao * 2, pady=pady_padrao * 2)
checkb_bigbuttons_mode.pack(anchor=W, padx=padx_padrao * 2, pady=pady_padrao * 2)
checkb_printer_mode.pack(anchor=W, padx=padx_padrao * 2, pady=pady_padrao * 2)
debug_mode = checkbox_debugmode_ischecked.get()
seta_aparencia_de_widgets()
seta_estado_inicial_do_app()
finaliza_venda()

# Loop da janela
janela.mainloop()
