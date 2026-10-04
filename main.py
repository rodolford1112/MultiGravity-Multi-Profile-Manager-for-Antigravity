import os
import sys
import re
import json
import shutil
import sqlite3
import subprocess
import urllib.parse
import uuid
import time
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PROFILES_DIR = os.path.join(BASE_DIR, "profiles")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
MASTER_DIR = os.path.join(os.path.expanduser("~"), ".gemini", "config", "projects")
MASTER_AG = os.path.join(os.path.expanduser("~"), ".gemini", "antigravity")
DB_PATH = os.path.join(MASTER_AG, "conversation_summaries.db")

CLAUDE_PKG = "Claude_pzs8sxrjxfjjc"
CHATGPT_PKG = "OpenAI.Codex_2p2nqsd0c76g0"
CLAUDE_JSON_PATH = os.path.expanduser("~/.claude.json")
CLAUDE_PROJECTS_DIR = os.path.expanduser("~/.claude/projects")

CODEX_DIR = os.path.expanduser("~/.codex")
CODEX_DB = os.path.join(CODEX_DIR, "state_5.sqlite")
CODEX_CONFIG = os.path.join(CODEX_DIR, "config.toml")
CODEX_GLOBAL_STATE = os.path.join(CODEX_DIR, ".codex-global-state.json")

def get_antigravity_exe():
    local = os.environ.get("LOCALAPPDATA", "")
    p1 = os.path.join(local, "Programs", "antigravity", "Antigravity.exe")
    if os.path.exists(p1):
        return p1
    prog = os.environ.get("PROGRAMFILES", "C:\\Program Files")
    p2 = os.path.join(prog, "Antigravity", "Antigravity.exe")
    if os.path.exists(p2):
        return p2
    return p1

EXE_PATH = get_antigravity_exe()

def is_claude_installed():
    local_apps = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WindowsApps", "claude-desktop.exe")
    if os.path.exists(local_apps):
        return True
    pkg_dir = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Packages", CLAUDE_PKG)
    return os.path.exists(pkg_dir)

def is_chatgpt_installed():
    pkg_dir = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Packages", CHATGPT_PKG)
    return os.path.exists(pkg_dir) or os.path.exists(CODEX_DIR)

os.makedirs(PROFILES_DIR, exist_ok=True)

TEXTOS = {
    "pt": {
        "title": "Gerenciador de Perfis Antigravity",
        "frame_create": "Criar Novo Perfil",
        "lbl_nome": "Nome:",
        "btn_add": "Adicionar",
        "chk_copiar": "Compartilhar todos os projetos neste novo perfil",
        "frame_perfis": "Perfis",
        "btn_abrir": "Abrir Perfil Selecionado",
        "btn_proj": "Compartilhar Projetos do Perfil",
        "btn_atalho": "Criar Atalho na Area de Trabalho",
        "btn_del": "Excluir Perfil",
        "lbl_idioma": "Idioma:",
        "projetos_sufixo": "projetos",
        "aviso_selecao": "Selecione um perfil na lista!",
        "aviso_nome": "Digite um nome para o perfil!",
        "aviso_nome_invalido": "Nome invalido! Nao use caracteres especiais (< > : \" / \\ | ? *) nem termine com espaco ou ponto.",
        "erro_existe": "Ja existe um perfil com esse nome!",
        "sucesso_criado": "Perfil '{nome}' criado com sucesso!",
        "sucesso_atalho": "Atalho criado na Area de Trabalho:\nAntigravity - {nome}.lnk",
        "confirma_del": "Tem certeza que deseja apagar o perfil '{nome}' e todos os dados dele?",
        "top_titulo": "Compartilhar Projetos - {nome}",
        "top_aviso": "Selecione os projetos visiveis para: {nome}",
        "filtrar": "Filtrar:",
        "marcar_todos": "Marcar Todos",
        "desmarcar_todos": "Desmarcar Todos",
        "btn_salvar": "Salvar Alteracoes",
        "btn_cancelar": "Cancelar",
        "sucesso_proj": "Projetos do perfil '{nome}' atualizados com sucesso!",
        "info_sem_proj": "Nenhum projeto encontrado no sistema!",
        "t_aviso": "Aviso",
        "t_erro": "Erro",
        "t_sucesso": "Sucesso",
        "t_confirma": "Confirmar",
        "t_info": "Info"
    },
    "en": {
        "title": "Antigravity Profile Manager",
        "frame_create": "Create New Profile",
        "lbl_nome": "Name:",
        "btn_add": "Add",
        "chk_copiar": "Share all projects in this new profile",
        "frame_perfis": "Profiles",
        "btn_abrir": "Open Selected Profile",
        "btn_proj": "Share Profile Projects",
        "btn_atalho": "Create Desktop Shortcut",
        "btn_del": "Delete Profile",
        "lbl_idioma": "Language:",
        "projetos_sufixo": "projects",
        "aviso_selecao": "Select a profile from the list!",
        "aviso_nome": "Enter a name for the profile!",
        "aviso_nome_invalido": "Invalid profile name! Do not use special characters (< > : \" / \\ | ? *) or trailing spaces/dots.",
        "erro_existe": "A profile with this name already exists!",
        "sucesso_criado": "Profile '{nome}' created successfully!",
        "sucesso_atalho": "Shortcut created on Desktop:\nAntigravity - {nome}.lnk",
        "confirma_del": "Are you sure you want to delete profile '{nome}' and all its data?",
        "top_titulo": "Share Projects - {nome}",
        "top_aviso": "Select visible projects for: {nome}",
        "filtrar": "Filter:",
        "marcar_todos": "Select All",
        "desmarcar_todos": "Deselect All",
        "btn_salvar": "Save Changes",
        "btn_cancelar": "Cancel",
        "sucesso_proj": "Projects for profile '{nome}' updated successfully!",
        "info_sem_proj": "No projects found on system!",
        "t_aviso": "Warning",
        "t_erro": "Error",
        "t_sucesso": "Success",
        "t_confirma": "Confirm",
        "t_info": "Info"
    },
    "es": {
        "title": "Administrador de Perfiles Antigravity",
        "frame_create": "Crear Nuevo Perfil",
        "lbl_nome": "Nombre:",
        "btn_add": "Agregar",
        "chk_copiar": "Compartir todos los proyectos en este nuevo perfil",
        "frame_perfis": "Perfiles",
        "btn_abrir": "Abrir Perfil Seleccionado",
        "btn_proj": "Compartir Proyectos del Perfil",
        "btn_atalho": "Crear Acceso Directo en el Escritorio",
        "btn_del": "Eliminar Perfil",
        "lbl_idioma": "Idioma:",
        "projetos_sufixo": "proyectos",
        "aviso_selecao": "¡Selecciona un perfil de la lista!",
        "aviso_nome": "¡Introduce un nombre para el perfil!",
        "aviso_nome_invalido": "¡Nombre de perfil no valido! No use caracteres especiales (< > : \" / \\ | ? *) ni espacios o puntos finales.",
        "erro_existe": "¡Ya existe un perfil con ese nombre!",
        "sucesso_criado": "¡Perfil '{nome}' creado con exito!",
        "sucesso_atalho": "Acceso directo creado en el Escritorio:\nAntigravity - {nome}.lnk",
        "confirma_del": "¿Estas seguro de que deseas eliminar el perfil '{nome}' y todos sus datos?",
        "top_titulo": "Compartir Proyectos - {nome}",
        "top_aviso": "Selecciona los proyectos visibles para: {nome}",
        "filtrar": "Filtrar:",
        "marcar_todos": "Marcar Todos",
        "desmarcar_todos": "Desmarcar Todos",
        "btn_salvar": "Guardar Cambios",
        "btn_cancelar": "Cancelar",
        "sucesso_proj": "¡Proyectos del perfil '{nome}' actualizados con exito!",
        "info_sem_proj": "¡No se encontraron proyectos en el sistema!",
        "t_aviso": "Aviso",
        "t_erro": "Error",
        "t_sucesso": "Exito",
        "t_confirma": "Confirmar",
        "t_info": "Info"
    },
    "ru": {
        "title": "Менеджер профилей Antigravity",
        "frame_create": "Создать новый профиль",
        "lbl_nome": "Имя:",
        "btn_add": "Добавить",
        "chk_copiar": "Поделиться всеми проектами в новом профиле",
        "frame_perfis": "Профили",
        "btn_abrir": "Открыть выбранный профиль",
        "btn_proj": "Управление проектами профиля",
        "btn_atalho": "Создать ярлык на рабочем столе",
        "btn_del": "Удалить профиль",
        "lbl_idioma": "Язык:",
        "projetos_sufixo": "проектов",
        "aviso_selecao": "Выберите профиль из списка!",
        "aviso_nome": "Введите имя для профиля!",
        "aviso_nome_invalido": "Недопустимое имя профиля! Не используйте специальные символы (< > : \" / \\ | ? *) или пробелы/точки в конце.",
        "erro_existe": "Профиль с таким именем уже существует!",
        "sucesso_criado": "Профиль '{nome}' успешно создан!",
        "sucesso_atalho": "Ярлык создан на рабочем столе:\nAntigravity - {nome}.lnk",
        "confirma_del": "Вы уверены, что хотите удалить профиль '{nome}' и все его данные?",
        "top_titulo": "Управление проектами - {nome}",
        "top_aviso": "Выберите проекты, доступные для: {nome}",
        "filtrar": "Фильтр:",
        "marcar_todos": "Выбрать все",
        "desmarcar_todos": "Снять выделение",
        "btn_salvar": "Сохранить изменения",
        "btn_cancelar": "Отмена",
        "sucesso_proj": "Проекты профиля '{nome}' успешно обновлены!",
        "info_sem_proj": "Проекты в системе не найдены!",
        "t_aviso": "Предупреждение",
        "t_erro": "Ошибка",
        "t_sucesso": "Успех",
        "t_confirma": "Подтверждение",
        "t_info": "Информация"
    }
}

