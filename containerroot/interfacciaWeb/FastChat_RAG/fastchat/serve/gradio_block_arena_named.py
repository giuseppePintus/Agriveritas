"""
Chatbot Arena (side-by-side) tab.
Users chat with two chosen models.
"""

import json
import time

import gradio as gr
import numpy as np
from copy import deepcopy

from fastchat.constants import (
    MODERATION_MSG,
    CONVERSATION_LIMIT_MSG,
    INPUT_CHAR_LEN_LIMIT,
    CONVERSATION_TURN_LIMIT,
)
from fastchat.model.model_adapter import get_conversation_template
from fastchat.serve.gradio_web_server import (
    State,
    bot_response,
    get_conv_log_filename,
    no_change_btn,
    enable_btn,
    disable_btn,
    invisible_btn,
    acknowledgment_md,
    get_ip,
    log_upload, upload_document,
    retrieve_documents
)
from fastchat.serve.remote_logger import get_remote_logger
from fastchat.utils import (
    build_logger,
    moderation_filter,
)

# >> Templates for RAG cards
from jinja2 import Environment, FileSystemLoader
# Set up the template environment with the templates directory
env = Environment(loader=FileSystemLoader('style/templates'))
context_html_template = env.get_template('fancy_context_html_template.j2')

# List of buttons as globoal vars
no_change_btn = gr.Button()
no_change_radio = gr.Radio()
enable_radio = gr.Radio(interactive=True, visible=True)
enable_btn = gr.Button(interactive=True, visible=True)
disable_btn = gr.Button(interactive=False)
disable_radio = gr.Radio(interactive=False)
invisible_btn = gr.Button(interactive=False, visible=False)
invisible_html = gr.HTML()

logger = build_logger("gradio_web_server_multi", "gradio_web_server_multi.log")

num_sides = 2
enable_moderation = False

from fastchat.rag_constants import *
temperature = TEMPERATURE
top_p = TOP_P
max_new_tokens = MAX_NEW_TOKENS
repetition_penalty = REP_PENALTY


def set_global_vars_named(enable_moderation_):
    global enable_moderation
    enable_moderation = enable_moderation_


def load_demo_side_by_side_named(models, url_params):
    states = (None,) * num_sides

    model_left = models[0] if len(models) > 0 else ""
    if len(models) > 1:
        weights = ([8] * 4 + [4] * 8 + [1] * 32)[: len(models) - 1]
        weights = weights / np.sum(weights)
        model_right = np.random.choice(models[1:], p=weights)
    else:
        model_right = model_left

    selector_updates = (
        gr.Dropdown(choices=models, value=model_left, visible=True),
        gr.Dropdown(choices=models, value=model_right, visible=True),
    )

    return states + selector_updates


def vote_last_response(states, vote_type, model_selectors, request: gr.Request):
    with open(get_conv_log_filename(), "a") as fout:
        data = {
            "tstamp": round(time.time(), 4),
            "type": vote_type,
            "models": [x for x in model_selectors],
            "states": [x.dict() for x in states],
            "ip": get_ip(request),
        }
        fout.write(json.dumps(data) + "\n")
    get_remote_logger().log(data)


def leftvote_last_response(
    state0, state1, model_selector0, model_selector1, request: gr.Request
):
    logger.info(f"leftvote (named). ip: {get_ip(request)}")
    vote_last_response(
        [state0, state1], "leftvote", [model_selector0, model_selector1], request
    )
    return ("",) + (disable_btn,) * 4


def rightvote_last_response(
    state0, state1, model_selector0, model_selector1, request: gr.Request
):
    logger.info(f"rightvote (named). ip: {get_ip(request)}")
    vote_last_response(
        [state0, state1], "rightvote", [model_selector0, model_selector1], request
    )
    return ("",) + (disable_btn,) * 4


def tievote_last_response(
    state0, state1, model_selector0, model_selector1, request: gr.Request
):
    logger.info(f"tievote (named). ip: {get_ip(request)}")
    vote_last_response(
        [state0, state1], "tievote", [model_selector0, model_selector1], request
    )
    return ("",) + (disable_btn,) * 4


def bothbad_vote_last_response(
    state0, state1, model_selector0, model_selector1, request: gr.Request
):
    logger.info(f"bothbad_vote (named). ip: {get_ip(request)}")
    vote_last_response(
        [state0, state1], "bothbad_vote", [model_selector0, model_selector1], request
    )
    return ("",) + (disable_btn,) * 4


