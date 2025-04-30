from textual.app import App, ComposeResult
from textual.widgets import Input, Static, LoadingIndicator, Footer
from textual.binding import Binding
from chatbot import ChatBot
import asyncio

class Pager(Static):
    """
    A simple widget to display text pages.
    """
    can_focus = True
    def show_page(self, content: str) -> None:
        self.update(content)

class PromptDisplay(Static):
    def show_prompt(self, prompt: str) -> None:
        self.update(f"[Bold]User: [/] {prompt}")

class TextPagerApp(App[None]):
    BINDINGS = [
        Binding("left", "prev_page", "Previous Page"),
        Binding("right", "next_page", "Next Page"),
        Binding("enter", "focus_input", "Focus Input"),
        Binding("escape", "unfocus_input", "Unfocus Input")
    ]

    CSS = """
    Screen {
        layout: vertical;
        align: center middle;
    }
    Pager {
        height: 1fr;
        width: 100%;
        padding: 1;
        border: solid green;
    }
    PromptDisplay {
        height: 3;
        width: 100%;
        padding: 1;
        border: solid yellow;
    }
    Input {
        width: 100%;
        border: solid blue;
    }
    LoadingIndicator {
        dock: bottom;
        padding: 1;
    }
    """

    def __init__(self, pages: list[str], chatbot, **kwargs):
        super().__init__(**kwargs)
        self.pages = pages
        self.current_index = 0
        self.chatbot = chatbot

    def compose(self) -> ComposeResult:
        page = self.pages[self.current_index]
        if isinstance(page, dict):
            resp = page.get("response", "")
        else:
            resp = page
            
        yield Pager(resp, id="pager")
        yield PromptDisplay("", id="prompt_display")
        yield Input(placeholder="Type and press Enter to add a page...", id="cmd_input")
        yield LoadingIndicator(id="loading")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(PromptDisplay).display = False
        self.query_one(LoadingIndicator).display = False
        # Ensure initial focus and correct widget visibility
        self.update_view()
        self.set_focus(self.query_one(Input))

    def update_view(self) -> None:
        page = self.pages[self.current_index]
        if isinstance(page, dict):
            resp = page.get("response", "")
            prompt = page.get("prompt")
        else:
            resp = page
            prompt = None
        self.query_one(Pager).show_page(resp)
        prompt_widget = self.query_one(PromptDisplay)
        input_widget = self.query_one(Input)
        if prompt:
            prompt_widget.display = True
            prompt_widget.show_prompt(prompt)
            input_widget.display = False
        else:
            prompt_widget.display = False
            input_widget.display = True

    def action_next_page(self) -> None:
        if len(self.pages) > 1:
            self.current_index = (self.current_index + 1) % len(self.pages)
            self.update_view()

    def action_prev_page(self) -> None:
        if len(self.pages) > 1:
            self.current_index = (self.current_index - 1) % len(self.pages)
            self.update_view()

    def action_focus_input(self) -> None:
        self.set_focus(self.query_one(Input))

    def action_unfocus_input(self) -> None:
        self.set_focus(self.query_one(Pager))

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        # Add input text as a new page and display it
        prompt = event.value.strip()
        if not prompt:
            prompt = "You are a dungeon master in a fantasy text adventure. Respond to the player's commands with vivid, " \
            "story-driven descriptions and react to their actions. Keep the world internally consistent. " \
            "Do not advance time unless the player acts. Never take control of the player's character. " \
            "The story begins with the player in a cave chained to a wall. Begin"
        
        # Show spinner while waiting
        spinner = self.query_one(LoadingIndicator)
        spinner.display = True
        self.refresh(layout=True)

        # Run blocking LLM call in thread
        try:
            _, response = await asyncio.to_thread(self.chatbot.prompt, prompt)
        except Exception as err:
            response = f"[red]Error:[/] {err}"
        finally:
            spinner.display = False

        # Hide spinner and update pages
        spinner.display = False
        last_index = len(self.pages) - 1
        self.pages[last_index]["prompt"] = prompt
        self.pages.append({"response": response, "prompt": None})
        self.current_index = len(self.pages) - 1
        event.input.value = ""
        # Return focus to pager so arrow keys work
        self.update_view()

if __name__ == "__main__":
    chatbot = ChatBot()
    # Initialize with only the first page
    sample_pages = [
        { "response": "Hello, welcome to our text adventure app. This is powered by Ollama and PygmalionAI. Press enter below to start. Use arrow keys to navigate between pages.",
         "prompt": None
        }
    ]
    app = TextPagerApp(pages=sample_pages, chatbot=chatbot)
    app.run()