IDIOMAS_NOMES = {
    "Português": "pt",
    "English": "en",
    "Español": "es",
    "Русский": "ru"
}

def carregar_idioma_salvo():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
                return d.get("lang", "pt")
        except:
            pass
    example_config = os.path.join(BASE_DIR, "config.example.json")
    if os.path.exists(example_config):
        try:
            with open(example_config, "r", encoding="utf-8") as f:
                d = json.load(f)
                return d.get("lang", "pt")
        except:
            pass
    return "pt"

def salvar_idioma(sigla):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({"lang": sigla}, f)
    except:
        pass

idioma_atual = carregar_idioma_salvo()

def t(chave, **kwargs):
    dic = TEXTOS.get(idioma_atual, TEXTOS["pt"])
    val = dic.get(chave, chave)
    if kwargs:
        return val.format(**kwargs)
    return val

def obter_todos_projetos():
    projetos = {}
    pastas = [MASTER_DIR]
    if os.path.exists(PROFILES_DIR):
        for p in os.listdir(PROFILES_DIR):
            d = os.path.join(PROFILES_DIR, p, "home", ".gemini", "config", "projects")
            if os.path.exists(d):
                pastas.append(d)
    for d in pastas:
        if not os.path.exists(d):
            continue
        for f in os.listdir(d):
            if f.endswith(".json") and f != "outside-of-project.json":
                caminho = os.path.join(d, f)
                try:
                    with open(caminho, "r", encoding="utf-8") as fp:
                        dados = json.load(fp)
                        nome = dados.get("name", f[:-5])
                        pid = dados.get("id", f[:-5])
                        if pid not in projetos:
                            projetos[pid] = {"id": pid, "name": nome, "filename": f, "src": caminho}
                except:
                    pass
    return projetos

def carregar_lista():
    lista.delete(0, tk.END)
    if os.path.exists(PROFILES_DIR):
        for pasta in sorted(os.listdir(PROFILES_DIR)):
            caminho = os.path.join(PROFILES_DIR, pasta)
            if os.path.isdir(caminho):
                d_proj = os.path.join(caminho, "home", ".gemini", "config", "projects")
                qtd = 0
                if os.path.exists(d_proj):
                    qtd = len([f for f in os.listdir(d_proj) if f.endswith(".json") and f != "outside-of-project.json"])
                sufixo = t("projetos_sufixo")
                lista.insert(tk.END, f"{pasta}  ({qtd} {sufixo})")

def encode_claude_project_dir(path):
    p = os.path.normpath(path)
    if len(p) > 1 and p[1] == ":":
        drive = p[0]
        rest = p[2:].lstrip("\\")
        parts = [part.replace(" ", "-") for part in rest.split("\\")]
        return f"{drive}--" + "-".join(parts)
    return p.replace(":", "--").replace("\\", "-").replace("/", "-").replace(" ", "-")

def clean_user_text(text):
    text = re.sub(r'<USER_REQUEST>\s*', '', text)
    text = re.sub(r'\s*</USER_REQUEST>', '', text)
    text = re.sub(r'<ADDITIONAL_METADATA>[\s\S]*?</ADDITIONAL_METADATA>', '', text)
    text = re.sub(r'<CONTEXT_SUMMARY>[\s\S]*?</CONTEXT_SUMMARY>', '', text)
    return text.strip()


