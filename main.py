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
        "title": "MultiGravity - Universal AI Hub & Profile Manager",
        "tab_perfis": "Perfis Antigravity",
        "tab_projetos": "Central de Projetos (Hub)",
        "tab_ponte": "Ponte de Memória & Sincronizador",
        "frame_create": "Criar Novo Perfil",
        "lbl_nome": "Nome:",
        "btn_add": "Adicionar",
        "chk_copiar": "Compartilhar todos os projetos neste novo perfil",
        "frame_perfis": "Perfis Cadastrados",
        "btn_abrir": "Abrir Perfil Selecionado",
        "btn_proj": "Compartilhar Projetos do Perfil",
        "btn_atalho": "Criar Atalho na Area de Trabalho",
        "btn_del": "Excluir Perfil",
        "lbl_idioma": "Idioma:",
        "projetos_sufixo": "projetos",
        "conversas_sufixo": "conversas",
        "aviso_selecao": "Selecione um perfil na lista!",
        "aviso_selecao_proj": "Selecione um projeto na lista!",
        "aviso_nome": "Digite um nome para o perfil!",
        "aviso_nome_invalido": "Nome invalido! Nao use caracteres especiais (< > : \" / \\ | ? *) nem termine com espaco ou ponto.",
        "erro_existe": "Ja existe um perfil com esse nome!",
        "sucesso_criado": "Perfil '{nome}' criado com sucesso!",
        "sucesso_atalho": "Atalho criado na Area de Trabalho:\nAntigravity - {nome}.lnk",
        "confirma_del": "Tem certeza que deseja apagar o perfil '{nome}' e todos os dados dele?",
        "top_titulo": "Compartilhar Projetos - {nome}",
        "top_aviso": "Selecione os projetos visiveis para: {nome}",
        "filtrar": "Filtrar Projetos:",
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
        "t_info": "Info",
        "lbl_acoes_ia": "Acoes para o Projeto Selecionado:",
        "btn_abrir_ag": "Abrir no Antigravity",
        "btn_abrir_claude": "Abrir no Claude Desktop",
        "btn_abrir_chatgpt": "Abrir no ChatGPT Desktop",
        "btn_abrir_pasta": "Abrir Pasta no Explorer",
        "lbl_perfil_alvo": "Perfil:",
        "lbl_status_detect": "Status das IAs:",
        "status_instalado": "Instalado",
        "status_nao_encontrado": "Nao Detectado",
        "lbl_selecione_proj": "Selecione um projeto na lista acima.",
        "btn_copiar_ctx": "Copiar Contexto para Clipboard (Prompt Pronto)",
        "btn_exportar_ctx": "Salvar .ai-context.md na Pasta do Projeto",
        "btn_atualizar_ctx": "Atualizar Pre-visualizacao",
        "sucesso_copiado": "Contexto copiado para a Area de Transferencia!\nBasta colar (Ctrl+V) no Claude ou ChatGPT.",
        "sucesso_exportado": "Arquivo .ai-context.md criado com sucesso em:\n{caminho}",
        "erro_sem_pasta": "Este projeto nao possui pasta fisica vinculada no disco.",
        "preview_titulo": "Pre-visualizacao do Contexto Compartilhado:",
        "lbl_caminho_proj": "Caminho no Disco:",
        "lbl_conversas_proj": "Total de Conversas:",
        "lbl_projeto_topo": "Projeto:",
        "btn_sync_universal": "Sincronizar Todos os Projetos & Chats (Antigravity <-> Claude <-> ChatGPT)",
        "btn_sync_este_proj": "Sincronizar Chats Deste Projeto com Claude & ChatGPT",
        "sucesso_sync": "Sincronizacao universal concluida!\n\n- Antigravity -> Claude: {p_ag} projetos, {c_ag} conversas.\n- Claude -> Antigravity: {p_cl} projetos, {c_cl} conversas.\n- ChatGPT / Codex: {p_gpt} projetos, {c_gpt} conversas sincronizadas.\n\nTodos os modelos agora compartilham todos os projetos e chats!",
        "sucesso_sync_proj": "Chats do projeto '{nome}' sincronizados com sucesso entre Antigravity, Claude e ChatGPT!"
    },
    "en": {
        "title": "MultiGravity - Universal AI Hub & Profile Manager",
        "tab_perfis": "Antigravity Profiles",
        "tab_projetos": "Projects Hub",
        "tab_ponte": "Cross-AI Memory & Sync",
        "frame_create": "Create New Profile",
        "lbl_nome": "Name:",
        "btn_add": "Add",
        "chk_copiar": "Share all projects in this new profile",
        "frame_perfis": "Registered Profiles",
        "btn_abrir": "Open Selected Profile",
        "btn_proj": "Share Profile Projects",
        "btn_atalho": "Create Desktop Shortcut",
        "btn_del": "Delete Profile",
        "lbl_idioma": "Language:",
        "projetos_sufixo": "projects",
        "conversas_sufixo": "conversations",
        "aviso_selecao": "Select a profile from the list!",
        "aviso_selecao_proj": "Select a project from the list!",
        "aviso_nome": "Enter a name for the profile!",
        "aviso_nome_invalido": "Invalid profile name! Do not use special characters (< > : \" / \\ | ? *) or trailing spaces/dots.",
        "erro_existe": "A profile with this name already exists!",
        "sucesso_criado": "Profile '{nome}' created successfully!",
        "sucesso_atalho": "Shortcut created on Desktop:\nAntigravity - {nome}.lnk",
        "confirma_del": "Are you sure you want to delete profile '{nome}' and all its data?",
        "top_titulo": "Share Projects - {nome}",
        "top_aviso": "Select visible projects for: {nome}",
        "filtrar": "Filter Projects:",
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
        "t_info": "Info",
        "lbl_acoes_ia": "Actions for Selected Project:",
        "btn_abrir_ag": "Open in Antigravity",
        "btn_abrir_claude": "Open in Claude Desktop",
        "btn_abrir_chatgpt": "Open in ChatGPT Desktop",
        "btn_abrir_pasta": "Open Folder in Explorer",
        "lbl_perfil_alvo": "Profile:",
        "lbl_status_detect": "AI Apps Status:",
        "status_instalado": "Installed",
        "status_nao_encontrado": "Not Detected",
        "lbl_selecione_proj": "Select a project from the list above.",
        "btn_copiar_ctx": "Copy Context to Clipboard (Ready Prompt)",
        "btn_exportar_ctx": "Save .ai-context.md in Project Folder",
        "btn_atualizar_ctx": "Refresh Preview",
        "sucesso_copiado": "Context copied to Clipboard!\nPress Ctrl+V in Claude or ChatGPT.",
        "sucesso_exportado": "File .ai-context.md created successfully at:\n{caminho}",
        "erro_sem_pasta": "This project has no local folder linked on disk.",
        "preview_titulo": "Shared Context Preview:",
        "lbl_caminho_proj": "Disk Path:",
        "lbl_conversas_proj": "Total Conversations:",
        "lbl_projeto_topo": "Project:",
        "btn_sync_universal": "Sync All Projects & Chats (Antigravity <-> Claude <-> ChatGPT)",
        "btn_sync_este_proj": "Sync This Project's Chats with Claude & ChatGPT",
        "sucesso_sync": "Universal sync completed!\n\n- Antigravity -> Claude: {p_ag} projects, {c_ag} chats.\n- Claude -> Antigravity: {p_cl} projects, {c_cl} chats.\n- ChatGPT / Codex: {p_gpt} projects, {c_gpt} chats.\n\nAll AI models now share all projects and conversations!",
        "sucesso_sync_proj": "Chats for project '{nome}' synced successfully between Antigravity, Claude, and ChatGPT!"
    },
    "es": {
        "title": "MultiGravity - Universal AI Hub & Profile Manager",
        "tab_perfis": "Perfiles Antigravity",
        "tab_projetos": "Central de Proyectos (Hub)",
        "tab_ponte": "Puente de Memoria y Sincronizador",
        "frame_create": "Crear Nuevo Perfil",
        "lbl_nome": "Nombre:",
        "btn_add": "Agregar",
        "chk_copiar": "Compartir todos los proyectos en este nuevo perfil",
        "frame_perfis": "Perfiles Registrados",
        "btn_abrir": "Abrir Perfil Seleccionado",
        "btn_proj": "Compartir Proyectos del Perfil",
        "btn_atalho": "Crear Acceso Directo en el Escritorio",
        "btn_del": "Eliminar Perfil",
        "lbl_idioma": "Idioma:",
        "projetos_sufixo": "proyectos",
        "conversas_sufixo": "conversaciones",
        "aviso_selecao": "¡Selecciona un perfil de la lista!",
        "aviso_selecao_proj": "¡Selecciona un proyecto de la lista!",
        "aviso_nome": "¡Introduce un nombre para el perfil!",
        "aviso_nome_invalido": "¡Nombre de perfil no valido! No use caracteres especiales (< > : \" / \\ | ? *) ni espacios o puntos finales.",
        "erro_existe": "¡Ya existe un perfil con ese nombre!",
        "sucesso_criado": "¡Perfil '{nome}' creado con exito!",
        "sucesso_atalho": "Acceso directo creado en el Escritorio:\nAntigravity - {nome}.lnk",
        "confirma_del": "¿Estas seguro de que deseas eliminar el perfil '{nome}' y todos sus datos?",
        "top_titulo": "Compartir Proyectos - {nome}",
        "top_aviso": "Selecciona los proyectos visibles para: {nome}",
        "filtrar": "Filtrar Proyectos:",
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
        "t_info": "Info",
        "lbl_acoes_ia": "Acciones para el Proyecto Seleccionado:",
        "btn_abrir_ag": "Abrir en Antigravity",
        "btn_abrir_claude": "Abrir en Claude Desktop",
        "btn_abrir_chatgpt": "Abrir en ChatGPT Desktop",
        "btn_abrir_pasta": "Abrir Carpeta en el Explorador",
        "lbl_perfil_alvo": "Perfil:",
        "lbl_status_detect": "Estado de las IAs:",
        "status_instalado": "Instalado",
        "status_nao_encontrado": "No Detectado",
        "lbl_selecione_proj": "Seleccione un proyecto en la lista superior.",
        "btn_copiar_ctx": "Copiar Contexto al Portapapeles (Prompt Listo)",
        "btn_exportar_ctx": "Guardar .ai-context.md en Carpeta del Proyecto",
        "btn_atualizar_ctx": "Actualizar Vista Previa",
        "sucesso_copiado": "¡Contexto copiado al portapapeles!\nPresione Ctrl+V en Claude o ChatGPT.",
        "sucesso_exportado": "Archivo .ai-context.md creado con exito en:\n{caminho}",
        "erro_sem_pasta": "Este proyecto no tiene carpeta fisica vinculada en el disco.",
        "preview_titulo": "Vista Previa del Contexto Compartido:",
        "lbl_caminho_proj": "Ruta en Disco:",
        "lbl_conversas_proj": "Total de Conversaciones:",
        "lbl_projeto_topo": "Proyecto:",
        "btn_sync_universal": "Sincronizar Todos los Proyectos y Chats (Antigravity <-> Claude <-> ChatGPT)",
        "btn_sync_este_proj": "Sincronizar Chats de Este Proyecto con Claude y ChatGPT",
        "sucesso_sync": "¡Sincronizacion universal completada!\n\n- Antigravity -> Claude: {p_ag} proyectos, {c_ag} chats.\n- Claude -> Antigravity: {p_cl} proyectos, {c_cl} chats.\n- ChatGPT / Codex: {p_gpt} proyectos, {c_gpt} chats.\n\n¡Todos los modelos ahora comparten todos los proyectos y chats!",
        "sucesso_sync_proj": "¡Chats del proyecto '{nome}' sincronizados con exito entre Antigravity, Claude y ChatGPT!"
    },
    "ru": {
        "title": "MultiGravity - Universal AI Hub & Profile Manager",
        "tab_perfis": "Профили Antigravity",
        "tab_projetos": "Центр проектов (Hub)",
        "tab_ponte": "Мост памяти и синхронизация",
        "frame_create": "Создать новый профиль",
        "lbl_nome": "Имя:",
        "btn_add": "Добавить",
        "chk_copiar": "Поделиться всеми проектами в новом профиле",
        "frame_perfis": "Зарегистрированные профили",
        "btn_abrir": "Открыть выбранный профиль",
        "btn_proj": "Управление проектами профиля",
        "btn_atalho": "Создать ярлык на рабочем столе",
        "btn_del": "Удалить профиль",
        "lbl_idioma": "Язык:",
        "projetos_sufixo": "проектов",
        "conversas_sufixo": "бесед",
        "aviso_selecao": "Выберите профиль из списка!",
        "aviso_selecao_proj": "Выберите проект из списка!",
        "aviso_nome": "Введите имя для профиля!",
        "aviso_nome_invalido": "Недопустимое имя профиля! Не используйте специальные символы (< > : \" / \\ | ? *) или пробелы/точки в конце.",
        "erro_existe": "Профиль с таким именем уже существует!",
        "sucesso_criado": "Профиль '{nome}' успешно создан!",
        "sucesso_atalho": "Ярлык создан на рабочем столе:\nAntigravity - {nome}.lnk",
        "confirma_del": "Вы уверены, что хотите удалить профиль '{nome}' и все его данные?",
        "top_titulo": "Управление проектами - {nome}",
        "top_aviso": "Выберите проекты, доступные для: {nome}",
        "filtrar": "Фильтр проектов:",
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
        "t_info": "Информация",
        "lbl_acoes_ia": "Действия для выбранного проекта:",
        "btn_abrir_ag": "Открыть в Antigravity",
        "btn_abrir_claude": "Открыть в Claude Desktop",
        "btn_abrir_chatgpt": "Открыть в ChatGPT Desktop",
        "btn_abrir_pasta": "Открыть папку в Проводнике",
        "lbl_perfil_alvo": "Профиль:",
        "lbl_status_detect": "Статус приложений ИИ:",
        "status_instalado": "Установлено",
        "status_nao_encontrado": "Не найдено",
        "lbl_selecione_proj": "Выберите проект в списке выше.",
        "btn_copiar_ctx": "Копировать контекст в буфер (готовый промпт)",
        "btn_exportar_ctx": "Сохранить .ai-context.md в папке проекта",
        "btn_atualizar_ctx": "Обновить предпросмотр",
        "sucesso_copiado": "Контекст скопирован в буфер обмена!\nНажмите Ctrl+V в Claude или ChatGPT.",
        "sucesso_exportado": "Файл .ai-context.md успешно создан:\n{caminho}",
        "erro_sem_pasta": "У этого проекта нет привязанной папки на диске.",
        "preview_titulo": "Предпросмотр общего контекста:",
        "lbl_caminho_proj": "Путь на диске:",
        "lbl_conversas_proj": "Всего бесед:",
        "lbl_projeto_topo": "Проект:",
        "btn_sync_universal": "Синхронизировать все проекты и чаты (Antigravity <-> Claude <-> ChatGPT)",
        "btn_sync_este_proj": "Синхронизировать чаты этого проекта с Claude и ChatGPT",
        "sucesso_sync": "Универсальная синхронизация завершена!\n\n- Antigravity -> Claude: {p_ag} проектов, {c_ag} чатов.\n- Claude -> Antigravity: {p_cl} проектов, {c_cl} чатов.\n- ChatGPT / Codex: {p_gpt} проектов, {c_gpt} чатов.\n\nВсе модели теперь имеют доступ ко всем проектам и чатам!",
        "sucesso_sync_proj": "Чаты проекта '{nome}' успешно синхронизированы между Antigravity, Claude и ChatGPT!"
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
    if not os.path.exists(MASTER_AG):
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
        subprocess.run(["cmd", "/c", "mklink", "/J", ag_dir, MASTER_AG], capture_output=True)
    except:
        pass
    if not os.path.exists(ag_dir):
        try:
            os.makedirs(ag_dir, exist_ok=True)
            for f in ["conversation_summaries.db", "antigravity_state.pbtxt"]:
                src = os.path.join(MASTER_AG, f)
                if os.path.exists(src):
                    shutil.copy2(src, os.path.join(ag_dir, f))
            for d in ["conversations", "brain"]:
                src = os.path.join(MASTER_AG, d)
                dst = os.path.join(ag_dir, d)
                if os.path.exists(src) and not os.path.exists(dst):
                    shutil.copytree(src, dst)
        except:
            pass

def validar_nome_perfil(nome):
    if not nome:
        return False
    if re.search(r'[<>:"/\\|?*]', nome):
        return False
    if nome.endswith(".") or nome.endswith(" "):
        return False
    return True

def obter_nomes_perfis():
    res = []
    if os.path.exists(PROFILES_DIR):
        for pasta in sorted(os.listdir(PROFILES_DIR)):
            c = os.path.join(PROFILES_DIR, pasta)
            if os.path.isdir(c):
                res.append(pasta)
    return res

def obter_todos_projetos():
    projetos = {}
    pastas = [MASTER_DIR]
    if os.path.exists(PROFILES_DIR):
        for p in os.listdir(PROFILES_DIR):
            d = os.path.join(PROFILES_DIR, p, "home", ".gemini", "config", "projects")
            if os.path.exists(d):
                pastas.append(d)
    conn = None
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
        except:
            conn = None

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
                        folder = ""
                        res = dados.get("projectResources", {}).get("resources", [])
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

                        chat_count = 0
                        if conn:
                            try:
                                r = conn.execute("SELECT COUNT(*) FROM conversation_summaries WHERE project_id = ?", (pid,)).fetchone()
                                chat_count = r[0] if r else 0
                            except:
                                pass

                        if pid not in projetos:
                            projetos[pid] = {
                                "id": pid,
                                "name": nome,
                                "filename": f,
                                "src": caminho,
                                "path": folder,
                                "chats": chat_count
                            }
                except:
                    pass
    if conn:
        try:
            conn.close()
        except:
            pass
    return projetos

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

def executar_sincronizacao_universal():
    res1 = sincronizar_antigravity_para_claude()
    res2 = sincronizar_claude_para_antigravity()
    res3 = sincronizar_todos_para_chatgpt()
    carregar_lista_projetos()
    messagebox.showinfo(
        t("t_sucesso"),
        t(
            "sucesso_sync",
            p_ag=res1["projetos"],
            c_ag=res1["conversas"],
            p_cl=res2["projetos"],
            c_cl=res2["conversas"],
            p_gpt=res3["projects"],
            c_gpt=res3["threads"]
        )
    )

def executar_sincronizacao_projeto_atual():
    if not PROJETO_SELECIONADO:
        messagebox.showwarning(t("t_aviso"), t("aviso_selecao_proj"))
        return
    pid = PROJETO_SELECIONADO.get("id")
    pname = PROJETO_SELECIONADO.get("name")
    sincronizar_antigravity_para_claude(pid)
    sincronizar_claude_para_antigravity(pname)
    sincronizar_todos_para_chatgpt()
    carregar_lista_projetos()
    messagebox.showinfo(t("t_sucesso"), t("sucesso_sync_proj", nome=pname))

def gerar_contexto_markdown(project_id):
    todos = obter_todos_projetos()
    p_info = todos.get(project_id)
    if not p_info:
        for p in todos.values():
            if p["name"].lower() == str(project_id).lower():
                p_info = p
                project_id = p["id"]
                break
    if not p_info:
        return t("erro_sem_pasta")

    pname = p_info["name"]
    ppath = p_info["path"]
    total_chats = p_info["chats"]

    linhas = []
    linhas.append(f"# AI Context Bridge: {pname}")
    linhas.append(f"- Diretório Local: {ppath if ppath else 'Nao vinculado'}")
    linhas.append(f"- Total de Conversas no Antigravity: {total_chats}")
    linhas.append(f"- Sincronizado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    linhas.append("")
    linhas.append("## Resumo Recente e Atividades Realizadas")

    if not os.path.exists(DB_PATH):
        linhas.append("Banco de conversas do Antigravity nao encontrado.")
        return "\n".join(linhas)

    try:
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute(
            "SELECT conversation_id, title, preview, last_modified_time FROM conversation_summaries WHERE project_id = ? ORDER BY last_modified_time DESC LIMIT 4",
            (project_id,)
        ).fetchall()
        conn.close()
    except:
        rows = []

    if not rows:
        linhas.append("Nenhuma sessao anterior registrada para este projeto.")
        return "\n".join(linhas)

    for r in rows:
        cid, title, preview, mtime = r
        clean_title = title if title and len(title) > 2 and not title.startswith("2c5e") else "Sessao de Desenvolvimento"
        data_str = mtime[:10] if mtime else ""
        linhas.append(f"### {clean_title} ({data_str})")

        t_path = os.path.join(MASTER_AG, "brain", cid, ".system_generated", "logs", "transcript.jsonl")
        if os.path.exists(t_path):
            user_prompts = []
            files_touched = set()
            try:
                with open(t_path, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            d = json.loads(line)
                            stype = d.get("type")
                            if stype == "USER_INPUT":
                                c = clean_user_text(d.get("content", ""))
                                if c and not c.startswith("<SYSTEM_MESSAGE>") and len(c) > 3:
                                    user_prompts.append(c)
                            elif stype == "PLANNER_RESPONSE":
                                t_calls = d.get("tool_calls", [])
                                for tc in t_calls:
                                    args = tc.get("args", {})
                                    for k in ["TargetFile", "AbsolutePath"]:
                                        if k in args:
                                            files_touched.add(os.path.basename(args[k]))
                        except:
                            pass
            except:
                pass

            if user_prompts:
                linhas.append("**Solicitacoes do usuario:**")
                for u in user_prompts[-3:]:
                    primeira_linha = u.split("\n")[0].strip()
                    linhas.append(f"- {primeira_linha[:140]}")
            if files_touched:
                arquivos_str = ", ".join(sorted(files_touched)[:6])
                linhas.append(f"**Arquivos trabalhados:** `{arquivos_str}`")
        linhas.append("")

    linhas.append("## Instrucoes para Claude Desktop / ChatGPT")
    linhas.append("Voce esta trabalhando neste mesmo projeto. Utilize o historico de tarefas e contexto acima para manter coerencia com o trabalho ja realizado no Antigravity.")
    return "\n".join(linhas)

def executar_antigravity(nome_perfil, pasta_alvo=None):
    if not nome_perfil:
        perfis = obter_nomes_perfis()
        if perfis:
            nome_perfil = perfis[0]
        else:
            nome_perfil = "Default"

    pasta_perfil = os.path.join(PROFILES_DIR, nome_perfil)
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
    if pasta_alvo and os.path.exists(pasta_alvo):
        cmd.append(pasta_alvo)

    subprocess.Popen(
        cmd,
        env=env,
        cwd=os.path.dirname(EXE_PATH),
        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
    )

def executar_claude(pasta_alvo=None):
    cmd = ["explorer.exe", f"shell:appsFolder\\{CLAUDE_PKG}!Claude"]
    subprocess.Popen(cmd)
    if pasta_alvo and os.path.exists(pasta_alvo):
        try:
            sincronizar_antigravity_para_claude(os.path.basename(pasta_alvo))
            ctx = gerar_contexto_markdown(os.path.basename(pasta_alvo))
            janela.clipboard_clear()
            janela.clipboard_append(ctx)
            messagebox.showinfo(
                t("t_info"),
                f"Claude Desktop aberto!\n\nOs chats e o contexto de '{os.path.basename(pasta_alvo)}' foram sincronizados e copiados para sua Area de Transferencia.\nBasta pressionar Ctrl+V no chat do Claude."
            )
        except:
            pass

def executar_chatgpt(pasta_alvo=None):
    cmd = ["explorer.exe", f"shell:appsFolder\\{CHATGPT_PKG}!App"]
    subprocess.Popen(cmd)
    if pasta_alvo and os.path.exists(pasta_alvo):
        try:
            sincronizar_antigravity_para_claude(os.path.basename(pasta_alvo))
            sincronizar_todos_para_chatgpt()
            ctx = gerar_contexto_markdown(os.path.basename(pasta_alvo))
            janela.clipboard_clear()
            janela.clipboard_append(ctx)
            messagebox.showinfo(
                t("t_info"),
                f"ChatGPT Desktop aberto!\n\nOs chats e o contexto de '{os.path.basename(pasta_alvo)}' foram sincronizados e copiados para sua Area de Transferencia.\nBasta pressionar Ctrl+V no chat do ChatGPT."
            )
        except:
            pass

def abrir_pasta_explorer(caminho):
    if caminho and os.path.exists(caminho):
        os.startfile(caminho)
    else:
        messagebox.showwarning(t("t_aviso"), t("erro_sem_pasta"))

janela = tk.Tk()
janela.geometry("650x670")
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

frame_cabecalho = tk.Frame(janela, padx=10, pady=6)
frame_cabecalho.pack(fill="x")

frame_status_ias = tk.Frame(frame_cabecalho)
frame_status_ias.pack(side="left")

tem_ag = os.path.exists(EXE_PATH)
tem_claude = is_claude_installed()
tem_chatgpt = is_chatgpt_installed()

lbl_badge_ag = tk.Label(frame_status_ias, text=f"Antigravity: {'OK' if tem_ag else '-'}", font=("Arial", 8, "bold"), fg="#1e7e34" if tem_ag else "#6c757d")
lbl_badge_ag.pack(side="left", padx=(0, 6))

lbl_badge_claude = tk.Label(frame_status_ias, text=f"Claude: {'OK' if tem_claude else '-'}", font=("Arial", 8, "bold"), fg="#1e7e34" if tem_claude else "#6c757d")
lbl_badge_claude.pack(side="left", padx=6)

lbl_badge_chatgpt = tk.Label(frame_status_ias, text=f"ChatGPT: {'OK' if tem_chatgpt else '-'}", font=("Arial", 8, "bold"), fg="#1e7e34" if tem_chatgpt else "#6c757d")
lbl_badge_chatgpt.pack(side="left", padx=6)

frame_idioma = tk.Frame(frame_cabecalho)
frame_idioma.pack(side="right")

lbl_idioma = tk.Label(frame_idioma, text=t("lbl_idioma"), font=("Arial", 9))
lbl_idioma.pack(side="left")

var_idioma = tk.StringVar(janela)
nome_inverso = {v: k for k, v in IDIOMAS_NOMES.items()}
var_idioma.set(nome_inverso.get(idioma_atual, "Português"))

notebook = ttk.Notebook(janela)
notebook.pack(fill="both", expand=True, padx=8, pady=4)

tab_perfis = ttk.Frame(notebook)
tab_projetos = ttk.Frame(notebook)
tab_ponte = ttk.Frame(notebook)

notebook.add(tab_perfis, text=t("tab_perfis"))
notebook.add(tab_projetos, text=t("tab_projetos"))
notebook.add(tab_ponte, text=t("tab_ponte"))

frame_topo_perfis = tk.LabelFrame(tab_perfis, text=t("frame_create"), padx=10, pady=8)
frame_topo_perfis.pack(padx=10, pady=5, fill="x")

lbl_nome = tk.Label(frame_topo_perfis, text=t("lbl_nome"))
lbl_nome.grid(row=0, column=0, sticky="w")

entrada_nome = tk.Entry(frame_topo_perfis, width=32)
entrada_nome.grid(row=0, column=1, padx=5)

btn_add = tk.Button(frame_topo_perfis, text=t("btn_add"), width=12)
btn_add.grid(row=0, column=2, padx=5)

var_copiar_tudo = tk.BooleanVar(value=False)
chk_copiar = tk.Checkbutton(frame_topo_perfis, text=t("chk_copiar"), variable=var_copiar_tudo)
chk_copiar.grid(row=1, column=0, columnspan=3, sticky="w", pady=(4, 0))

frame_meio_perfis = tk.LabelFrame(tab_perfis, text=t("frame_perfis"), padx=10, pady=8)
frame_meio_perfis.pack(padx=10, pady=5, fill="both", expand=True)

scroll_perfis = tk.Scrollbar(frame_meio_perfis)
scroll_perfis.pack(side="right", fill="y")

lista_perfis = tk.Listbox(frame_meio_perfis, yscrollcommand=scroll_perfis.set, font=("Arial", 10), height=7)
lista_perfis.pack(side="left", fill="both", expand=True)
scroll_perfis.config(command=lista_perfis.yview)

frame_botoes_perfis = tk.Frame(tab_perfis, padx=10, pady=5)
frame_botoes_perfis.pack(fill="x")

btn_abrir_perfil = tk.Button(frame_botoes_perfis, text=t("btn_abrir"), height=2, bg="#d9d9d9")
btn_abrir_perfil.pack(fill="x", pady=2)

btn_proj_perfil = tk.Button(frame_botoes_perfis, text=t("btn_proj"))
btn_proj_perfil.pack(fill="x", pady=2)

btn_atalho_perfil = tk.Button(frame_botoes_perfis, text=t("btn_atalho"))
btn_atalho_perfil.pack(fill="x", pady=2)

btn_del_perfil = tk.Button(frame_botoes_perfis, text=t("btn_del"))
btn_del_perfil.pack(fill="x", pady=2)

frame_topo_hub = tk.Frame(tab_projetos, padx=10, pady=4)
frame_topo_hub.pack(fill="x")

btn_sync_all_hub = tk.Button(frame_topo_hub, text=t("btn_sync_universal"), bg="#e2e8f0", font=("Arial", 9, "bold"), height=2)
btn_sync_all_hub.pack(fill="x", pady=(0, 4))

frame_busca_proj = tk.Frame(tab_projetos, padx=10, pady=2)
frame_busca_proj.pack(fill="x")

lbl_filtrar_proj = tk.Label(frame_busca_proj, text=t("filtrar"), font=("Arial", 9))
lbl_filtrar_proj.pack(side="left")

entrada_filtro_proj = tk.Entry(frame_busca_proj)
entrada_filtro_proj.pack(side="left", fill="x", expand=True, padx=6)

frame_lista_proj = tk.Frame(tab_projetos, padx=10, pady=2)
frame_lista_proj.pack(fill="both", expand=True)

scroll_proj = tk.Scrollbar(frame_lista_proj)
scroll_proj.pack(side="right", fill="y")

lista_projetos = tk.Listbox(frame_lista_proj, yscrollcommand=scroll_proj.set, font=("Arial", 9), height=8)
lista_projetos.pack(side="left", fill="both", expand=True)
scroll_proj.config(command=lista_projetos.yview)

frame_detalhe_proj = tk.LabelFrame(tab_projetos, text=t("lbl_acoes_ia"), padx=10, pady=4)
frame_detalhe_proj.pack(padx=10, pady=4, fill="x")

lbl_info_proj_nome = tk.Label(frame_detalhe_proj, text=t("lbl_selecione_proj"), font=("Arial", 9, "bold"), anchor="w")
lbl_info_proj_nome.pack(fill="x")

lbl_info_proj_path = tk.Label(frame_detalhe_proj, text="", font=("Arial", 8), fg="#555555", anchor="w")
lbl_info_proj_path.pack(fill="x", pady=(1, 2))

frame_linha_ag = tk.Frame(frame_detalhe_proj)
frame_linha_ag.pack(fill="x", pady=2)

lbl_perfil_escolha = tk.Label(frame_linha_ag, text=t("lbl_perfil_alvo"), font=("Arial", 9))
lbl_perfil_escolha.pack(side="left")

var_perfil_para_abrir = tk.StringVar(janela)
opt_perfil_abrir = tk.OptionMenu(frame_linha_ag, var_perfil_para_abrir, "")
opt_perfil_abrir.config(font=("Arial", 9), width=14)
opt_perfil_abrir.pack(side="left", padx=4)

btn_abrir_proj_ag = tk.Button(frame_linha_ag, text=t("btn_abrir_ag"), bg="#d9d9d9")
btn_abrir_proj_ag.pack(side="left", fill="x", expand=True, padx=2)

frame_linha_outras_ias = tk.Frame(frame_detalhe_proj)
frame_linha_outras_ias.pack(fill="x", pady=2)

btn_abrir_proj_claude = tk.Button(frame_linha_outras_ias, text=t("btn_abrir_claude"))
btn_abrir_proj_claude.pack(side="left", fill="x", expand=True, padx=2)

btn_abrir_proj_chatgpt = tk.Button(frame_linha_outras_ias, text=t("btn_abrir_chatgpt"))
btn_abrir_proj_chatgpt.pack(side="left", fill="x", expand=True, padx=2)

btn_abrir_proj_pasta = tk.Button(frame_linha_outras_ias, text=t("btn_abrir_pasta"))
btn_abrir_proj_pasta.pack(side="left", fill="x", expand=True, padx=2)

frame_linha_sync_proj = tk.Frame(frame_detalhe_proj)
frame_linha_sync_proj.pack(fill="x", pady=2)

btn_sync_proj_chats = tk.Button(frame_linha_sync_proj, text=t("btn_sync_este_proj"))
btn_sync_proj_chats.pack(fill="x", expand=True, padx=2)

frame_topo_ponte = tk.Frame(tab_ponte, padx=10, pady=4)
frame_topo_ponte.pack(fill="x")

lbl_projeto_ponte = tk.Label(frame_topo_ponte, text=t("lbl_projeto_topo"), font=("Arial", 9))
lbl_projeto_ponte.pack(side="left")

var_ponte_proj = tk.StringVar(janela)
opt_ponte_proj = tk.OptionMenu(frame_topo_ponte, var_ponte_proj, "")
opt_ponte_proj.config(font=("Arial", 9), width=24)
opt_ponte_proj.pack(side="left", padx=5)

btn_refresh_preview = tk.Button(frame_topo_ponte, text=t("btn_atualizar_ctx"))
btn_refresh_preview.pack(side="left", padx=4)

btn_sync_all_ponte = tk.Button(frame_topo_ponte, text="Sincronizar Tudo", bg="#e2e8f0")
btn_sync_all_ponte.pack(side="right", padx=2)

frame_txt_ponte = tk.Frame(tab_ponte, padx=10, pady=2)
frame_txt_ponte.pack(fill="both", expand=True)

scroll_txt_ponte = tk.Scrollbar(frame_txt_ponte)
scroll_txt_ponte.pack(side="right", fill="y")

txt_preview = tk.Text(frame_txt_ponte, wrap="word", yscrollcommand=scroll_txt_ponte.set, font=("Consolas", 9), height=13)
txt_preview.pack(side="left", fill="both", expand=True)
scroll_txt_ponte.config(command=txt_preview.yview)

frame_botoes_ponte = tk.Frame(tab_ponte, padx=10, pady=6)
frame_botoes_ponte.pack(fill="x")

btn_copiar_prompt = tk.Button(frame_botoes_ponte, text=t("btn_copiar_ctx"), bg="#d9d9d9", height=2)
btn_copiar_prompt.pack(side="left", fill="x", expand=True, padx=3)

btn_exportar_md = tk.Button(frame_botoes_ponte, text=t("btn_exportar_ctx"), height=2)
btn_exportar_md.pack(side="left", fill="x", expand=True, padx=3)

PROJETOS_CACHE = {}
PROJETOS_FILTRADOS = []
PROJETO_SELECIONADO = None

def carregar_lista_perfis():
    lista_perfis.delete(0, tk.END)
    perfis = obter_nomes_perfis()
    for pasta in perfis:
        caminho = os.path.join(PROFILES_DIR, pasta)
        d_proj = os.path.join(caminho, "home", ".gemini", "config", "projects")
        qtd = 0
        if os.path.exists(d_proj):
            qtd = len([f for f in os.listdir(d_proj) if f.endswith(".json") and f != "outside-of-project.json"])
        sufixo = t("projetos_sufixo")
        lista_perfis.insert(tk.END, f"{pasta}  ({qtd} {sufixo})")

    menu_abrir = opt_perfil_abrir["menu"]
    menu_abrir.delete(0, "end")
    if perfis:
        for p in perfis:
            menu_abrir.add_command(label=p, command=lambda v=p: var_perfil_para_abrir.set(v))
        if var_perfil_para_abrir.get() not in perfis:
            var_perfil_para_abrir.set(perfis[0])
    else:
        var_perfil_para_abrir.set("")

def carregar_lista_projetos():
    global PROJETOS_CACHE, PROJETOS_FILTRADOS
    PROJETOS_CACHE = obter_todos_projetos()
    filtrar_projetos()
    atualizar_menu_ponte()

def filtrar_projetos(evento=None):
    global PROJETOS_FILTRADOS
    termo = entrada_filtro_proj.get().strip().lower()
    lista_projetos.delete(0, tk.END)
    PROJETOS_FILTRADOS = []

    ordenados = sorted(PROJETOS_CACHE.values(), key=lambda x: x["name"].lower())
    for p in ordenados:
        if not termo or termo in p["name"].lower() or termo in p["path"].lower():
            PROJETOS_FILTRADOS.append(p)
            chats_txt = f"{p['chats']} {t('conversas_sufixo')}"
            path_txt = f"[{p['path']}]" if p["path"] else "[Sem pasta]"
            lista_projetos.insert(tk.END, f"{p['name']}  -  {chats_txt}  {path_txt}")

def atualizar_menu_ponte():
    menu_ponte = opt_ponte_proj["menu"]
    menu_ponte.delete(0, "end")
    ordenados = sorted(PROJETOS_CACHE.values(), key=lambda x: x["name"].lower())
    if ordenados:
        for p in ordenados:
            label_nome = p["name"]
            menu_ponte.add_command(label=label_nome, command=lambda v=label_nome: selecionar_projeto_ponte(v))
        if not var_ponte_proj.get() or var_ponte_proj.get() not in [x["name"] for x in ordenados]:
            var_ponte_proj.set(ordenados[0]["name"])
            atualizar_preview_ponte()
    else:
        var_ponte_proj.set("")
        txt_preview.delete("1.0", tk.END)

def selecionar_projeto_ponte(nome_projeto):
    var_ponte_proj.set(nome_projeto)
    atualizar_preview_ponte()

def atualizar_preview_ponte():
    nome_projeto = var_ponte_proj.get().strip()
    if not nome_projeto:
        txt_preview.delete("1.0", tk.END)
        return
    txt = gerar_contexto_markdown(nome_projeto)
    txt_preview.delete("1.0", tk.END)
    txt_preview.insert("1.0", txt)

def ao_selecionar_projeto(evento=None):
    global PROJETO_SELECIONADO
    selecao = lista_projetos.curselection()
    if not selecao:
        return
    idx = selecao[0]
    if idx < len(PROJETOS_FILTRADOS):
        p = PROJETOS_FILTRADOS[idx]
        PROJETO_SELECIONADO = p
        lbl_info_proj_nome.config(text=f"{p['name']}  ({p['chats']} {t('conversas_sufixo')})")
        lbl_info_proj_path.config(text=p["path"] if p["path"] else t("erro_sem_pasta"))
        var_ponte_proj.set(p["name"])
        atualizar_preview_ponte()

lista_projetos.bind("<<ListboxSelect>>", ao_selecionar_projeto)
entrada_filtro_proj.bind("<KeyRelease>", filtrar_projetos)

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
    carregar_lista_perfis()
    messagebox.showinfo(t("t_sucesso"), t("sucesso_criado", nome=nome))

def abrir_perfil_selecionado():
    selecao = lista_perfis.curselection()
    if not selecao:
        messagebox.showwarning(t("t_aviso"), t("aviso_selecao"))
        return
    item = lista_perfis.get(selecao[0])
    nome = item.split("  (")[0]
    executar_antigravity(nome)

def criar_atalho():
    selecao = lista_perfis.curselection()
    if not selecao:
        messagebox.showwarning(t("t_aviso"), t("aviso_selecao"))
        return
    item = lista_perfis.get(selecao[0])
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
    selecao = lista_perfis.curselection()
    if not selecao:
        messagebox.showwarning(t("t_aviso"), t("aviso_selecao"))
        return
    item = lista_perfis.get(selecao[0])
    nome = item.split("  (")[0]
    if messagebox.askyesno(t("t_confirma"), t("confirma_del", nome=nome)):
        shutil.rmtree(os.path.join(PROFILES_DIR, nome), ignore_errors=True)
        carregar_lista_perfis()

def gerenciar_projetos_perfil():
    selecao = lista_perfis.curselection()
    if not selecao:
        messagebox.showwarning(t("t_aviso"), t("aviso_selecao"))
        return
    item = lista_perfis.get(selecao[0])
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
        carregar_lista_perfis()
        messagebox.showinfo(t("t_sucesso"), t("sucesso_proj", nome=nome))

    btn_salvar = tk.Button(frame_rodape, text=t("btn_salvar"), command=salvar, width=18, bg="#d9d9d9", height=2)
    btn_salvar.pack(side="left", padx=5)

    btn_cancelar = tk.Button(frame_rodape, text=t("btn_cancelar"), command=lambda: (canvas.unbind_all("<MouseWheel>"), top.destroy()), width=12, height=2)
    btn_cancelar.pack(side="right", padx=5)

def abrir_projeto_antigravity():
    if not PROJETO_SELECIONADO:
        messagebox.showwarning(t("t_aviso"), t("aviso_selecao_proj"))
        return
    perfil = var_perfil_para_abrir.get().strip()
    executar_antigravity(perfil, PROJETO_SELECIONADO.get("path"))

def abrir_projeto_claude():
    if not PROJETO_SELECIONADO:
        messagebox.showwarning(t("t_aviso"), t("aviso_selecao_proj"))
        return
    executar_claude(PROJETO_SELECIONADO.get("path"))

def abrir_projeto_chatgpt():
    if not PROJETO_SELECIONADO:
        messagebox.showwarning(t("t_aviso"), t("aviso_selecao_proj"))
        return
    executar_chatgpt(PROJETO_SELECIONADO.get("path"))

def abrir_projeto_pasta():
    if not PROJETO_SELECIONADO:
        messagebox.showwarning(t("t_aviso"), t("aviso_selecao_proj"))
        return
    abrir_pasta_explorer(PROJETO_SELECIONADO.get("path"))

def copiar_contexto_clipboard():
    nome = var_ponte_proj.get().strip()
    if not nome:
        messagebox.showwarning(t("t_aviso"), t("aviso_selecao_proj"))
        return
    ctx = gerar_contexto_markdown(nome)
    janela.clipboard_clear()
    janela.clipboard_append(ctx)
    messagebox.showinfo(t("t_sucesso"), t("sucesso_copiado"))

def exportar_contexto_arquivo():
    nome = var_ponte_proj.get().strip()
    if not nome:
        messagebox.showwarning(t("t_aviso"), t("aviso_selecao_proj"))
        return
    p_info = None
    for p in PROJETOS_CACHE.values():
        if p["name"].lower() == nome.lower():
            p_info = p
            break
    if not p_info or not p_info.get("path") or not os.path.exists(p_info["path"]):
        messagebox.showwarning(t("t_aviso"), t("erro_sem_pasta"))
        return
    ctx = gerar_contexto_markdown(nome)
    alvo = os.path.join(p_info["path"], ".ai-context.md")
    try:
        with open(alvo, "w", encoding="utf-8") as f:
            f.write(ctx)
        messagebox.showinfo(t("t_sucesso"), t("sucesso_exportado", caminho=alvo))
    except Exception as e:
        messagebox.showerror(t("t_erro"), str(e))

btn_add.config(command=criar_perfil)
btn_abrir_perfil.config(command=abrir_perfil_selecionado)
btn_proj_perfil.config(command=gerenciar_projetos_perfil)
btn_atalho_perfil.config(command=criar_atalho)
btn_del_perfil.config(command=excluir_perfil)

btn_sync_all_hub.config(command=executar_sincronizacao_universal)
btn_sync_proj_chats.config(command=executar_sincronizacao_projeto_atual)
btn_sync_all_ponte.config(command=executar_sincronizacao_universal)

btn_abrir_proj_ag.config(command=abrir_projeto_antigravity)
btn_abrir_proj_claude.config(command=abrir_projeto_claude)
btn_abrir_proj_chatgpt.config(command=abrir_projeto_chatgpt)
btn_abrir_proj_pasta.config(command=abrir_projeto_pasta)

btn_refresh_preview.config(command=atualizar_preview_ponte)
btn_copiar_prompt.config(command=copiar_contexto_clipboard)
btn_exportar_md.config(command=exportar_contexto_arquivo)

def atualizar_textos_interface():
    janela.title(t("title"))
    lbl_idioma.config(text=t("lbl_idioma"))

    notebook.tab(tab_perfis, text=t("tab_perfis"))
    notebook.tab(tab_projetos, text=t("tab_projetos"))
    notebook.tab(tab_ponte, text=t("tab_ponte"))

    frame_topo_perfis.config(text=t("frame_create"))
    lbl_nome.config(text=t("lbl_nome"))
    btn_add.config(text=t("btn_add"))
    chk_copiar.config(text=t("chk_copiar"))
    frame_meio_perfis.config(text=t("frame_perfis"))
    btn_abrir_perfil.config(text=t("btn_abrir"))
    btn_proj_perfil.config(text=t("btn_proj"))
    btn_atalho_perfil.config(text=t("btn_atalho"))
    btn_del_perfil.config(text=t("btn_del"))

    btn_sync_all_hub.config(text=t("btn_sync_universal"))
    lbl_filtrar_proj.config(text=t("filtrar"))
    frame_detalhe_proj.config(text=t("lbl_acoes_ia"))
    lbl_perfil_escolha.config(text=t("lbl_perfil_alvo"))
    btn_abrir_proj_ag.config(text=t("btn_abrir_ag"))
    btn_abrir_proj_claude.config(text=t("btn_abrir_claude"))
    btn_abrir_proj_chatgpt.config(text=t("btn_abrir_chatgpt"))
    btn_abrir_proj_pasta.config(text=t("btn_abrir_pasta"))
    btn_sync_proj_chats.config(text=t("btn_sync_este_proj"))

    lbl_projeto_ponte.config(text=t("lbl_projeto_topo"))
    btn_refresh_preview.config(text=t("btn_atualizar_ctx"))
    btn_copiar_prompt.config(text=t("btn_copiar_ctx"))
    btn_exportar_md.config(text=t("btn_exportar_ctx"))

    carregar_lista_perfis()
    filtrar_projetos()

def mudar_idioma(escolha):
    global idioma_atual
    sigla = IDIOMAS_NOMES.get(escolha, "pt")
    idioma_atual = sigla
    salvar_idioma(sigla)
    atualizar_textos_interface()

opt_idioma = tk.OptionMenu(frame_idioma, var_idioma, *IDIOMAS_NOMES.keys(), command=mudar_idioma)
opt_idioma.config(font=("Arial", 9), width=12)
opt_idioma.pack(side="left", padx=5)

carregar_lista_perfis()
carregar_lista_projetos()
atualizar_textos_interface()

if __name__ == "__main__":
    janela.mainloop()
