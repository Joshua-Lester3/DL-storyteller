from textual.app import App, ComposeResult
from textual.widgets import Input, Static, LoadingIndicator, Footer, Button, Select
from textual.containers import Horizontal, Vertical
from textual.binding import Binding
from improved_chatbot import ChatBot
import asyncio
import time

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
        
class StatusDisplay(Static):
    def show_status(self, message: str) -> None:
        self.update(f"[italic]{message}[/]")

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
    
    #main_vertical {
        height: 100%;
        width: 100%;
    }
    
    #controls {
        width: 100%;
        height: auto;
        padding: 1;
        background: $surface;
    }
    
    Pager {
        height: 1fr;
        width: 100%;
        padding: 1;
        border: solid green;
        overflow-y: scroll;
    }
    
    PromptDisplay {
        height: auto;
        width: 100%;
        padding: 1;
        border: solid yellow;
    }
    
    StatusDisplay {
        height: 1;
        width: 100%;
        background: $boost;
        color: $text-muted;
    }
    
    Input {
        width: 1fr;
        border: solid blue;
    }
    
    LoadingIndicator {
        height: 1;
    }
    
    Button {
        min-width: 15;
    }
    
    Select {
        width: 25;
    }
    """

    def __init__(self, pages: list[str], chatbot, **kwargs):
        super().__init__(**kwargs)
        self.pages = pages
        self.current_index = 0
        self.chatbot = chatbot

    def compose(self) -> ComposeResult:
        with Vertical(id="main_vertical"):
            # Top controls row
            with Horizontal(id="controls"):
                yield Select(
                    [(m, m) for m in [
                        "Pygmalion-3-12B-Q3_K.gguf",
                        "Pygmalion-3-8B-Q3_K.gguf",
                        "Pygmalion-3-6B-Q3_K.gguf",
                    ]],
                    value="Pygmalion-3-12B-Q3_K.gguf",
                    id="model_select"
                )
                yield Button("Change Model", id="change_model_btn")
                yield Button("Use GPU", id="gpu_toggle", variant="success")
                
            # Content area
            page = self.pages[self.current_index]
            if isinstance(page, dict):
                resp = page.get("response", "")
            else:
                resp = page
                
            yield Pager(resp, id="pager")
            yield StatusDisplay("Ready", id="status_display")
            yield PromptDisplay("", id="prompt_display")
            
            # Bottom input area
            with Horizontal():
                yield Input(placeholder="Type and press Enter to add a page...", id="cmd_input")
                yield LoadingIndicator(id="loading")
            
            yield Footer()

    def on_mount(self) -> None:
        self.query_one(PromptDisplay).display = False
        self.query_one(LoadingIndicator).display = False
        # Set initial GPU state
        self.use_gpu = True
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
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        
        # Toggle GPU usage
        if button_id == "gpu_toggle":
            self.use_gpu = not self.use_gpu
            if self.use_gpu:
                event.button.variant = "success"
                event.button.label = "Use GPU"
                self.query_one(StatusDisplay).show_status("GPU mode enabled")
            else:
                event.button.variant = "default"
                event.button.label = "Use CPU"
                self.query_one(StatusDisplay).show_status("CPU mode enabled")
                
        # Change model
        if button_id == "change_model_btn":
            model_select = self.query_one(Select)
            model_name = model_select.value
            self.query_one(StatusDisplay).show_status(f"Changing model to {model_name}...")
            asyncio.create_task(self.change_model(model_name))
            
    async def change_model(self, model_name):
        """Change the chatbot model"""
        try:
            # Show loading indicator
            spinner = self.query_one(LoadingIndicator)
            spinner.display = True
            
            # Create new chatbot with selected model
            self.chatbot = await asyncio.to_thread(
                ChatBot, 
                model_name=model_name, 
                use_gpu=self.use_gpu
            )
            
            self.query_one(StatusDisplay).show_status(f"Model changed to {model_name}")
        except Exception as err:
            self.query_one(StatusDisplay).show_status(f"Error: {err}")
        finally:
            spinner.display = False

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
        status = self.query_one(StatusDisplay)
        start_time = time.time()
        status.show_status("Generating response...")
        self.refresh(layout=True)

        # Run blocking LLM call in thread
        try:
            _, response = await asyncio.to_thread(self.chatbot.prompt, prompt)
            elapsed = time.time() - start_time
            status.show_status(f"Response generated in {elapsed:.2f} seconds")
        except Exception as err:
            response = f"[red]Error:[/] {err}"
            status.show_status(f"Error: {err}")
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
    chatbot = ChatBot(use_gpu=True)
    # Initialize with only the first page
    sample_pages = [
        { "response": "Hello, welcome to our text adventure app. This is powered by Ollama and PygmalionAI. Press enter below to start. Use arrow keys to navigate between pages.",
         "prompt": None
        }
    ]
    app = TextPagerApp(pages=sample_pages, chatbot=chatbot)
    app.run()