def garantir_link_antigravity(pasta_perfil):
    master_ag = os.path.join(os.path.expanduser("~"), ".gemini", "antigravity")
    if not os.path.exists(master_ag):
        return
    ag_dir = os.path.join(pasta_perfil, "home", ".gemini", "antigravity")
    gemini_dir = os.path.join(pasta_perfil, "home", ".gemini")
    os.makedirs(gemini_dir, exist_ok=True)
    if os.path.islink(ag_dir):
        return
    if os.path.exists(ag_dir):
        summaries = os.path.join(ag_dir, "conversation_summaries.db")
        if os.path.exists(summaries) and os.path.getsize(summaries) > 30000:
            return
        try:
            shutil.rmtree(ag_dir, ignore_errors=True)
        except:
            pass
    try:
        subprocess.run(["cmd", "/c", "mklink", "/J", ag_dir, master_ag], capture_output=True)
    except:
        pass
    if not os.path.exists(ag_dir):
        try:
            os.makedirs(ag_dir, exist_ok=True)
            for f in ["conversation_summaries.db", "antigravity_state.pbtxt"]:
                src = os.path.join(master_ag, f)
                if os.path.exists(src):
                    shutil.copy2(src, os.path.join(ag_dir, f))
            for d in ["conversations", "brain"]:
                src = os.path.join(master_ag, d)
                dst = os.path.join(ag_dir, d)
                if os.path.exists(src) and not os.path.exists(dst):
                    shutil.copytree(src, dst)
        except:
            pass

def validar_nome_perfil(nome):
    if not nome:
        return False
    # Caracteres invalidos para pastas no Windows: \ / : * ? " < > |
    if re.search(r'[<>:"/\\|?*]', nome):
        return False
    if nome.endswith(".") or nome.endswith(" "):
        return False
    return True

def criar_perfil():
    nome = entrada_nome.get().strip()
    if not nome:
        messagebox.showwarning(t("t_aviso"), t("aviso_nome"))
        return
    if not validar_nome_perfil(nome):
        messagebox.showwarning(t("t_aviso"), t("aviso_nome_invalido"))
        return
    pasta_perfil = os.path.join(PROFILES_DIR, nome)
    if os.path.exists(pasta_perfil):
        messagebox.showerror(t("t_erro"), t("erro_existe"))
        return
    pasta_proj = os.path.join(pasta_perfil, "home", ".gemini", "config", "projects")
    os.makedirs(os.path.join(pasta_perfil, "data"), exist_ok=True)
    os.makedirs(pasta_proj, exist_ok=True)
    garantir_link_antigravity(pasta_perfil)
    
    with open(os.path.join(pasta_proj, "outside-of-project.json"), "w", encoding="utf-8") as fp:
        json.dump({"id": "outside-of-project", "name": "Outside of Project"}, fp)

    if var_copiar_tudo.get():
        todos = obter_todos_projetos()
        for p in todos.values():
            try:
                shutil.copy2(p["src"], os.path.join(pasta_proj, p["filename"]))
            except:
                pass

    entrada_nome.delete(0, tk.END)
    carregar_lista()
    messagebox.showinfo(t("t_sucesso"), t("sucesso_criado", nome=nome))

def abrir_perfil():
    selecao = lista.curselection()
    if not selecao:
        messagebox.showwarning(t("t_aviso"), t("aviso_selecao"))
        return
    item = lista.get(selecao[0])
    nome = item.split("  (")[0]
    pasta_perfil = os.path.join(PROFILES_DIR, nome)
    data_dir = os.path.join(pasta_perfil, "data")
    home_dir = os.path.join(pasta_perfil, "home")
    pasta_proj = os.path.join(home_dir, ".gemini", "config", "projects")
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(pasta_proj, exist_ok=True)
    garantir_link_antigravity(pasta_perfil)
    
    outside_file = os.path.join(pasta_proj, "outside-of-project.json")
    if not os.path.exists(outside_file):
        with open(outside_file, "w", encoding="utf-8") as fp:
            json.dump({"id": "outside-of-project", "name": "Outside of Project"}, fp)

    env = os.environ.copy()
    env["USERPROFILE"] = home_dir
    env["SSH_CONNECTION"] = "127.0.0.1 1234 127.0.0.1 22"
    env["SSH_CLIENT"] = "127.0.0.1 1234 22"
    cmd = [EXE_PATH, f"--user-data-dir={data_dir}"]
    subprocess.Popen(cmd, env=env, cwd=os.path.dirname(EXE_PATH), creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)

def criar_atalho():
    selecao = lista.curselection()
    if not selecao:
        messagebox.showwarning(t("t_aviso"), t("aviso_selecao"))
        return
    item = lista.get(selecao[0])
    nome = item.split("  (")[0]
    pasta_perfil = os.path.join(PROFILES_DIR, nome)
    data_dir = os.path.join(pasta_perfil, "data")
    home_dir = os.path.join(pasta_perfil, "home")
    garantir_link_antigravity(pasta_perfil)
    runner_script = os.path.join(pasta_perfil, "launch.vbs")
    vbs = f'''Set WshShell = CreateObject("WScript.Shell")
Set objEnv = WshShell.Environment("PROCESS")
objEnv("USERPROFILE") = "{home_dir}"
objEnv("SSH_CONNECTION") = "127.0.0.1 1234 127.0.0.1 22"
objEnv("SSH_CLIENT") = "127.0.0.1 1234 22"
WshShell.Run """{EXE_PATH}"" --user-data-dir=""{data_dir}""", 1, False
'''
    with open(runner_script, "w", encoding="utf-8") as f:
        f.write(vbs)
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    shortcut_path = os.path.join(desktop, f"Antigravity - {nome}.lnk")
    ps = f'''
$sh = New-Object -ComObject WScript.Shell
$s = $sh.CreateShortcut('{shortcut_path}')
$s.TargetPath = 'wscript.exe'
$s.Arguments = '"{runner_script}"'
$s.WorkingDirectory = '{os.path.dirname(EXE_PATH)}'
$s.IconLocation = '{EXE_PATH},0'
$s.Description = 'Antigravity - {nome}'
$s.Save()
'''
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True)
    messagebox.showinfo(t("t_sucesso"), t("sucesso_atalho", nome=nome))

def excluir_perfil():
    selecao = lista.curselection()
    if not selecao:
        messagebox.showwarning(t("t_aviso"), t("aviso_selecao"))
        return
    item = lista.get(selecao[0])
    nome = item.split("  (")[0]
    if messagebox.askyesno(t("t_confirma"), t("confirma_del", nome=nome)):
        shutil.rmtree(os.path.join(PROFILES_DIR, nome), ignore_errors=True)
        carregar_lista()