def log_quality(state0, state1, quality_value_a, quality_value_b, model_selector0, model_selector1, request: gr.Request):
    """
    Log the quality of the answer

    quality_button.click(
        log_quality,
        [states, quality_value_a, quality_value_b, model_selectors],
        [quality_value_a, quality_value_b, quality_button]
    )
    """
    if quality_value_a or quality_value_b:
        # if user selected a quality value (!= None)
        ip = get_ip(request)
        logger.info(f"quality score. ip: {ip} --> {quality_value_a} | {quality_value_b}")

        if quality_value_a:
            vote_last_response([state0], quality_value_a, [model_selector0], request)
        
        if quality_value_b:
            vote_last_response([state1], quality_value_b, [model_selector1], request)

        return (disable_radio, disable_radio, disable_btn)

    return (no_change_radio, no_change_radio, no_change_btn)


def regenerate(state0, state1, request: gr.Request):
    logger.info(f"regenerate (named). ip: {get_ip(request)}")
    states = [state0, state1]
    if state0.regen_support and state1.regen_support:
        for i in range(num_sides):
            states[i].conv.update_last_message(None)
        return (
            states + [x.to_gradio_chatbot() for x in states] + [""] + [disable_btn] * 6 + [disable_radio, disable_radio, disable_btn]
        )
    states[0].skip_next = True
    states[1].skip_next = True
    return states + [x.to_gradio_chatbot() for x in states] + [""] + [no_change_btn] * 6 + [disable_radio, disable_radio, disable_btn]


def clear_history(request: gr.Request):
    logger.info(f"clear_history (named). ip: {get_ip(request)}")
    return (
        [None] * num_sides
        + [None] * num_sides
        + [""]
        + [invisible_btn] * 4
        + [disable_btn] * 2
    )


def share_click(state0, state1, model_selector0, model_selector1, request: gr.Request):
    logger.info(f"share (named). ip: {get_ip(request)}")
    if state0 is not None and state1 is not None:
        vote_last_response(
            [state0, state1], "share", [model_selector0, model_selector1], request
        )


def add_text(
    state0, state1, model_selector0, model_selector1, text, image, request: gr.Request
):
    ip = get_ip(request)
    logger.info(f"add_text (named). ip: {ip}. len: {len(text)}")
    states = [state0, state1]
    model_selectors = [model_selector0, model_selector1]

    # Init states if necessary
    for i in range(num_sides):
        if states[i] is None:
            states[i] = State(model_selectors[i])

    if len(text) <= 0:
        for i in range(num_sides):
            states[i].skip_next = True
        return (
            states
            + [x.to_gradio_chatbot() for x in states]
            + ["", None]
            + [
                no_change_btn,
            ]
            * 6
            + [disable_radio, disable_radio, disable_btn]
        )

    model_list = [states[i].model_name for i in range(num_sides)]
    all_conv_text_left = states[0].conv.get_prompt()
    all_conv_text_right = states[0].conv.get_prompt()
    all_conv_text = (
        all_conv_text_left[-1000:] + all_conv_text_right[-1000:] + "\nuser: " + text
    )
    flagged = moderation_filter(all_conv_text, model_list)
    if flagged:
        logger.info(f"violate moderation (named). ip: {ip}. text: {text}")
        # overwrite the original text
        text = MODERATION_MSG

    conv = states[0].conv
    if (len(conv.messages) - conv.offset) // 2 >= CONVERSATION_TURN_LIMIT:
        logger.info(f"conversation turn limit. ip: {ip}. text: {text}")
        for i in range(num_sides):
            states[i].skip_next = True
        return (
            states
            + [x.to_gradio_chatbot() for x in states]
            + [CONVERSATION_LIMIT_MSG, None]
            + [
                no_change_btn,
            ]
            * 6
            + [disable_radio, disable_radio, disable_btn]
        )

    text = text[:INPUT_CHAR_LEN_LIMIT]  # Hard cut-off


    # >> Retrieval
    prompt_w_context = retrieve_documents(text)

    for i in range(num_sides):
        post_processed_text = prompt_w_context

        # Format data with roles (w/ context for model inference)
        states[i].conv.append_message(states[i].conv.roles[0], post_processed_text)
        states[i].conv.append_message(states[i].conv.roles[1], None)

        # (w/o context for chat GUI)
        states[i].conv_wo_context.append_message(states[i].conv.roles[0], text)
        states[i].conv_wo_context.append_message(states[i].conv.roles[1], None)

        states[i].skip_next = False

    return (
        states
        + [x.to_gradio_chatbot() for x in states]
        + ["", None]
        + [
            disable_btn,
        ]
        * 6
        + [disable_radio, disable_radio, disable_btn]
    )


