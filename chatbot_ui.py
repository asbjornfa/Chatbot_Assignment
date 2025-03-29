import flet as ft
import requests
import threading
from datetime import datetime

# API Endpoint for chat
API_URL = 'http://127.0.0.1:8001/AI/Communicate'


# Simplified theme constants
class AppTheme:
    # Light theme
    LIGHT = {
        "bg": "#F8F9FA",
        "card": "#FFFFFF",
        "sidebar": "#F1F5F9",
        "primary": "#3B82F6",
        "text": "#0c0c0d",
        "text_2": "#0c0c0d",
        "user_msg": "#DBEAFE",
        "ai_msg": "#F1F5F9",
        "system_msg": "#F8FAFC",
        "divider": "#E2E8F0",
        "success": "#10B981"
    }

    # Dark theme
    DARK = {
        "bg": "#0F172A",
        "card": "#1E293B",
        "sidebar": "#0F172A",
        "primary": "#3B82F6",
        "text": "#E2E8F0",
        "text_2": "#94A3B8",
        "user_msg": "#1E40AF",
        "ai_msg": "#1E293B",
        "system_msg": "#1E293B",
        "divider": "#2D3748",
        "success": "#10B981"
    }


def main(page: ft.Page):
    # Initialize state
    current_theme = AppTheme.DARK
    sidebar_width = 240

    # Page setup
    page.window_width = 900
    page.window_height = 800
    page.title = "AI Raider - Dialog Interface"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.bgcolor = current_theme["bg"]

    # Theme toggle function
    def toggle_theme(e):
        nonlocal current_theme
        if page.theme_mode == ft.ThemeMode.DARK:
            page.theme_mode = ft.ThemeMode.LIGHT
            current_theme = AppTheme.LIGHT
            theme_button.icon = ft.Icons.DARK_MODE
        else:
            page.theme_mode = ft.ThemeMode.DARK
            current_theme = AppTheme.DARK
            theme_button.icon = ft.Icons.LIGHT_MODE

        update_theme_colors()
        page.update()

    def update_theme_colors():
        # Update all UI elements with current theme colors
        sidebar.bgcolor = current_theme["sidebar"]
        main_content.bgcolor = current_theme["bg"]
        header.bgcolor = current_theme["card"]
        conversation_container.bgcolor = current_theme["bg"]
        input_container.bgcolor = current_theme["card"]

        # Update text colors
        app_title.color = current_theme["text"]
        current_subject.color = current_theme["text_2"]

        # Update input fields
        subject_input.bgcolor = current_theme["card"]
        subject_input.color = current_theme["text"]
        message_input.bgcolor = current_theme["card"]
        message_input.color = current_theme["text"]

    # Create UI components
    current_subject = ft.Text("No subject selected", size=14, color=current_theme["text_2"])

    subject_input = ft.TextField(
        hint_text="Choose a subject...",
        border_radius=8,
        bgcolor=current_theme["card"],
        color=current_theme["text"],
        label="Subject",
        suffix_icon=ft.Icons.SCIENCE_ROUNDED,
        expand=True
    )

    # Update subject function
    def update_subject(e):
        if subject_input.value.strip():
            current_subject.value = f"Subject: {subject_input.value}"
            message_input.disabled = False
            conversation.controls.clear()
            add_system_message(f"New subject selected: {subject_input.value}\nAsk your questions about this subject.")
            page.update()

    subject_button = ft.ElevatedButton(
        "Set subject",
        icon=ft.Icons.CHECK_CIRCLE_OUTLINED,
        on_click=update_subject,
        bgcolor=current_theme["primary"],
        color=current_theme["card"]
    )

    # Conversation view
    conversation = ft.ListView(
        expand=True,
        spacing=16,
        padding=20,
        auto_scroll=True
    )

    # Message creation functions
    def add_system_message(text):
        conversation.controls.append(
            ft.Container(
                content=ft.Text(text, size=12, color=current_theme["text_2"], text_align=ft.TextAlign.CENTER),
                alignment=ft.alignment.center,
                margin=ft.margin.symmetric(vertical=8),
                padding=ft.padding.all(12),
                bgcolor=current_theme["system_msg"],
                border_radius=12,
                width=400
            )
        )

    def add_user_message(text):
        message_time = datetime.now().strftime("%H:%M")
        conversation.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Text(text, size=14, color=current_theme["text"], selectable=True),
                    ft.Container(
                        content=ft.Text(message_time, size=10, color=current_theme["text_2"]),
                        alignment=ft.alignment.bottom_right,
                        margin=ft.margin.only(top=4)
                    )
                ]),
                alignment=ft.alignment.center_right,
                margin=ft.margin.only(left=60),
                padding=ft.padding.all(12),
                bgcolor=current_theme["user_msg"],
                border_radius=12
            )
        )

    def add_bot_message(text):
        message_time = datetime.now().strftime("%H:%M")
        conversation.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Text(text, size=14, color=current_theme["text"], selectable=True),
                    ft.Container(
                        content=ft.Text(message_time, size=10, color=current_theme["text_2"]),
                        alignment=ft.alignment.bottom_left,
                        margin=ft.margin.only(top=4)
                    )
                ]),
                alignment=ft.alignment.center_left,
                margin=ft.margin.only(right=60),
                padding=ft.padding.all(16),
                bgcolor=current_theme["ai_msg"],
                border_radius=12
            )
        )

    def add_thinking_indicator():
        return ft.Container(
            content=ft.Row([
                ft.ProgressRing(width=16, height=16, stroke_width=2, color=current_theme["primary"]),
                ft.Text("AI is thinking...", size=12, color=current_theme["text_2"])
            ], spacing=10),
            alignment=ft.alignment.center_left,
            margin=ft.margin.only(right=120),
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
            bgcolor=current_theme["ai_msg"],
            border_radius=12
        )

    # Send message function
    def send_message(e=None):
        if not message_input.value.strip() or not subject_input.value.strip():
            return

        user_text = message_input.value
        subject = subject_input.value

        message_input.value = ""
        page.update()
        add_user_message(user_text)

        thinking = add_thinking_indicator()
        conversation.controls.append(thinking)
        page.update()

        def get_response():
            try:
                response = requests.post(
                    API_URL,
                    json={"prompt": user_text, "subject": subject}
                )

                if thinking in conversation.controls:
                    conversation.controls.remove(thinking)

                if response.status_code == 200:
                    bot_text = response.json().get("prompt_response", "Ingen respons modtaget.")
                else:
                    bot_text = f"Fejl: Kunne ikke få svar fra AI (Statuskode: {response.status_code})"

            except Exception as ex:
                bot_text = f"Fejl ved kommunikation med AI-serveren: {str(ex)}"
                if thinking in conversation.controls:
                    conversation.controls.remove(thinking)

            add_bot_message(bot_text)
            page.update()

        threading.Thread(target=get_response, daemon=True).start()

    # Message input field
    message_input = ft.TextField(
        hint_text="Ask your question here...",
        border_radius=12,
        bgcolor=current_theme["card"],
        color=current_theme["text"],
        multiline=True,
        min_lines=1,
        max_lines=5,
        disabled=True,
        expand=True,
        shift_enter=True,  # This enables Enter to submit, Shift+Enter for newline
        on_submit=send_message  # This will trigger when Enter is pressed
    )

    # Action buttons
    send_button = ft.IconButton(
        icon=ft.Icons.SEND_ROUNDED,
        icon_color=current_theme["primary"],
        bgcolor="transparent",
        tooltip="Send besked",
        on_click=send_message
    )

    clear_button = ft.IconButton(
        icon=ft.Icons.DELETE_OUTLINE,
        icon_color=current_theme["text_2"],
        bgcolor="transparent",
        tooltip="Ryd chat",
        on_click=lambda _: conversation.controls.clear() or page.update()
    )

    theme_button = ft.IconButton(
        icon=ft.Icons.LIGHT_MODE,
        icon_color=current_theme["primary"],
        bgcolor="transparent",
        tooltip="Skift tema",
        on_click=toggle_theme
    )

    # App title and icon
    sidebar_icon = ft.Icon(name=ft.Icons.PSYCHOLOGY_ALT, color=current_theme["primary"], size=28)
    app_title = ft.Text("AI Raider", size=20, color=current_theme["text"], weight=ft.FontWeight.BOLD)

    # Build UI layout
    # Sidebar
    sidebar = ft.Container(
        content=ft.Column([
            # Logo and title
            ft.Container(
                content=ft.Row([sidebar_icon, app_title], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
                padding=ft.padding.symmetric(vertical=20)
            ),

            # Subject settings
            ft.Container(
                content=ft.Column([
                    ft.Text("DIALOG SETTINGS", size=12, color=current_theme["text_2"], weight=ft.FontWeight.BOLD),
                    subject_input,
                    ft.Container(content=subject_button, margin=ft.margin.only(top=12)),
                    ft.Divider(color=current_theme["divider"], height=24),
                    current_subject
                ], spacing=8),
                padding=ft.padding.all(16)
            ),

            # Information section
            ft.Container(
                content=ft.Column([
                    ft.Text("INFORMATION", size=12, color=current_theme["text_2"], weight=ft.FontWeight.BOLD),
                    ft.Text("1. Choose a specific topic for the conversation", size=12, color=current_theme["text_2"]),
                    ft.Text("2. AI will tailor its response based on the subject", size=12, color=current_theme["text_2"]),
                    ft.Text("3. Change the subject for a new conversation", size=12, color=current_theme["text_2"])
                ], spacing=8),
                margin=ft.margin.only(top=12),
                padding=ft.padding.all(16)
            ),

            # Status
            ft.Container(
                content=ft.Row([
                    ft.Icon(name=ft.Icons.CIRCLE, color=current_theme["success"], size=16),
                    ft.Text("AIRaider Model v1.0.0", size=12, color=current_theme["text"])
                ]),
                margin=ft.margin.only(top=130),
                bgcolor=current_theme["sidebar"],
                padding=ft.padding.all(20),

            )
        ]),
        width=sidebar_width,
        bgcolor=current_theme["sidebar"]
    )

    # Header
    header = ft.Container(
        content=ft.Row([
            ft.Text("Dialog with AI", size=18, color=current_theme["text_2"], weight=ft.FontWeight.BOLD),
            ft.Row([theme_button, clear_button])
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=ft.padding.symmetric(horizontal=20, vertical=12),
        bgcolor=current_theme["card"]
    )

    # Conversation area
    conversation_container = ft.Container(
        content=conversation,
        expand=True,
        bgcolor=current_theme["bg"]
    )

    # Input area
    input_container = ft.Container(
        content=ft.Row([message_input, send_button], spacing=12),
        padding=ft.padding.all(16),
        bgcolor=current_theme["card"]
    )

    # Main layout
    main_content = ft.Container(
        content=ft.Column([header, conversation_container, input_container]),
        expand=True,
        bgcolor=current_theme["bg"]
    )

    # Add to page
    page.add(
        ft.Row([sidebar, main_content], spacing=0, expand=True)
    )

    # Welcome message
    add_system_message("Welcome to AI Raider!\nChoose a topic to start a conversation.")


# Start application
if __name__ == "__main__":
    ft.app(target=main)