def gerenciar_projetos():
    selecao = lista.curselection()
    if not selecao:
        messagebox.showwarning(t("t_aviso"), t("aviso_selecao"))
        return
    item = lista.get(selecao[0])
    nome = item.split("  (")[0]
    pasta_perfil = os.path.join(PROFILES_DIR, nome)
    pasta_proj_perfil = os.path.join(pasta_perfil, "home", ".gemini", "config", "projects")
    os.makedirs(pasta_proj_perfil, exist_ok=True)

    todos = obter_todos_projetos()
    if not todos:
        messagebox.showinfo(t("t_info"), t("info_sem_proj"))
        return

    arquivos_atuais = set(os.listdir(pasta_proj_perfil)) if os.path.exists(pasta_proj_perfil) else set()

    top = tk.Toplevel(janela)
    top.title(t("top_titulo", nome=nome))
    top.geometry("470x520")
    top.transient(janela)

    frame_topo_top = tk.Frame(top, padx=10, pady=5)
    frame_topo_top.pack(fill="x")

    lbl_aviso = tk.Label(frame_topo_top, text=t("top_aviso", nome=nome), font=("Arial", 9, "bold"))
    lbl_aviso.pack(anchor="w", pady=(0, 5))

    frame_busca = tk.Frame(frame_topo_top)
    frame_busca.pack(fill="x", pady=2)
    tk.Label(frame_busca, text=t("filtrar")).pack(side="left")
    entrada_filtro = tk.Entry(frame_busca)
    entrada_filtro.pack(side="left", fill="x", expand=True, padx=5)

    frame_acoes = tk.Frame(frame_topo_top)
    frame_acoes.pack(fill="x", pady=4)

    def marcar_todos():
        for pid in vars_map:
            vars_map[pid].set(True)

    def desmarcar_todos():
        for pid in vars_map:
            vars_map[pid].set(False)

    btn_marcar = tk.Button(frame_acoes, text=t("marcar_todos"), command=marcar_todos, width=15)
    btn_marcar.pack(side="left", padx=2)

    btn_desmarcar = tk.Button(frame_acoes, text=t("desmarcar_todos"), command=desmarcar_todos, width=15)
    btn_desmarcar.pack(side="left", padx=2)

    frame_conteudo = tk.Frame(top, padx=10, pady=5)
    frame_conteudo.pack(fill="both", expand=True)

    canvas = tk.Canvas(frame_conteudo, borderwidth=1, relief="sunken")
    scroll = tk.Scrollbar(frame_conteudo, orient="vertical", command=canvas.yview)
    frame_scroll = tk.Frame(canvas)

    frame_scroll.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=frame_scroll, anchor="nw")
    canvas.configure(yscrollcommand=scroll.set)

    canvas.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")

    def rolar(evento):
        canvas.yview_scroll(int(-1 * (evento.delta / 120)), "units")
    canvas.bind_all("<MouseWheel>", rolar)

    vars_map = {}
    widgets_map = {}

    projetos_ordenados = sorted(todos.values(), key=lambda x: x["name"].lower())

    for p in projetos_ordenados:
        pid = p["id"]
        esta_presente = p["filename"] in arquivos_atuais
        var = tk.BooleanVar(value=esta_presente)
        vars_map[pid] = var
        cb = tk.Checkbutton(frame_scroll, text=p["name"], variable=var, font=("Arial", 9))
        cb.pack(anchor="w", padx=4, pady=2)
        widgets_map[pid] = (cb, p["name"].lower())

    def filtrar(evento=None):
        texto = entrada_filtro.get().strip().lower()
        for pid, (cb, nome_p) in widgets_map.items():
            if texto in nome_p:
                cb.pack(anchor="w", padx=4, pady=2)
            else:
                cb.pack_forget()

    entrada_filtro.bind("<KeyRelease>", filtrar)

    frame_rodape = tk.Frame(top, padx=10, pady=10)
    frame_rodape.pack(fill="x")

    def salvar():
        os.makedirs(pasta_proj_perfil, exist_ok=True)
        outside_f = os.path.join(pasta_proj_perfil, "outside-of-project.json")
        if not os.path.exists(outside_f):
            with open(outside_f, "w", encoding="utf-8") as fp:
                json.dump({"id": "outside-of-project", "name": "Outside of Project"}, fp)

        for pid, var in vars_map.items():
            p_info = todos[pid]
            destino = os.path.join(pasta_proj_perfil, p_info["filename"])
            if var.get():
                if not os.path.exists(destino):
                    try:
                        shutil.copy2(p_info["src"], destino)
                    except:
                        pass
            else:
                if os.path.exists(destino):
                    try:
                        os.remove(destino)
                    except:
                        pass
        canvas.unbind_all("<MouseWheel>")
        top.destroy()
        carregar_lista()
        messagebox.showinfo(t("t_sucesso"), t("sucesso_proj", nome=nome))

    btn_salvar = tk.Button(frame_rodape, text=t("btn_salvar"), command=salvar, width=18, bg="#d9d9d9", height=2)
    btn_salvar.pack(side="left", padx=5)

    btn_cancelar = tk.Button(frame_rodape, text=t("btn_cancelar"), command=lambda: (canvas.unbind_all("<MouseWheel>"), top.destroy()), width=12, height=2)
    btn_cancelar.pack(side="right", padx=5)

def atualizar_textos_interface():
    janela.title(t("title"))
    frame_topo.config(text=t("frame_create"))
    lbl_nome.config(text=t("lbl_nome"))
    btn_add.config(text=t("btn_add"))
    chk_copiar.config(text=t("chk_copiar"))
    frame_meio.config(text=t("frame_perfis"))
    btn_abrir.config(text=t("btn_abrir"))
    btn_proj.config(text=t("btn_proj"))
    btn_atalho.config(text=t("btn_atalho"))
    btn_del.config(text=t("btn_del"))
    lbl_idioma.config(text=t("lbl_idioma"))
    carregar_lista()

def mudar_idioma(escolha):
    global idioma_atual
    sigla = IDIOMAS_NOMES.get(escolha, "pt")
    idioma_atual = sigla
    salvar_idioma(sigla)
    atualizar_textos_interface()