def bot_response_multi(
    state0,
    state1,
    request: gr.Request,
):
    """
    OUTPUT:
    states + chatbots + [context_html] + btn_list + score_list,
    """

    logger.info(f"bot_response_multi (named). ip: {get_ip(request)}")

    documents_html = [{"source" : "", "year" : "", "title" : "", "content" : "..."}]
    context_html = context_html_template.render(documents=documents_html)

    if state0.skip_next:
        # This generate call is skipped due to invalid inputs
        yield (
            state0,
            state1,
            state0.to_gradio_chatbot(),
            state1.to_gradio_chatbot(),
        ) + context_html + (no_change_btn,) * 6 + (no_change_radio, no_change_radio, no_change_btn)
        return

    states = [state0, state1]
    gen = []
    for i in range(num_sides):
        out_resp = bot_response(
            states[i],
            request,
            already_retrieved_context_html=None if i==0 else ""
        )
        gen.append(out_resp)

    is_stream_batch = []
    for i in range(num_sides):
        is_stream_batch.append(
            states[i].model_name
            in [
                "gemini-pro",
                "gemini-pro-dev-api",
                "gemma-1.1-2b-it",
                "gemma-1.1-7b-it",
            ]
        )

    chatbots = [None] * num_sides
    iters = 0
    context_html = ""
    while True:
        stop = True
        iters += 1
        for i in range(num_sides):
            try:
                # yield gemini fewer times as its chunk size is larger
                # otherwise, gemini will stream too fast
                if not is_stream_batch[i] or (iters % 30 == 1 or iters < 3):
                    ret = next(gen[i])
                    states[i], chatbots[i] = ret[0], ret[1]
                    if i==0: context_html = ret[2]
                stop = False
            except StopIteration:
                pass
        yield states + chatbots + [context_html] + [disable_btn] * 6 + [enable_radio, enable_radio, enable_btn]
        
        if stop:
            break


def flash_buttons():
    btn_updates = [
        [disable_btn] * 4 + [enable_btn] * 2,
        [enable_btn] * 6,
    ]
    for i in range(4):
        yield btn_updates[i % 2]
        time.sleep(0.3)


def build_side_by_side_ui_named(models):
    notice_markdown = """
# <span style="color:orange">A</span>ss<span style="color:orange">i</span>stente <span style="color:blue">x</span> Codice degli Appalti D.Lgs. 36/2023
### Modelli IA a confronto

Scegli due modelli da confrontare e vota la risposta migliore!
"""

    states = [gr.State() for _ in range(num_sides)]
    model_selectors = [None] * num_sides
    chatbots = [None] * num_sides

    notice = gr.Markdown(notice_markdown, elem_id="notice_markdown")

    # ----------------------------------------------------------------------
    # >> PANEL MODELS A & B side by side
    #with gr.Group(elem_id="share-region-named"):
    with gr.Blocks(elem_id="main_block"):
        with gr.Row(elem_id="left_right_disposiion"):

            with gr.Column(elem_id="share-region-named", scale=3):
                with gr.Row():
                    for i in range(num_sides):
                        with gr.Column():
                            model_selectors[i] = gr.Dropdown(
                                choices=models,
                                value=models[i] if len(models) > i else "",
                                interactive=True,
                                show_label=False,
                                container=False,
                            )

                with gr.Row():
                    for i in range(num_sides):
                        label = "Modello A" if i == 0 else "Modello B"
                        with gr.Column():
                            chatbots[i] = gr.Chatbot(
                                label=label,
                                elem_id=f"chatbot",
                                height=550,
                                show_copy_button=True,
                                avatar_images=('assets/user_avatar.png', # user
                                                'assets/assistant_icon.png'), # agent
                                bubble_full_width=False
                            )


                # ----------------------------------------------------------------------
                # >> Input text
                with gr.Row():
                    textbox = gr.Textbox(
                        show_label=False,
                        placeholder="La tua domanda ...",
                        elem_id="input_box",
                    )
                    send_btn = gr.Button(value="💬 Invia", variant="primary", scale=0)

                # ----------------------------------------------------------------------
                # >> Regenerate or Delete
                with gr.Row() as button_row:
                    clear_btn = gr.Button(value="🗑️ Cancella chat", interactive=False)
                    regenerate_btn = gr.Button(value="🔄  Rigenera risposte", interactive=False)

                # *************
                # SCORING
                gr.Markdown("## Valutazione delle risposte")

                with gr.Column():
                    # ----------------------------------------------------------------------
                    # >> Comparison better/worse
                    with gr.Row():
                        leftvote_btn = gr.Button(
                            value="👈  A è meglio", visible=True, interactive=False
                        )
                        rightvote_btn = gr.Button(
                            value="👉  B è meglio", visible=True, interactive=False
                        )
                        tie_btn = gr.Button(value="🤝  Pareggio", visible=True, interactive=False)
                        bothbad_btn = gr.Button(
                            value="👎  Entrambi errati", visible=True, interactive=False
                        )

                    # ------------------------------------------------------------------------
                    # >>> Scoring System
                    
                    with gr.Row():
                        quality_value_a = gr.Radio(
                            choices=[
                                "Eccellente",
                                "Soddisfacente",
                                "Insufficiente"
                            ],
                            value=None,
                            label='Valutazione di qualità: risposta A',
                            interactive=False
                        )
                        quality_value_b = gr.Radio(
                            choices=[
                                "Eccellente",
                                "Soddisfacente",
                                "Insufficiente"
                            ],
                            value=None,
                            label='Valutazione di qualità: risposta B',
                            interactive=False
                        )

                    quality_button = gr.Button(value="📝 Valuta", variant="primary", interactive=False)


                # ----------------------------------------------------------------------
                # >> Load Documents
                gr.Markdown("## Caricamento Nuove Fonti Giuridiche")
                # >>> Data Upload
                with gr.Column():
                    with gr.Row():
                        doc_src = gr.Textbox(
                            show_label=False,
                            placeholder="Fonte Giuridica",
                            elem_id="upload_src"
                        )
                        doc_year = gr.Textbox(
                            show_label=False,
                            placeholder="Anno di emanazione",
                            elem_id="upload_year"
                        )
                        doc_title = gr.Textbox(
                            show_label=False,
                            placeholder="Titolo",
                            elem_id="upload_title"
                        )
                        
                    # Upload document
                    with gr.Row():
                        upload_button = gr.UploadButton(label="📎 Allega", file_types=[".pdf",".docx", ".txt"], file_count="multiple")
                        load_button = gr.Button(value="📤 Carica", interactive=False)

            with gr.Column(elem_id="retrieval_cards_frame", scale=1):
                context_html = gr.HTML()
    
    # ----------------------------------------------------------------------
    # >> Buttons and callback functions

    # Register listeners
    imagebox = gr.State(None)

    score_list = [quality_value_a, quality_value_b, quality_button]

    # >>> VOTING
    # - Preference
    btn_list = [
        leftvote_btn,
        rightvote_btn,
        tie_btn,
        bothbad_btn,
        regenerate_btn,
        clear_btn,
    ]
    leftvote_btn.click(
        leftvote_last_response,
        states + model_selectors,
        [textbox, leftvote_btn, rightvote_btn, tie_btn, bothbad_btn],
    )
    rightvote_btn.click(
        rightvote_last_response,
        states + model_selectors,
        [textbox, leftvote_btn, rightvote_btn, tie_btn, bothbad_btn],
    )
    tie_btn.click(
        tievote_last_response,
        states + model_selectors,
        [textbox, leftvote_btn, rightvote_btn, tie_btn, bothbad_btn],
    )
    bothbad_btn.click(
        bothbad_vote_last_response,
        states + model_selectors,
        [textbox, leftvote_btn, rightvote_btn, tie_btn, bothbad_btn],
    )

    # - Quality
    quality_button.click(
        log_quality,
        states + [quality_value_a, quality_value_b] + model_selectors,
        [quality_value_a, quality_value_b, quality_button]
    )

    # Callback REGEN
    regenerate_btn.click(
        regenerate, states, states + chatbots + [textbox] + btn_list + score_list
    ).then(
        bot_response_multi,
        states,
        states + chatbots + [context_html] + btn_list + score_list,
    ).then(
        flash_buttons, [], btn_list
    )
    # Callback CLEAR
    clear_btn.click(clear_history, None, states + chatbots + [textbox] + btn_list)

    for i in range(num_sides):
        model_selectors[i].change(
            clear_history, None, states + chatbots + [textbox] + btn_list
        )
    
    # >>> UPLOAD FILES
    upload_button.upload(
        log_upload,
        [upload_button],
        [load_button]
    )

    load_button.click(
        upload_document,
        [upload_button, doc_src, doc_title, doc_year],
        [doc_src, doc_title, doc_year, load_button]
    )

    # >>> CHAT HANDLING
    textbox.submit(
        add_text,
        states + model_selectors + [textbox, imagebox],
        states + chatbots + [textbox, imagebox] + btn_list + score_list,
    ).then(
        bot_response_multi,
        states,
        states + chatbots + [context_html] + btn_list + score_list,
    ).then(
        flash_buttons, [], btn_list
    )
    send_btn.click(
        add_text,
        states + model_selectors + [textbox, imagebox],
        states + chatbots + [textbox, imagebox] + btn_list,
    ).then(
        bot_response_multi,
        states,
        states + chatbots + [context_html] + btn_list + score_list,
    ).then(
        flash_buttons, [], btn_list
    )

    return states + model_selectors