def sincronizar_antigravity_para_claude(projeto_especifico=None):
    if not os.path.exists(MASTER_DIR):
        return {"projetos": 0, "conversas": 0}

    claude_data = {}
    if os.path.exists(CLAUDE_JSON_PATH):
        try:
            with open(CLAUDE_JSON_PATH, "r", encoding="utf-8") as f:
                claude_data = json.load(f)
        except:
            claude_data = {}
    if "projects" not in claude_data:
        claude_data["projects"] = {}

    conn = None
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
        except:
            pass

    os.makedirs(CLAUDE_PROJECTS_DIR, exist_ok=True)
    projetos_sincronizados = 0
    conversas_sincronizadas = 0

    todos = obter_todos_projetos()
    for pid, p in todos.items():
        if projeto_especifico and p["id"] != projeto_especifico and p["name"].lower() != str(projeto_especifico).lower():
            continue
        folder = p["path"]
        if not folder or not os.path.exists(folder):
            continue

        if folder not in claude_data["projects"]:
            claude_data["projects"][folder] = {
                "allowedTools": [],
                "mcpContextUris": [],
                "enabledMcpjsonServers": [],
                "disabledMcpjsonServers": [],
                "hasTrustDialogAccepted": True,
                "hasClaudeMdExternalIncludesApproved": False,
                "hasClaudeMdExternalIncludesWarningShown": False
            }
            projetos_sincronizados += 1

        encoded_name = encode_claude_project_dir(folder)
        target_claude_dir = os.path.join(CLAUDE_PROJECTS_DIR, encoded_name)
        os.makedirs(target_claude_dir, exist_ok=True)

        if conn:
            try:
                rows = conn.execute(
                    "SELECT conversation_id, title FROM conversation_summaries WHERE project_id = ?",
                    (pid,)
                ).fetchall()
                for r in rows:
                    cid, title = r
                    target_file = os.path.join(target_claude_dir, f"{cid}.jsonl")
                    sub_title_dir = os.path.join(target_claude_dir, cid)
                    os.makedirs(sub_title_dir, exist_ok=True)
                    clean_title = title if title and not title.startswith("2c5e") else p["name"]
                    title_file = os.path.join(sub_title_dir, "custom-title.json")
                    if not os.path.exists(title_file):
                        with open(title_file, "w", encoding="utf-8") as tf:
                            json.dump({"customTitle": clean_title}, tf)

                    if not os.path.exists(target_file) or os.path.getsize(target_file) == 0:
                        src_transcript = os.path.join(MASTER_AG, "brain", cid, ".system_generated", "logs", "transcript.jsonl")
                        if os.path.exists(src_transcript):
                            claude_lines = []
                            first_prompt = None
                            prev_uuid = None
                            with open(src_transcript, "r", encoding="utf-8") as tf:
                                for line in tf:
                                    try:
                                        sd = json.loads(line)
                                        stype = sd.get("type")
                                        ts = sd.get("created_at", datetime.now().isoformat() + "Z")
                                        if stype == "USER_INPUT":
                                            c = clean_user_text(sd.get("content", ""))
                                            if not c or c.startswith("<SYSTEM_MESSAGE>"):
                                                continue
                                            if first_prompt is None:
                                                first_prompt = c
                                                claude_lines.append(json.dumps({
                                                    "type": "queue-operation",
                                                    "operation": "enqueue",
                                                    "timestamp": ts,
                                                    "sessionId": cid,
                                                    "content": c[:300]
                                                }))
                                                claude_lines.append(json.dumps({
                                                    "type": "queue-operation",
                                                    "operation": "dequeue",
                                                    "timestamp": ts,
                                                    "sessionId": cid
                                                }))
                                            msg_uuid = str(uuid.uuid4())
                                            claude_lines.append(json.dumps({
                                                "parentUuid": prev_uuid,
                                                "isSidechain": False,
                                                "type": "user",
                                                "message": {"role": "user", "content": c},
                                                "uuid": msg_uuid,
                                                "timestamp": ts,
                                                "sessionId": cid,
                                                "cwd": folder
                                            }))
                                            prev_uuid = msg_uuid
                                        elif stype == "PLANNER_RESPONSE":
                                            c = sd.get("content", "")
                                            if not c:
                                                t_calls = sd.get("tool_calls", [])
                                                if t_calls:
                                                    names = [tc.get("name", "tool") for tc in t_calls]
                                                    c = f"Acoes executadas: {', '.join(names)}"
                                            if not c or not prev_uuid:
                                                continue
                                            msg_uuid = str(uuid.uuid4())
                                            claude_lines.append(json.dumps({
                                                "parentUuid": prev_uuid,
                                                "isSidechain": False,
                                                "type": "assistant",
                                                "message": {"role": "assistant", "content": [{"type": "text", "text": c}]},
                                                "uuid": msg_uuid,
                                                "timestamp": ts,
                                                "sessionId": cid,
                                                "cwd": folder
                                            }))
                                            prev_uuid = msg_uuid
                                    except:
                                        pass
                            if claude_lines:
                                if title:
                                    claude_lines.append(json.dumps({
                                        "type": "custom-title",
                                        "customTitle": title,
                                        "sessionId": cid
                                    }))
                                with open(target_file, "w", encoding="utf-8") as out_f:
                                    for cl in claude_lines:
                                        out_f.write(cl + "\n")
                                conversas_sincronizadas += 1
            except:
                pass

    if conn:
        conn.close()

    try:
        with open(CLAUDE_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(claude_data, f, indent=2)
    except:
        pass

    return {"projetos": projetos_sincronizados, "conversas": conversas_sincronizadas}


def sincronizar_claude_para_antigravity(projeto_especifico=None):
    if not os.path.exists(CLAUDE_JSON_PATH):
        return {"projetos": 0, "conversas": 0}

    try:
        with open(CLAUDE_JSON_PATH, "r", encoding="utf-8") as f:
            claude_data = json.load(f)
    except:
        return {"projetos": 0, "conversas": 0}

    claude_projects = claude_data.get("projects", {})
    os.makedirs(MASTER_DIR, exist_ok=True)

    ag_paths = {}
    for f in os.listdir(MASTER_DIR):
        if not f.endswith(".json") or f == "outside-of-project.json":
            continue
        try:
            with open(os.path.join(MASTER_DIR, f), "r", encoding="utf-8") as fp:
                d = json.load(fp)
            res = d.get("projectResources", {}).get("resources", [])
            raw_uri = ""
            if res:
                item = res[0]
                if "folderUri" in item:
                    raw_uri = item["folderUri"]
                elif "gitFolder" in item:
                    raw_uri = item["gitFolder"].get("folderUri", "")
                elif "workspaceUri" in item:
                    raw_uri = item["workspaceUri"]
            if raw_uri:
                folder = urllib.parse.unquote(raw_uri.replace("file:///", "").replace("file://", ""))
                folder = folder.replace("/", "\\")
                if len(folder) > 1 and folder[1] == ":":
                    pass
                elif len(folder) > 2 and folder[2] == ":":
                    folder = folder[1:]
                folder = os.path.normpath(folder)
                ag_paths[folder.lower()] = d.get("id")
        except:
            pass

    conn = None
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
        except:
            pass

    novos_projetos = 0
    conversas_convertidas = 0

    for path in claude_projects.keys():
        norm_path = os.path.normpath(path)
        if not os.path.exists(norm_path):
            continue
        if projeto_especifico and os.path.basename(norm_path).lower() != str(projeto_especifico).lower() and norm_path.lower() != str(projeto_especifico).lower():
            continue

        pid = ag_paths.get(norm_path.lower())
        if not pid:
            pid = str(uuid.uuid4())
            pname = os.path.basename(norm_path)
            folder_uri = f"file:///{norm_path.replace(os.sep, '/')}"
            ag_proj_data = {
                "id": pid,
                "name": pname,
                "projectResources": {
                    "resources": [{"folderUri": folder_uri}]
                },
                "settings": {},
                "isWorkspaceOnly": False
            }
            with open(os.path.join(MASTER_DIR, f"{pid}.json"), "w", encoding="utf-8") as fp:
                json.dump(ag_proj_data, fp, indent=2)
            ag_paths[norm_path.lower()] = pid
            novos_projetos += 1

        encoded_name = encode_claude_project_dir(norm_path)
        claude_dir = os.path.join(CLAUDE_PROJECTS_DIR, encoded_name)
        if os.path.exists(claude_dir):
            for cf in os.listdir(claude_dir):
                if cf.endswith(".jsonl") and not cf.endswith(".desktop-released.json"):
                    session_id = os.path.splitext(cf)[0]
                    ag_transcript = os.path.join(MASTER_AG, "brain", session_id, ".system_generated", "logs", "transcript.jsonl")
                    if not os.path.exists(ag_transcript):
                        cpath = os.path.join(claude_dir, cf)
                        steps = []
                        step_idx = 0
                        title = os.path.basename(norm_path)
                        first_preview = ""
                        last_mtime = ""
                        with open(cpath, "r", encoding="utf-8") as f_in:
                            for line in f_in:
                                try:
                                    sd = json.loads(line)
                                    stype = sd.get("type")
                                    ts = sd.get("timestamp", "")
                                    if ts:
                                        last_mtime = ts
                                    if stype == "custom-title":
                                        title = sd.get("customTitle", title)
                                    elif stype == "user":
                                        msg = sd.get("message", {})
                                        content = msg.get("content", "")
                                        if isinstance(content, list):
                                            parts = [p.get("text", "") for p in content if isinstance(p, dict) and p.get("type") == "text"]
                                            content = "\n".join(parts)
                                        if content:
                                            if not first_preview:
                                                first_preview = content[:80]
                                            steps.append({
                                                "step_index": step_idx,
                                                "source": "USER_EXPLICIT",
                                                "type": "USER_INPUT",
                                                "status": "DONE",
                                                "created_at": ts,
                                                "content": f"<USER_REQUEST>\n{content}\n</USER_REQUEST>"
                                            })
                                            step_idx += 1
                                    elif stype == "assistant":
                                        msg = sd.get("message", {})
                                        content = msg.get("content", "")
                                        if isinstance(content, list):
                                            parts = [p.get("text", "") for p in content if isinstance(p, dict) and p.get("type") == "text"]
                                            content = "\n".join(parts)
                                        if content:
                                            steps.append({
                                                "step_index": step_idx,
                                                "source": "MODEL",
                                                "type": "PLANNER_RESPONSE",
                                                "status": "DONE",
                                                "created_at": ts,
                                                "content": content
                                            })
                                            step_idx += 1
                                except:
                                    pass
                        if steps:
                            os.makedirs(os.path.dirname(ag_transcript), exist_ok=True)
                            with open(ag_transcript, "w", encoding="utf-8") as out_t:
                                for s in steps:
                                    out_t.write(json.dumps(s) + "\n")
                            if conn:
                                folder_uri = f"file:///{norm_path.replace(os.sep, '/')}"
                                uris_json = json.dumps([folder_uri])
                                mtime = last_mtime if last_mtime else datetime.now().isoformat() + "+00:00"
                                conn.execute("""
                                    INSERT OR REPLACE INTO conversation_summaries
                                    (conversation_id, title, preview, step_count, last_modified_time, workspace_uris,
                                     status, source, project_id, agent_name, parent_conversation_id, nesting_depth,
                                     battle_id, winning_conversation_id, not_fully_idle, killed, last_user_input_time,
                                     last_user_input_step_index, app_data_dir, group_id)
                                    VALUES (?, ?, ?, ?, ?, ?, 'CASCADE_RUN_STATUS_IDLE', '', ?, '', '', 0, '', '', 0, 0, ?, 0, 'antigravity', '')
                                """, (session_id, title, first_preview, len(steps), mtime, uris_json, pid, mtime))
                                conn.commit()
                            conversas_convertidas += 1

    if conn:
        conn.close()

    return {"projetos": novos_projetos, "conversas": conversas_convertidas}


def sincronizar_todos_para_chatgpt():
    if not os.path.exists(CODEX_DIR):
        return {"projects": 0, "threads": 0}

    projetos_unificados = {}

    if os.path.exists(MASTER_DIR):
        for f in os.listdir(MASTER_DIR):
            if not f.endswith(".json") or f == "outside-of-project.json":
                continue
            try:
                with open(os.path.join(MASTER_DIR, f), "r", encoding="utf-8") as jf:
                    d = json.load(jf)
                res = d.get("projectResources", {}).get("resources", [])
                raw_uri = ""
                if res:
                    item = res[0]
                    if "folderUri" in item:
                        raw_uri = item["folderUri"]
                    elif "gitFolder" in item:
                        raw_uri = item["gitFolder"].get("folderUri", "")
                    elif "workspaceUri" in item:
                        raw_uri = item["workspaceUri"]
                if raw_uri:
                    folder = urllib.parse.unquote(raw_uri.replace("file:///", "").replace("file://", ""))
                    folder = folder.replace("/", "\\")
                    if len(folder) > 1 and folder[1] == ":":
                        pass
                    elif len(folder) > 2 and folder[2] == ":":
                        folder = folder[1:]
                    folder = os.path.normpath(folder)
                    name = d.get("name") or os.path.basename(folder)
                    k = folder.lower()
                    if k not in projetos_unificados:
                        projetos_unificados[k] = {"name": name, "path": folder, "ag_id": d.get("id", f[:-5])}
            except:
                pass

    if os.path.exists(CLAUDE_JSON_PATH):
        try:
            with open(CLAUDE_JSON_PATH, "r", encoding="utf-8") as jf:
                cdata = json.load(jf)
            for cp in cdata.get("projects", {}).keys():
                p = os.path.normpath(cp.replace("/", "\\"))
                k = p.lower()
                if k not in projetos_unificados:
                    projetos_unificados[k] = {"name": os.path.basename(p), "path": p}
        except:
            pass

    if os.path.exists(CODEX_DB):
        try:
            cconn = sqlite3.connect(CODEX_DB)
            for pid, pos, path in cconn.execute("SELECT project_id, position, path FROM project_roots").fetchall():
                p = os.path.normpath(path.replace("/", "\\"))
                k = p.lower()
                r = cconn.execute("SELECT name FROM projects WHERE id = ?", (pid,)).fetchone()
                pname = r[0] if r else os.path.basename(p)
                if k not in projetos_unificados:
                    projetos_unificados[k] = {"name": pname, "path": p, "codex_pid": pid}
                else:
                    projetos_unificados[k]["codex_pid"] = pid
            cconn.close()
        except:
            pass

    projetos_unificados = {k: v for k, v in projetos_unificados.items() if os.path.exists(v["path"])}

    claude_data = {}
    if os.path.exists(CLAUDE_JSON_PATH):
        try:
            with open(CLAUDE_JSON_PATH, "r", encoding="utf-8") as jf:
                claude_data = json.load(jf)
        except:
            claude_data = {}
    claude_projects = claude_data.setdefault("projects", {})
    for pinfo in projetos_unificados.values():
        folder = pinfo["path"]
        if folder not in claude_projects:
            claude_projects[folder] = {
                "allowedTools": [],
                "mcpContextUris": [],
                "enabledMcpjsonServers": [],
                "disabledMcpjsonServers": [],
                "hasTrustDialogAccepted": True,
                "hasClaudeMdExternalIncludesApproved": False,
                "hasClaudeMdExternalIncludesWarningShown": False
            }
    try:
        with open(CLAUDE_JSON_PATH, "w", encoding="utf-8") as jf:
            json.dump(claude_data, jf, indent=2)
    except:
        pass

    os.makedirs(MASTER_DIR, exist_ok=True)
    existing_ag_paths = set()
    for f in os.listdir(MASTER_DIR):
        if not f.endswith(".json") or f == "outside-of-project.json":
            continue
        try:
            with open(os.path.join(MASTER_DIR, f), "r", encoding="utf-8") as fp:
                d = json.load(fp)
            res = d.get("projectResources", {}).get("resources", [])
            raw_uri = ""
            if res:
                item = res[0]
                if "folderUri" in item:
                    raw_uri = item["folderUri"]
                elif "gitFolder" in item:
                    raw_uri = item["gitFolder"].get("folderUri", "")
                elif "workspaceUri" in item:
                    raw_uri = item["workspaceUri"]
            if raw_uri:
                folder = urllib.parse.unquote(raw_uri.replace("file:///", "").replace("file://", ""))
                folder = os.path.normpath(folder.replace("/", "\\"))
                existing_ag_paths.add(folder.lower())
        except:
            pass

    for pinfo in projetos_unificados.values():
        folder = pinfo["path"]
        if folder.lower() not in existing_ag_paths:
            new_id = str(uuid.uuid4())
            pname = pinfo["name"]
            folder_uri = f"file:///{folder.replace('\\', '/')}"
            ag_proj_data = {
                "id": new_id,
                "name": pname,
                "projectResources": {
                    "resources": [{"folderUri": folder_uri}]
                },
                "settings": {},
                "isWorkspaceOnly": False
            }
            try:
                with open(os.path.join(MASTER_DIR, f"{new_id}.json"), "w", encoding="utf-8") as fp:
                    json.dump(ag_proj_data, fp, indent=2)
                existing_ag_paths.add(folder.lower())
                pinfo["ag_id"] = new_id
            except:
                pass

    novos_projetos = 0
    novas_threads = 0

    if os.path.exists(CODEX_DB):
        conn = sqlite3.connect(CODEX_DB)
        existing_roots = {}
        for pid, pos, path in conn.execute("SELECT project_id, position, path FROM project_roots").fetchall():
            existing_roots[os.path.normpath(path.replace("/", "\\")).lower()] = pid

        r = conn.execute("SELECT MAX(position) FROM projects").fetchone()
        current_pos = (r[0] if r and r[0] is not None else 0) + 1
        now_ms = int(time.time() * 1000)
        now_sec = int(time.time())
        paths_to_trust = []

        for pinfo in projetos_unificados.values():
            folder = pinfo["path"]
            k = folder.lower()
            if k not in existing_roots:
                new_pid = str(uuid.uuid4())
                conn.execute(
                    "INSERT INTO projects (id, name, metadata, position, created_at_ms, updated_at_ms) VALUES (?, ?, '{}', ?, ?, ?)",
                    (new_pid, pinfo["name"], current_pos, now_ms, now_ms)
                )
                conn.execute(
                    "INSERT INTO project_roots (project_id, position, path) VALUES (?, 0, ?)",
                    (new_pid, folder)
                )
                existing_roots[k] = new_pid
                pinfo["codex_pid"] = new_pid
                current_pos += 1
                novos_projetos += 1
                paths_to_trust.append(folder)
            else:
                pinfo["codex_pid"] = existing_roots[k]

        existing_threads = set(r[0] for r in conn.execute("SELECT id FROM threads").fetchall())

        ag_rows = []
        if os.path.exists(DB_PATH):
            try:
                conn_ag = sqlite3.connect(DB_PATH)
                ag_rows = conn_ag.execute("SELECT conversation_id, title, preview, last_modified_time, project_id FROM conversation_summaries").fetchall()
                conn_ag.close()
            except:
                ag_rows = []

        ag_id_to_pinfo = {pinfo.get("ag_id"): pinfo for pinfo in projetos_unificados.values() if pinfo.get("ag_id")}

        for cid, title, preview, mtime, pid in ag_rows:
            if cid in existing_threads:
                continue
            pinfo = ag_id_to_pinfo.get(pid)
            if not pinfo:
                continue
            folder = pinfo["path"]
            clean_title = title if title and not title.startswith("2c5e") else pinfo["name"]
            first_msg = preview if preview else clean_title

            today_str = datetime.now().strftime("%Y\\%m\\%d")
            rollout_dir = os.path.join(CODEX_DIR, "sessions", today_str)
            os.makedirs(rollout_dir, exist_ok=True)
            rollout_filename = f"rollout-{datetime.now().strftime('%Y-%m-%dT%H-%M-%S')}-{cid}.jsonl"
            rollout_path = os.path.normpath(os.path.join(rollout_dir, rollout_filename))

            try:
                with open(rollout_path, "w", encoding="utf-8") as rf:
                    rf.write(json.dumps({
                        "timestamp": datetime.now().isoformat() + "Z",
                        "ordinal": 0,
                        "type": "session_meta",
                        "payload": {
                            "session_id": cid,
                            "id": cid,
                            "timestamp": datetime.now().isoformat() + "Z",
                            "cwd": f"\\\\?\\{folder}",
                            "originator": "Codex Desktop",
                            "cli_version": "0.158.0-alpha.2"
                        }
                    }) + "\n")
                    rf.write(json.dumps({
                        "timestamp": datetime.now().isoformat() + "Z",
                        "ordinal": 1,
                        "type": "event_msg",
                        "payload": {
                            "type": "task_started",
                            "turn_id": "turn-1",
                            "started_at": now_sec
                        }
                    }) + "\n")

                codex_project_id = pinfo["codex_pid"]
                conn.execute("""
                    INSERT INTO threads (
                        id, rollout_path, created_at, updated_at, source, model_provider, cwd,
                        title, sandbox_policy, approval_mode, tokens_used, has_user_event, archived,
                        cli_version, first_user_message, memory_mode, model, preview,
                        recency_at, recency_at_ms, history_mode, name, is_pinned,
                        project_id, originator
                    ) VALUES (
                        ?, ?, ?, ?, 'vscode', 'openai', ?,
                        ?, '{"type":"managed"}', 'on-request', 100, 1, 0,
                        '0.158.0-alpha.2', ?, 'enabled', 'gpt-6-astra', ?,
                        ?, ?, 'paginated', ?, 0,
                        ?, 'Codex Desktop'
                    )
                """, (
                    cid, f"\\\\?\\{rollout_path}", now_sec, now_sec, f"\\\\?\\{folder}",
                    clean_title, first_msg, first_msg,
                    now_sec, now_ms, clean_title,
                    codex_project_id
                ))
                existing_threads.add(cid)
                novas_threads += 1
            except:
                pass

        conn.commit()
        conn.close()

        if os.path.exists(CODEX_CONFIG) and paths_to_trust:
            try:
                with open(CODEX_CONFIG, "r", encoding="utf-8") as f:
                    content = f.read()
                new_sections = []
                for p in paths_to_trust:
                    sec_header = f"[projects.'{p.lower()}']"
                    if sec_header not in content.lower():
                        new_sections.append(f"\n[projects.'{p}']\ntrust_level = \"trusted\"")
                if new_sections:
                    with open(CODEX_CONFIG, "a", encoding="utf-8") as f:
                        f.write("\n".join(new_sections) + "\n")
            except:
                pass

    if os.path.exists(CODEX_GLOBAL_STATE):
        try:
            with open(CODEX_GLOBAL_STATE, "r", encoding="utf-8") as f:
                state = json.load(f)

            now_ms = int(time.time() * 1000)
            local_projects = state.setdefault("local-projects", {})
            project_order = state.setdefault("project-order", [])
            host_key = r"local:C:\Users\tokugawa\.codex"
            host_map = state.setdefault("app-server-project-id-by-legacy-project-id-by-host", {}).setdefault(host_key, {})
            thread_assign = state.setdefault("thread-project-assignments", {})
            thread_hosts = state.setdefault("thread-project-membership-host-ids", {})
            thread_roots = state.setdefault("thread-writable-roots", {})
            sidebar_orders = state.setdefault("sidebar-project-thread-orders", {})

            reverse_host_map = {v: k for k, v in host_map.items()}

            existing_lp_paths = {}
            for leg_id, pdata in local_projects.items():
                for r in pdata.get("rootPaths", []):
                    existing_lp_paths[os.path.normpath(r.replace("/", "\\")).lower()] = leg_id

            for pinfo in projetos_unificados.values():
                folder = pinfo["path"]
                k = folder.lower()
                codex_pid = pinfo.get("codex_pid", str(uuid.uuid4()))

                if k in existing_lp_paths:
                    leg_id = existing_lp_paths[k]
                else:
                    leg_id = reverse_host_map.get(codex_pid, codex_pid)
                    local_projects[leg_id] = {
                        "id": leg_id,
                        "name": pinfo["name"],
                        "rootPaths": [folder],
                        "createdAt": now_ms,
                        "updatedAt": now_ms
                    }
                    existing_lp_paths[k] = leg_id
                    if leg_id not in project_order:
                        project_order.append(leg_id)
                    host_map[leg_id] = codex_pid
                    reverse_host_map[codex_pid] = leg_id

            if os.path.exists(CODEX_DB):
                conn = sqlite3.connect(CODEX_DB)
                threads_db = conn.execute("SELECT id, project_id, cwd FROM threads").fetchall()
                conn.close()

                for tid, t_pid, t_cwd in threads_db:
                    if not t_pid and t_cwd:
                        clean_cwd = t_cwd
                        if clean_cwd.startswith("\\\\?\\"):
                            clean_cwd = clean_cwd[4:]
                        norm_cwd = os.path.normpath(clean_cwd.replace("/", "\\")).lower()
                        if norm_cwd in existing_lp_paths:
                            leg_id = existing_lp_paths[norm_cwd]
                            t_pid = host_map.get(leg_id)

                    if t_pid:
                        leg_id = reverse_host_map.get(t_pid, t_pid)
                        thread_assign[tid] = {
                            "projectKind": "local",
                            "projectId": leg_id
                        }
                        thread_hosts[tid] = "local"
                        thread_roots[tid] = [t_cwd]
                        sidebar_orders.setdefault(leg_id, [])
                        if tid not in sidebar_orders[leg_id]:
                            sidebar_orders[leg_id].append(tid)

            with open(CODEX_GLOBAL_STATE, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
        except:
            pass

    return {"projects": novos_projetos, "threads": novas_threads}


janela = tk.Tk()
janela.geometry("500x510")
janela.resizable(False, False)

ico_caminho = os.path.join(BASE_DIR, "icon.ico")
if os.path.exists(ico_caminho):
    try:
        janela.iconbitmap(ico_caminho)
    except:
        pass
elif os.path.exists(EXE_PATH):
    try:
        janela.iconbitmap(EXE_PATH)
    except:
        pass

frame_idioma = tk.Frame(janela, padx=10, pady=5)
frame_idioma.pack(fill="x")

lbl_idioma = tk.Label(frame_idioma, text=t("lbl_idioma"), font=("Arial", 9))
lbl_idioma.pack(side="left")

var_idioma = tk.StringVar(janela)
nome_inverso = {v: k for k, v in IDIOMAS_NOMES.items()}
var_idioma.set(nome_inverso.get(idioma_atual, "Português"))

opt_idioma = tk.OptionMenu(frame_idioma, var_idioma, *IDIOMAS_NOMES.keys(), command=mudar_idioma)
opt_idioma.config(font=("Arial", 9), width=12)
opt_idioma.pack(side="left", padx=5)

frame_topo = tk.LabelFrame(janela, text=t("frame_create"), padx=10, pady=10)
frame_topo.pack(padx=10, pady=5, fill="x")

lbl_nome = tk.Label(frame_topo, text=t("lbl_nome"))
lbl_nome.grid(row=0, column=0, sticky="w")

entrada_nome = tk.Entry(frame_topo, width=28)
entrada_nome.grid(row=0, column=1, padx=5)

btn_add = tk.Button(frame_topo, text=t("btn_add"), command=criar_perfil, width=10)
btn_add.grid(row=0, column=2, padx=5)

var_copiar_tudo = tk.BooleanVar(value=False)
chk_copiar = tk.Checkbutton(frame_topo, text=t("chk_copiar"), variable=var_copiar_tudo)
chk_copiar.grid(row=1, column=0, columnspan=3, sticky="w", pady=(6, 0))

frame_meio = tk.LabelFrame(janela, text=t("frame_perfis"), padx=10, pady=10)
frame_meio.pack(padx=10, pady=5, fill="both", expand=True)

scrollbar = tk.Scrollbar(frame_meio)
scrollbar.pack(side="right", fill="y")

lista = tk.Listbox(frame_meio, yscrollcommand=scrollbar.set, font=("Arial", 10), height=7)
lista.pack(side="left", fill="both", expand=True)
scrollbar.config(command=lista.yview)

frame_botoes = tk.Frame(janela, padx=10, pady=5)
frame_botoes.pack(fill="x")

btn_abrir = tk.Button(frame_botoes, text=t("btn_abrir"), command=abrir_perfil, height=2, bg="#d9d9d9")
btn_abrir.pack(fill="x", pady=2)

btn_proj = tk.Button(frame_botoes, text=t("btn_proj"), command=gerenciar_projetos, height=1)
btn_proj.pack(fill="x", pady=2)

btn_atalho = tk.Button(frame_botoes, text=t("btn_atalho"), command=criar_atalho)
btn_atalho.pack(fill="x", pady=2)

btn_del = tk.Button(frame_botoes, text=t("btn_del"), command=excluir_perfil)
btn_del.pack(fill="x", pady=2)

atualizar_textos_interface()
janela.mainloop()
